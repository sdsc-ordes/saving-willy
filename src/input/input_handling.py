from typing import List, Tuple
import datetime
import logging
import hashlib

import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from streamlit.runtime.uploaded_file_manager import UploadedFile

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

def check_inputs_are_set(empty_ok:bool=False, debug:bool=False) -> bool:
    """
    Checks if all expected inputs have been entered 
    
    Implementation: via the Streamlit session state.

    Args:
        empty_ok (bool): If True, returns True if no inputs are set. Default is False.
        debug (bool): If True, prints and logs the status of each expected input key. Default is False.
    Returns:
        bool: True if all expected input keys are set, False otherwise.
    """
    image_hashes = st.session_state.image_hashes
    if len(image_hashes) == 0:
        return empty_ok
    
    exp_input_key_stubs = ["input_latitude", "input_longitude", "input_date", "input_time"]
    #exp_input_key_stubs = ["input_latitude", "input_longitude", "input_author_email", "input_date", "input_time", 

    vals = []
    # the author_email is global/one-off - no hash extension.
    if "input_author_email" in st.session_state:
        val = st.session_state["input_author_email"]
        vals.append(val)
        if debug:
            msg = f"{'input_author_email':15}, {(val is not None):8}, {val}"
            m_logger.debug(msg)
            print(msg)


    for image_hash in image_hashes:
        for stub in exp_input_key_stubs:
            key = f"{stub}_{image_hash}"
            val = None
            if key in st.session_state:
                val = st.session_state[key]
            
            # handle cases where it is defined but empty 
            # if val is a string and empty, set to None
            if isinstance(val, str) and not val:
                val = None
            # if val is a list and empty, set to None (not sure what UI elements would return a list?)
            if isinstance(val, list) and not val:
                val = None
            # number 0 is ok - possibly. could be on the equator, e.g.
            
            vals.append(val)
            if debug:
                msg = f"{key:15}, {(val is not None):8}, {val}"
                m_logger.debug(msg)
                print(msg)


    
    return all([v is not None for v in vals])


def process_one_file(file:UploadedFile) -> Tuple[np.ndarray, str, str, InputObservation]:
    # do all the non-UI calcs
    # add the UI elements
    # and in-line, do processing/validation of the inputs
    # - how to deal with the gathered data? a) push into session state, b) return all the elements needed?
    
    viewcontainer = st.sidebar

    # do all the non-UI calcs first
    ## get the bytes first, then convert into 1) image, 2) md5
    _bytes = file.read()
    image_hash = hashlib.md5(_bytes).hexdigest()
    #file_bytes = np.asarray(bytearray(_bytes), dtype=np.uint8)
    image: np.ndarray = cv2.imdecode(np.asarray(bytearray(_bytes), dtype=np.uint8), 1)
    filename:str = file.name 
    image_datetime = get_image_datetime(file)
    m_logger.debug(f"image date extracted as {image_datetime} (from {file})")

    author_email = st.session_state["input_author_email"]
    

    # add the UI elements
    viewcontainer.title(f"Metadata for {filename}")
    ukey = image_hash

    # 3. Latitude Entry Box
    latitude = viewcontainer.text_input(
        "Latitude for " + filename, 
        #spoof_metadata.get('latitude', ""),
        key=f"input_latitude_{ukey}")
    if latitude and not is_valid_number(latitude):
        viewcontainer.error("Please enter a valid latitude (numerical only).")
        m_logger.error(f"Invalid latitude entered: {latitude}.")
    # 4. Longitude Entry Box
    longitude = viewcontainer.text_input(
        "Longitude for " + filename, 
        spoof_metadata.get('longitude', ""),
        key=f"input_longitude_{ukey}")
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
    date_option = st.sidebar.date_input("Date for "+filename, value=date_value, key=f"input_date_{ukey}")
    time_option = st.sidebar.time_input("Time for "+filename, time_value, key=f"input_time_{ukey}")

    observation = InputObservation(image=file, latitude=latitude, longitude=longitude,
                                author_email=author_email, date=image_datetime, time=None,
                                date_option=date_option, time_option=time_option,
                                uploaded_filename=file,
                                )

    #the_data = [] \
    #    + [image, file, image_hash, filename, ] \
    #    + [latitude, longitude, date_option, time_option]
    # TODO: pass in the hash to InputObservation, so it is done once only. (need to refactor the class a bit)
    
    the_data = (image, image_hash, filename, observation)
    
    return the_data



    
    # 

    
    

