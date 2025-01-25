import datetime
import logging

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import cv2
import numpy as np

from input.input_observation import InputObservation
from input.input_validator import get_image_datetime, is_valid_email, is_valid_number

m_logger = logging.getLogger(__name__)
m_logger.setLevel(logging.INFO)

''' 
A module to setup the input handling for the whale observation guidance tool

both the UI elements (setup_input_UI) and the validation functions.
'''
allowed_image_types = ['jpg', 'jpeg', 'png', 'webp']

# an arbitrary set of defaults so testing is less painful...
# ideally we add in some randomization to the defaults
spoof_metadata = {
    "latitude": 23.5,
    "longitude": 44,
    "author_email": "super@whale.org",
    "date": None,
    "time": None,
}

def setup_input(
    viewcontainer: DeltaGenerator=None,
    _allowed_image_types: list=None, ) -> InputObservation:
    """
    Sets up the input interface for uploading an image and entering metadata.

    It provides input fields for an image upload, lat/lon, author email, and date-time. 
    In the ideal case, the image metadata will be used to populate location and datetime.

    Parameters:
        viewcontainer (DeltaGenerator, optional): The Streamlit container to use for the input interface. Defaults to st.sidebar.
        _allowed_image_types (list, optional): List of allowed image file types for upload. Defaults to allowed_image_types.

    Returns:
        InputObservation: An object containing the uploaded image and entered metadata.

    """
                
    if viewcontainer is None:
        viewcontainer = st.sidebar
        
    if _allowed_image_types is None:
        _allowed_image_types = allowed_image_types
    

    viewcontainer.title("Input image and data")

    # 1. Input the author email 
    author_email = viewcontainer.text_input("Author Email", spoof_metadata.get('author_email', ""))
    if author_email and not is_valid_email(author_email):   
        viewcontainer.error("Please enter a valid email address.")

    # 2. Image Selector
    uploaded_files = viewcontainer.file_uploader("Upload an image", type=allowed_image_types, accept_multiple_files=True)
    observations = {}
    images = {}
    image_hashes =[]
    if uploaded_files is not None:
        for file in uploaded_files:

            viewcontainer.title(f"Metadata for {file.name}")

            # Display the uploaded image
            # load image using cv2 format, so it is compatible with the ML models
            file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
            filename = file.name
            image = cv2.imdecode(file_bytes, 1)
            # Extract and display image date-time
            image_datetime = None  # For storing date-time from image
            image_datetime = get_image_datetime(file)
            m_logger.debug(f"image date extracted as {image_datetime} (from {uploaded_files})")
        

            # 3. Latitude Entry Box
            latitude = viewcontainer.text_input("Latitude for "+filename, spoof_metadata.get('latitude', ""))
            if latitude and not is_valid_number(latitude):
                viewcontainer.error("Please enter a valid latitude (numerical only).")
                m_logger.error(f"Invalid latitude entered: {latitude}.")
            # 4. Longitude Entry Box
            longitude = viewcontainer.text_input("Longitude for "+filename, spoof_metadata.get('longitude', ""))
            if longitude and not is_valid_number(longitude):
                viewcontainer.error("Please enter a valid longitude (numerical only).")
                m_logger.error(f"Invalid latitude entered: {latitude}.")
            # 5. Date/time
            ## first from image metadata
            if image_datetime is not None:
                time_value = datetime.datetime.strptime(image_datetime, '%Y:%m:%d %H:%M:%S').time()
                date_value = datetime.datetime.strptime(image_datetime, '%Y:%m:%d %H:%M:%S').date()
            else:
                time_value = datetime.datetime.now().time()  # Default to current time
                date_value = datetime.datetime.now().date()

            ## if not, give user the option to enter manually
            date_option = st.sidebar.date_input("Date for "+filename, value=date_value)
            time_option = st.sidebar.time_input("Time for "+filename, time_value)

            observation = InputObservation(image=file, latitude=latitude, longitude=longitude, 
                                        author_email=author_email, date=image_datetime, time=None, 
                                        date_option=date_option, time_option=time_option)
            image_hash = observation.to_dict()["image_md5"]
            observations[image_hash] = observation
            images[image_hash] = image
            image_hashes.append(image_hash)
    
    st.session_state.images = images
    st.session_state.files = uploaded_files
    st.session_state.observations = observations
    st.session_state.image_hashes = image_hashes

