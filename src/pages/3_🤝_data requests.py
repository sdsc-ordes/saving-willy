import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Requests",
    page_icon="🤝",
)

from dataset.data_requests import data_prep, show_new_data_view

st.title("Data Requests")
st.write("This page is ensure findability of data across the community.")
st.write("You can filter the metadata by longitude, latitude and date. You can select data from multiple actors, for multiple species and make a grouped request. " \
"The request for the relevant data will be adressed individually to each owner. ")

# Initialize the default data view
df = data_prep()

if 'checkbox_states' not in st.session_state:
    st.session_state.checkbox_states = {}

if 'lat_range' not in st.session_state:
    st.session_state.lat_range = (float(df['lat'].min()), float(df['lat'].max()))

if 'lon_range' not in st.session_state:
    st.session_state.lon_range = (df['lon'].min(), df['lon'].max())

if 'date_range' not in st.session_state:
    st.session_state.date_range = (df['date'].min(), df['date'].max())

# Request button at the bottom
if st.button("REQUEST DATA",
             type="primary",
             icon="🐚"):
    selected = [k for k, v in st.session_state.checkbox_states.items() if v]
    if selected:
        st.success(f"Request submitted for: the species {', '.join(selected)}")
    else:
        st.warning("No selections made.")

# validate that we have sufficient data to filter
# NOTE: this strategy does not implement partial filtering, so if any of the 
#       dimensions is unsuitable, we give up. However, we report all problems
#       first, and then stop the page
give_up_insufficient_data = False

# basic protection: if df is empty, don't/can't proceed
if df.empty or len(df) == 0: 
    st.warning("Fetched dataset is empty, not attempting to present filtering options")
    give_up_insufficient_data = True

# check data is valid for all sliders, else give up
lat_min, lat_max = float(df['lat'].min()), float(df['lat'].max())
lon_min, lon_max = float(df['lon'].min()), float(df['lon'].max())
date_min, date_max = df['date'].min(), df['date'].max()

if np.isnan(lat_min) or np.isnan(lat_max):
    st.warning("Latitude range includes NaN, not attempting to present filtering options")
    give_up_insufficient_data = True

if np.isnan(lon_min) or np.isnan(lon_max):
    st.warning("Longitude range includes NaN, not attempting to present filtering options")
    give_up_insufficient_data = True
    
if date_min is pd.NaT or date_max is pd.NaT:
    st.warning("One or both dates are undefined (NaT), not attempting to present filtering options")
    give_up_insufficient_data = True

if give_up_insufficient_data:
    st.stop()    

# Latitude range filter
lat_range = st.sidebar.slider(
    "Latitude range",
    min_value=lat_min,
    max_value=lat_max,
    value=st.session_state.get("lat_range", (lat_min, lat_max))
)
st.session_state.lat_range = lat_range

# Longitude range filter
lon_range = st.sidebar.slider(
    "Longitude range",
    min_value=lon_min,
    max_value=lon_max,
    value=st.session_state.get("lon_range", (lon_min, lon_max))
)
st.session_state.lon_range = lon_range

# Date range filter
date_range = st.sidebar.date_input(
    "Date range",
    value=st.session_state.get("date_range", (date_min, date_max)),
    min_value=date_min,
    max_value=date_max
)
st.session_state.date_range = date_range

# Show authors per species
show_new_data_view(df)




