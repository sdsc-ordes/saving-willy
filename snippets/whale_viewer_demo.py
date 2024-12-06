import numpy as np
import pandas as pd


WHALE_CLASSES = np.array(
    [
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
)

WHALE_IMAGES = np.array(
    [
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
        "pantropic-spotted-dolphin.webp",
        "pygmy-killer-whale.webp",
        "rough-toothed-dolphin.webp",
        "sei.webp",
        "Whale_Short-Finned_Pilot-markedDW.png",  ## Background
        "640x427-southern-right-whale.jpg",  ## background
        "spinner.webp",
        "pantropical-spotted-dolphin.webp",  ## duplicate also used for
        "640x427-atlantic-white-sided-dolphin.jpg",  ##background
    ]
)

WHALE_REFERENCES = np.array(
    [
        "https://www.fisheries.noaa.gov/species/beluga-whale",
        "https://www.fisheries.noaa.gov/species/blue-whale",
        "https://www.fisheries.noaa.gov/species/common-bottlenose-dolphin",
        "https://www.fisheries.noaa.gov/species/brydes-whale",
        "commersons_dolphin - reference missing - classification to be verified",  ## class matching to be verified
        "https://www.fisheries.noaa.gov/species/short-beaked-common-dolphin",
        "https://www.fisheries.noaa.gov/species/cuviers-beaked-whale",
        "dusky_dolphin - reference missing - classification to be verified",  ## class matching to be verified
        "https://www.fisheries.noaa.gov/species/false-killer-whale",
        "https://www.fisheries.noaa.gov/species/fin-whale",
        "frasiers_dolphin - reference missing - classification to be verified",  ## class matching to be verified
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
)


# Create a dataframe
df_whale_img_ref = pd.DataFrame(
    {
        "WHALE_CLASSES": WHALE_CLASSES,
        "WHALE_IMAGES": WHALE_IMAGES,
        "WHALE_REFERENCES": WHALE_REFERENCES,
    }
).set_index("WHALE_CLASSES")


import streamlit as st
from PIL import Image


## Replace this with model's output
whale_classes = ["blue_whale", "gray_whale", "spotted_dolphin"]


def format_whale_name(whale_class):
    whale_name = whale_class.replace("_", " ").title()
    return whale_name


def display_whale(whale_class, i):
    st.markdown(
        "## :whale:  #" + str(i + 1) + ": " + format_whale_name(whale_classes[i])
    )
    image = Image.open("images/references/" + df_whale_img_ref.loc[whale_classes[i], "WHALE_IMAGES"])

    st.image(image, caption=df_whale_img_ref.loc[whale_classes[i], "WHALE_REFERENCES"])
    # link st.markdown(f"[{df.loc[whale_classes[i], 'WHALE_REFERENCES']}]({df.loc[whale_classes[i], 'WHALE_REFERENCES']})")


st.markdown("# Species detected (Cetacean Classifier):")

for i in range(len(whale_classes)):
    display_whale(whale_classes[i], i)
