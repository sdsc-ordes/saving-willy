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
from input.input_validator import get_image_datetime, is_valid_email, is_valid_number, get_image_latlon

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
    "latitude": 0.5,
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


def buffer_uploaded_files():
    """
    Buffers uploaded files to session_state (images, image_hashes, filenames).

    Buffers uploaded files by extracting and storing filenames, images, and
    image hashes in the session state.

    Adds the following keys to `st.session_state`:
    - `images`: dict mapping image hashes to image data (numpy arrays)
    - `files`: list of uploaded files
    - `image_hashes`: list of image hashes
    - `image_filenames`: list of filenames
    """

    
    # buffer info from the file_uploader that doesn't require further user input
    # - the image, the hash, the filename
    # a separate function takes care of per-file user inputs for metadata
    # - this is necessary because dynamically producing more widgets should be
    #   avoided inside callbacks (tl;dr: they dissapear)
    
    # - note that the UploadedFile objects have file_ids, which are unique to each file
    #   - these file_ids are not persistent between sessions, seem to just be random identifiers. 
    

    # get files from state 
    uploaded_files:List = st.session_state.file_uploader_data
    
    filenames = []
    images = {}
    image_hashes = []
    
    for ix, file in enumerate(uploaded_files):
        filename:str = file.name
        print(f"[D] processing {ix}th file {filename}. {file.file_id} {file.type} {file.size}")
        # image to np and hash both require reading the file so do together
        image, image_hash = load_file_and_hash(file)
        print(f"   [D] {ix}th file {filename} hash: {image_hash}")
        
        filenames.append(filename)
        image_hashes.append(image_hash)

        images[image_hash] = image
        
    st.session_state.images = images
    st.session_state.files = uploaded_files
    st.session_state.image_hashes = image_hashes
    st.session_state.image_filenames = filenames

    
def load_file_and_hash(file:UploadedFile) -> Tuple[np.ndarray, str]:
    """
    Loads an image file and computes its MD5 hash.
    
    Since both operations require reading the full file contentsV, they are done
    together for efficiency.
    
    Args:
        file (UploadedFile): The uploaded file to be processed.
    Returns:
        Tuple[np.ndarray, str]: A tuple containing the decoded image as a NumPy array and the MD5 hash of the file's contents.
    """
    # two operations that require reading the file done together for efficiency
    # load the file, compute the hash, return the image and hash
    _bytes = file.read()
    image_hash = hashlib.md5(_bytes).hexdigest()
    image: np.ndarray = cv2.imdecode(np.asarray(bytearray(_bytes), dtype=np.uint8), 1)
    
    return (image, image_hash)

    
        
