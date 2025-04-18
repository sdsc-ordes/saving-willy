import streamlit as st
import os
import pandas as pd
import logging

st.set_page_config(
    page_title="ML Models",
    page_icon="🔥",
)

from utils.st_logs import init_logging_session_states

from transformers import pipeline
from transformers import AutoModelForImageClassification
from classifier.classifier_image import add_classifier_header 

from input.input_handling import setup_input, check_inputs_are_set
from input.input_handling import init_input_container_states, add_input_UI_elements, init_input_data_session_states
from input.input_handling import dbg_show_observation_hashes

from utils.workflow_ui import refresh_progress_display, init_workflow_viz, init_workflow_session_states
from dataset.hf_push_observations import push_all_observations

from classifier.classifier_image import cetacean_just_classify, cetacean_show_results_and_review, cetacean_show_results, init_classifier_session_states
from classifier.classifier_hotdog import hotdog_classify

############################################################
classifier_name = "Saving-Willy/cetacean-classifier"
#classifier_revision = '0f9c15e2db4d64e7f622ade518854b488d8d35e6'
classifier_revision = 'main' # default/latest version
############################################################

g_logger = logging.getLogger(__name__)
# setup for the ML model on huggingface (our wrapper)
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
# one toggle for all the extra debug text
if "MODE_DEV_STATEFUL" not in st.session_state:
    st.session_state.MODE_DEV_STATEFUL = False

############################################################


 # Streamlit app
tab_inference, tab_hotdogs= \
    st.tabs(["Cetecean classifier", "Hotdog classifier"])

# initialise various session state variables
init_logging_session_states() # logging init should be early 
init_workflow_session_states() 
init_input_data_session_states()
init_input_container_states()
init_workflow_viz()
init_classifier_session_states()

# put this early so the progress indicator is at the top (also refreshed at end)
refresh_progress_display()    

# create a sidebar, and parse all the input (returned as `observations` object)
with st.sidebar:
    # layout handling
    add_input_UI_elements()
    # input elements (file upload, text input, etc)
    setup_input()

with tab_inference:
    if st.session_state.workflow_fsm.is_in_state('doing_data_entry'):
            # can we advance state? - only when all inputs are set for all uploaded files
            all_inputs_set = check_inputs_are_set(debug=True, empty_ok=False)
            if all_inputs_set:
                st.session_state.workflow_fsm.complete_current_state()
                # -> data_entry_complete
            else: 
                # button, disabled; no state change yet.
                st.sidebar.button(":gray[*Validate*]", disabled=True, help="Please fill in all fields.")
                
        
    if st.session_state.workflow_fsm.is_in_state('data_entry_complete'):
        # can we advance state? - only when the validate button is pressed
        if st.sidebar.button(":white_check_mark:[**Validate**]"):
            # create a dictionary with the submitted observation

            g_logger.info(f"{st.session_state.observations}")

            df = pd.DataFrame([obs.to_dict() for obs in st.session_state.observations.values()])
            # with tab_coords:
            #     st.table(df)
           
            # now disable all the input boxes / widgets
            st.session_state.input_disabled = True
            
            # there doesn't seem to be any actual validation here?? TODO: find validator function (each element is validated by the input box, but is there something at the whole image level?)
            # hmm, maybe it should actually just be "I'm done with data entry"
            st.session_state.workflow_fsm.complete_current_state()
            # -> data_entry_validated
            st.rerun() # refresh so the input widgets are immediately disabled

    if st.session_state.MODE_DEV_STATEFUL:
                dbg_show_observation_hashes()

    add_classifier_header()
    # if we are before data_entry_validated, show the button, disabled.
    if not st.session_state.workflow_fsm.is_in_state_or_beyond('data_entry_validated'):
        tab_inference.button(":gray[*Identify with cetacean classifier*]", disabled=True, 
                            help="Please validate inputs before proceeding", 
                            key="button_infer_ceteans")

    if st.session_state.workflow_fsm.is_in_state('data_entry_validated'):
        # show the button, enabled. If pressed, we start the ML model (And advance state)
        if tab_inference.button("Identify with cetacean classifier", 
                                key="button_infer_ceteans"):
            cetacean_classifier = AutoModelForImageClassification.from_pretrained(
                classifier_name, 
                revision=classifier_revision, 
                trust_remote_code=True)

            cetacean_just_classify(cetacean_classifier)
            st.session_state.workflow_fsm.complete_current_state()
            # trigger a refresh too (refreshhing the prog indicator means the script reruns and 
            # we can enter the next state - visualising the results / review)
            # ok it doesn't if done programmatically. maybe interacting with teh button? check docs.
            refresh_progress_display()
            #TODO: validate this doesn't harm performance adversely.
            st.rerun()

    elif st.session_state.workflow_fsm.is_in_state('ml_classification_completed'):
        # show the results, and allow manual validation
        st.markdown("""### Inference results and manual validation/adjustment """)
        if st.session_state.MODE_DEV_STATEFUL:
            s = ""
            for k, v in st.session_state.whale_prediction1.items():
                s += f"* Image {k}: {v}\n"
                
            st.markdown(s)

        # add a button to advance the state
        if st.button("I have looked over predictions and confirm correct species", icon= "👀",
                    type="primary",
                    help="Confirm that all species are selected correctly"):
            st.session_state.workflow_fsm.complete_current_state()
            # -> manual_inspection_completed
            st.rerun()
        
        cetacean_show_results_and_review()

    elif st.session_state.workflow_fsm.is_in_state('manual_inspection_completed'):
        # show the ML results, and allow the user to upload the observation
        st.markdown("""### Inference Results (after manual validation) """)
        
        
        if st.button("Upload all observations to THE INTERNET!", icon= "⬆️",
                    type="primary",):
            # let this go through to the push_all func, since it just reports to log for now.
            push_all_observations(enable_push=False)
            st.session_state.workflow_fsm.complete_current_state()
            # -> data_uploaded
            st.rerun()

        cetacean_show_results()

    elif st.session_state.workflow_fsm.is_in_state('data_uploaded'):
        # the data has been sent. Lets show the observations again
        # but no buttons to upload (or greyed out ok)
        st.markdown("""### Observation(s) uploaded - thank you!""")
        cetacean_show_results()

        st.divider()
        df = pd.DataFrame([obs.to_dict() for obs in st.session_state.observations.values()])
        st.table(df)

        # didn't decide what the next state is here - I think we are in the terminal state.
        #st.session_state.workflow_fsm.complete_current_state()
        
  
with tab_hotdogs:
    # inside the hotdog tab, on button press we call a 2nd model (totally unrelated at present, just for demo
    # purposes, an hotdog image classifier) which will be run locally.
    # - this model predicts if the image is a hotdog or not, and returns probabilities
    # - the input image is the same as for the ceteacean classifier - defined in the sidebar
    tab_hotdogs.title("Hot Dog? Or Not?")
    tab_hotdogs.write("""
                *Run alternative classifer on input images. Here we are using
                a binary classifier - hotdog or not - from
                huggingface.co/julien-c/hotdog-not-hotdog.*""")

    if tab_hotdogs.button("Get Hotdog Prediction"):   
        
        pipeline_hot_dog = pipeline(task="image-classification", model="julien-c/hotdog-not-hotdog")

        if st.session_state.image is None:
            st.info("Please upload an image first.")
            #st.info(str(observations.to_dict()))
            
        else:
            hotdog_classify(pipeline_hot_dog, tab_hotdogs)
            
        
# after all other processing, we can show the stage/state
refresh_progress_display()
