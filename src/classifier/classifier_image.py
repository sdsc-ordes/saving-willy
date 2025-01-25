import streamlit as st
import logging

# get a global var for logger accessor in this module
LOG_LEVEL = logging.DEBUG
g_logger = logging.getLogger(__name__)
g_logger.setLevel(LOG_LEVEL)

import whale_viewer as viewer
from hf_push_observations import push_observations
from utils.grid_maker import gridder
from utils.metadata_handler import metadata2md

# need to divide this into two functions, one for the classification and one for the display
# it is currently somewhat interleaved, not totally clear how to separate them.
# perhaps we have more stages than I realised.
# ML started, ML completed, manual review completed, data uploaded

# for now, let's implement the division between ML classification, and display+manual review. 

def cetacean_classify_list(cetacean_classifier):
    success = False
    
    files = st.session_state.files
    images = st.session_state.images
    observations = st.session_state.observations

    #batch_size, row_size, page = gridder(files)
    #grid = st.columns(row_size)
    #col = 0

    for file in files: 
        key = file.name
        image = images[key]
        
        observation = observations[key].to_dict()
        # run classifier model on `image`, and persistently store the output
        out = cetacean_classifier(image) # get top 3 matches
        st.session_state.whale_prediction1[key] = out['predictions'][0]
        st.session_state.classify_whale_done[key] = True # TODO 25.01 unclear what this is for; 
        msg = f"[D]2 classify_whale_done: {st.session_state.classify_whale_done[key]}, whale_prediction1: {st.session_state.whale_prediction1[key]}"
        g_logger.info(msg)

        observations[key].set_top_predictions(out['predictions'][:])
        
        st.session_state.public_observation[key] = observation # 
        msg = f"[D] full observation after inference: {observation}"
        g_logger.debug(msg)
        print(msg)
    
    # TODO: add some mech to test if it was successful. 
    success = True
    st.balloons()
    return success

def cetacean_show_classifications():
    st.write("TOP TEXT")
    st.write("Reviewing the classifications :construction:")
    files = st.session_state.files
    images = st.session_state.images
    observations = st.session_state.observations

    batch_size, row_size, page = gridder(files)
    
    grid = st.columns(row_size)
    col = 0

    for file in files: 
        key = file.name
        image = images[key]
        
        with grid[col]:
            st.image(image, use_column_width=True)
            observation = observations[key].to_dict()
            # fetch the classification results
            # run classifier model on `image`, and persistently store the output
            msg = f"[D]2b classify_whale_done ({file}): {st.session_state.classify_whale_done[key]}, whale_prediction1: {st.session_state.whale_prediction1[key]}"
            g_logger.info(msg)
            
            # dropdown for selecting/overriding the species prediction
            # TODO: the "it's done" flag seems to get reset when we re-load the tab. Not quite right.
            if not st.session_state.classify_whale_done[key]:
                #selected_class = st.sidebar.selectbox("Species", viewer.WHALE_CLASSES, 
                # TODO: ask LV why it is in the sidebar, and not in the grid
                selected_class = st.selectbox("Species", viewer.WHALE_CLASSES, 
                                            index=None, placeholder="Species not yet identified...", 
                                            disabled=True, key=f"cldd_{key}")
            else:
                pred1 = st.session_state.whale_prediction1[key]
                # get index of pred1 from WHALE_CLASSES, none if not present
                print(f"[D] pred1: {pred1}")
                ix = viewer.WHALE_CLASSES.index(pred1) if pred1 in viewer.WHALE_CLASSES else None
                selected_class = st.selectbox(f"Species for {file.name}", viewer.WHALE_CLASSES, index=ix)
            
            observation['predicted_class'] = selected_class
            if selected_class != st.session_state.whale_prediction1[key]:
                observation['class_overriden'] = selected_class
            
            st.session_state.public_observation = observation
            st.button(f"Upload observation for {file.name} to THE INTERNET!", on_click=push_observations)
            # TODO: the metadata only fills properly if `validate` was clicked.
            st.markdown(metadata2md())

            msg = f"[D] full observation after inference: {observation}"
            g_logger.debug(msg)
            print(msg)
            # TODO: add a link to more info on the model, next to the button.
            whale_classes = observations[key].top_predictions
            # render images for the top 3 (that is what the model api returns)
            n = len(whale_classes)
            st.markdown(f"Top {n} Predictions for {file.name}")
            for i in range(n):
                viewer.display_whale(whale_classes, i)
        col = (col + 1) % row_size
    return True


def cetacean_classify_and_review(cetacean_classifier):
    files = st.session_state.files
    images = st.session_state.images
    observations = st.session_state.observations

    batch_size, row_size, page = gridder(files)
    
    grid = st.columns(row_size)
    col = 0

    for file in files: 
        image = images[file.name]
        
        with grid[col]:
            st.image(image, use_column_width=True)
            observation = observations[file.name].to_dict()
            # run classifier model on `image`, and persistently store the output
            out = cetacean_classifier(image) # get top 3 matches
            st.session_state.whale_prediction1 = out['predictions'][0]
            st.session_state.classify_whale_done = True
            msg = f"[D]2 classify_whale_done: {st.session_state.classify_whale_done}, whale_prediction1: {st.session_state.whale_prediction1}"
            g_logger.info(msg)
            
            # dropdown for selecting/overriding the species prediction
            if not st.session_state.classify_whale_done:
                selected_class = st.sidebar.selectbox("Species", viewer.WHALE_CLASSES, 
                                                                index=None, placeholder="Species not yet identified...", 
                                                                disabled=True)
            else:
                pred1 = st.session_state.whale_prediction1
                # get index of pred1 from WHALE_CLASSES, none if not present
                print(f"[D] pred1: {pred1}")
                ix = viewer.WHALE_CLASSES.index(pred1) if pred1 in viewer.WHALE_CLASSES else None
                selected_class = st.selectbox(f"Species for {file.name}", viewer.WHALE_CLASSES, index=ix)
            
            observation['predicted_class'] = selected_class
            if selected_class != st.session_state.whale_prediction1:
                observation['class_overriden'] = selected_class
            
            st.session_state.public_observation = observation
            st.button(f"Upload observation for {file.name} to THE INTERNET!", on_click=push_observations)
            # TODO: the metadata only fills properly if `validate` was clicked.
            st.markdown(metadata2md())

            msg = f"[D] full observation after inference: {observation}"
            g_logger.debug(msg)
            print(msg)
            # TODO: add a link to more info on the model, next to the button.

            whale_classes = out['predictions'][:]
            # render images for the top 3 (that is what the model api returns)
            st.markdown(f"Top 3 Predictions for {file.name}")
            for i in range(len(whale_classes)):
                viewer.display_whale(whale_classes, i)
        col = (col + 1) % row_size