def metadata_inputs_one_file(file:UploadedFile, image_hash:str, dbg_ix:int=0) -> InputObservation:
    """
    Creates and parses metadata inputs for a single file
    
    Args:
        file (UploadedFile): The uploaded file for which metadata is being handled.
        image_hash (str): The hash of the image.
        dbg_ix (int, optional): Debug index to differentiate data in each input group. Defaults to 0.
    Returns:
        InputObservation: An object containing the metadata and other information for the input file.
    """
    # dbg_ix is a hack to have different data in each input group, checking persistence
    
    if st.session_state.container_metadata_inputs is not None:
        _viewcontainer = st.session_state.container_metadata_inputs
    else:
        _viewcontainer = st.sidebar
        m_logger.warning("[W] `container_metadata_inputs` is None, using sidebar")
        


    author_email = st.session_state["input_author_email"]
    filename = file.name
    image_datetime_raw = get_image_datetime(file)
    latitude0, longitude0 = get_image_latlon(file)
    msg = f"[D] {filename}: lat, lon from image metadata: {latitude0}, {longitude0}"
    m_logger.debug(msg)
    
    if latitude0 is None: # get some default values if not found in exifdata
        latitude0:float = spoof_metadata.get('latitude', 0) + dbg_ix
    if longitude0 is None:
        longitude0:float = spoof_metadata.get('longitude', 0) - dbg_ix
        
    image = st.session_state.images.get(image_hash, None)
    # add the UI elements
    #viewcontainer.title(f"Metadata for {filename}")
    viewcontainer = _viewcontainer.expander(f"Metadata for {file.name}", expanded=True)

    # TODO: use session state so any changes are persisted within session -- currently I think
    # we are going to take the defaults over and over again -- if the user adjusts coords, or date, it will get lost
    # - it is a bit complicated, if no values change, they persist (the widget definition: params, name, key, etc)
    #   even if the code is re-run. but if the value changes, it is lost.
    

    # 3. Latitude Entry Box
    latitude = viewcontainer.text_input(
        "Latitude for " + filename, 
        latitude0,
        key=f"input_latitude_{image_hash}")
    if latitude and not is_valid_number(latitude):
        viewcontainer.error("Please enter a valid latitude (numerical only).")
        m_logger.error(f"Invalid latitude entered: {latitude}.")
    # 4. Longitude Entry Box
    longitude = viewcontainer.text_input(
        "Longitude for " + filename, 
        longitude0,
        key=f"input_longitude_{image_hash}")
    if longitude and not is_valid_number(longitude):
        viewcontainer.error("Please enter a valid longitude (numerical only).")
        m_logger.error(f"Invalid latitude entered: {latitude}.")

    # 5. Date/time
    ## first from image metadata
    if image_datetime_raw is not None:
        time_value = datetime.datetime.strptime(image_datetime_raw, '%Y:%m:%d %H:%M:%S').time()
        date_value = datetime.datetime.strptime(image_datetime_raw, '%Y:%m:%d %H:%M:%S').date()
    else:
        time_value = datetime.datetime.now().time()  # Default to current time
        date_value = datetime.datetime.now().date()

    ## either way, give user the option to enter manually (or correct, e.g. if camera has no rtc clock)
    date = viewcontainer.date_input("Date for "+filename, value=date_value, key=f"input_date_{image_hash}")
    time = viewcontainer.time_input("Time for "+filename, time_value, key=f"input_time_{image_hash}")

    observation = InputObservation(image=image, latitude=latitude, longitude=longitude,
                                author_email=author_email, image_datetime_raw=image_datetime_raw, 
                                date=date, time=time,
                                uploaded_file=file, image_md5=image_hash
                                )

    return observation
    

    
def _setup_dynamic_inputs() -> None:
    """
    Setup metadata inputs dynamically for each uploaded file, and process.
    
    This operates on the data buffered in the session state, and writes 
    the observation objects back to the session state.
    
    """

    # for each file uploaded,
    # - add the UI elements for the metadata
    # - validate the data
    # end of cycle should have observation objects set for each file.
    # - and these go into session state
    
    # load the files from the session state
    uploaded_files:List = st.session_state.files
    hashes = st.session_state.image_hashes
    #images = st.session_state.images
    observations = {}
    
    for ix, file in enumerate(uploaded_files):
        hash = hashes[ix]
        observation = metadata_inputs_one_file(file, hash, ix)
        old_obs = st.session_state.observations.get(hash, None)
        if old_obs is not None:
            if old_obs == observation:
                m_logger.debug(f"[D] {ix}th observation is the same as before. retaining")
                observations[hash] = old_obs
            else:
                m_logger.debug(f"[D] {ix}th observation is different from before. updating")
                observations[hash] = observation
                observation.show_diff(old_obs)
        else:
            m_logger.debug(f"[D] {ix}th observation is new (image_hash not seen before). Storing")
            observations[hash] = observation
        
    st.session_state.observations = observations


