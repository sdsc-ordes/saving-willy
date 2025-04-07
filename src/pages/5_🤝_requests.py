import streamlit as st

st.set_page_config(
    page_title="Requests",
    page_icon="🤝",
)

from utils.st_logs import parse_log_buffer, init_logging_session_states

from datasets import disable_caching
disable_caching()

############################################################
# the dataset of observations (hf dataset in our space)
dataset_id = "Saving-Willy/temp_dataset"
data_files = "data/train-00000-of-00001.parquet"
############################################################