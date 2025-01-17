import logging
import os

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

from transformers import pipeline
from transformers import AutoModelForImageClassification

from datasets import disable_caching
disable_caching()

import whale_gallery as gallery
import whale_viewer as viewer
from input.input_handling import setup_input
from maps.alps_map import present_alps_map
from maps.obs_map import present_obs_map
from utils.st_logs import setup_logging, parse_log_buffer
from classifier.classifier_image import cetacean_classify
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

# get a global var for logger accessor in this module
LOG_LEVEL = logging.DEBUG
g_logger = logging.getLogger(__name__)
g_logger.setLevel(LOG_LEVEL)

st.set_page_config(layout="wide")

# initialise various session state variables
if "handler" not in st.session_state:
    st.session_state['handler'] = setup_logging()

if "observations" not in st.session_state:
    st.session_state.observations = {}

if "images" not in st.session_state:
    st.session_state.images = {}

if "files" not in st.session_state:
    st.session_state.files = {}

if "public_observation" not in st.session_state:
    st.session_state.public_observation = {}

if "classify_whale_done" not in st.session_state:
    st.session_state.classify_whale_done = False

if "whale_prediction1" not in st.session_state:
    st.session_state.whale_prediction1 = None

if "tab_log" not in st.session_state:
    st.session_state.tab_log = None
    

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
    #tab_gallery, tab_inference, tab_hotdogs, tab_map, tab_data, tab_log = st.tabs(["Cetecean classifier", "Hotdog classifier", "Map", "observation", "Log", "Beautiful cetaceans"])
    tab_inference, tab_hotdogs, tab_map, tab_data, tab_log, tab_gallery = st.tabs(["Cetecean classifier", "Hotdog classifier", "Map", "observation", "Log", "Beautiful cetaceans"])
    st.session_state.tab_log = tab_log


    # create a sidebar, and parse all the input (returned as `observations` object)
    observations = setup_input(viewcontainer=st.sidebar)

        
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

        
        
    with tab_data:
        # the goal of this tab is to allow selection of the new obsvation's location by map click/adjust.
        st.markdown("Coming later hope! :construction:")

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
        

    # Display submitted observation
    if st.sidebar.button("Validate"):
        # create a dictionary with the submitted observation
        submitted_data = observations
        st.session_state.observations = observations
            
        tab_log.info(f"{st.session_state.observations}")

        df = pd.DataFrame(submitted_data, index=[0])
        with tab_data:
            st.table(df)
        
        

        
    # inside the inference tab, on button press we call the model (on huggingface hub)
    # which will be run locally. 
    # - the model predicts the top 3 most likely species from the input image
    # - these species are shown
    # - the user can override the species prediction using the dropdown 
    # - an observation is uploaded if the user chooses.
        
    if tab_inference.button("Identify with cetacean classifier"):
        #pipe = pipeline("image-classification", model="Saving-Willy/cetacean-classifier", trust_remote_code=True)
        cetacean_classifier = AutoModelForImageClassification.from_pretrained("Saving-Willy/cetacean-classifier", 
                                                                            revision=classifier_revision,
                                                                            trust_remote_code=True)
        
        if st.session_state.images is None:
            # TODO: cleaner design to disable the button until data input done?
            st.info("Please upload an image first.")
        else:
            cetacean_classify(cetacean_classifier)
                
        

        
    # inside the hotdog tab, on button press we call a 2nd model (totally unrelated at present, just for demo
    # purposes, an hotdog image classifier) which will be run locally.
    # - this model predicts if the image is a hotdog or not, and returns probabilities
    # - the input image is the same as for the ceteacean classifier - defined in the sidebar

    if tab_hotdogs.button("Get Hotdog Prediction"):   
        
        pipeline_hot_dog = pipeline(task="image-classification", model="julien-c/hotdog-not-hotdog")
        tab_hotdogs.title("Hot Dog? Or Not?")

        if st.session_state.image is None:
            st.info("Please upload an image first.")
            #st.info(str(observations.to_dict()))
            
        else:
            hotdog_classify(pipeline_hot_dog, tab_hotdogs)
            
            

if __name__ == "__main__":
    main()