def _setup_oneoff_inputs() -> None:
    '''
    Add the UI input elements for which we have one covering all files
    
    - author email
    - file uploader (accepts multiple files)
    '''

    # fetch the container for the file uploader input elements
    container_file_uploader = st.session_state.container_file_uploader 

    with container_file_uploader:
        # 1. Input the author email 
        author_email = st.text_input("Author Email", spoof_metadata.get('author_email', ""),
                                                key="input_author_email")
        if author_email and not is_valid_email(author_email):   
            st.error("Please enter a valid email address.")

        # 2. Image Selector
        st.file_uploader(
            "Upload one or more images", type=["png", 'jpg', 'jpeg', 'webp'],
            accept_multiple_files=True, 
            key="file_uploader_data", on_change=buffer_uploaded_files)

        
                                    
                                    
    

        
def setup_input() -> None:
    '''
    Set up the user input handling (files and metadata) 

    It provides input fields for an image upload, and author email.
    Then for each uploaded image, 
    - it provides input fields for lat/lon, date-time.
    - In the ideal case, the image metadata will be used to populate location and datetime.

    Data is stored in the Streamlit session state for downstream processing,
    nothing is returned
    
    '''
    # configure the author email and file_uploader (with callback to buffer files)
    _setup_oneoff_inputs()
    
    # setup dynamic UI input elements, based on the data that is buffered in session_state
    _setup_dynamic_inputs()
    

def init_input_container_states() -> None:
    '''
    Initialise the layout containers used in the input handling
    '''
    #if "container_per_file_input_elems" not in st.session_state:
    #    st.session_state.container_per_file_input_elems = None

    if "container_file_uploader" not in st.session_state:
        st.session_state.container_file_uploader = None

    if "container_metadata_inputs" not in st.session_state:
        st.session_state.container_metadata_inputs = None    

def init_input_data_session_states() -> None:
    '''
    Initialise the session state variables used in the input handling
    '''

    if "image_hashes" not in st.session_state:
        st.session_state.image_hashes = []

    # TODO: ideally just use image_hashes, but need a unique key for the ui elements
    # to track the user input phase; and these are created before the hash is generated. 
    if "image_filenames" not in st.session_state:
        st.session_state.image_filenames = []

    if "observations" not in st.session_state:
        st.session_state.observations = {}

    if "images" not in st.session_state:
        st.session_state.images = {}

    if "files" not in st.session_state:
        st.session_state.files = []

    if "public_observations" not in st.session_state:
        st.session_state.public_observations = {}


    
def add_input_UI_elements() -> None:
    '''
    Create the containers within which user input elements will be placed
    '''
    # we make containers ahead of time, allowing consistent order of elements
    # which are not created in the same order.
    
    st.divider()
    st.title("Input image and data")
    
    # create and style a container for the file uploader/other one-off inputs
    st.markdown('<style>.st-key-container_file_uploader_id { border: 1px solid skyblue; border-radius: 5px; }</style>', unsafe_allow_html=True)
    container_file_uploader = st.container(border=True, key="container_file_uploader_id")
    st.session_state.container_file_uploader = container_file_uploader

    # create and style a container for the dynamic metadata inputs
    st.markdown('<style>.st-key-container_metadata_inputs_id { border: 1px solid lightgreen; border-radius: 5px; }</style>', unsafe_allow_html=True)
    container_metadata_inputs = st.container(border=True, key="container_metadata_inputs_id")
    container_metadata_inputs.write("Metadata Inputs... wait for file upload ")
    st.session_state.container_metadata_inputs = container_metadata_inputs


def dbg_show_observation_hashes() -> None:
    """
    Displays information about each observation including the hash 
    
    - debug usage, keeping track of the hashes and persistence of the InputObservations.
    - it renders text to the current container, not intended for final app.
    
    """

    # a debug: we seem to be losing the whale classes?
    st.write(f"[D] num observations: {len(st.session_state.observations)}")
    s = ""
    for hash in st.session_state.observations.keys():
        obs = st.session_state.observations[hash]
        s += f"- [D] observation {hash} ({obs._inst_id}) has {len(obs.top_predictions)} predictions\n"
        #s += f"   - {repr(obs)}\n" # check the str / repr method
        
        #print(obs)
    
    st.markdown(s)
