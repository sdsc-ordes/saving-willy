#import datetime
from PIL import Image

import json
import logging
import os
import tempfile

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator # for type hinting
import folium
from streamlit_folium import st_folium
from huggingface_hub import HfApi
from transformers import pipeline
from transformers import AutoModelForImageClassification

from datasets import disable_caching
disable_caching()

import alps_map as sw_am
import input_handling as sw_inp
import obs_map as sw_map
import st_logs as sw_logs
import whale_gallery as sw_wg
import whale_viewer as sw_wv




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
#sw_logs.setup_logging(level=LOG_LEVEL, buffer_len=40)



# initialise various session state variables
if "handler" not in st.session_state:
    st.session_state['handler'] = sw_logs.setup_logging()

if "full_data" not in st.session_state:
    st.session_state.full_data = {}

if "classify_whale_done" not in st.session_state:
    st.session_state.classify_whale_done = False

if "whale_prediction1" not in st.session_state:
    st.session_state.whale_prediction1 = None
    
if "image" not in st.session_state:
    st.session_state.image = None

if "tab_log" not in st.session_state:
    st.session_state.tab_log = None
    

def metadata2md() -> str:
    """Get metadata from cache and return as markdown-formatted key-value list

    Returns:
        str: Markdown-formatted key-value list of metadata
        
    """
    markdown_str = "\n"
    for key, value in st.session_state.full_data.items():
            markdown_str += f"- **{key}**: {value}\n"
    return markdown_str


def push_observation(tab_log:DeltaGenerator=None):
    """
    Push the observation to the Hugging Face dataset
    
    Args:
        tab_log (streamlit.container): The container to log messages to. If not provided,
            log messages are in any case written to the global logger (TODO: test - didn't 
            push any data since generating the logger)
    
    """
    # we get the data from session state: 1 is the dict 2 is the image.
    # first, lets do an info display (popup)
    metadata_str = json.dumps(st.session_state.full_data)
    
    st.toast(f"Uploading observation: {metadata_str}", icon="🦭")
    tab_log = st.session_state.tab_log
    if tab_log is not None:
        tab_log.info(f"Uploading observation: {metadata_str}")
        
    # get huggingface api
    import os 
    token = os.environ.get("HF_TOKEN", None)
    api = HfApi(token=token)

    f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    f.write(metadata_str)
    f.close()
    st.info(f"temp file: {f.name} with metadata written...")

    path_in_repo= f"metadata/{st.session_state.full_data['author_email']}/{st.session_state.full_data['image_md5']}.json"
    msg = f"fname: {f.name} | path: {path_in_repo}"
    print(msg)
    st.warning(msg)
    rv = api.upload_file(
        path_or_fileobj=f.name,
        path_in_repo=path_in_repo,
        repo_id="Saving-Willy/temp_dataset",
        repo_type="dataset",
    )
    print(rv)
    msg = f"data attempted tx to repo happy walrus: {rv}"
    g_logger.info(msg)
    st.info(msg)
    


