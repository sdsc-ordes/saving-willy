from typing import Protocol, runtime_checkable

from pathlib import Path
from io import BytesIO
from PIL import Image

import pytest
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest

# - tests for apptest/demo_multifile_upload

# zero test: no inputs -> empty session state 
# (or maybe even non-existent session state; for file_uploader we are not allowed to initialise the keyed variable, st borks)

# many test: list of 2 inputs -> session state with 2 files



# for expectations
from input.input_handling import spoof_metadata
from input.input_validator import get_image_datetime, get_image_latlon


@runtime_checkable
class UploadedFile(Protocol):
    name: str
    size: int
    type: str
    #RANDO: str
    _file_urls: list

    def getvalue(self) -> bytes: ...
    def read(self) -> bytes: ... 

        
class MockUploadedFile(BytesIO):
    def __init__(self, 
                 initial_bytes: bytes, 
                 *, 
                 name: str, 
                 size: int, 
                 type: str):
        super().__init__(initial_bytes)
        self.name = name  # Simulate a filename
        self.size = size  # Simulate file size
        self.type = type  # Simulate MIME type
        self.file_id = None 


@pytest.fixture
def mock_uploadedFile():
    def _mock_uploadedFile(name: str, size: int, type: str):
        test_data = b'test data'
        # now load some real data, if fname exists
        base = Path(__file__).parent.parent
        fname = Path(base / f"tests/data/{name}")
        
        if fname.exists():
            with open(fname, 'rb') as f:
                #test_data = BytesIO(f.read()) 
                test_data = f.read()
        else:
            #print(f"[DDDD] {name}, {size}, {type} not found")
            raise FileNotFoundError(f"file {fname} not found ({name}, {size}, {type})")
    
        return MockUploadedFile(
                test_data, name=name, size=size, type=type,)
    
    return _mock_uploadedFile

    
@pytest.fixture
def mock_uploadedFileNoRealData():
    class MockGUIClassFakeData(MagicMock):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            name = kwargs.get('fname', 'image2.jpg')
            size = kwargs.get('size', 123456)
            type = kwargs.get('type', 'image/jpeg')
            self.bytes_io = MockUploadedFile(
                b"test data", name=name, size=size, type=type)
            self.get_data = MagicMock(return_value=self.bytes_io)
            # it seems unclear to me which member attributes get set by the MockUploadedFile constructor
            # - for some reason, size and type get set, but name does not, and results in 
            #   <MockGUIClass name='mock.name' id='<12345>'>.
            #   so let's sjust explicitly set all the relevant attributes here.
            self.name = name
            self.size = size
            self.type = type
            
    return MockGUIClassFakeData

@pytest.fixture
def mock_uploadedFile_List(mock_uploadedFileNoRealData):
    def create_list_of_mocks(num_files=3, **kwargs):
        return [mock_uploadedFileNoRealData(**kwargs) for _ in range(num_files)]
    return create_list_of_mocks

@pytest.fixture
def mock_uploadedFile_List_ImageData(mock_uploadedFile):
    def create_list_of_mocks_realdata(num_files=3, **kwargs):
        print(f"[D] [mock_uploadedFile_List_Img-internal] num_files: {num_files}")
        data = [
            {"name": "cakes.jpg", "size": 1234, "type": "image/jpeg"},
            {"name": "cakes_no_exif_datetime.jpg", "size": 12345, "type": "image/jpeg"},
            {"name": "cakes_no_exif_gps.jpg", "size": 123456, "type": "image/jpeg"},
        ]
        
        _the_files = []
        for i in range(num_files):
            _the_files.append( mock_uploadedFile(**data[i]))
        
        print(f"========== finished init of {num_files} mock_uploaded files | {len(_the_files)} ==========")
        return _the_files
            
        #return [mock_uploadedFile(**kwargs) for _ in range(num_files)]
    return create_list_of_mocks_realdata

    
    
def test_no_input_no_interaction():
    at = AppTest.from_file("src/apptest/demo_multifile_upload.py").run()
    
    assert at.session_state.observations == {}
    assert at.session_state.input_author_email == spoof_metadata.get("author_email")



@patch("streamlit.file_uploader")
def test_mockupload_list(mock_file_uploader_rtn: MagicMock, mock_uploadedFile_List):
    # Create a list of 2 mock files
    mock_files = mock_uploadedFile_List(num_files=2, fname="test.jpg", size=100, type="image/jpeg")
    
    # Set the return value of the mocked file_uploader to the list of mock files
    mock_file_uploader_rtn.return_value = mock_files

    # Run the Streamlit app
    at = AppTest.from_file("src/apptest/demo_multifile_upload.py").run()

    # put the mocked file_upload into session state, as if it were the result of a file upload, with the key 'file_uploader_data'
    at.session_state["file_uploader_data"] = mock_files

    #print(f"[I] session state: {at.session_state}")
    #print(f"[I] uploaded files: {at.session_state.file_uploader_data}")

    if 1:
        print(f"[I] uploaded files: {at.session_state.file_uploader_data}")
        for _f in at.session_state.file_uploader_data:
            print(f"[I]  props: {dir(_f)}")
            print(f"[I]  name: {_f.name}")
            print(f"[I]  size: {_f.size}")
            print(f"[I]  type: {_f.type}")
            print(f"[I] data : {type(_f)} | {type(_f.return_value)} | {_f}")
            # lets make an image from it.
            #im = Image.open(_f)
            

            


        # Verify behavior in the app
        assert len(at.session_state.file_uploader_data) == 2
        
        assert at.session_state.file_uploader_data[0].size == 100  # Check properties of the first file
        assert at.session_state.file_uploader_data[1].name == "test.jpg"  # Check properties of the second file

