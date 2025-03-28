from typing import Tuple
import logging

import pandas as pd
from datasets import load_dataset
import streamlit as st
import folium
from streamlit_folium import st_folium

import whale_viewer as viewer
from utils.fix_tabrender import js_show_zeroheight_iframe

m_logger = logging.getLogger(__name__)
# we can set the log level locally for funcs in this module
#g_m_logger.setLevel(logging.DEBUG)
m_logger.setLevel(logging.INFO)

# TODO: refactor so we have richer data: a tuple or dict combining
# the dropdown label, the tileset name, the attribution - everything
# needed to make the map logic simplified
tile_sets = [
    'Open Street Map',
    #'Stamen Terrain',
    #'Stamen Toner',
    'Esri Ocean',
    'Esri Images',
    'Stamen Watercolor',
    'CartoDB Positron',
    #'CartoDB Dark_Matter'
]

# a list of unique colours for each whale class (for the map)
_colors = [
    "#FFD700", # Gold
    "#FF5733", # Red
    "#33FF57", # Green
    "#3357FF", # Blue
    "#FFFF33", # Yellow
    "#FF33FF", # Magenta
    "#33FFFF", # Cyan
    "#FF8C00", # Dark Orange
    "#8A2BE2", # Blue Violet
    "#DEB887", # Burlywood
    "#5F9EA0", # Cadet Blue
    "#D2691E", # Chocolate
    "#FF4500", # Orange Red
    "#2E8B57", # Sea Green
    "#DA70D6", # Orchid
    "#FF6347", # Tomato
    "#7FFF00", # Chartreuse
    "#DDA0DD", # Plum
    "#A0522D", # Sienna
    "#4682B4", # Steel Blue
    "#7B68EE", # Medium Slate Blue
    "#F0E68C", # Khaki
    "#B22222", # Firebrick
    "#FF1493", # Deep Pink
    "#FFFACD", # Lemon Chiffon
    "#20B2AA", # Light Sea Green
    "#778899" # Light Slate Gray
]

whale2color = {k: v for k, v in zip(viewer.WHALE_CLASSES, _colors)}

def create_map(tile_name:str, location:Tuple[float], zoom_start: int = 7) -> folium.Map:
    """
    Create a folium map with the specified tile layer

    Parameters:
        tile_name (str): The name of the tile layer to use. Options include:
                        'Open Street Map', 'Esri Ocean', 'Esri Images', 
                        'Stamen Toner', 'Stamen Watercolor', 
                        'CartoDB Positron', 'CartoDB Dark_Matter'.
        location (Tuple): Coordinates (lat, lon) of the map center, as floats.
        zoom_start (int, optional): The initial zoom level for the map. Default is 7.

    Returns:
        folium.Map: A folium Map object with the specified settings.
    """
    # https://xyzservices.readthedocs.io/en/stable/gallery.html 
    # get teh attribtuions from here once we pick the 2-3-4 options 
    # make esri ocean the default
    m = folium.Map(location=location, zoom_start=zoom_start,
                   tiles='Esri.OceanBasemap', attr="Esri")
    #m = folium.Map(location=location, zoom_start=zoom_start)

    attr = ""
    if tile_name == 'Open Street Map':
        folium.TileLayer('openstreetmap').add_to(m)
        pass

    #Esri.OceanBasemap
    elif tile_name == 'Esri Ocean':
        pass # made this one default ()
        #attr = "Esri"
        #folium.TileLayer('Esri.OceanBasemap', attr=attr).add_to(m)

    elif tile_name == 'Esri Images':
        attr = "Esri &mdash; Source: Esri, i-cubed, USDA"
        #folium.TileLayer('stamenterrain', attr=attr).add_to(m)
        folium.TileLayer('Esri.WorldImagery', attr=attr).add_to(m)
    elif tile_name == 'Stamen Toner':
        attr = "Stamen"
        folium.TileLayer('stamentoner', attr=attr).add_to(m)
    elif tile_name == 'Stamen Watercolor':
        attr = "Stamen"
        folium.TileLayer('Stadia.StamenWatercolor', attr=attr).add_to(m)
    elif tile_name == 'CartoDB Positron':
        folium.TileLayer('cartodb positron').add_to(m)
    elif tile_name == 'CartoDB Dark_Matter':
        folium.TileLayer('cartodb dark_matter').add_to(m)

    #folium.LayerControl().add_to(m)
    return m



def present_obs_map(dataset_id:str = "Saving-Willy/Happywhale-kaggle",
                    data_files:str = "data/train-00000-of-00001.parquet", 
                    dbg_show_extra:bool = False) -> dict:
    """
    Render map plus tile selector, with markers for whale observations
    

    This function loads whale observation data from a specified dataset and
    file, creates a pandas DataFrame compliant with Folium/Streamlit maps, and
    renders an interactive map with markers for each observation.  The map
    allows users to select a tileset, and displays markers with species-specific
    colors.

    Args:
        dataset_id (str): The ID of the dataset to load from Hugging Face. Default is "Saving-Willy/Happywhale-kaggle".
        data_files (str): The path to the data file to load. Default is "data/train-00000-of-00001.parquet".
        dbg_show_extra (bool): If True, add a few extra sample markers for visualization. Default is False.

    Returns:
        dict: Selected data from the Folium/leaflet.js interactions in the browser.

    """

    # load/download data from huggingface dataset
    metadata = load_dataset(dataset_id, data_files=data_files)
    
    # make a pandas df that is compliant with folium/streamlit maps
    _df = pd.DataFrame({
        'lat': metadata["train"]["latitude"],
        'lon': metadata["train"]["longitude"],
        'species': metadata["train"]["selected_class"], 
        }
        #'species': metadata["train"]["predicted_class"],}
    )
    if dbg_show_extra:
        # add a few samples to visualise colours 
        _df.loc[len(_df)] = {'lat': 0, 'lon': 0, 'species': 'rough_toothed_dolphin'}
        _df.loc[len(_df)] = {'lat': -3, 'lon': 0, 'species': 'pygmy_killer_whale'}
        _df.loc[len(_df)] = {'lat': 45.7, 'lon': -2.6, 'species': 'humpback_whale'}

    ocean_loc = 0, 10
    selected_tile = st.selectbox("Choose a tile set", tile_sets, index=None, placeholder="Choose a tile set...", disabled=False)
    map_ = create_map(selected_tile, ocean_loc, zoom_start=2)

    folium.Marker(
        location=ocean_loc,
        popup="Atlantis",
        tooltip="Atlantis",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(map_)
    
    for _, row in _df.iterrows():
        c = whale2color.get(row['species'], 'red')
        msg = f"[D] color for {row['species']} is {c}"
        m_logger.debug(msg) # depends on m_logger logging level (*not* the main st app's logger)
        #m_logger.info(msg)
        
        kw = {"prefix": "fa", "color": 'gray', "icon_color": c, "icon": "binoculars" } 
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=f"{row['species']} ",
            tooltip=row['species'],
            icon=folium.Icon(**kw)
        ).add_to(map_)
        #st.info(f"Added marker for {row['name']} {row['lat']} {row['lon']}")

    st_data = st_folium(map_, width=725)

    # workaround for correctly showing js components in tabs
    js_show_zeroheight_iframe(
        component_iframe_title="streamlit_folium.st_folium",
        height=800,
    )
    # this is just debug info -- 
    #st.info("[D]" + str(metadata.column_names))
    st.table(_df)

    return st_data

    
def add_obs_map_header() -> None:
    """
    Add brief explainer text to the tab 
    """
    st.write("A map showing the observations in the dataset, with markers colored by species.")
