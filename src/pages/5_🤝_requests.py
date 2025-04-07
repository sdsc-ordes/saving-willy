import streamlit as st

st.set_page_config(
    page_title="Requests",
    page_icon="🤝",
)

from utils.st_logs import parse_log_buffer, init_logging_session_states
from dataset.requests import default_data_view, show_new_data_view
from datasets import disable_caching
disable_caching()

st.title("Requests")

# Initialize the default data view
df = default_data_view()
print(df)

if 'checkbox_states' not in st.session_state:
    st.session_state.checkbox_states = {}

if 'lat_range' not in st.session_state:
    st.session_state.lat_range = (float(df['lat'].min()), float(df['lat'].max()))

if 'lon_range' not in st.session_state:
    st.session_state.lon_range = (df['lon'].min(), df['lon'].max())

if 'date_range' not in st.session_state:
    st.session_state.date_range = (df['date'].min(), df['date'].max())

# Request button at the bottom
if st.button("Request (Bottom)"):
    selected = [k for k, v in st.session_state.checkbox_states.items() if v]
    if selected:
        st.success(f"Request submitted for: {', '.join(selected)}")
    else:
        st.warning("No selections made.")

# Latitude range filter
lat_min, lat_max = float(df['lat'].min()), float(df['lat'].max())
lat_range = st.sidebar.slider("Latitude range", 
                              min_value=lat_min, 
                              max_value=lat_max, 
                              value=(lat_min, lat_max),
                              key='lat_range')

# Longitude range filter
lon_min, lon_max = float(df['lon'].min()), float(df['lon'].max())
lon_range = st.sidebar.slider("Longitude range", 
                              min_value=lon_min, 
                              max_value=lon_max, 
                              value=(lon_min, lon_max),
                              key='lon_range')

# Date range filter
date_min, date_max = df['date'].min(), df['date'].max()
date_range = st.sidebar.date_input("Date range", 
                                   value=(date_min, date_max), 
                                   min_value=date_min, 
                                   max_value=date_max,
                                   key='date_range')

# Show authors per specie
show_new_data_view(df)




