# a minimal snippet for validating the upload sequence, for testing purposes (with AppTest)
from typing import List
import streamlit as st

# to run streamlit from this subdir, we need the the src dir on the path
# NOTE: pytest doesn't need this to run the tests, but to develop the test
# harness is hard without running streamlit 
import sys
from os import path
# src (parent from here)
src_dir = path.dirname( path.dirname( path.abspath(__file__) ) )
sys.path.append(src_dir)

# we aim to validate: 
# - user uploads multple files via FileUploader (with key=file_uploader_data)
# - they get buffered into session state
# - some properties are extracted from the files, and are displayed in a visual
#   element so we can validate them with apptest.


from input.input_handling import (
    spoof_metadata, is_valid_email,
    get_image_datetime, get_image_latlon,
    init_input_data_session_states
)

def buffer_uploaded_files():
    st.write("buffering files! ")
    uploaded_files:List = st.session_state.file_uploader_data
    for ix, file in enumerate(uploaded_files):
        image_datetime_raw = get_image_datetime(file)
        latitude0, longitude0 = get_image_latlon(file)
        #st.write(f"- file {ix}: {file.name}")
        #st.write(f"  - datetime: {image_datetime_raw}")
        #st.write(f"  - lat/lon: {latitude0}, {longitude0}")
        s = f"index: {ix}, name: {file.name}, datetime: {image_datetime_raw}, lat: {latitude0}, lon:{longitude0}"
        st.text_area(f"{file.name}", value=s, key=f"metadata_{ix}")
        print(s)
        
init_input_data_session_states()

with st.sidebar:
    author_email = st.text_input("Author Email", spoof_metadata.get('author_email', ""),
                                                key="input_author_email")
    if author_email and not is_valid_email(author_email):   
        st.error("Please enter a valid email address.")

    st.file_uploader(
        "Upload one or more images", type=["png", 'jpg', 'jpeg', 'webp'],
        accept_multiple_files=True, 
        key="file_uploader_data", 
        on_change=buffer_uploaded_files
        )

# this is the callback that would be triggered by the FileUploader
# - unfortunately, we get into a mess now
#   - in real app, this runs twice and breaks (because of the duplicate keys)
#   - in the test, if we don't run manually, we don't get the frontend elements to validate
#   - if we remove the on_change, both run ok. but it deviates from the true app.
# - possible ways forward?
#   - could we patch the on_change, or substitute the buffer_uploaded_files?
if (1 and "file_uploader_data" in st.session_state and 
    len(st.session_state.file_uploader_data) ):
    print(f"buffering files: {len(st.session_state.file_uploader_data)}")
    buffer_uploaded_files()