def main() -> None:
    """
    Main entry point to set up the streamlit UI and run the application.

    The organisation is as follows:

    1. data input (a new observation) is handled in the sidebar
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
    #tab_gallery, tab_inference, tab_hotdogs, tab_map, tab_data, tab_log = st.tabs(["Cetecean classifier", "Hotdog classifier", "Map", "Data", "Log", "Beautiful cetaceans"])
    tab_inference, tab_hotdogs, tab_map, tab_data, tab_log, tab_gallery = st.tabs(["Cetecean classifier", "Hotdog classifier", "Map", "Data", "Log", "Beautiful cetaceans"])
    st.session_state.tab_log = tab_log


    # create a sidebar, and parse all the input (returned as `observation` object)
    observation = sw_inp.setup_input(viewcontainer=st.sidebar)

        
    if 0:## WIP
        # goal of this code is to allow the user to override the ML prediction, before transmitting an observation
        predicted_class = st.sidebar.selectbox("Predicted Class", sw_wv.WHALE_CLASSES)
        override_prediction = st.sidebar.checkbox("Override Prediction")

        if override_prediction:
            overridden_class = st.sidebar.selectbox("Override Class", sw_wv.WHALE_CLASSES)
            st.session_state.full_data['class_overriden'] = overridden_class
        else:
            st.session_state.full_data['class_overriden'] = None


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
            st_data = sw_map.present_obs_map(
                dataset_id=dataset_id, data_files=data_files,
                dbg_show_extra=dbg_show_extra)
            
        else:
            # development map.
            st_data = sw_am.present_alps_map()
            

    with tab_log:
        handler = st.session_state['handler']
        if handler is not None:
            records = sw_logs.parse_log_buffer(handler.buffer)
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
            sw_wg.render_whale_gallery(n_cols=4)
        

    # Display submitted data
    if st.sidebar.button("Validate"):
        # create a dictionary with the submitted data
        submitted_data = observation.to_dict()
        #print(submitted_data)
        
        #full_data.update(**submitted_data)
        for k, v in submitted_data.items():
            st.session_state.full_data[k] = v
            
        #st.write(f"full dict of data: {json.dumps(submitted_data)}")
        #tab_inference.info(f"{st.session_state.full_data}")
        tab_log.info(f"{st.session_state.full_data}")

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
        
        if st.session_state.image is None:
            # TODO: cleaner design to disable the button until data input done?
            st.info("Please upload an image first.")
        else:
            # run classifier model on `image`, and persistently store the output
            out = cetacean_classifier(st.session_state.image) # get top 3 matches
            st.session_state.whale_prediction1 = out['predictions'][0]
            st.session_state.classify_whale_done = True
            msg = f"[D]2 classify_whale_done: {st.session_state.classify_whale_done}, whale_prediction1: {st.session_state.whale_prediction1}"
            st.info(msg)
            g_logger.info(msg)
            
            # dropdown for selecting/overriding the species prediction
            #st.info(f"[D] classify_whale_done: {st.session_state.classify_whale_done}, whale_prediction1: {st.session_state.whale_prediction1}")
            if not st.session_state.classify_whale_done:
                selected_class = tab_inference.sidebar.selectbox("Species", sw_wv.WHALE_CLASSES, index=None, placeholder="Species not yet identified...", disabled=True)
            else:
                pred1 = st.session_state.whale_prediction1
                # get index of pred1 from WHALE_CLASSES, none if not present
                print(f"[D] pred1: {pred1}")
                ix = sw_wv.WHALE_CLASSES.index(pred1) if pred1 in sw_wv.WHALE_CLASSES else None
                selected_class = tab_inference.selectbox("Species", sw_wv.WHALE_CLASSES, index=ix)
            
            st.session_state.full_data['predicted_class'] = selected_class
            if selected_class != st.session_state.whale_prediction1:
                st.session_state.full_data['class_overriden'] = selected_class
                
            btn = st.button("Upload observation to THE INTERNET!", on_click=push_observation)
            # TODO: the metadata only fills properly if `validate` was clicked.
            tab_inference.markdown(metadata2md())

            msg = f"[D] full data after inference: {st.session_state.full_data}"
            g_logger.debug(msg)
            print(msg)
            # TODO: add a link to more info on the model, next to the button.

            whale_classes = out['predictions'][:]
            # render images for the top 3 (that is what the model api returns)
            with tab_inference:
                st.markdown("## Species detected")
                for i in range(len(whale_classes)):
                    sw_wv.display_whale(whale_classes, i)
            
        

        
    # inside the hotdog tab, on button press we call a 2nd model (totally unrelated at present, just for demo
    # purposes, an hotdog image classifier) which will be run locally.
    # - this model predicts if the image is a hotdog or not, and returns probabilities
    # - the input image is the same as for the ceteacean classifier - defined in the sidebar

    if tab_hotdogs.button("Get Hotdog Prediction"):   
        
        pipeline_hot_dog = pipeline(task="image-classification", model="julien-c/hotdog-not-hotdog")
        tab_hotdogs.title("Hot Dog? Or Not?")

        if st.session_state.image is None:
            st.info("Please upload an image first.")
            st.info(str(observation.to_dict()))
            
        else:
            col1, col2 = tab_hotdogs.columns(2)

            # display the image (use cached version, no need to reread)
            col1.image(st.session_state.image, use_column_width=True)
            # and then run inference on the image
            predictions = pipeline_hot_dog(Image(st.session_state.image))

            col2.header("Probabilities")
            first = True
            for p in predictions:
                col2.subheader(f"{ p['label'] }: { round(p['score'] * 100, 1)}%")
                if first:
                    st.session_state.full_data['predicted_class'] = p['label']
                    st.session_state.full_data['predicted_score'] = round(p['score'] * 100, 1)
                    first = False
            
            tab_hotdogs.write(f"Session Data: {json.dumps(st.session_state.full_data)}")
            
            

if __name__ == "__main__":
    main()
