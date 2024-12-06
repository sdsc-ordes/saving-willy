# lets try using map stuff without folium, maybe stlite doesnt support that.

import streamlit as st
import pandas as pd

# Load data
f = 'mountains_clr.csv'
df = pd.read_csv(f).dropna()

print(df)

st.markdown("# :whale: :whale: Cetaceans :red[& friends] :balloon:")

st.markdown("## :mountain: Mountains")
st.markdown(f"library version: **{st.__version__}**")
# not sure where my versions are getting pegged from, but we have a 1y spread :(
# https://github.com/streamlit/streamlit/blob/1.24.1/lib/streamlit/elements/map.py
#    rather hard to find the docs for old versions, no selector unlike many libraries.

visp_loc = 46.295833, 7.883333
tile_xyz = 'https://tile.opentopomap.org/{z}/{x}/{y}.png'
tile_attr = '<a href="https://opentopomap.org/">Open Topo Map</a>'
st.map(df, latitude='lat', longitude='lon', color='color', size='size', zoom=7)
#, tiles=tile_xyz, attr=tile_attr)

#st.map(df)

#st.map(df, latitude="col1", longitude="col2", size="col3", color="col4")

import numpy as np

df2 = pd.DataFrame(
    {
        "col1": np.random.randn(1000) / 50 + 37.76,
        "col2": np.random.randn(1000) / 50 + -122.4,
        "col3": np.random.randn(1000) * 100,
        "col4": np.random.rand(1000, 4).tolist(),
    }
)
#st.map(df, latitude="col1", longitude="col2", size="col3", color="col4")


