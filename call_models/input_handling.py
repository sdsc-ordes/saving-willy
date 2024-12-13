from PIL import Image
from PIL import ExifTags
import re
import datetime
import hashlib
import logging

import streamlit as st
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

# define function to validate number, allowing signed float
def is_valid_number(number:str) -> bool:
    pattern = r'^[-+]?[0-9]*\.?[0-9]+$'
    return re.match(pattern, number) is not None


# Function to validate email address
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Function to extract date and time from image metadata
def get_image_datetime(image_file):
    try:
        image = Image.open(image_file)
        exif_data = image._getexif()
        if exif_data is not None:
            for tag, value in exif_data.items():
                if ExifTags.TAGS.get(tag) == 'DateTimeOriginal':
                    return value
    except Exception as e:
        st.warning("Could not extract date from image metadata.")
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
def setup_input(viewcontainer: st.delta_generator.DeltaGenerator=None, _allowed_image_types: list=None, ):
                
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

