import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

_map_data = {
    'name': {
        0: 'matterhorn',
        1: 'zinalrothorn',
        2: 'alphubel',
        3: 'allalinhorn',
        4: 'weissmies',
        5: 'lagginhorn',
        6: 'lenzspitze',
        10: 'strahlhorn',
        11: 'parrotspitze'},
    'lat': {
        0: 45.9764263,
        1: 46.0648271,
        2: 46.0628767,
        3: 46.0460858,
        4: 46.127633,
        5: 46.1570635,
        6: 46.1045505,
        10: 46.0131498,
        11: 45.9197881},
    'lon': {
        0: 7.6586024,
        1: 7.6901238,
        2: 7.8638549,
        3: 7.8945842,
        4: 8.0120569,
        5: 8.0031044,
        6: 7.8686568,
        10: 7.9021703,
        11: 7.8710552},
    'height': {
        0: 4181.0,
        1: 3944.0,
        2: 4174.0,
        3: 3940.0,
        4: 3983.0,
        5: 3916.0,
        6: 4255.0,
        10: 4072.0,
        11: 4419.0},
    'color': {
        0: '#aa0000',
        1: '#aa0000',
        2: '#aa0000',
        3: '#aa0000',
        4: '#aa0000',
        5: '#aa0000',
        6: '#aa0000',
        10: '#00aa00',
        11: '#aa0000'},
    'size': {0: 30, 1: 30, 2: 30, 3: 30, 4: 30, 5: 30, 6: 30, 10: 500, 11: 30}
}

tile_sets = [
    'Open Street Map',
    #'Stamen Terrain',
    #'Stamen Toner',
    'Esri Ocean',
    'Esri Images',
    'Stamen Watercolor',
    'CartoDB Positron',
    #'CartoDB Dark_Matter'
]

def create_map(tile_name, location, zoom_start: int = 7):
    # https://xyzservices.readthedocs.io/en/stable/gallery.html 
    # get teh attribtuions from here once we pick the 2-3-4 options 
    # make esri ocean the default
    m = folium.Map(location=location, zoom_start=zoom_start,
                   tiles='Esri.OceanBasemap', attr="Esri")
    #m = folium.Map(location=location, zoom_start=zoom_start)

    attr = ""
    if tile_name == 'Open Street Map':
        folium.TileLayer('openstreetmap').add_to(m)
        pass

    #Esri.OceanBasemap
    elif tile_name == 'Esri Ocean':
        pass # made this one default ()
        #attr = "Esri"
        #folium.TileLayer('Esri.OceanBasemap', attr=attr).add_to(m)

    elif tile_name == 'Esri Images':
        attr = "Esri &mdash; Source: Esri, i-cubed, USDA"
        #folium.TileLayer('stamenterrain', attr=attr).add_to(m)
        folium.TileLayer('Esri.WorldImagery', attr=attr).add_to(m)
    elif tile_name == 'Stamen Toner':
        attr = "Stamen"
        folium.TileLayer('stamentoner', attr=attr).add_to(m)
    elif tile_name == 'Stamen Watercolor':
        attr = "Stamen"
        folium.TileLayer('Stadia.StamenWatercolor', attr=attr).add_to(m)
    elif tile_name == 'CartoDB Positron':
        folium.TileLayer('cartodb positron').add_to(m)
    elif tile_name == 'CartoDB Dark_Matter':
        folium.TileLayer('cartodb dark_matter').add_to(m)

    #folium.LayerControl().add_to(m)
    return m


def present_alps_map():
  '''show a map of the alps with peaks (from the event's teamnames) marked

  there are two rendering modes: 
  a) basic - this uses a streamlit map, which doesn't offer much flexibility on
  the tiles, but if you supply a dataframe then you just tell it the columns to
  use for lat, lon, color, size of points

  b) advanced - this uses folium, which allows for more control over the tiles,
  but sadly it seems much less flexible for the point markers. 
  
  '''

  st.markdown("# :whale: :whale: Cetaceans :red[& friends] :balloon:")
  show_points = st.toggle("Show Points", False)
  basic_map = st.toggle("Use Basic Map", False)
  
  visp_loc = 46.295833, 7.883333 # position of town nearby to the peaks
  # (maybe zermatt or Taesch better? all the mountains seem on valais gauche)
  _df = pd.DataFrame(_map_data)
  if basic_map:
      # render using streamlit map element
      st.map(_df, latitude='lat', longitude='lon', color='color', size='size', zoom=7)
  else:
      # setup a dropdown to pick tiles, and render with folium
      selected_tile = st.selectbox("Choose a tile set", tile_sets)
      #st.info(f"Selected tile: {selected_tile}") 
      # don't get why the default selection doesn't get renderd.
      # generate a layer
      map_ = create_map(selected_tile, visp_loc)
      # and render it
      #tile_xyz = 'https://tile.opentopomap.org/{z}/{x}/{y}.png'
      #tile_attr = '<a href="https://opentopomap.org/">Open Topo Map</a>'

      if show_points:
          folium.Marker(
              location=visp_loc,
              popup="Visp",
              tooltip="Visp",
              icon=folium.Icon(color='blue', icon='info-sign')
          ).add_to(map_)
          
          for i, row in _df.iterrows():
              c = 'red'
              if row['name'] == 'strahlhorn':
                  c = 'green'
              kw = {"prefix": "fa", "color": c, "icon": "mountain-sun"}
              folium.Marker(
                  location=[row['lat'], row['lon']],
                  popup=f"{row['name']} ({row['height']} m)",
                  tooltip=row['name'],
                  icon=folium.Icon(**kw)
              ).add_to(map_)
              #st.info(f"Added marker for {row['name']} {row['lat']} {row['lon']}")

      
      #folium_static(map_)
      st_data = st_folium(map_, width=725)
              
      # maybe solution for click => new marker
      # https://discuss.streamlit.io/t/add-marker-after-clicking-on-map/69472        
      return st_data
    
