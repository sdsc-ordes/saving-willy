from typing import List
from types import SimpleNamespace
import json
import os
from pathlib import Path
import pytest
import streamlit as st
from unittest.mock import patch, MagicMock
from datetime import datetime 

from huggingface_hub import CommitInfo, HfApi
from hf_push_observations import push_observation, construct_path_in_repo


class DotDict(SimpleNamespace):
    '''
    Class to allow for dot notation access to dictionary keys
    
    behaves similarly to streamlit.session_state, where both
    dot notation and dictionary access are allowed.
    
    Args:
        **kwargs: key-value pairs to initialize the object with
        
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__dict__.update(kwargs)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __delitem__(self, key):
        delattr(self, key)



'''
# here we are going to use the API for real.
- should I add a flag to the test datapoints?
1. mocking the API?
2. roundtrip:
- send valid data (1x)
- check no exceptions I suppose
- check data is now part of the dataset
- delete it
- check it's gone
'''

'''
the string version of CommitInfo comes out as:
https://huggingface.co/datasets/Saving-Willy/temp_dataset/blob/main/metadata/super@whale.org/e6ce30c3f403d98067e45101eb4c3c3f.json

form:
    <base> /datasets/<user>/<dataset>/blob/main/<path_in_repo>
  where path_in_repo is 
    metadata/<author_email>/<image_md5>.json
'''

@pytest.fixture
def valid_public_observations() -> List[dict]:
    ''' load test data into dicts (i.e., not just file names) '''

    # path is relative to repo root
    pth = Path("tests/data/uploadable_json")
    
    # skip 000 as it is on land
    files = [pth / f"test_{i:03d}.json" for i in range(1, 5)]
    #print(files)
    return [json.loads(f.read_text()) for f in files]


@pytest.fixture
def mock_session_state_simple():
    with patch('streamlit.session_state', new_callable=dict) as mock:
        yield mock    


@pytest.fixture
def mock_session_state():
    mock_session_state = DotDict()
    with patch('streamlit.session_state', new=mock_session_state) as mock:
        yield mock    

 

def check_observation_in_dataset(api:HfApi, commit_info:CommitInfo, observation:dict) -> bool:
    '''given a commit, check if the observation file is in the dataset'''
    # check if the file is in the metadata dir
    path_in_repo = construct_path_in_repo(observation)
    print(path_in_repo)
    dataset_id = commit_info.repo_url.repo_id

    rv = api.file_exists(
        repo_id=dataset_id,
        filename=path_in_repo,
        repo_type="dataset",
    )
    return rv



def cleanup_remove_files_from_dataset(api:HfApi , commit_info:CommitInfo, observation:dict) -> CommitInfo:
    '''
    remove the files from the dataset
    '''
    if commit_info is None:
        return

    # hmm, path_in_repo is not part of the CommitInfo object (except in _url which is 
    # presumably not stable)
    path_in_repo1 = commit_info._url.removeprefix(commit_info.repo_url).removeprefix('/blob/main/')
    print(path_in_repo1)
    # - refactored the hf_push_observations library to have this exposed separately
    path_in_repo2 = construct_path_in_repo(observation)
    print(path_in_repo2)
    assert path_in_repo1 == path_in_repo2
    path_in_repo = path_in_repo2
    
    # dataset_id can be accessed from commit_info
    dataset_id = commit_info.repo_url.repo_id

    try:
        rv = api.delete_file(
            path_in_repo=path_in_repo,
            repo_id=dataset_id,
            repo_type="dataset",
            commit_message=f"Remove testing file {path_in_repo} from dataset",
        )
    except Exception as e:
        # if we fail to delete this, first let's log to file so it can be cleaned up manually
        # - if this happens on a remote runner (well, any ephemeral runner), we won't have the file, so have to also log to stderr
        msg1 = f"Failed to delete {path_in_repo} from dataset {dataset_id}: {e}"
        print(msg1)
        msg2 = f"call api.delete_file(path_in_repo={path_in_repo}, repo_id={dataset_id}, repo_type='dataset', commit_message='Remove testing file {path_in_repo} from dataset')"
        print(msg2)
        with open("failed_deletes.log", "a") as f:
            f.write(f"{datetime.now()}: {msg1}\n")
            f.write(f"{datetime.now()}: {msg2}\n")
            
        raise e
    
    return rv
        

@pytest.mark.live_database_test
@patch("hf_push_observations.st.error")
@patch("hf_push_observations.st.info")
def test_push_observation(mock_err, mock_inf, valid_public_observations, mock_session_state):
    # load test data
    jsons: List[dict] = valid_public_observations[:]
    # and put it into the session state
    mock_session_state['public_observations'] = {j["image_md5"]: j for j in jsons}
    
    for j in jsons:
        image_md5 = j['image_md5']
        #obs = st.session_state['public_observations'].get(image_md5)
        assert st.session_state['public_observations'].get(image_md5) == j
        print(f"{j.get('image_filename')}: {j['latitude']:6}, {j['longitude']:6} {j.get('timezone'):>6}")
        #print(obs)
        #print("\n=======")
    
    # ok, we see we have the data
    # now we need to push it
    token = os.environ.get("HF_TOKEN", None)
    api = HfApi(token=token)
    i = 1
    image_md5:str = jsons[i]['image_md5']
    
    #print(image_md5)
    rv:CommitInfo = push_observation(image_hash=image_md5, api=api, enable_push=True)
    print(rv)
    for k in ['commit_message', 'commit_url', 'commit_description', 'oid', 'repo_url', '_url']:
        print(f"{k}: {getattr(rv, k)}")
    
    # now we need to check if it's in the dataset
    assert check_observation_in_dataset(api, rv, jsons[i]) == True
    
    if 0:
        # now we need to remove it, will only get this far if the above passes
        rv_cleanup = cleanup_remove_files_from_dataset(api, rv, jsons[i])
        print(rv_cleanup)
        assert rv_cleanup is not None

        # now we need to check if it's gone
        assert check_observation_in_dataset(api, rv, jsons[i]) == False
        
        
