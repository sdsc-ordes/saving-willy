import pytest
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest
import time

from input.input_handling import spoof_metadata
from input.input_observation import InputObservation
from input.input_handling import buffer_uploaded_files

from streamlit.runtime.uploaded_file_manager import UploadedFile
from numpy import ndarray

from test_demo_multifile_upload import (
    mock_uploadedFile_List_ImageData, mock_uploadedFile,
    MockUploadedFile, )


from test_demo_input_sidebar import (
    verify_initial_session_state, verify_session_state_after_processing_files, 
    wrapped_buffer_uploaded_files_allowed_once)

from test_demo_input_sidebar import _cprint, OKBLUE, OKGREEN, OKCYAN, FAIL, PURPLE

TIMEOUT = 15
SCRIPT_UNDER_TEST = "src/main.py"

def debug_check_images(at:AppTest, msg:str=""):
    _cprint(f"[I] num images in session state {msg}: {len(at.session_state.images)}", OKCYAN)
    for i, (key, img) in enumerate(at.session_state.images.items()):
    #for i, img in enumerate(at.session_state.images.values()):
        #assert isinstance(img, ndarray)
        if isinstance(img, ndarray):
            print(f"image {i}: {img.shape} [{key}]")
        else:
            print(f"image {i}: {type(img)} [{key}]")    

def nooop():
    _cprint("skipping the buffering -- shoul only happen once", FAIL)
    raise RuntimeError
    pass

