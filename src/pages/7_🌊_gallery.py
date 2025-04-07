import streamlit as st

st.set_page_config(
    page_title="ML Models",
    page_icon="🌊",
    layout="wide",
)
from utils.st_logs import parse_log_buffer, init_logging_session_states

import whale_gallery as gallery
import whale_viewer as viewer

# here we make a container to allow filtering css properties 
# specific to the gallery (otherwise we get side effects)
tg_cont = st.container(key="swgallery")
with tg_cont:
    gallery.render_whale_gallery(n_cols=4)