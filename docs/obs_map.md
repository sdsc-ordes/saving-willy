This module provides rendering of observations on an interactive map, with a variety of tilesets available. 

Note: OSM, ESRI, and CartoDB map tiles are served without authentication/tokens,
and so render correctly on the huggingface deployment. The Stamen tiles render
on localhost but require a token to present on a 3rd-party site.

::: src.maps.obs_map