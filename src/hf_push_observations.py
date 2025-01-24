from streamlit.delta_generator import DeltaGenerator
import streamlit as st
from huggingface_hub import HfApi
import json
import tempfile
import logging

# get a global var for logger accessor in this module
LOG_LEVEL = logging.DEBUG
g_logger = logging.getLogger(__name__)
g_logger.setLevel(LOG_LEVEL)

def push_observations(tab_log:DeltaGenerator=None):
    """
    Push the observations to the Hugging Face dataset
    
    Args:
        tab_log (streamlit.container): The container to log messages to. If not provided,
            log messages are in any case written to the global logger (TODO: test - didn't 
            push any observation since generating the logger)
    
    """
    # we get the observation from session state: 1 is the dict 2 is the image.
    # first, lets do an info display (popup)
    metadata_str = json.dumps(st.session_state.public_observation)
    
    st.toast(f"Uploading observations: {metadata_str}", icon="🦭")
    tab_log = st.session_state.tab_log
    if tab_log is not None:
        tab_log.info(f"Uploading observations: {metadata_str}")
        
    # get huggingface api
    import os 
    token = os.environ.get("HF_TOKEN", None)
    api = HfApi(token=token)

    f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    f.write(metadata_str)
    f.close()
    st.info(f"temp file: {f.name} with metadata written...")

    path_in_repo= f"metadata/{st.session_state.public_observation['author_email']}/{st.session_state.public_observation['image_md5']}.json"
    msg = f"fname: {f.name} | path: {path_in_repo}"
    print(msg)
    st.warning(msg)
    # rv = api.upload_file(
    #     path_or_fileobj=f.name,
    #     path_in_repo=path_in_repo,
    #     repo_id="Saving-Willy/temp_dataset",
    #     repo_type="dataset",
    # )
    # print(rv)
    # msg = f"observation attempted tx to repo happy walrus: {rv}"
    g_logger.info(msg)
    st.info(msg)
    