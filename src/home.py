import streamlit as st
import os

import logging

st.set_page_config(
    page_title="Home",
    page_icon="🐳",
)

# get a global var for logger accessor in this module
LOG_LEVEL = logging.DEBUG
g_logger = logging.getLogger(__name__)
g_logger.setLevel(LOG_LEVEL)

# one toggle for all the extra debug text
if "MODE_DEV_STATEFUL" not in st.session_state:
    st.session_state.MODE_DEV_STATEFUL = False
    
from utils.st_logs import init_logging_session_states
init_logging_session_states() # logging init should be early 


st.write("# Welcome to Cetacean Research Data Infrastructure! 🐬˚˖𓍢ִ໋ 🐋✧˚.⋆")

st.sidebar.success("Here are the pages.")

st.markdown(
    """
    About: blablabla
"""
)



g_logger.info("App started.")
g_logger.warning(f"[D] Streamlit version: {st.__version__}. Python version: {os.sys.version}")

#g_logger.debug("debug message")
#g_logger.info("info message")
#g_logger.warning("warning message")
