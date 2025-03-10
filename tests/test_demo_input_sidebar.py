
from pathlib import Path
from io import BytesIO
from PIL import Image
import numpy as np
import os

import pytest
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest
from datetime import datetime, timedelta
import time

from input.input_handling import spoof_metadata
from input.input_observation import InputObservation
from input.input_handling import buffer_uploaded_files, load_debug_autopopulate

from streamlit.runtime.uploaded_file_manager import UploadedFile

from test_demo_multifile_upload import (
    mock_uploadedFile_List_ImageData, mock_uploadedFile,
    MockUploadedFile, )


# decorator that counts the number of times a function is called
def count_calls(func):
    def wrapper(*args, **kwargs):
        wrapper.called += 1
        return func(*args, **kwargs)
    wrapper.called = 0
    return wrapper


@count_calls
def wrapped_buffer_uploaded_files(*args, **kwargs):
    import streamlit as st
    uploaded_files = st.session_state.file_uploader_data
    _cprint(f"[I] buffering files in my side-effect! cool | {len(uploaded_files)}")
    for i, (key, img) in enumerate(st.session_state.images.items()):
        _cprint(f"    - image {i}: {type(img)} [{key}]")

    buffer_uploaded_files() # nowcall the real prod func
    _cprint(f"[I] finished the real buffering ! cool | {len(uploaded_files)}")

    
@count_calls
def wrapped_buffer_uploaded_files_allowed_once(*args, **kwargs):
    # this is a wrapper that only allows the real function to be called once
    # - this is to prevent the side-effect from being called multiple times
    # - the callback is only invoked when the input data is changed for the 
    #   real file_uploader object; but due to the 're-run script on interaction' 
    #   model, the side-effect is called each time.
    import streamlit as st
    uploaded_files = st.session_state.file_uploader_data
    if len(st.session_state.images) != 0:
        _cprint(f"[I] buffering already called before, side-effect! not rerun inner func | {len(uploaded_files)} | {len(st.session_state.images)}")
        for i, (key, img) in enumerate(st.session_state.images.items()):
            _cprint(f"    - image {i}: {type(img)} [{key}]")
        return
    
    _cprint(f"[I] buffering files in my side-effect! cool | {len(uploaded_files)}")
    for i, (key, img) in enumerate(st.session_state.images.items()):
        _cprint(f"    - image {i}: {type(img)} [{key}]")

    buffer_uploaded_files() # nowcall the real prod func
    _cprint(f"[I] finished the real buffering ! cool | {len(uploaded_files)}")
    
    

# - tests for apptest/demo_input_sidebar 

# zero test: no inputs 
#   -> empty session state
#   -> file_uploader with no files, ready to accept input
#   -> a couple of containers
#   -> not much on the main tab.

# many test: list of 2 inputs
#   -> session state with 2 files
#   -> file_uploader with 2 files, ready to accept more
#   -> the metadata container will have two groups inside, with several input elements
#   -> the main tab will have a couple of text_area elements showing the uploaded file metadata


OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
OKCYAN = '\033[96m'
FAIL = '\033[91m'
PURPLE = '\033[35m'
ENDC = '\033[0m'

def _cprint(msg:str, color:str=OKCYAN):
    print(f"{color}{msg}{ENDC}")


TIMEOUT = 10
#SCRIPT_UNDER_TEST = "src/main.py"
SCRIPT_UNDER_TEST = "src/apptest/demo_input_sidebar.py"

def verify_initial_session_state(at:AppTest):
    # the initialised states we expect 
    # - container_file_uploader exists
    # - container_metadata_inputs exists
    # - observations {}
    # - image_hashes []
    # - images {}
    # - files []
    # - public_observations {}
    assert at.session_state.observations == {}
    assert at.session_state.image_hashes == []
    assert at.session_state.images == {}
    assert at.session_state.files == []
    assert at.session_state.public_observations == {}
    assert "container_file_uploader" in at.session_state
    assert "container_metadata_inputs" in at.session_state

def verify_session_state_after_processing_files(at:AppTest, num_files:int):
    # this is after buffering & metadata extraction, but *BEFORE* the ML is run. 

    # now we've processed the files and got metadata, we expect some
    # changes in the elements in the session_state (x=same)
        # x container_file_uploader exists
        # x container_metadata_inputs exists
        # - observations 2 elements, keys -> some hashes. values: InputObservation objects
        # - image_hashes 2 elements, hashes (str) | 
        # - images {} 2 elements, keys -> hashes, values -> np.ndarray. 
        # - files [] a list of 2 MockUploadedFile objects
        # x public_observations {}
    # I think just verify the sizes and types, we could do a data integrity 
    # check on the hashes matching everywhere, but that is far from visual.
     
    assert len(at.session_state.observations) == num_files
    for obs in at.session_state.observations.values():
        assert isinstance(obs, InputObservation)
    assert len(at.session_state.image_hashes) == num_files
    for hash in at.session_state.image_hashes:
        assert isinstance(hash, str)
    assert len(at.session_state.images) == num_files
    for img in at.session_state.images.values():
        assert isinstance(img, np.ndarray)
    assert len(at.session_state.image_hashes) == num_files
    for hash in at.session_state.image_hashes:
        assert isinstance(hash, str)
    assert len(at.session_state.files) == num_files
    for file in at.session_state.files:
        assert isinstance(file, MockUploadedFile)
        assert isinstance(file, BytesIO) # cool it looks like the FileUploader.
        #assert isinstance(file, UploadedFile) no... it isn't  but bytesIO is the parent class

    assert at.session_state.public_observations == {}

