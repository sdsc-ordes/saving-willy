import os 
import json
import tempfile
import logging

from streamlit.delta_generator import DeltaGenerator
import streamlit as st
from huggingface_hub import HfApi, CommitInfo

from dataset.download import dataset_id

# get a global var for logger accessor in this module
LOG_LEVEL = logging.DEBUG
g_logger = logging.getLogger(__name__)
g_logger.setLevel(LOG_LEVEL)

def push_observation(image_hash:str, api:HfApi, enable_push:False) -> CommitInfo:
    '''
    push one observation to the Hugging Face dataset
    
    '''
    # get the observation
    observation = st.session_state.public_observations.get(image_hash)
    if observation is None:
        msg = f"Could not find observation with hash {image_hash}"
        g_logger.error(msg)
        st.error(msg)
        return None
    
    # convert to json
    metadata_str = json.dumps(observation) # doesn't work yet, TODO
    
    st.toast(f"Uploading observation: {metadata_str}", icon="🦭")
    g_logger.info(f"Uploading observation: {metadata_str}")
        
    # write to temp file so we can send it (why is this not using context mgr?)
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    f.write(metadata_str)
    f.close()
    #st.info(f"temp file: {f.name} with metadata written...")

    path_in_repo = f"metadata/{observation['author_email']}/{observation['image_md5']}.json"
    
    msg = f"fname: {f.name} | path: {path_in_repo}"
    print(msg)
    st.warning(msg)

    if enable_push:
        rv = api.upload_file(
            path_or_fileobj=f.name,
            path_in_repo=path_in_repo,
            repo_id=dataset_id,
            repo_type="dataset",
        )
        print(rv)
        msg = f"observation attempted tx to repo happy walrus: {rv}"
        g_logger.info(msg)
        st.info(msg)
    else:
        rv = None # temp don't send anything

    return rv

    

def push_all_observations(enable_push:bool=False):
    '''
    open an API connection to Hugging Face, and push all observation one by one
    '''
    
    # get huggingface api
    token = os.environ.get("HF_TOKEN", None)
    api = HfApi(token=token)

    # iterate over the list of observations
    for hash in st.session_state.public_observations.keys():
        rv = push_observation(hash, api, enable_push=enable_push)