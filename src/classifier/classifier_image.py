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
from input.input_observation import InputObservation

def add_header_text() -> None:
    """
    Add brief explainer text about cetacean classification to the tab 
    """
    st.markdown("""
                *Run classifer to identify the species of cetean on the uploaded image.
                Once inference is complete, the top three predictions are shown.
                You can override the prediction by selecting a species from the dropdown.*""")

# func to just run classification, store results.
def cetacean_just_classify(cetacean_classifier):

    images = st.session_state.images
    #observations = st.session_state.observations
    hashes = st.session_state.image_hashes
    
    for hash in hashes: 
        image = images[hash]
        # run classifier model on `image`, and persistently store the output
        out = cetacean_classifier(image) # get top 3 matches
        st.session_state.whale_prediction1[hash] = out['predictions'][0]
        st.session_state.classify_whale_done[hash] = True
        st.session_state.observations[hash].set_top_predictions(out['predictions'][:])

        msg = f"[D]2 classify_whale_done for {hash}: {st.session_state.classify_whale_done[hash]}, whale_prediction1: {st.session_state.whale_prediction1[hash]}"
        g_logger.info(msg)

        if st.session_state.MODE_DEV_STATEFUL:
            st.write(f"*[D] Observation {hash} classified as {st.session_state.whale_prediction1[hash]}*")
       
        
# func to show results and allow review
def cetacean_show_results_and_review():
    images = st.session_state.images
    observations = st.session_state.observations
    hashes = st.session_state.image_hashes
    batch_size, row_size, page = gridder(hashes)
    
    grid = st.columns(row_size)
    col = 0
    o = 1

    for hash in hashes:
        image = images[hash]
        #observation = observations[hash].to_dict()
        _observation:InputObservation = observations[hash]
    
        with grid[col]:
            st.image(image, use_column_width=True)
            
            # dropdown for selecting/overriding the species prediction
            if not st.session_state.classify_whale_done[hash]:
                selected_class = st.sidebar.selectbox("Species", viewer.WHALE_CLASSES, 
                                                                index=None, placeholder="Species not yet identified...", 
                                                                disabled=True)
            else:
                pred1 = st.session_state.whale_prediction1[hash]
                # get index of pred1 from WHALE_CLASSES, none if not present
                print(f"[D] {o:3} pred1: {pred1:30} | {hash}")
                ix = viewer.WHALE_CLASSES.index(pred1) if pred1 in viewer.WHALE_CLASSES else None
                selected_class = st.selectbox(f"Species for observation {str(o)}", viewer.WHALE_CLASSES, index=ix)
            
            _observation.set_selected_class(selected_class)
            #observation['predicted_class'] = selected_class
            # this logic is now in the InputObservation class automatially
            #if selected_class != st.session_state.whale_prediction1[hash]:
            #    observation['class_overriden'] = selected_class # TODO: this should be boolean!
            
            # store the elements of the observation that will be transmitted (not image)
            observation = _observation.to_dict()
            st.session_state.public_observations[hash] = observation
            
            #st.button(f"Upload observation {str(o)} to THE INTERNET!", on_click=push_observations)
            # TODO: the metadata only fills properly if `validate` was clicked.
            st.markdown(metadata2md(hash, debug=True))

            msg = f"[D] full observation after inference: {observation}"
            g_logger.debug(msg)
            print(msg)
            # TODO: add a link to more info on the model, next to the button.

            whale_classes = observations[hash].top_predictions
            # render images for the top 3 (that is what the model api returns)
            n = len(whale_classes)
            st.markdown(f"**Top {n} Predictions for observation {str(o)}**")
            for i in range(n):
                viewer.display_whale(whale_classes, i)
        o += 1
        col = (col + 1) % row_size


