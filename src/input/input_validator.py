import random
import string
import hashlib
import re
import streamlit as st

from PIL import Image
from PIL import ExifTags

def generate_random_md5():
    # Generate a random string
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
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
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Function to extract date and time from image metadata
def get_image_datetime(image_file): 
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