from typing import List
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from PIL import Image
import pandas as pd
import os

WHALE_CLASSES = [
        "beluga",
        "blue_whale",
        "bottlenose_dolphin",
        "brydes_whale",
        "commersons_dolphin",
        "common_dolphin",
        "cuviers_beaked_whale",
        "dusky_dolphin",
        "false_killer_whale",
        "fin_whale",
        "frasiers_dolphin",
        "gray_whale",
        "humpback_whale",
        "killer_whale",
        "long_finned_pilot_whale",
        "melon_headed_whale",
        "minke_whale",
        "pantropic_spotted_dolphin",
        "pygmy_killer_whale",        
        "rough_toothed_dolphin",
        "sei_whale",
        "short_finned_pilot_whale",
        "southern_right_whale",
        "spinner_dolphin",
        "spotted_dolphin",
        "white_sided_dolphin",
    ]

WHALE_IMAGES = [
        "beluga.webp",
        "blue-whale.webp",
        "bottlenose_dolphin.webp",
        "brydes.webp",
        "common_dolphin.webp",
        "common_dolphin.webp",
        "cuviers_beaked_whale.webp",
        "common_dolphin.webp",
        "false-killer-whale.webp",
        "fin-whale.webp",
        "fin-whale.webp",
        "gray-whale.webp",
        "Humpback.webp",
        "killer_whale.webp",
        "640x427-long-finned-pilot-whale.webp",
        "melon.webp",
        "minke-whale.webp",
        "pantropical-spotted-dolphin.webp",
        "pygmy-killer-whale.webp",
        "rough-toothed-dolphin.webp",
        "sei.webp",
        "Whale_Short-Finned_Pilot-markedDW.png",  ## Background
        "640x427-southern-right-whale.jpg",  ## background
        "spinner.webp",
        "pantropical-spotted-dolphin.webp",  ## duplicate also used for
        "640x427-atlantic-white-sided-dolphin.jpg",  ##background
    ]

WHALE_REFERENCES = [
        "https://www.fisheries.noaa.gov/species/beluga-whale",
        "https://www.fisheries.noaa.gov/species/blue-whale",
        "https://www.fisheries.noaa.gov/species/common-bottlenose-dolphin",
        "https://www.fisheries.noaa.gov/species/brydes-whale",
        "https://en.wikipedia.org/wiki/Commerson's_dolphin",
        #"commersons_dolphin - reference missing - classification to be verified",  ## class matching to be verified
        "https://www.fisheries.noaa.gov/species/short-beaked-common-dolphin",
        "https://www.fisheries.noaa.gov/species/cuviers-beaked-whale",
        "https://en.wikipedia.org/wiki/Dusky_dolphin",
        #"dusky_dolphin - reference missing - classification to be verified",  ## class matching to be verified
        "https://www.fisheries.noaa.gov/species/false-killer-whale",
        "https://www.fisheries.noaa.gov/species/fin-whale",
        "https://www.fisheries.noaa.gov/species/frasers-dolphin",
        #"frasiers_dolphin - reference missing - classification to be verified",  ## class matching to be verified
        "https://www.fisheries.noaa.gov/species/gray-whale",
        "https://www.fisheries.noaa.gov/species/humpback-whale",
        "https://www.fisheries.noaa.gov/species/killer-whale",
        "https://www.fisheries.noaa.gov/species/long-finned-pilot-whale",
        "https://www.fisheries.noaa.gov/species/melon-headed-whale",
        "https://www.fisheries.noaa.gov/species/minke-whale",
        "https://www.fisheries.noaa.gov/species/pantropical-spotted-dolphin",
        "https://www.fisheries.noaa.gov/species/pygmy-killer-whale",
        "https://www.fisheries.noaa.gov/species/rough-toothed-dolphin",
        "https://www.fisheries.noaa.gov/species/sei-whale",
        "https://www.fisheries.noaa.gov/species/short-finned-pilot-whale",
        "https://www.fisheries.noaa.gov/species/southern-right-whale",
        "https://www.fisheries.noaa.gov/species/spinner-dolphin",
        "https://www.fisheries.noaa.gov/species/pantropical-spotted-dolphin",
        "https://www.fisheries.noaa.gov/species/atlantic-white-sided-dolphin",
    ]

# Create a dataframe
df_whale_img_ref = pd.DataFrame(
    {
        "WHALE_CLASSES": WHALE_CLASSES,
        "WHALE_IMAGES": WHALE_IMAGES,
        "WHALE_REFERENCES": WHALE_REFERENCES,
    }
).set_index("WHALE_CLASSES")

def format_whale_name(whale_class:str) -> str:
    """
    Formats a whale class name for display 
    
    Args:
        whale_class (str): The class name of the whale, with words separated by underscores.

    Returns:
        str: The formatted whale name with spaces instead of underscores and each word capitalized.
    """
    if not isinstance(whale_class, str):
        raise TypeError("whale_class should be a string.")
    
    whale_name = whale_class.replace("_", " ").title()
    return whale_name


def display_whale(whale_classes:List[str], i:int, viewcontainer:DeltaGenerator=None) -> None:
    """
    Display whale image and reference to the provided viewcontainer.

    Args:
        whale_classes (List[str]): A list of whale class names.
        i (int): The index of the whale class to display.
        viewcontainer (streamlit.delta_generator.DeltaGenerator): The container
            to display the whale information. If not provided, use the current
            streamlit context (works via 'with `container`' syntax)

    Returns:
        None
    
    """
    
    if viewcontainer is None:
        viewcontainer = st

    # validate the input i should be within the range of the whale_classes
    if i >= len(whale_classes):
        raise ValueError(f"Index {i} is out of range. The whale_classes list has only {len(whale_classes)} elements.")
    
    # validate the existence of the whale class in the dataframe as a row key
    if whale_classes[i] not in df_whale_img_ref.index:
        raise ValueError(f"Whale class {whale_classes[i]} not found in the dataframe.")
    
    
    viewcontainer.markdown(
        ":whale:  #" + str(i + 1) + ": " + format_whale_name(whale_classes[i])
    )
    current_dir = os.getcwd()
    image_path = os.path.join(current_dir, "src/images/references/")
    image = Image.open(image_path + df_whale_img_ref.loc[whale_classes[i], "WHALE_IMAGES"])

    viewcontainer.image(image, caption=df_whale_img_ref.loc[whale_classes[i], "WHALE_REFERENCES"], use_column_width=True)