def verify_metadata_in_demo_display(at:AppTest, num_files:int):
    # we can check the metadata display in the main area
    # - this presentation is not part of the normal app, but is a test-only feature

    if 'src/main.py' in SCRIPT_UNDER_TEST:
        raise ValueError("This test is not valid for the main app, only for unit/component test snippets")

    # finally we can check the main area, where the metadata is displayed
    # since we uplaoded num_files files, hopefully we get num_files text areas 
    assert len(at.text_area) == num_files
    # expecting 
    exp0 = "index: 0, name: cakes.jpg, datetime: 2024:10:24 15:59:45, lat: 46.51860277777778, lon:6.562075"
    exp1 = "index: 1, name: cakes_no_exif_datetime.jpg, datetime: None, lat: 46.51860277777778, lon:6.562075"
    exp2 = "index: 2, name: cakes_no_exif_gps.jpg, datetime: 2024:10:24 15:59:45, lat: None, lon:None"

    assert at.text_area[0].value == exp0
    assert at.text_area[1].value == exp1
    if num_files >= 1:
        assert at.text_area(key='metadata_0').value == exp0
    if num_files >= 2:
        assert at.text_area(key='metadata_1').value == exp1
    if num_files >= 3:
        assert at.text_area(key='metadata_2').value == exp2

@pytest.mark.component
def test_no_input_no_interaction():
    
    # zero test: no inputs 
    #   -> empty session state (ok many initialised, but empty data)
    #   -> file_uploader with no files, ready to accept input
    #   -> a couple of containers
    #   -> not much on the main tab.

    at = AppTest.from_file(SCRIPT_UNDER_TEST, default_timeout=10).run()
    verify_initial_session_state(at)

    dbg = load_debug_autopopulate()
    #var = at.session_state.input_author_email
    #_cprint(f"[I] input email is '{var}' type: {type(var)} | is None? {var is None} | {dbg}", PURPLE)
    if dbg: # autopopulated
        assert at.session_state.input_author_email == spoof_metadata.get("author_email")
    else: # should be empty, the user has to fill it in
        assert at.session_state.input_author_email == ""

    # print (f"[I] whole tree: {at._tree}")
    # for elem in at.sidebar.markdown:
    #     print("\t", elem.value)

    # do some basic checks on what is present in the sidebar
    assert len(at.sidebar.divider) == 1
    
    # in the sidebar, we have the progress indicator, then the fileuploader and metadata inputs
    # - annoyingly we can't use keys for markdown. 
    # - so we are sensitive to the order. 
    # - we could grab all the text, and just be content with presence of the target strings 
    #   anywhere in the sidebar? that would be more robust at least.
    assert "Progress: 0/5" in at.sidebar.markdown[0].value
    assert "st-key-container_file_uploader_id" in at.sidebar.markdown[1].value
    assert "st-key-container_metadata_inputs_id" in at.sidebar.markdown[2].value
    assert "Metadata Inputs... wait for file upload" in at.sidebar.markdown[3].value

    # there should be 1 input, for the author_email, in this path (no files uploaded)
    assert len(at.sidebar.text_input) == 1
    
    # can't check for the presence of containers (they are st.Block elements in the tree)
    # - no way to access the list of them, nor by key/id. nor by getter (unlike
    #   images which seem to have an undocumented accessor, "imgs")
    # best we can do is check that the session state ids exist, which is really basic but ok
    assert "container_file_uploader" in at.session_state
    assert "container_metadata_inputs" in at.session_state
    # wow, the keys defined in the constructor are not honoured in session_state, unlike with
    #   the text_input elements.  
    #   code init -- st.container(border=True, key="container_file_uploader_id")
    # so skip these ones for now. 
    #   assert "container_file_uploader_id" in at.session_state
    #   assert "container_metadata_inputs_id" in at.session_state
    
@pytest.mark.component
@patch("streamlit.file_uploader")
def test_two_input_files_realdata(mock_file_rv: MagicMock, mock_uploadedFile_List_ImageData):
    # many test: list of 2 inputs
    #   -> session state with 2 files
    #   -> file_uploader with 2 files, ready to accept more
    #   -> the metadata container will have two groups inside, with several input elements
    #   -> the main tab will have a couple of text_area elements showing the uploaded file metadata

    
    # Create a list of 2 mock files
    num_files = 2
    mock_files = mock_uploadedFile_List_ImageData(num_files=num_files)
    
    # Set the return value of the mocked file_uploader to the list of mock files
    mock_file_rv.return_value = mock_files

    # Run the Streamlit app
    at = AppTest.from_file(SCRIPT_UNDER_TEST, default_timeout=TIMEOUT).run()
    verify_initial_session_state(at)

    # put the mocked file_upload into session state, as if it were the result of a file upload, with the key 'file_uploader_data'
    at.session_state["file_uploader_data"] = mock_files
    # the side effect cant run until now (need file_uploader_data to be set)
    mock_file_rv.side_effect = wrapped_buffer_uploaded_files

    print(f"[I] session state: {at.session_state}")
    at.run()
    print(f"[I] session state: {at.session_state}")
    print(f"full tree: {at._tree}")

    verify_session_state_after_processing_files(at, num_files)

    # and then there are plenty of visual elements, based on the image hashes.
    for hash in at.session_state.image_hashes:
        # check that each of the 4 inputs is present
        assert at.sidebar.text_input(key=f"input_latitude_{hash}") is not None
        assert at.sidebar.text_input(key=f"input_longitude_{hash}") is not None
        assert at.sidebar.date_input(key=f"input_date_{hash}") is not None
        assert at.sidebar.time_input(key=f"input_time_{hash}") is not None

    if 'demo_input_sidebar' in SCRIPT_UNDER_TEST:
        verify_metadata_in_demo_display(at, num_files)
