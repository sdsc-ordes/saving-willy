import streamlit as st
import logging

# get a global var for logger accessor in this module
LOG_LEVEL = logging.DEBUG
g_logger = logging.getLogger(__name__)
g_logger.setLevel(LOG_LEVEL)

import whale_viewer as viewer
from dataset.hf_push_observations import push_observations
from utils.grid_maker import gridder
from utils.metadata_handler import metadata2md
from input.input_observation import InputObservation

def init_classifier_session_states() -> None:
    '''
    Initialise the session state variables used in classification
    '''
    if "classify_whale_done" not in st.session_state:
        st.session_state.classify_whale_done = {}

    if "whale_prediction1" not in st.session_state:
        st.session_state.whale_prediction1 = {}


def add_classifier_header() -> None:
    """
    Add brief explainer text about cetacean classification to the tab 
    """
    st.markdown("""
                *Run classifer to identify the species of cetean on the uploaded image.
                Once inference is complete, the top three predictions are shown.
                You can override the prediction by selecting a species from the dropdown.*""")


# func to just run classification, store results.
def cetacean_just_classify(cetacean_classifier):
    """
    Infer cetacean species for all observations in the session state.
    
    - this function runs the classifier, and stores results in the session state. 
    - the top 3 predictions are stored in the observation object, which is retained
      in st.session_state.observations
    - to display results use cetacean_show_results() or cetacean_show_results_and_review()
    
    Args:
        cetacean_classifier ([type]):  saving-willy model from Saving Willy Hugging Face space
    """

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
def cetacean_show_results_and_review() -> None:
    """
    Present classification results and allow user to review and override the prediction.
    
    - for each observation in the session state, displays the image, summarised 
      metadata, and the top 3 predictions. 
    - allows user to override the prediction by selecting a species from the dropdown.
    - the selected species is stored in the observation object, which is retained in
      st.session_state.observations

    """

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
            
            # store the elements of the observation that will be transmitted (not image)
            observation = _observation.to_dict()
            st.session_state.public_observations[hash] = observation
            
            #st.button(f"Upload observation {str(o)} to THE INTERNET!", on_click=push_observations)
            # TODO: the metadata only fills properly if `validate` was clicked.
            # TODO put condition on the debug
            st.markdown(metadata2md(hash, debug=False))

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
    """
    Present classification results that may be pushed to the online dataset.
    
    - for each observation in the session state, displays the image, summarised 
      metadata, the top 3 predictions, and the selected species (which may have 
      been manually selected, or the top prediction accepted). 

    """
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
