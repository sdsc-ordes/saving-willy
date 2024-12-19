from PIL import Image
from PIL import ExifTags
import re
import datetime
import hashlib
import logging

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile # for type hinting
from streamlit.delta_generator import DeltaGenerator

import cv2
import numpy as np

m_logger = logging.getLogger(__name__)
# we can set the log level locally for funcs in this module
#g_m_logger.setLevel(logging.DEBUG)
m_logger.setLevel(logging.INFO)

''' 
A module to setup the input handling for the whale observation guidance tool

both the UI elements (setup_input_UI) and the validation functions.
'''
#allowed_image_types = ['webp']
allowed_image_types = ['jpg', 'jpeg', 'png', 'webp']


# autogenerated class to hold the input data
class InputObservation:
    """
    A class to hold an input observation and associated metadata

    Attributes:
        image (Any): 
            The image associated with the observation.
        latitude (float): 
            The latitude where the observation was made.
        longitude (float): 
            The longitude where the observation was made.
        author_email (str): 
            The email of the author of the observation.
        date (str): 
            The date when the observation was made.
        time (str): 
            The time when the observation was made.
        date_option (str): 
            Additional date option for the observation.
        time_option (str): 
            Additional time option for the observation.
        uploaded_filename (Any): 
            The uploaded filename associated with the observation.

    Methods:
        __str__():
            Returns a string representation of the observation.
        __repr__():
            Returns a string representation of the observation.
        __eq__(other):
            Checks if two observations are equal.
        __ne__(other):
            Checks if two observations are not equal.
        __hash__():
            Returns the hash of the observation.
        to_dict():
            Converts the observation to a dictionary.
        from_dict(data):
            Creates an observation from a dictionary.
        from_input(input):
            Creates an observation from another input observation.
    """
    def __init__(self, image=None, latitude=None, longitude=None, author_email=None, date=None, time=None, date_option=None, time_option=None, uploaded_filename=None):
        self.image = image
        self.latitude = latitude
        self.longitude = longitude
        self.author_email = author_email
        self.date = date
        self.time = time
        self.date_option = date_option
        self.time_option = time_option
        self.uploaded_filename = uploaded_filename

    def __str__(self):
        return f"Observation: {self.image}, {self.latitude}, {self.longitude}, {self.author_email}, {self.date}, {self.time}, {self.date_option}, {self.time_option}, {self.uploaded_filename}"

    def __repr__(self):
        return f"Observation: {self.image}, {self.latitude}, {self.longitude}, {self.author_email}, {self.date}, {self.time}, {self.date_option}, {self.time_option}, {self.uploaded_filename}"

    def __eq__(self, other):
        return (self.image == other.image and self.latitude == other.latitude and self.longitude == other.longitude and 
                self.author_email == other.author_email and self.date == other.date and self.time == other.time and 
                self.date_option == other.date_option and self.time_option == other.time_option and self.uploaded_filename == other.uploaded_filename)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.image, self.latitude, self.longitude, self.author_email, self.date, self.time, self.date_option, self.time_option, self.uploaded_filename))

    def to_dict(self):
        return {
            #"image": self.image,
            "image_filename": self.uploaded_filename.name if self.uploaded_filename else None,
            "image_md5": hashlib.md5(self.uploaded_filename.read()).hexdigest() if self.uploaded_filename else None,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "author_email": self.author_email,
            "date": self.date,
            "time": self.time,
            "date_option": self.date_option,
            "time_option": self.time_option,
            "uploaded_filename": self.uploaded_filename
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["image"], data["latitude"], data["longitude"], data["author_email"], data["date"], data["time"], data["date_option"], data["time_option"], data["uploaded_filename"])

    @classmethod
    def from_input(cls, input):
        return cls(input.image, input.latitude, input.longitude, input.author_email, input.date, input.time, input.date_option, input.time_option, input.uploaded_filename)

    @staticmethod
    def from_input(input):
        return InputObservation(input.image, input.latitude, input.longitude, input.author_email, input.date, input.time, input.date_option, input.time_option, input.uploaded_filename)

    @staticmethod
    def from_dict(data):
        return InputObservation(data["image"], data["latitude"], data["longitude"], data["author_email"], data["date"], data["time"], data["date_option"], data["time_option"], data["uploaded_filename"])


