# a minimal snippet for the whale viewer, for testing purposes
# - using AppTest to validate that the display_whale functionality
#   is ok
# - currently placed in the src directory (not optimal) because 
#   I couldn't get pytest to pick it up from the tests directory. 
#   - TODO: find a cleaner solution for organisation (maybe just config to pytest?)

import streamlit as st
import whale_viewer as sw_wv


# a menu to pick one of the images 
title = st.title("Whale Viewer testing")
species = st.selectbox("Species", sw_wv.WHALE_CLASSES) 

if species is not None:
    # and display the image + reference
    st.write(f"Selected species: {species}")
    sw_wv.display_whale([species], 0, st)
    
