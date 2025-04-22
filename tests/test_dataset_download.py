import pytest
from unittest.mock import patch, MagicMock
from dataset.download import try_download_dataset

# tests for try_download_dataset
# - the main aim here is to mock the function load_dataset which makes external HTTP requests, 
#   and follow the successful and failing pathways. 
# - tests templates generated with copilot, they test the text/messages too; the core
#   is the return value, which should have similar form but change according to if an exception was raised or not
# since this function uses st and m_logger to keep track of the download status, we need to mock them too

#@patch('maps.obs_map.load_dataset')
#@patch('maps.obs_map.m_logger')
@patch('dataset.download.load_dataset')
@patch('dataset.download.m_logger')
def test_try_download_dataset_success(mock_logger, mock_load_dataset):
    # Mock the return value of load_dataset
    mock_load_dataset.return_value = {'train': {'latitude': [1], 'longitude': [2], 'predicted_class': ['whale']}}

    dataset_id = "test_dataset"
    data_files = "test_file"
    result = try_download_dataset(dataset_id, data_files)

    # Assertions
    mock_logger.info.assert_any_call(f"Starting to download dataset {dataset_id} from Hugging Face")
    mock_load_dataset.assert_called_once_with(dataset_id, data_files=data_files)
    assert result == {'train': {'latitude': [1], 'longitude': [2], 'predicted_class': ['whale']}}
    mock_logger.info.assert_called_with("Downloaded dataset: (after 0.00s). ")


@patch('dataset.download.load_dataset', side_effect=ValueError("Download failed"))
@patch('dataset.download.m_logger')
def test_try_download_dataset_failure_known(mock_logger, mock_load_dataset):
    # testing the case where we've found (can reproduce by removing network connection)
    dataset_id = "test_dataset"
    data_files = "test_file"
    result = try_download_dataset(dataset_id, data_files)

    # Assertions
    mock_logger.info.assert_any_call(f"Starting to download dataset {dataset_id} from Hugging Face")
    mock_load_dataset.assert_called_once_with(dataset_id, data_files=data_files)
    mock_logger.error.assert_called_with("Error downloading dataset: Download failed.  (after 0.00s).")
    assert result == {}
    mock_logger.info.assert_called_with("Downloaded dataset: (after 0.00s). ")

@patch('dataset.download.load_dataset', side_effect=Exception("Download engine corrupt"))
@patch('dataset.download.m_logger')
def test_try_download_dataset_failure_unknown(mock_logger, mock_load_dataset):
    # the cases we haven't found, but should still be handled (maybe network error, etc)
    dataset_id = "test_dataset"
    data_files = "test_file"
    result = try_download_dataset(dataset_id, data_files)

    # Assertions
    mock_logger.info.assert_any_call(f"Starting to download dataset {dataset_id} from Hugging Face")
    mock_load_dataset.assert_called_once_with(dataset_id, data_files=data_files)
    mock_logger.error.assert_called_with("!!Unknown Error!! downloading dataset: Download engine corrupt.  (after 0.00s).")
    assert result == {}
    mock_logger.info.assert_called_with("Downloaded dataset: (after 0.00s). ")