# func to just present results
def cetacean_show_results():
    images = st.session_state.images
    observations = st.session_state.observations
    hashes = st.session_state.image_hashes
    batch_size, row_size, page = gridder(hashes)
    
    
    grid = st.columns(row_size)
    col = 0
    o = 1

    for hash in hashes:
        image = images[hash]
        observation = observations[hash].to_dict()
    
        with grid[col]:
            st.image(image, use_column_width=True)
            
            # # dropdown for selecting/overriding the species prediction
            # if not st.session_state.classify_whale_done[hash]:
            #     selected_class = st.sidebar.selectbox("Species", viewer.WHALE_CLASSES, 
            #                                                     index=None, placeholder="Species not yet identified...", 
            #                                                     disabled=True)
            # else:
            #     pred1 = st.session_state.whale_prediction1[hash]
            #     # get index of pred1 from WHALE_CLASSES, none if not present
            #     print(f"[D] pred1: {pred1}")
            #     ix = viewer.WHALE_CLASSES.index(pred1) if pred1 in viewer.WHALE_CLASSES else None
            #     selected_class = st.selectbox(f"Species for observation {str(o)}", viewer.WHALE_CLASSES, index=ix)
            
            # observation['predicted_class'] = selected_class
            # if selected_class != st.session_state.whale_prediction1[hash]:
            #     observation['class_overriden'] = selected_class # TODO: this should be boolean!
            
            # st.session_state.public_observation = observation
            
            #st.button(f"Upload observation {str(o)} to THE INTERNET!", on_click=push_observations)
            # 
            st.markdown(metadata2md(hash, debug=True))

            msg = f"[D] full observation after inference: {observation}"
            g_logger.debug(msg)
            print(msg)
            # TODO: add a link to more info on the model, next to the button.

            whale_classes = observations[hash].top_predictions
            # render images for the top 3 (that is what the model api returns)
            n = len(whale_classes)
            st.markdown(f"**Top {n} Predictions for observation {str(o)}**")
            for i in range(n):
                viewer.display_whale(whale_classes, i)
        o += 1
        col = (col + 1) % row_size




# func to do all in one
def cetacean_classify_show_and_review(cetacean_classifier):
    """Cetacean classifier using the saving-willy model from Saving Willy Hugging Face space.
    For each image in the session state, classify the image and display the top 3 predictions.
    Args:
        cetacean_classifier ([type]):  saving-willy model from Saving Willy Hugging Face space
    """
    raise DeprecationWarning("This function is deprecated. Use individual steps instead")
    images = st.session_state.images
    observations = st.session_state.observations
    hashes = st.session_state.image_hashes
    batch_size, row_size, page = gridder(hashes)
    
    grid = st.columns(row_size)
    col = 0
    o=1
    for hash in hashes: 
        image = images[hash]
        
        with grid[col]:
            st.image(image, use_column_width=True)
            observation = observations[hash].to_dict()
            # run classifier model on `image`, and persistently store the output
            out = cetacean_classifier(image) # get top 3 matches
            st.session_state.whale_prediction1[hash] = out['predictions'][0]
            st.session_state.classify_whale_done[hash] = True
            msg = f"[D]2 classify_whale_done for {hash}: {st.session_state.classify_whale_done[hash]}, whale_prediction1: {st.session_state.whale_prediction1[hash]}"
            g_logger.info(msg)
            
            # dropdown for selecting/overriding the species prediction
            if not st.session_state.classify_whale_done[hash]:
                selected_class = st.sidebar.selectbox("Species", viewer.WHALE_CLASSES, 
                                                                index=None, placeholder="Species not yet identified...", 
                                                                disabled=True)
            else:
                pred1 = st.session_state.whale_prediction1[hash]
                # get index of pred1 from WHALE_CLASSES, none if not present
                print(f"[D] pred1: {pred1}")
                ix = viewer.WHALE_CLASSES.index(pred1) if pred1 in viewer.WHALE_CLASSES else None
                selected_class = st.selectbox(f"Species for observation {str(o)}", viewer.WHALE_CLASSES, index=ix)
            
            observation['predicted_class'] = selected_class
            if selected_class != st.session_state.whale_prediction1[hash]:
                observation['class_overriden'] = selected_class
            
            st.session_state.public_observation = observation
            st.button(f"Upload observation {str(o)} to THE INTERNET!", on_click=push_observations)
            # TODO: the metadata only fills properly if `validate` was clicked.
            st.markdown(metadata2md())

            msg = f"[D] full observation after inference: {observation}"
            g_logger.debug(msg)
            print(msg)
            # TODO: add a link to more info on the model, next to the button.

            whale_classes = out['predictions'][:]
            # render images for the top 3 (that is what the model api returns)
            st.markdown(f"Top 3 Predictions for observation {str(o)}")
            for i in range(len(whale_classes)):
                viewer.display_whale(whale_classes, i)
        o += 1
        col = (col + 1) % row_size