def process_files():
    # this is triggered whenever the uploaded files are changed.
    
    # process one file: add UI elements, and process the inputs
    # generate an observation from the return info
    # finally, put all the relevant stuff into the session state
    # - note: here we overwrite the session state, we aren't extending it. 

    # get files from state
    uploaded_files = st.session_state.file_uploader_data
    
    observations = {}
    images = {}
    image_hashes = []
    filenames = []
    
    for file in uploaded_files:
        (image, image_hash, filename, observation) = process_one_file(file)
        # big old debug because of pain.
        
        filenames.append(filename)
        image_hashes.append(image_hash)

        observations[image_hash] = observation
        images[image_hash] = image
        
    st.session_state.images = images
    st.session_state.files = uploaded_files
    st.session_state.observations = observations
    st.session_state.image_hashes = image_hashes
    st.session_state.image_filenames = filenames

        
    




def _setup_oneoff_inputs() -> None:
    '''
    Add the UI input elements for which we have one each
    
    '''
    viewcontainer = st.sidebar
    viewcontainer.title("Input image and data")

    # 1. Input the author email 
    author_email = viewcontainer.text_input("Author Email", spoof_metadata.get('author_email', ""),
                                            key="input_author_email")
    if author_email and not is_valid_email(author_email):   
        viewcontainer.error("Please enter a valid email address.")

    # 2. Image Selector
    #uploaded_files = viewcontainer.file_uploader("Upload an image", type=allowed_image_types, accept_multiple_files=True)

    st.file_uploader("Upload one or more images", type=["png", 'jpg', 'jpeg', 'webp'],
                                    accept_multiple_files=True, 
                                    key="file_uploader_data", 
                                    on_change=process_files)
    

        
def setup_input(
    viewcontainer: DeltaGenerator=None,
    _allowed_image_types: list=None, ) -> None:
    '''
    Set up the input handling for the whale observation guidance tool
    
    '''
    _setup_oneoff_inputs()
    # amazingly we just have to add the uploader and its callback, and the rest is dynamic.
    

def setup_input_monolithic(
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
    image_hashes = []
    filenames = []
    if uploaded_files is not None:
        for file in uploaded_files:

            viewcontainer.title(f"Metadata for {file.name}")

            # Display the uploaded image
            # load image using cv2 format, so it is compatible with the ML models
            file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
            filename = file.name
            filenames.append(filename) 
            image = cv2.imdecode(file_bytes, 1)
            # Extract and display image date-time
            image_datetime = None  # For storing date-time from image
            image_datetime = get_image_datetime(file)
            m_logger.debug(f"image date extracted as {image_datetime} (from {uploaded_files})")
        

            # 3. Latitude Entry Box
            latitude = viewcontainer.text_input(
                "Latitude for "+filename, 
                spoof_metadata.get('latitude', ""),
                key=f"input_latitude_{filename}")
            if latitude and not is_valid_number(latitude):
                viewcontainer.error("Please enter a valid latitude (numerical only).")
                m_logger.error(f"Invalid latitude entered: {latitude}.")
            # 4. Longitude Entry Box
            longitude = viewcontainer.text_input(
                "Longitude for "+filename, 
                spoof_metadata.get('longitude', ""),
                key=f"input_longitude_{filename}")
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
    st.session_state.image_filenames = filenames


