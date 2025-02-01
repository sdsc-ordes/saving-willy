import logging
import os

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

from transformers import pipeline
from transformers import AutoModelForImageClassification

from maps.obs_map import add_obs_map_header 
from classifier.classifier_image import add_classifier_header 
from datasets import disable_caching
disable_caching()

import whale_gallery as gallery
import whale_viewer as viewer
from input.input_handling import setup_input, check_inputs_are_set
from input.input_handling import init_input_container_states, add_input_UI_elements, init_input_data_session_states
from input.input_handling import dbg_show_observation_hashes

from maps.alps_map import present_alps_map
from maps.obs_map import present_obs_map
from utils.st_logs import parse_log_buffer, init_logging_session_states
from utils.workflow_ui import refresh_progress_display, init_workflow_viz, init_workflow_session_states
from hf_push_observations import push_all_observations

from classifier.classifier_image import cetacean_just_classify, cetacean_show_results_and_review, cetacean_show_results, init_classifier_session_states
from classifier.classifier_hotdog import hotdog_classify


# setup for the ML model on huggingface (our wrapper)
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
#classifier_revision = '0f9c15e2db4d64e7f622ade518854b488d8d35e6'
classifier_revision = 'main' # default/latest version
# and the dataset of observations (hf dataset in our space)
dataset_id = "Saving-Willy/temp_dataset"
data_files = "data/train-00000-of-00001.parquet"

USE_BASIC_MAP = False
DEV_SIDEBAR_LIB = True

# one toggle for all the extra debug text
if "MODE_DEV_STATEFUL" not in st.session_state:
    st.session_state.MODE_DEV_STATEFUL = False
    

# get a global var for logger accessor in this module
LOG_LEVEL = logging.DEBUG
g_logger = logging.getLogger(__name__)
g_logger.setLevel(LOG_LEVEL)

st.set_page_config(layout="wide")

# initialise various session state variables
init_logging_session_states() # logging should be early 
init_workflow_session_states() 

# TODO: this is obselete, now we have the st_logs functionality.
if "tab_log" not in st.session_state:
    st.session_state.tab_log = None
    
init_input_data_session_states()
init_input_container_states()
init_workflow_viz()
init_classifier_session_states()

    
    
        


