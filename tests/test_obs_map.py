import pytest
from unittest.mock import patch, MagicMock
from maps.obs_map import try_download_dataset

# tests for try_download_dataset
# - the main aim here is to mock the function load_dataset which makes external HTTP requests, 
#   and follow the successful and failing pathways. 
# - tests templates generated with copilot, they test the text/messages too; the core
#   is the return value, which should have similar form but change according to if an exception was raised or not
# since this function uses st and m_logger to keep track of the download status, we need to mock them too

@patch('maps.obs_map.load_dataset')
@patch('maps.obs_map.st')
@patch('maps.obs_map.m_logger')
def test_try_download_dataset_success(mock_logger, mock_st, mock_load_dataset):
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
    mock_st.write.assert_called_with("Downloaded dataset: (after 0.00s). ")


@patch('maps.obs_map.load_dataset', side_effect=ValueError("Download failed"))
@patch('maps.obs_map.st')
@patch('maps.obs_map.m_logger')
def test_try_download_dataset_failure(mock_logger, mock_st, mock_load_dataset):
    dataset_id = "test_dataset"
    data_files = "test_file"
    result = try_download_dataset(dataset_id, data_files)

    # Assertions
    mock_logger.info.assert_any_call(f"Starting to download dataset {dataset_id} from Hugging Face")
    mock_load_dataset.assert_called_once_with(dataset_id, data_files=data_files)
    mock_logger.error.assert_called_with("Error downloading dataset: Download failed.  (after 0.00s).")
    mock_st.error.assert_called_with("Error downloading dataset: Download failed.  (after 0.00s).")
    assert result == {}
    mock_logger.info.assert_called_with("Downloaded dataset: (after 0.00s). ")
    mock_st.write.assert_called_with("Downloaded dataset: (after 0.00s). ")
