import streamlit as st
import time
import logging
import pandas as pd
from datasets import load_dataset
from datasets import DatasetDict

############################################################
# the dataset of observations (hf dataset in our space)
dataset_id = "Saving-Willy/main_dataset"
data_files = "data/train-00000-of-00001.parquet"
############################################################

m_logger = logging.getLogger(__name__)
# we can set the log level locally for funcs in this module
#g_m_logger.setLevel(logging.DEBUG)
m_logger.setLevel(logging.INFO)

presentation_data_schema = {
    'lat': 'float',
    'lon': 'float',
    'species': 'str',
    'author_email': 'str',
    'date' : 'timestamp',
}

def try_download_dataset(dataset_id:str, data_files:str) -> dict:
    """
    Attempts to download a dataset from Hugging Face, catching any errors that occur.
    
    Args:
        dataset_id (str): The ID of the dataset to download.
        data_files (str): The data files associated with the dataset.
    Returns:
        dict: A dictionary containing the dataset metadata if the download is successful, 
              or an empty dictionary if an error occurs.

    """

    m_logger.info(f"Starting to download dataset {dataset_id} from Hugging Face")
    t1 = time.time()
    try:
        metadata:DatasetDict = load_dataset(dataset_id, data_files=data_files)
        t2 = time.time(); elap = t2 - t1
    except ValueError as e:
        t2 = time.time(); elap = t2 - t1
        msg = f"Error downloading dataset: {e}.  (after {elap:.2f}s)."
        st.error(msg)
        m_logger.error(msg)
        metadata = {}
    except Exception as e:
        # catch all (other) exceptions and log them, handle them once isolated 
        t2 = time.time(); elap = t2 - t1
        msg = f"!!Unknown Error!! downloading dataset: {e}.  (after {elap:.2f}s)."
        st.error(msg)
        m_logger.error(msg)
        metadata = {}
        

    msg = f"Downloaded dataset: (after {elap:.2f}s). "
    m_logger.info(msg)
    #st.write(msg)
    return metadata

def get_dataset() -> pd.DataFrame:
    """
    Downloads the dataset from Hugging Face and prepares it for use.
    If the dataset is not available, it creates an empty DataFrame with the specified schema.
    Returns:
        pd.DataFrame: A DataFrame containing the dataset, or an empty DataFrame if the dataset is not available.
    """
    # load/download data from huggingface dataset
    metadata = try_download_dataset(dataset_id, data_files)
    
    if not metadata:
        # create an empty, but compliant dataframe
        df = pd.DataFrame(columns=presentation_data_schema).astype(presentation_data_schema)
    else:
        # make a pandas df that is compliant with folium/streamlit maps
        df = pd.DataFrame({
            'lat': metadata["train"]["latitude"],
            'lon': metadata["train"]["longitude"],
            'species': metadata["train"]["selected_class"],
            'author_email': metadata["train"]["author_email"],
            'date': metadata["train"]["date"],}
        )
    return df