import os
import pathlib
import app.pages.utils.system_operation_prerun as helper

import pandas as pd
import pypsa
import numpy as np
import plotly.express as px
import xarray as xr
import geopandas as gpd
import plotly.graph_objects as go
import shapely.geometry
import math
import yaml
import hvplot.pandas
import holoviews as hv
from bokeh.models import HoverTool  
from bokeh.plotting import figure, show
from holoviews import Store
import networkx as nx
import hvplot.networkx as hvnx
from shapely.geometry import Point, LineString, shape
import streamlit as st

st.set_page_config(
    layout="wide"
)

gen_df=helper.get_gen_t_dict()
lines_df=helper.get_lines_t_dict()
storage_df=helper.get_storage_t_dict()
links_df=helper.get_links_t_dict()


kwargs = dict(
        stacked=True,
        line_width=0,
        xlabel='',
        width=800,
        height=550,
        hover=False,
        legend='top'
    )

st.title("System operation")


#####################generators#####################
st.write("Generators plot is here.")
_, main_col, _ = st.columns([1,90,1])

with main_col:
    selected_network = st.selectbox(
        "Select which scenario's plot you want to see :",
        list(gen_df.keys()),
    )

country_data=gen_df.get(selected_network)

_, gen_param_col, _ = st.columns([1,40,1])

with gen_param_col:
    selected_gen = st.selectbox(
        "Select which generator's plot you want to see :",
        list(country_data.keys()),
    )

gen_area_plot=country_data[selected_gen].hvplot.area(**kwargs)
s=hv.render(gen_area_plot,backend='bokeh')
st.bokeh_chart(s, use_container_width=True)

#####################lines#####################

st.write("Lines plot is here.")
_, lines_param_col, _ = st.columns([1,40,1])

lines_country_data=lines_df.get(selected_network)

with lines_param_col:
    selected_line = st.selectbox(
        "Select which line's plot you want to see :",
        list(lines_country_data.keys()),
    )

lines_area_plot=lines_country_data[selected_line].hvplot.area(**kwargs)
s=hv.render(lines_area_plot,backend='bokeh')
st.bokeh_chart(s, use_container_width=True)

##################### storage #####################
st.write("Storage plot is here.")
_, storage_param_col, _ = st.columns([1,40,1])

storage_country_data=storage_df.get(selected_network)

with storage_param_col:
    selected_storage = st.selectbox(
        "Select which storage's plot you want to see :",
        list(storage_country_data.keys()),
    )

storage_area_plot=storage_country_data[selected_storage].hvplot.area(**kwargs)
s=hv.render(storage_area_plot,backend='bokeh')
st.bokeh_chart(s, use_container_width=True)

##################### links #####################

st.write("Links plot is here.")
_, links_param_col, _ = st.columns([1,40,1])

links_country_data=links_df.get(selected_network)

with links_param_col:
    selected_link = st.selectbox(
        "Select which link's plot you want to see :",
        list(links_country_data.keys()),
    )

links_area_plot=links_country_data[selected_link].hvplot.area(**kwargs)
s=hv.render(links_area_plot,backend='bokeh')
st.bokeh_chart(s, use_container_width=True)