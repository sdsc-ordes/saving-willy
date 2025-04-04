import streamlit as st

st.set_page_config(
    page_title="Benchmarking",
    page_icon="🏆",
)

from utils.st_logs import parse_log_buffer, init_logging_session_states