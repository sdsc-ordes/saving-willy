from typing import Protocol, runtime_checkable

from pathlib import Path
from io import BytesIO
from PIL import Image

import pytest
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest

# tests for apptest/demo_multifile_upload
# - the functionality in the test harness is a file_uploader that is configured
#   for multi-file input; and uses a callback to buffer the files into session state.
#   - the handling of individual files includes extracting metadata from the files
#   - a text_area is created for each file, to display the metadata extracted;
#     this deviates from the presentation in the real app, but the extracted info 
#     is the same (here we put it all in text which is far easier to validate using AppTest)
# - the demo also has the author email input


# zero test: no inputs -> empty session state 
#  (or maybe even non-existent session state; for file_uploader we are not
#  allowed to initialise the keyed variable, st borks)

# many test: list of >=2 inputs -> session state with 2 files


# for expectations
from input.input_handling import spoof_metadata, load_debug_autopopulate
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

    
# simple tests on the author email input via AppTest    
# - empty input should propagate to session state
# - invalid email should trigger an error
def test_no_input_no_interaction():
    with patch.dict(spoof_metadata, {"author_email": None}):
        at = AppTest.from_file("src/apptest/demo_multifile_upload.py").run()
        assert at.session_state.observations == {}
        assert at.session_state.input_author_email == None

    at = AppTest.from_file("src/apptest/demo_multifile_upload.py").run()
    assert at.session_state.observations == {}
    dbg = load_debug_autopopulate()
    if dbg: # autopopulated
        assert at.session_state.input_author_email == spoof_metadata.get("author_email")
    else: # should be empty, the user has to fill it in
        assert at.session_state.input_author_email == ""

def test_bad_email():
    with patch.dict(spoof_metadata, {"author_email": "notanemail"}):
        at = AppTest.from_file("src/apptest/demo_multifile_upload.py").run()
        assert at.session_state.input_author_email == "notanemail"
        assert at.error[0].value == "Please enter a valid email address."
    

# test when we load real data files, with all properties as per real app
# - if files loaded correctly and metadata is extracted correctly, we should see the
#   the data in both the session state and in the visual elements.
@patch("streamlit.file_uploader")
def test_mockupload_list_realdata(mock_file_rv: MagicMock, mock_uploadedFile_List_ImageData):
#def test_mockupload_list(mock_file_uploader_rtn: MagicMock, mock_uploadedFile_List):
    num_files = 3
    PRINT_PROPS = False
    # Create a list of n mock files
    mock_files = mock_uploadedFile_List_ImageData(num_files=num_files)
    
    # Set the return value of the mocked file_uploader to the list of mock files
    mock_file_rv.return_value = mock_files

    # Run the Streamlit app
    at = AppTest.from_file("src/apptest/demo_multifile_upload.py").run()

    # put the mocked file_upload into session state, as if it were the result of a file upload, with the key 'file_uploader_data'
    at.session_state["file_uploader_data"] = mock_files

    #print(f"[I] session state: {at.session_state}")
    #print(f"[I] uploaded files: {at.session_state.file_uploader_data}")

    if PRINT_PROPS:
        print(f"[I] uploaded files: ({len(at.session_state.file_uploader_data)}) {at.session_state.file_uploader_data}")
        for _f in at.session_state.file_uploader_data:
            #print(f"\t[I]  props: {dir(_f)}")
            print(f"  [I]  name: {_f.name}")
            print(f"\t[I]  size: {_f.size}")
            print(f"\t[I]  type: {_f.type}")
            # lets make an image from the data
            im = Image.open(_f)
 
            # lets see what metadata we can get to.
            dt = get_image_datetime(_f)
            print(f"\t[I]  datetime: {dt}")
            lat, lon = get_image_latlon(_f)
            print(f"\t[I]  lat, lon: {lat}, {lon}")
            
            
        # we expect to get the following info from the files
        # file1:
        # datetime: 2024:10:24 15:59:45
        # lat, lon: 46.51860277777778, 6.562075
        # file2:
        # datetime: None
        # lat, lon: 46.51860277777778, 6.562075

        # let's run assertions on the backend data (session_state)
        # and then on the front end too (visual elements)
        f1 = at.session_state.file_uploader_data[0]
        f2 = at.session_state.file_uploader_data[1]
        
        assert get_image_datetime(f1) == "2024:10:24 15:59:45"
        assert get_image_datetime(f2) == None
        # use a tolerance of 1e-6, assert that the lat, lon is close to 46.5186 
        assert abs(get_image_latlon(f1)[0] - 46.51860277777778) < 1e-6
        assert abs(get_image_latlon(f1)[1] - 6.562075) < 1e-6
        assert abs(get_image_latlon(f2)[0] - 46.51860277777778) < 1e-6
        assert abs(get_image_latlon(f2)[1] - 6.562075) < 1e-6
        
        # need to run the script top-to-bottom to get the text_area elements
        # since they are dynamically created.
        at.run()
        
        # since we uplaoded num_files files, hopefully we get num_files text areas 
        assert len(at.text_area) == num_files
        # expecting 
        exp0 = "index: 0, name: cakes.jpg, datetime: 2024:10:24 15:59:45, lat: 46.51860277777778, lon:6.562075"
        exp1 = "index: 1, name: cakes_no_exif_datetime.jpg, datetime: None, lat: 46.51860277777778, lon:6.562075"
        exp2 = "index: 2, name: cakes_no_exif_gps.jpg, datetime: 2024:10:24 15:59:45, lat: None, lon:None"

        assert at.text_area[0].value == exp0
        assert at.text_area[1].value == exp1
        if num_files >= 1:
            assert at.text_area(key='metadata_0').value == exp0
        if num_files >= 2:
            assert at.text_area(key='metadata_1').value == exp1
        if num_files >= 3:
            assert at.text_area(key='metadata_2').value == exp2
        
        #    {"fname": "cakes.jpg", "size": 1234, "type": "image/jpeg"},
        #    {"fname": "cakes_no_exif_datetime.jpg", "size": 12345, "type": "image/jpeg"},
        #    {"fname": "cakes_no_exif_gps.jpg", "size": 123456, "type": "image/jpeg"},
        #] 


        # Verify the behavior in your app
        assert len(at.session_state.file_uploader_data) == num_files
       
        assert at.session_state.file_uploader_data[0].size == 1234  # Check properties of the first file
        assert at.session_state.file_uploader_data[1].name == "cakes_no_exif_datetime.jpg"


# this test was a stepping stone; when I was mocking files that didn't have any real data
# - it helped to explore how properties should be set in the mock object and generator funcs.
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

