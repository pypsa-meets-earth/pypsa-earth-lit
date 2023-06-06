import streamlit as st
import geopandas as gpd
import plotly.express as px

st.title("Scenario comparison")

st.write("Scenario comparison plots will be added here.")

geo_df = gpd.read_file("./data/resources/NG/osm/clean/all_clean_generators.geojson")

fig = px.scatter_mapbox(geo_df, lat=geo_df.geometry.y, lon=geo_df.geometry.x, zoom=1)

st.plotly_chart(fig)
