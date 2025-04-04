import streamlit as st

st.set_page_config(
    page_title="About",
    page_icon="🌍",
    layout="wide",
)

from utils.st_logs import parse_log_buffer, init_logging_session_states

from maps.obs_map import add_obs_map_header 
from maps.alps_map import present_alps_map
from maps.obs_map import present_obs_map

from datasets import disable_caching
disable_caching()

############################################################
# TO- DO: MAKE ENV FILE 
# the dataset of observations (hf dataset in our space)
dataset_id = "Saving-Willy/temp_dataset"
data_files = "data/train-00000-of-00001.parquet"
USE_BASIC_MAP = False
DEV_SIDEBAR_LIB = True
############################################################

# visual structure: a couple of toggles at the top, then the map inlcuding a
# dropdown for tileset selection.
add_obs_map_header()
tab_map_ui_cols = st.columns(2)
with tab_map_ui_cols[0]:
    show_db_points = st.toggle("Show Points from DB", True)
with tab_map_ui_cols[1]:
    dbg_show_extra = st.toggle("Show Extra points (test)", False)
    
if show_db_points:
    # show a nicer map, observations marked, tileset selectable.
    st_observation = present_obs_map(
        dataset_id=dataset_id, data_files=data_files,
        dbg_show_extra=dbg_show_extra)
    
else:
    # development map.
    st_observation = present_alps_map()
