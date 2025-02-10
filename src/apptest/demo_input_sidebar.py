# a chunk of the full app, covering the elements presented on the sidebar
# - this includes both input and workflow items.
import streamlit as st

# to run streamlit from this subdir, we need the the src dir on the path
# NOTE: pytest doesn't need this to run the tests, but to develop the test
# harness is hard without running streamlit 
import sys
from os import path
# src (parent from here)
src_dir = path.dirname( path.dirname( path.abspath(__file__) ) )
sys.path.append(src_dir)

from input.input_handling import (
    init_input_data_session_states,
    init_input_container_states,
    add_input_UI_elements,
    setup_input,
)
from utils.workflow_ui import refresh_progress_display, init_workflow_viz, init_workflow_session_states

from apptest.demo_elements import show_uploaded_file_info



if __name__ == "__main__":
    
    init_input_data_session_states()
    init_input_container_states()
    init_workflow_session_states()

    init_workflow_viz()


    with st.sidebar:
        refresh_progress_display()
        # layout handling
        add_input_UI_elements()
        # input elements (file upload, text input, etc)
        setup_input()

    # as a debug, let's add some text_area elements to show the files  (no clash
    #   with testing the prod app since we dont use text_area at all)
    show_uploaded_file_info ()