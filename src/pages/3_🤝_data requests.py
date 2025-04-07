import streamlit as st

st.set_page_config(
    page_title="Requests",
    page_icon="🤝",
)

from dataset.requests import data_prep, show_new_data_view

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
        st.success(f"Request submitted for: the specie {', '.join(selected)}")
    else:
        st.warning("No selections made.")

# Latitude range filter
lat_min, lat_max = float(df['lat'].min()), float(df['lat'].max())
lat_range = st.sidebar.slider(
    "Latitude range",
    min_value=float(df['lat'].min()),
    max_value=float(df['lat'].max()),
    value=st.session_state.get("lat_range", (df['lat'].min(), df['lat'].max()))
)
st.session_state.lat_range = lat_range

# Longitude range filter
lon_min, lon_max = float(df['lon'].min()), float(df['lon'].max())
lon_range = st.sidebar.slider(
    "Longitude range",
    min_value=float(df['lon'].min()),
    max_value=float(df['lon'].max()),
    value=st.session_state.get("lon_range", (df['lon'].min(), df['lon'].max()))
)
st.session_state.lon_range = lon_range
# Date range filter
date_range = st.sidebar.date_input(
    "Date range",
    value=st.session_state.get("date_range", (df['date'].min(), df['date'].max())),
    min_value=df['date'].min(),
    max_value=df['date'].max()
)
st.session_state.date_range = date_range

# Show authors per specie
show_new_data_view(df)