def is_valid_number(number:str) -> bool:
    """
    Check if the given string is a valid number (int or float, sign ok)

    Args:
        number (str): The string to be checked.

    Returns:
        bool: True if the string is a valid number, False otherwise.
    """
    pattern = r'^[-+]?[0-9]*\.?[0-9]+$'
    return re.match(pattern, number) is not None


# Function to validate email address
def is_valid_email(email:str) -> bool:
    """
    Validates if the provided email address is in a correct format.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email address is valid, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Function to extract date and time from image metadata
def get_image_datetime(image_file: UploadedFile) -> str | None: 
    """
    Extracts the original date and time from the EXIF metadata of an uploaded image file.

    Args:
        image_file (UploadedFile): The uploaded image file from which to extract the date and time.

    Returns:
        str: The original date and time as a string if available, otherwise None.

    Raises:
        Warning: If the date and time could not be extracted from the image metadata.
    """
    try:
        image = Image.open(image_file)
        exif_data = image._getexif()
        if exif_data is not None:
            for tag, value in exif_data.items():
                if ExifTags.TAGS.get(tag) == 'DateTimeOriginal':
                    return value
    except Exception as e: # FIXME: what types of exception?
         st.warning(f"Could not extract date from image metadata. (file: {image_file.name})")
         # TODO: add to logger
    return None


# an arbitrary set of defaults so testing is less painful...
# ideally we add in some randomization to the defaults
spoof_metadata = {
    "latitude": 23.5,
    "longitude": 44,
    "author_email": "super@whale.org",
    "date": None,
    "time": None,
}

#def display_whale(whale_classes:List[str], i:int, viewcontainer=None):
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

    # 1. Image Selector
    uploaded_filename = viewcontainer.file_uploader("Upload an image", type=allowed_image_types)
    image_datetime = None  # For storing date-time from image

    if uploaded_filename is not None:
        # Display the uploaded image
        #image = Image.open(uploaded_filename)
        # load image using cv2 format, so it is compatible with the ML models
        file_bytes = np.asarray(bytearray(uploaded_filename.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)


        viewcontainer.image(image, caption='Uploaded Image.', use_column_width=True)
        # store the image in the session state
        st.session_state.image = image
        

        # Extract and display image date-time
        image_datetime = get_image_datetime(uploaded_filename)
        print(f"[D] image date extracted as {image_datetime}")
        m_logger.debug(f"image date extracted as {image_datetime} (from {uploaded_filename})")
        

    # 2. Latitude Entry Box
    latitude = viewcontainer.text_input("Latitude", spoof_metadata.get('latitude', ""))
    if latitude and not is_valid_number(latitude):
        viewcontainer.error("Please enter a valid latitude (numerical only).")
        m_logger.error(f"Invalid latitude entered: {latitude}.")
    # 3. Longitude Entry Box
    longitude = viewcontainer.text_input("Longitude", spoof_metadata.get('longitude', ""))
    if longitude and not is_valid_number(longitude):
        viewcontainer.error("Please enter a valid longitude (numerical only).")
        m_logger.error(f"Invalid latitude entered: {latitude}.")
        
    # 4. Author Box with Email Address Validator
    author_email = viewcontainer.text_input("Author Email", spoof_metadata.get('author_email', ""))

    if author_email and not is_valid_email(author_email):   
        viewcontainer.error("Please enter a valid email address.")

    # 5. date/time
    ## first from image metadata
    if image_datetime is not None:
        time_value = datetime.datetime.strptime(image_datetime, '%Y:%m:%d %H:%M:%S').time()
        date_value = datetime.datetime.strptime(image_datetime, '%Y:%m:%d %H:%M:%S').date()
    else:
        time_value = datetime.datetime.now().time()  # Default to current time
        date_value = datetime.datetime.now().date()

    ## if not, give user the option to enter manually
    date_option = st.sidebar.date_input("Date", value=date_value)
    time_option = st.sidebar.time_input("Time", time_value)

    observation = InputObservation(image=uploaded_filename, latitude=latitude, longitude=longitude, 
                                   author_email=author_email, date=image_datetime, time=None, 
                                   date_option=date_option, time_option=time_option)
    return observation

