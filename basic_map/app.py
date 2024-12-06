import pandas as pd
import streamlit as st
import folium

from streamlit_folium import st_folium
from streamlit_folium import folium_static


visp_loc = 46.295833, 7.883333
#m = folium.Map(location=visp_loc, zoom_start=9)


st.markdown("# :whale: :whale: Cetaceans :red[& friends] :balloon:")

m = folium.Map(location=visp_loc, zoom_start=9,
                              tiles='https://tile.opentopomap.org/{z}/{x}/{y}.png',
                              attr='<a href="https://opentopomap.org/">Open Topo Map</a>')

folium_static(m)


