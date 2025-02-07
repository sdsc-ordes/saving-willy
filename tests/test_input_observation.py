from typing import Protocol, runtime_checkable
import pytest
from unittest.mock import MagicMock, patch

from io import BytesIO
#from PIL import Image
import datetime
import numpy as np
    
#from streamlit.runtime.uploaded_file_manager import UploadedFile # for type hinting
#from typing import List, Union

from input.input_observation import InputObservation

@runtime_checkable
class UploadedFile(Protocol):
    name: str
    size: int
    type: str
    _file_urls: list

    def getvalue(self) -> bytes: ...
    def read(self) -> bytes: ... 


class MockUploadedFile(BytesIO):
    def __init__(self, 
                 initial_bytes: bytes,
                 *, # enforce keyword-only arguments after now
                 name:str,
                 size:int,
                 type:str): 
        #super().__init__(*args, **kwargs)
        super().__init__(initial_bytes)
        self.name = name 
        self.size = size
        self.type = type
        
        self._file_urls = [None,]

@pytest.fixture
def mock_uploadedFile():
    class MockGUIClass(MagicMock):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            name = kwargs.get('name', 'image2.jpg')
            size = kwargs.get('size', 123456)
            type = kwargs.get('type', 'image/jpeg')
            self.bytes_io = MockUploadedFile(
                b"test data", name=name, size=size, type=type)
            self.get_data = MagicMock(return_value=self.bytes_io)
    return MockGUIClass


# let's first generate a test for the mock_uploaded_file  and MockUploadedFile class
# - test with valid input
def test_mock_uploaded_file(mock_uploadedFile):
    # setup values for the test (all valid)
    image_name = "test_image.jpg"
    mock_file = mock_uploadedFile(name=image_name).get_data()
    
    #print(dir(mock_file))
    assert isinstance(mock_file, BytesIO)

    assert mock_file.name == image_name
    assert mock_file.size == 123456
    assert mock_file.type == "image/jpeg"
