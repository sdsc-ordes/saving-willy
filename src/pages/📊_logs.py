import streamlit as st
import os

st.set_page_config(
    page_title="Logs",
    page_icon="📊",
)

from utils.st_logs import parse_log_buffer

handler = st.session_state['handler']
if handler is not None:
    records = parse_log_buffer(handler.buffer)
    st.dataframe(records[::-1], use_container_width=True,)
    st.info(f"Length of records: {len(records)}")
else:
    st.error("⚠️ No log handler found!")