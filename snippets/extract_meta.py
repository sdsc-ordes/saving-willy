#!/usr/bin/env python3
from PIL import Image
import exifread

def extract_datetime(image_path):
    # Open the image file
    with open(image_path, 'rb') as image_file:
        # Read EXIF data
        tags = exifread.process_file(image_file)
        
        # Get the DateTimeOriginal tag
        datetime_original = tags.get('EXIF DateTimeOriginal')
        
        if datetime_original:
            return str(datetime_original)
        else:
            return None

def extract_gps(image_path):
    # Open the image file
    with open(image_path, 'rb') as image_file:
        # Read EXIF data
        tags = exifread.process_file(image_file)
        # print(tags)
        
         # Extract GPS information
        latitude = tags.get('GPS GPSLatitude')
        latitude_ref = tags.get('GPS GPSLatitudeRef')
        longitude = tags.get('GPS GPSLongitude')
        longitude_ref = tags.get('GPS GPSLongitude')

        # Convert latitude and longitude to decimal format
        if latitude and latitude_ref and longitude and longitude_ref:
            lat = "{}{}".format(latitude, latitude_ref)
            lon = "{}{}".format(longitude, longitude_ref)
        else:
            lat = lon = None

        return (lat, lon)
# Example usage
image_path = 'imgs/cakes.jpg' # this file has good exif data, inc GPS, timestamps etc.
datetime_info = extract_datetime(image_path)
gps_info = extract_gps(image_path)
print(f'Date and Time: {datetime_info}')
print(f'GPS          : {gps_info}')


