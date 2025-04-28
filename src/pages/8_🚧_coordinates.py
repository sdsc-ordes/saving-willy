import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Coordinates",
    page_icon="🚧",
    layout="wide",
)

# the goal of this tab is to allow selection of the new obsvation's location by map click/adjust.
st.markdown("Coming later! :construction:")
st.markdown(
    """*The goal is to allow interactive definition for the coordinates of a new
    observation, by click/drag points on the map.*""")


st.write("Click on the map to capture a location.")
#m = folium.Map(location=visp_loc, zoom_start=7)
mm = folium.Map(location=[39.949610, -75.150282], zoom_start=16)
folium.Marker( [39.949610, -75.150282], popup="Liberty Bell", tooltip="Liberty Bell"
).add_to(mm)

st_data2 = st_folium(mm, width=725)
st.write("below the map...")
if st_data2['last_clicked'] is not None:
    print(st_data2)
    st.info(st_data2['last_clicked'])