def main() -> None:
    """
    Main entry point to set up the streamlit UI and run the application.

    The organisation is as follows:

    1. observation input (a new observations) is handled in the sidebar
    2. the rest of the interface is organised in tabs:
    
        - cetean classifier
        - hotdog classifier
        - map to present the obersvations
        - table of recent log entries
        - gallery of whale images
    
    The majority of the tabs are instantiated from modules. Currently the two 
    classifiers are still in-line here.
    
    """

    g_logger.info("App started.")
    g_logger.warning(f"[D] Streamlit version: {st.__version__}. Python version: {os.sys.version}")

    #g_logger.debug("debug message")
    #g_logger.info("info message")
    #g_logger.warning("warning message")

    # Streamlit app
    tab_inference, tab_hotdogs, tab_map, tab_coords, tab_log, tab_gallery = \
        st.tabs(["Cetecean classifier", "Hotdog classifier", "Map", "*:gray[Dev:coordinates]*", "Log", "Beautiful cetaceans"])
    st.session_state.tab_log = tab_log

    # put this early so the progress indicator is at the top (also refreshed at end)
    refresh_progress_display()    

    # create a sidebar, and parse all the input (returned as `observations` object)
    with st.sidebar:
        # layout handling
        add_input_UI_elements()
        # input elements (file upload, text input, etc)
        setup_input()

        
    if 0:## WIP
        # goal of this code is to allow the user to override the ML prediction, before transmitting an observations
        predicted_class = st.sidebar.selectbox("Predicted Class", viewer.WHALE_CLASSES)
        override_prediction = st.sidebar.checkbox("Override Prediction")

        if override_prediction:
            overridden_class = st.sidebar.selectbox("Override Class", viewer.WHALE_CLASSES)
            st.session_state.observations['class_overriden'] = overridden_class
        else:
            st.session_state.observations['class_overriden'] = None


    with tab_map:
        # visual structure: a couple of toggles at the top, then the map inlcuding a
        # dropdown for tileset selection.
        add_obs_map_header()
        tab_map_ui_cols = st.columns(2)
        with tab_map_ui_cols[0]:
            show_db_points = st.toggle("Show Points from DB", True)
        with tab_map_ui_cols[1]:
            dbg_show_extra = st.toggle("Show Extra points (test)", False)
            
        if show_db_points:
            # show a nicer map, observations marked, tileset selectable.
            st_observation = present_obs_map(
                dataset_id=dataset_id, data_files=data_files,
                dbg_show_extra=dbg_show_extra)
            
        else:
            # development map.
            st_observation = present_alps_map()
            

    with tab_log:
        handler = st.session_state['handler']
        if handler is not None:
            records = parse_log_buffer(handler.buffer)
            st.dataframe(records[::-1], use_container_width=True,)
            st.info(f"Length of records: {len(records)}")
        else:
            st.error("⚠️ No log handler found!")

        
        
    with tab_coords:
        # the goal of this tab is to allow selection of the new obsvation's location by map click/adjust.
        st.markdown("Coming later! :construction:")
        st.markdown(
            f"""*The goal is to allow interactive definition for the coordinates of a new
            observation, by click/drag points on the map.*""")
        

        st.write("Click on the map to capture a location.")
        #m = folium.Map(location=visp_loc, zoom_start=7)
        mm = folium.Map(location=[39.949610, -75.150282], zoom_start=16)
        folium.Marker( [39.949610, -75.150282], popup="Liberty Bell", tooltip="Liberty Bell"
    ).add_to(mm)

        st_data2 = st_folium(mm, width=725)
        st.write("below the map...")
        if st_data2['last_clicked'] is not None:
            print(st_data2)
            st.info(st_data2['last_clicked'])


    with tab_gallery:
        # here we make a container to allow filtering css properties 
        # specific to the gallery (otherwise we get side effects)
        tg_cont = st.container(key="swgallery")
        with tg_cont:
            gallery.render_whale_gallery(n_cols=4)
        

    # state handling re data_entry phases
    # 0. no data entered yet -> display the file uploader thing
    # 1. we have some images, but not all the metadata fields are done -> validate button shown, disabled
    # 2. all data entered -> validate button enabled
    # 3. validation button pressed, validation done -> enable the inference button. 
    #    - at this point do we also want to disable changes to the metadata selectors?
    #    anyway, simple first. 

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
            tab_log.info(f"{st.session_state.observations}")
            df = pd.DataFrame([obs.to_dict() for obs in st.session_state.observations.values()])
            #df = pd.DataFrame(st.session_state.observations, index=[0])
            with tab_coords:
                st.table(df)
            # there doesn't seem to be any actual validation here?? TODO: find validator function (each element is validated by the input box, but is there something at the whole image level?)
            # hmm, maybe it should actually just be "I'm done with data entry"
            st.session_state.workflow_fsm.complete_current_state()
            # -> data_entry_validated
    
    # state handling re inference phases (tab_inference)
    # 3. validation button pressed, validation done -> enable the inference button.
    # 4. inference button pressed -> ML started. | let's cut this one out, since it would only
    #      make sense if we did it as an async action
    # 5. ML done -> show results, and manual validation options
    # 6. manual validation done -> enable the upload buttons
    # 
    with tab_inference:
        
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
            if tab_inference.button("Identify with cetacean classifier"):
                cetacean_classifier = AutoModelForImageClassification.from_pretrained(
                    "Saving-Willy/cetacean-classifier", 
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
            if st.button("Confirm species predictions", help="Confirm that all species are selected correctly"):
                st.session_state.workflow_fsm.complete_current_state()
                # -> manual_inspection_completed
                st.rerun()
            
            cetacean_show_results_and_review()

        elif st.session_state.workflow_fsm.is_in_state('manual_inspection_completed'):
            # show the ML results, and allow the user to upload the observation
            st.markdown("""### Inference Results (after manual validation) """)
            
            
            if st.button("Upload all observations to THE INTERNET!"):
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
            #df = pd.DataFrame(st.session_state.observations, index=[0])
            df = pd.DataFrame([obs.to_dict() for obs in st.session_state.observations.values()])
            st.table(df)

            # didn't decide what the next state is here - I think we are in the terminal state.
            #st.session_state.workflow_fsm.complete_current_state()
            
            
            
    
            
            

        
    # inside the inference tab, on button press we call the model (on huggingface hub)
    # which will be run locally. 
    # - the model predicts the top 3 most likely species from the input image
    # - these species are shown
    # - the user can override the species prediction using the dropdown 
    # - an observation is uploaded if the user chooses.

    # with tab_inference:
    #     add_classifier_header()
        

        
    # if tab_inference.button("Identify with cetacean classifier"):
    #     #pipe = pipeline("image-classification", model="Saving-Willy/cetacean-classifier", trust_remote_code=True)
    #     cetacean_classifier = AutoModelForImageClassification.from_pretrained("Saving-Willy/cetacean-classifier", 
    #                                                                         revision=classifier_revision,
    #                                                                         trust_remote_code=True)

        
    #     if st.session_state.images is None:
    #         # TODO: cleaner design to disable the button until data input done?
    #         st.info("Please upload an image first.")
    #     else:
    #         cetacean_classify(cetacean_classifier)
                
        

        
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


if __name__ == "__main__":
    main()
