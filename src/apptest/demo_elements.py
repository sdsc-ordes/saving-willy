# a small library of elements used in testing, presenting some 
# processed data in simple ways that are easily testable via AppTest
import streamlit as st
from input.input_handling import (
    get_image_datetime, get_image_latlon
)

def show_uploaded_file_info():
    if "file_uploader_data" not in st.session_state or \
        not st.session_state.file_uploader_data:
    
        st.write("No files uploaded yet")
        return

    st.write("the buffered files:")
    
    uploaded_files = st.session_state.file_uploader_data
    for ix, file in enumerate(uploaded_files):
        image_datetime_raw = get_image_datetime(file)
        latitude0, longitude0 = get_image_latlon(file)
        s = f"index: {ix}, name: {file.name}, datetime: {image_datetime_raw}, lat: {latitude0}, lon:{longitude0}"
        st.text_area(f"{file.name}", value=s, key=f"metadata_{ix}")
        print(s)

