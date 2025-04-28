from typing import Tuple, Union
import random
import string
import hashlib
import re
from fractions import Fraction
from PIL import Image
from PIL import ExifTags

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

def generate_random_md5(length:int=16) -> str:
    """
    Generate a random MD5 hash.

    Args:
        length (int): The length of the random string to generate. Default is 16.

    Returns:
        str: The MD5 hash of the generated random string.
    """

    # Generate a random string
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    # Encode the string and compute its MD5 hash
    md5_hash = hashlib.md5(random_string.encode()).hexdigest()
    return md5_hash


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
    #pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    # do not allow starting with a +
    pattern = r'^[a-zA-Z0-9_]+[a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# Function to extract date and time from image metadata
def get_image_datetime(image_file:UploadedFile) -> Union[str, None]: 
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
            if ExifTags.Base.DateTimeOriginal in exif_data:
                return exif_data.get(ExifTags.Base.DateTimeOriginal)
    except Exception as e: # FIXME: what types of exception?
         st.warning(f"Could not extract date from image metadata. (file: {image_file.name})")
         # TODO: add to logger
    return None

# function to extract the timezone from image metadata
def get_image_timezone(image_file:UploadedFile) -> Union[str, None]:
    """
    Extracts the timezone from the EXIF metadata of an uploaded image file.

    Args:
        image_file (UploadedFile): The uploaded image file from which to extract the timezone.

    Returns:
        str: The timezone as a string if available, otherwise None.

    Raises:
        Warning: If the timezone could not be extracted from the image metadata.
    """
    try:
        image = Image.open(image_file)
        exif_data = image._getexif()
        if exif_data is not None:
            if ExifTags.Base.OffsetTimeOriginal in exif_data:
                return exif_data.get(ExifTags.Base.OffsetTimeOriginal)
    except Exception as e: # FIXME: what types of exception?
         st.warning(f"Could not extract timezone from image metadata. (file: {image_file.name})")

def decimal_coords(coords:tuple, ref:str) -> Fraction:
    """
    Converts coordinates from degrees, minutes, and seconds to decimal degrees.

    Args:
        coords (tuple): A tuple containing three elements representing degrees, minutes, and seconds.
        ref (str): A string representing the reference direction ('N', 'S', 'E', 'W').

    Returns:
        Fraction: The coordinates in decimal degrees. Negative if the reference is 'S' or 'W'.

    Example:
        decimal_coords((40, 26, 46), 'N') -> 40.44611111111111
        decimal_coords((40, 26, 46), 'W') -> -40.44611111111111
    """
    # https://stackoverflow.com/a/73267185
    if ref not in ['N', 'S', 'E', 'W']:
        raise ValueError("Invalid reference direction. Must be 'N', 'S', 'E', or 'W'.")
    if len(coords) != 3:
        raise ValueError("Coordinates must be a tuple of three elements (degrees, minutes, seconds).")
    
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref =='W':
        decimal_degrees = -decimal_degrees
    return decimal_degrees


#def get_image_latlon(image_file: UploadedFile) : # if it is still not working
#def get_image_latlon(image_file: UploadedFile) -> Tuple[float, float] | None: # Python >=3.10
def get_image_latlon(image_file: UploadedFile) -> Union[Tuple[float, float], None]: # 3.6 <= Python < 3.10
    """
    Extracts the latitude and longitude from the EXIF metadata of an uploaded image file.

    Args:
        image_file (UploadedFile): The uploaded image file from which to extract the latitude and longitude.

    Returns:
        tuple[float, float]: The latitude and longitude as a tuple if available, otherwise None.

    Raises:
        Warning: If the latitude and longitude could not be extracted from the image metadata.
    """
    try:
        image = Image.open(image_file)
        exif_data = image._getexif()
        if exif_data is not None:
            if ExifTags.Base.GPSInfo in exif_data:
                gps_ifd = exif_data.get(ExifTags.Base.GPSInfo) 
                
                lat = float(decimal_coords(gps_ifd[ExifTags.GPS.GPSLatitude], gps_ifd[ExifTags.GPS.GPSLatitudeRef]))
                lon = float(decimal_coords(gps_ifd[ExifTags.GPS.GPSLongitude], gps_ifd[ExifTags.GPS.GPSLongitudeRef]))
            
                return lat, lon
            
    except Exception as e: # FIXME: what types of exception?
         st.warning(f"Could not extract latitude and longitude from image metadata. (file: {str(image_file)}")
    
    return None, None
