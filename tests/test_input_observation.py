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


# now we move on to test the class InputObservation
# - with valid input
# - with invalid input
# - with missing input

def test_input_observation_valid(mock_uploadedFile):
    # image: ndarray
    # lat, lon: float
    # author_email: str
    # date, time: datetime.date, datetime.time
    #uploaded_file: UploadedFile (need to mock this)
    # image_md5: str

    # setup values for the test (all valid)

    author_email = "test@example.com"
    image_name = "test_image.jpg"
    mock_file = mock_uploadedFile(name=image_name).get_data()
    
    _date="2023-10-10"
    _time="10:10:10"
    image_datetime_raw = _date + " " + _time
    dt = datetime.datetime.strptime(image_datetime_raw, "%Y-%m-%d %H:%M:%S")
    date = dt.date()    
    time = dt.time()

    ## make a random image with dtype uint8 using np.random.randint
    image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    image_md5 = 'd1d2515e6f6ac4c5ca6dd739d5143cd4' # 32 hex chars.
    
    obs = InputObservation(
        image=image, 
        latitude=12.34, longitude=56.78, author_email=author_email,
        time=time, date=date,
        uploaded_file=mock_file,
        image_md5=image_md5,
        )
    
    assert isinstance(obs.image, np.ndarray)
    assert (obs.image == image).all()
    
    assert obs.latitude == 12.34
    assert obs.longitude == 56.78
    assert obs.author_email == author_email
    assert isinstance(obs.date, datetime.date)
    assert isinstance(obs.time, datetime.time)
    assert str(obs.date) == "2023-10-10"
    assert str(obs.time) == "10:10:10"

    assert obs.uploaded_file.name == image_name
    assert obs.uploaded_file.size == 123456
    assert obs.uploaded_file.type == "image/jpeg"
    
    assert isinstance(obs.uploaded_file, BytesIO)
    #assert isinstance(obs.uploaded_file, MockUploadedFile) # is there any point in checking the type of the mock, ?


# a list of tuples (strings that are the keys of "valid_inputs", expected error type)
# loop over the list, and for each tuple, create a dictionary with all valid inputs, and one invalid input
# assert that the function raises the expected error type

invalid_input_scenarios = [ 
            ("author_email", TypeError),
            ("image_name", TypeError),
            ("uploaded_file", TypeError),
            ("date", TypeError),
            ("time", TypeError),
            ("image", TypeError),
            ("image_md5", TypeError),
    ]

@pytest.mark.parametrize("key, error_type", invalid_input_scenarios)
def test_input_observation_invalid(key, error_type, mock_uploadedFile):
    # correct datatypes are:
    # - image: ndarray
    # - lat, lon: float
    # - author_email: str
    # - date, time: datetime.date, datetime.time
    # - uploaded_file: UploadedFile (need to mock this)
    # - image_md5: str

    # the most critical/likely to go wrong would presumably be 
    # - date, time (strings not datetime objects)
    # - lat, lon (strings not numbers)
    # - image (not ndarray, maybe accidentally a PIL object or maybe the filename)
    # - uploaded_file (not UploadedFile, maybe a string, or maybe the ndarray)

    # check it fails when any of the datatypes are wrong,
    # even if the rest are all good want to loop over the inputs, take each one
    # from a bad list, and all others from a good list, and assert fails for
    # each one
    
    # set up the good and bad inputs
    _date="2023-10-10"
    _time="10:10:10"
    image_datetime_raw = _date + " " + _time
    fname = "test_image.jpg"
    image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    dt_ok = datetime.datetime.strptime(image_datetime_raw, "%Y-%m-%d %H:%M:%S")
    valid_inputs = {
        "author_email": "test@example.com",
        "image_name": "test_image.jpg",
        "uploaded_file": mock_uploadedFile(name=fname).get_data(),
        "date": dt_ok.date(),
        "time": dt_ok.time(),
        "image": image,
        "image_md5": 'd1d2515e6f6ac4c5ca6dd739d5143cd4', # 32 hex chars.
    }
    invalid_inputs = {
        "author_email": "@example",
        "image_name": 45,
        "uploaded_file": image,
        "date": _date,
        "time": _time,
        "image": fname,
        "image_md5": 45643
    }

    # test a valid set of inputs, minus the target key, substituted for something invalid
    inputs = valid_inputs.copy()
    inputs[key] = invalid_inputs[key]
    
    with pytest.raises(error_type):
        obs = InputObservation(**inputs)
    
    # now test the same key set to None 
    inputs = valid_inputs.copy()
    inputs[key] = None
    with pytest.raises(error_type):
        obs = InputObservation(**inputs)

# we can take a similar approach to test equality. 
# here, construct two dicts, each with valid inputs but all elements different.
# loop over the keys, and construct two InputObservations that differ on that key only.
# asser the expected output message.
# ah, it is the diff func that prints a message. Here we just assert boolean.

# we currently expect differences on time to be ignored. 
inequality_keys = [
    ("author_email", False),
    ("uploaded_file", False),
    ("date", False),
    #("time", True),
    pytest.param("time", False, marks=pytest.mark.xfail(reason="Time is currently ignored in __eq__")),
    ("image", False),
    ("image_md5", False),
]
@pytest.mark.parametrize("key, expect_equality", inequality_keys)
def test_input_observation_equality(key, expect_equality, mock_uploadedFile):

    # set up the two sets of good inputs
    _date1 = "2023-10-10"
    _time1 = "10:10:10"
    image_datetime_raw1 = _date1 + " " + _time1
    fname1 = "test_image.jpg"
    image1 = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    dt1 = datetime.datetime.strptime(image_datetime_raw1, "%Y-%m-%d %H:%M:%S")

    _date2 = "2023-10-11"
    _time2 = "12:13:14"
    image_datetime_raw2 = _date2 + " " + _time2
    fname2 = "test_image.jpg"
    image2 = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    dt2 = datetime.datetime.strptime(image_datetime_raw2, "%Y-%m-%d %H:%M:%S")
    valid_inputs1 = {
        "author_email": "test@example.com",
        #"image_name": "test_image.jpg",
        "uploaded_file": mock_uploadedFile(name=fname1).get_data(),
        "date": dt1.date(),
        "time": dt1.time(),
        "image": image1,
        "image_md5": 'd1d2515e6f6ac4c5ca6dd739d5143cd4', # 32 hex chars.
    }

    valid_inputs2 = {
        "author_email": "example@whales.org",
        #"image_name": "another.jpg",
        "uploaded_file": mock_uploadedFile(name=fname2).get_data(),
        "date": dt2.date(),
        "time": dt2.time(),
        "image": image2,
        "image_md5": 'cdb235587bdee5915d6ccfa52ca9f3ac', # 32 hex chars.
    }

    nearly_same_inputs = valid_inputs1.copy()
    nearly_same_inputs[key] = valid_inputs2[key]
    obs1 = InputObservation(**valid_inputs1)
    obs2 = InputObservation(**nearly_same_inputs)

    if expect_equality is True:
        assert obs1 == obs2
    else:
        assert obs1 != obs2
    

