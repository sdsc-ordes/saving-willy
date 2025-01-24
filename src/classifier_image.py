import streamlit as st
import logging
import os

# get a global var for logger accessor in this module
LOG_LEVEL = logging.DEBUG
g_logger = logging.getLogger(__name__)
g_logger.setLevel(LOG_LEVEL)

from grid_maker import gridder
import hf_push_observations as sw_push_obs
import utils.metadata_handler as meta_handler
import whale_viewer as sw_wv

def cetacean_classify(cetacean_classifier, tab_inference):
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
                selected_class = st.sidebar.selectbox("Species", sw_wv.WHALE_CLASSES, 
                                                                index=None, placeholder="Species not yet identified...", 
                                                                disabled=True)
            else:
                pred1 = st.session_state.whale_prediction1
                # get index of pred1 from WHALE_CLASSES, none if not present
                print(f"[D] pred1: {pred1}")
                ix = sw_wv.WHALE_CLASSES.index(pred1) if pred1 in sw_wv.WHALE_CLASSES else None
                selected_class = tab_inference.selectbox("Species", sw_wv.WHALE_CLASSES, index=ix)
            
            observation['predicted_class'] = selected_class
            if selected_class != st.session_state.whale_prediction1:
                observation['class_overriden'] = selected_class
            
            st.session_state.public_observation = observation
            st.button(f"Upload observation for {file.name} to THE INTERNET!", on_click=sw_push_obs.push_observations)
            # TODO: the metadata only fills properly if `validate` was clicked.
            st.markdown(meta_handler.metadata2md())

            msg = f"[D] full observation after inference: {observation}"
            g_logger.debug(msg)
            print(msg)
            # TODO: add a link to more info on the model, next to the button.

            whale_classes = out['predictions'][:]
            # render images for the top 3 (that is what the model api returns)
            #with tab_inference:
            st.title(f"Species detected for {file.name}")
            for i in range(len(whale_classes)):
                sw_wv.display_whale(whale_classes, i)
        col = (col + 1) % row_size