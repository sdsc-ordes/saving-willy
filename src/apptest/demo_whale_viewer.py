# a minimal snippet for the whale viewer, for testing purposes
# - using AppTest to validate that the display_whale functionality
#   is ok
# - currently placed in the src directory (not optimal) because 
#   I couldn't get pytest to pick it up from the tests directory. 
#   - TODO: find a cleaner solution for organisation (maybe just config to pytest?)

import streamlit as st

# to run streamlit from this subdir, we need the the src dir on the path
# NOTE: pytest doesn't need this to run the tests, but to develop the test
# harness is hard without running streamlit 
import sys
from os import path
# src (parent from here)
src_dir = path.dirname( path.dirname( path.abspath(__file__) ) )
sys.path.append(src_dir)


import whale_viewer as sw_wv

# a menu to pick one of the images 
title = st.title("Whale Viewer testing")
species = st.selectbox("Species", sw_wv.WHALE_CLASSES) 

if species is not None:
    # and display the image + reference
    st.write(f"Selected species: {species}")
    sw_wv.display_whale([species], 0, st)
    