@patch("streamlit.file_uploader")
def test_click_validate_after_data_entry(mock_file_rv: MagicMock, mock_uploadedFile_List_ImageData):
    # this test goes through several stages of the workflow
    # 
    
    # 1. get app started 
    
    # first we need to upload >0 files
    num_files = 2
    mock_files = mock_uploadedFile_List_ImageData(num_files=num_files)
    mock_file_rv.return_value = mock_files
    
    t0 = time.time()
    at = AppTest.from_file(SCRIPT_UNDER_TEST, default_timeout=TIMEOUT).run()
    t1 = time.time()
    _cprint(f"[T] time to load: {t1-t0:.2f}s", PURPLE)
    verify_initial_session_state(at)

    # 1-Test: at this initial state, we expect:
    # - the workflow state is 'doing_data_entry'
    # - the validate button is disabled
    # - the infer button (on main tab) is disabled
    #   - note: props of the button: label, value, proto, disabled. 
    #     don't need to check others here

    assert at.session_state.workflow_fsm.current_state == 'doing_data_entry'
    assert at.sidebar.button[1].disabled == True
    infer_button = at.tabs[0].button[0]
    assert infer_button.disabled == True 


    # 2. upload files, and trigger the callback

    # put the mocked file_upload into session state, as if it were the result of a file upload, with the key 'file_uploader_data'
    at.session_state["file_uploader_data"] = mock_files
    # the side effect cant run until now (need file_uploader_data to be set)
    if wrapped_buffer_uploaded_files_allowed_once.called == 0:
        mock_file_rv.side_effect = wrapped_buffer_uploaded_files_allowed_once
    else:
        mock_file_rv.side_effect = nooop
        
    _cprint(f"[I] buffering called {wrapped_buffer_uploaded_files_allowed_once.called} times", OKGREEN)

    t2 = time.time()
    at.run()
    t3 = time.time()    
    _cprint(f"[T] time to run with file processing: {t3-t2:.2f}s", PURPLE)
    
    # 2-Test: after uploading the files, we should have:
    # - the workflow state moved on to 'data_entry_complete'
    # - several changes applied to the session_state (handled by verify_session_state_after_processing_files)
    # - the validate button is enabled
    # - the infer button is still disabled
    
    verify_session_state_after_processing_files(at, num_files)
    debug_check_images(at, "after processing files")
    _cprint(f"[I] buffering called {wrapped_buffer_uploaded_files_allowed_once.called} times", OKGREEN)

    assert at.session_state.workflow_fsm.current_state == 'data_entry_complete'

    assert at.sidebar.button[1].disabled == False
    infer_button = at.tabs[0].button[0]
    assert infer_button.disabled == True 

    print(at.markdown[0])

    # 3. data entry complete, click the validate button
    at.sidebar.button[1].click().run()
    t4 = time.time()
    _cprint(f"[T] time to run step 3: {t4-t3:.2f}s", PURPLE)

    # 3-Test: after validating the data, we should have:
    # - the state (backend) should move to data_entry_validated
    # - the UI should show the new state (in sidebar.markdown[0])
    # - the infer button should now be enabled
    # - the validate button should be disabled
    
    assert at.session_state.workflow_fsm.current_state == 'data_entry_validated'
    assert "data_entry_validated" in at.sidebar.markdown[0].value 
    
    # TODO: this part of the test currently fails because hte main code doesn't
    # change the button; in this exec path/branch, the button is not rendered at all.
    # so if we did at.run() after the click, the button is absent entierly! 
    # If we don't run, the button is still present in its old state (enabled)
    # for btn in at.sidebar.button:
    #     print(f"button: {btn.label} {btn.disabled}")
    # #assert at.sidebar.button[1].disabled == True

    infer_button = at.tabs[0].button[0]
    assert infer_button.disabled == False 
    
    debug_check_images(at, "after validation button")
    _cprint(f"[I] buffering called {wrapped_buffer_uploaded_files_allowed_once.called} times", OKGREEN)

    # # at this point, we want to retrieve the main area, get the tabs child, 
    # # and then on the first tab get the first button & check not disabled (will click next step)
    # #print(at._tree)
    # # fragile: assume the first child is 'main'
    # # robust: walk through children until we find the main area
    # # main_area = at._tree.children[0]
    # # main_area = None
    # # for _id, child in at._tree.children.items():
    # #     if child.type == 'main':
    # #         main_area = child
    # #         break
    # # assert main_area is not None

    # # ah, we can go direct to the tabs. they are only plausible in main. (not supported in sidebar)
    # infer_tab = at.tabs[0]
    # #print(f"tab: {infer_tab}")
    # #print(dir(infer_tab))
    # btn = infer_tab.button[0]
    # print(f"button: {btn}")
    # print(btn.label)
    # print(btn.disabled) 

    # infer_button = at.tabs[0].button[0]
    # assert infer_button.disabled == False

    # check pre-ML click that we are ready for it.

    debug_check_images(at, "before clicking infer. ")
    _cprint(f"[I] buffering called {wrapped_buffer_uploaded_files_allowed_once.called} times", OKGREEN)
    TEST_ML = True
    SKIP_CHECK_OVERRIDE = False
    # 4. launch ML inference by clicking the button
    if TEST_ML:
        # infer_button = at.tabs[0].button[0]
        # assert infer_button.disabled == False
        # now test the ML step
        infer_button.click().run()
        t5 = time.time()
        _cprint(f"[T] time to run step 4: {t5-t4:.2f}s", PURPLE)

        # 4-Test: after clicking the infer button, we should have:
        # - workflow should have moved on to 'ml_classification_completed'
        # - the main tab button should now have new text (confirm species predictions)
        # - we should have the results presented on the main area
        #   - 2+6 image elements (the source image, images of 3 predictions) * num_files
        #   - 2 dropdown elements (one for each image) + 1 for the page selector
        #   - all of the observations should have class_overriden == False

        assert at.session_state.workflow_fsm.current_state == 'ml_classification_completed'
        # check the observations
        for i, obs in enumerate(at.session_state.observations.values()):
            print(f"obs {i}: {obs}")
            assert isinstance(obs, InputObservation)
            assert obs.class_overriden == False

        # check the visual elements
        infer_tab = at.tabs[0]
        print(f"tab: {infer_tab}")  
        img_elems = infer_tab.get("imgs")
        print(f"imgs: {len(img_elems)}")
        assert len(img_elems) == num_files*4

        infer_button = infer_tab.button[0]
        assert infer_button.disabled == False
        assert 'Confirm species predictions' in infer_button.label

        # we have 1 per file, and also one more to select the page of results being shown.
        # - hmm, so we aren't going to see the right number if it goes multipage :(
        # - but this test specifically uses 2 inputs. 
        assert len(infer_tab.selectbox) == num_files + 1 
        
        
        # 5. manually override the class of one of the observations
        idx_to_override = 1  # don't forget, we also have the page selector first.
        infer_tab.selectbox[idx_to_override + 1].select_index(20).run()  # FRAGILE!
            
        # 5-TEST. 
        # - expect that all class_overriden are False, except for the one we just set
        # - also expect there still to be num_files*4 images (2+6 per file) etc
        for i, obs in enumerate(at.session_state.observations.values()):
            _cprint(f"obs {i}: {obs.class_overriden} {obs.to_dict()}", OKBLUE)
            assert isinstance(obs, InputObservation)
            if not SKIP_CHECK_OVERRIDE:
                if i == idx_to_override:
                    assert obs.class_overriden == True
                else:
                    assert obs.class_overriden == False
                
        # 6. confirm the species predictions, get ready to allow upload
        infer_tab = at.tabs[0]
        confirm_button = infer_tab.button[0]
        confirm_button.click().run()
        t6 = time.time()
        _cprint(f"[T] time to run step 5: {t6-t5:.2f}s", PURPLE)
        
        # 6-TEST. Now we expect to see: 
        # - the workflow state should be 'manual_inspection_completed'
        # - the obsevations should be as per the previous step
        # - the main tab button should now have new text (Upload all observations)
        # - we should have 4n images
        # - we should have only 1 select box (page), (passed stage for overriding class)
        
        assert at.session_state.workflow_fsm.current_state == 'manual_inspection_completed'
        for i, obs in enumerate(at.session_state.observations.values()):
            _cprint(f"obs {i}: {obs.class_overriden} {obs.to_dict()}", OKBLUE)
            assert isinstance(obs, InputObservation)
            if not SKIP_CHECK_OVERRIDE:
                if i == idx_to_override:
                    assert obs.class_overriden == True
                else:
                    assert obs.class_overriden == False
        
        # we have to trigger a manual refresh? no, it seems that sometimes the tests fail, maybe 
        #   because the script is slow? it is not unique to here, various points that usually pass
        #   occasionally fail because elements haven't yet been drawn. I suppose the timing aspect 
        #   internally by AppTest is not perfect (selenium has moved from explicit to implicit waits,
        #   though I didn't look too deeply whether apptest also has an explicit wait mechanism)
        # # time.sleep(1)
        # #at.run()
        infer_tab = at.tabs[0]
        upload_button = infer_tab.button[0]
        assert upload_button.disabled == False
        assert 'Upload all observations' in upload_button.label
        
        img_elems = infer_tab.get("imgs")
        assert len(img_elems) == num_files*4
        
        assert len(infer_tab.selectbox) == 1 
        
        # 7. upload the observations
        upload_button.click().run()
        t7 = time.time()
        _cprint(f"[T] time to run step 6: {t7-t6:.2f}s", PURPLE)

        # 7-TEST. Now we expect to see:
        # - workflow state should be 'data_uploaded'
        # - nothing else in the back end should have changed (is that a mistake? should we 
        #   add a boolean tracking if the observations have been uploaded?)
        # - a toast presented for each observation uploaded
        # - the images should still be there, and 1 select box (page)
        # - no more button on the main area
        
        assert at.session_state.workflow_fsm.current_state == 'data_uploaded'
        #print(at.toast)
        assert len(at.toast) == num_files
        infer_tab = at.tabs[0]
        
        img_elems = infer_tab.get("imgs")
        assert len(img_elems) == num_files*4
        assert len(infer_tab.selectbox) == 1 
        assert len(infer_tab.button) == 0   
        
        
        
        
        
        
            
        


