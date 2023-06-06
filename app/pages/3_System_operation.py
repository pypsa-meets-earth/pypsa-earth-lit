import streamlit as st
import app.pages.utils.spatial_pre_run as helper

import os
import pathlib

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
st.set_page_config(
    layout="wide"
)


data=helper.make_return_dict()
st.title("System operation")

st.write("System operation plots will be added here.")




_, main_col, _ = st.columns([1,90,1])

with main_col:
    selected_network = st.selectbox(
        "Select which scenario's plot you want to see :",
        list(data.keys()),
    )

country_data=data.get(selected_network)

_, col1, col2, col3, _ = st.columns([1,30,30,30,1])

graph_opts = dict(
        xaxis=None,
        yaxis=None,
        active_tools=['pan', 'wheel_zoom']
    )

gen_unique_names=country_data["gen_unique_names"]
gen_parameters=country_data["gen_parameters"]
map_points_parameters=[]
for i in gen_unique_names:
    for j in gen_parameters:
        map_points_parameters.append(i+"$"+j)

polygon_gpd=country_data["polygon_gpd"]
points_gpd=country_data["nodes_gpd"]
map_points_df=country_data["nodes_polygon_df"]



with col1:
    colorpeth_param = st.selectbox(
            "Regions", map_points_parameters,    
        )

    if(colorpeth_param not in polygon_gpd.columns):
        selecter_col_data=map_points_df.loc[
        (colorpeth_param.split("$")[0]
        ,colorpeth_param.split("$")[1])].values.tolist()
        polygon_gpd.insert(loc=0,column=colorpeth_param,value=selecter_col_data)
    
    plot_area=polygon_gpd.hvplot(
    geo=True,
     tiles='OSM', alpha=1, 
            hover_cols=['name'],
            width=800, height=600,c=colorpeth_param).opts(**graph_opts)
    
    

with col3:
    points_param = st.selectbox(
            "Nodes", map_points_parameters,
           
        )
    if(points_param not in points_gpd.columns):
        selecter_col_data=map_points_df.loc[
        (points_param.split("$")[0]
        ,points_param.split("$")[1])].values.tolist()
        points_gpd.insert(loc=0,column=points_param,value=selecter_col_data)

    plot_ponts = points_gpd.hvplot(
            geo=True,
            hovercols=["name"],
            size=400,
            # s = 300,
            c=points_param,
            alpha=0.7
        ).opts(**graph_opts)

with col2:
    line_option = st.selectbox(
            "Network", country_data["line_parameters"]
            
        )
    G=country_data["lines_edge_netwok"]
    pos=country_data["lines_edge_pos_dict"]
    scale = pd.Series(nx.get_edge_attributes(G,line_option )).max() / 10
    
    network_lines_plot=hvnx.draw_networkx_edges(G, pos=pos,edge_color=line_option,responsive=True,
            inspection_policy="edges",node_color='#A0C0E2',geo=True,edge_width=hv.dim(line_option)/scale ).opts(**graph_opts)



st.bokeh_chart(hv.render(plot_area*plot_ponts*network_lines_plot, backend='bokeh'), use_container_width=True)