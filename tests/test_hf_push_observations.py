# copilot did this -- no idea whether they pass yet
import pytest
from unittest.mock import MagicMock, patch
import json
from huggingface_hub import CommitInfo
import streamlit as st
from hf_push_observations import push_observation

class AnyStringWith(str):
    '''
    Helper class to allow for partial string matching in mock calls
    
    Example:
        result = database.Query('complicated sql with an id: %s' % id)
        database.Query.assert_called_once_with(AnyStringWith(id))
    # https://stackoverflow.com/a/16976500
    '''
    
    def __eq__(self, other):
        return self in other
    
@pytest.fixture
def mock_api():
    return MagicMock()

@pytest.fixture
def mock_observation():
    return {
        "author_email": "test@example.com",
        "image_md5": "1234567890abcdef",
        "data": "test_data"
    }

@pytest.fixture
def setup_session_state(mock_observation):
    st.session_state.public_observations = {"test_hash": mock_observation}

@patch("hf_push_observations.tempfile.NamedTemporaryFile")
@patch("hf_push_observations.st.error")
@patch("hf_push_observations.st.info")
def test_push_observation_success(mock_info, mock_error, mock_tempfile, setup_session_state, mock_api, mock_observation):
    '''
    send a valid observation to the dataset (in mock mode)
    - fetch the observation from the session state
    - write it to a temp file
    - push it to the dataset
    - check the commit message
    (we mock the tempfile, and the api.upload_file, plus streamlit text funcs)
    '''
    mock_tempfile.return_value.__enter__.return_value.name = "/tmp/test.json"
    commit_url = "https://huggingface.co/Saving-Willy/temp_dataset/commit/1234567890abcdef"

    mock_api.upload_file.return_value = CommitInfo(
        commit_message="Test commit",
        commit_url=commit_url,
        commit_description="???",
        oid="123567890abcdef",
        )
    

    result = push_observation("test_hash", mock_api, enable_push=True)

    assert result.commit_message == "Test commit"
    mock_info.assert_called_with(f"observation attempted tx to repo happy walrus: {result}")
    mock_error.assert_not_called()

@patch("hf_push_observations.tempfile.NamedTemporaryFile")
@patch("hf_push_observations.st.error")
@patch("hf_push_observations.st.info")
def test_push_observation_no_push(mock_info, mock_error, mock_tempfile, setup_session_state, mock_api, mock_observation):
    '''
    execute push_observation with the push_enable flag set to False
    - fetch the observation from the session state
    - write it to a temp file
    - since no push should occur, the expected result is None
    (we mock the tempfile, and the api.upload_file, plus streamlit text funcs)
    '''
    mock_tempfile.return_value.__enter__.return_value.name = "/tmp/test.json"

    result = push_observation("test_hash", mock_api, enable_push=False)

    assert result is None
    mock_info.assert_called_with(AnyStringWith(f"fname ") and AnyStringWith("| path"))
    mock_error.assert_not_called()

@patch("hf_push_observations.st.error")
def test_push_observation_not_found(mock_error, mock_api):
    '''
    execute push_observation with data missing, provoke an error
    - fetch the observation from the session state
    - write it to a temp file
    - since no push should occur, the expected result is None
    (we mock the api.upload_file, plus streamlit text funcs)
    '''
    # empty state means when we try to fetch the observation, it will not be found
    st.session_state.public_observations = {}

    result = push_observation("invalid_hash", mock_api, enable_push=True)

    assert result is None
    mock_error.assert_called_once_with("Could not find observation with hash invalid_hash")

