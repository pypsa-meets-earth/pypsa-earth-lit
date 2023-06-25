import streamlit as st
st.set_page_config(
    layout="wide"
)


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



data=helper.make_return_dict()
st.title("System operation")


_, main_col, _ = st.columns([1,90,1])

def scenario_formatter(scenario):
    return helper.config["scenario_names"][scenario]

with main_col:
    selected_network = st.selectbox(
        "Select which scenario's plot you want to see :",
        list(data.keys()),
        format_func=scenario_formatter
    )

country_data=data.get(selected_network)

_, col1, col2, col3, _ = st.columns([1,30,30,30,1])

graph_opts = dict(
        xaxis=None,
        yaxis=None,
        active_tools=['pan', 'wheel_zoom']
    )

gen_parameters=[param for param in helper.config["gen_spatial_parameters"]]
gen_unique_names=country_data["gen_unique_names"]
polygon_gpd=country_data["polygon_gpd"]
points_gpd=country_data["nodes_gpd"]
map_points_df=country_data["nodes_polygon_df"]

def spatial_param_formatter(param):
    return helper.config["gen_spatial_parameters"][param]["nice_name"]+" "+helper.config["gen_spatial_parameters"][param]["unit"]

def carrier_formatter(carrier):
    return helper.config["carrier"][carrier]

with col1:
    st.subheader("Regions")
    colorpeth_param_carrier = st.selectbox(
            "Generator", gen_unique_names, 
            format_func=  carrier_formatter,
            key="colorpeth_param_carrier"

        )
    colorpeth_param_value = st.selectbox(
            "Parameter", gen_parameters,    
            format_func=  spatial_param_formatter,
            key="colorpeth_param_value"
        )

    colorpeth_param = f"{colorpeth_param_carrier}___{colorpeth_param_value}"

    if(colorpeth_param not in polygon_gpd.columns):
        selecter_col_data=map_points_df.loc[
        (colorpeth_param_carrier,colorpeth_param_value)].values.tolist()
        polygon_gpd.insert(loc=0,column=colorpeth_param,value=selecter_col_data)


    kargs=dict(
        cmap=helper.config["carrier_colors"][colorpeth_param_carrier],
    )
    
    plot_area=polygon_gpd.hvplot(
    geo=True,
     tiles='OSM', alpha=0.8, 
            # hover_cols=['name'],
            width=800, height=600,c=colorpeth_param,**kargs).opts(**graph_opts)
    
    

with col3:
    st.subheader("Nodes")
    points_param_carrier = st.selectbox(
            "Generator", gen_unique_names,
            format_func=  carrier_formatter,
           key="points_param_carrier"
        )
    points_param_value = st.selectbox(
            "Parameter", gen_parameters,
            format_func=  spatial_param_formatter,
            key="points_param_value"
    )
    points_param=f"{points_param_carrier}___{points_param_value}"
    points_param_size=f"{points_param_carrier}___{points_param_value}___size"

    if(points_param not in points_gpd.columns):
        # adding values
        selecter_col_data=map_points_df.loc[
        (points_param_carrier
        ,points_param_value) ].values.tolist()
        points_gpd.insert(loc=0,column=points_param,value=selecter_col_data)
        # adding size factor
        scale = pd.Series(points_gpd[points_param]).max() 
        temp_size=pd.DataFrame()
        temp_size["scale"]=(1+points_gpd[points_param]/scale)*500
        points_gpd.insert(loc=0,column=points_param_size,value=temp_size["scale"].values.tolist())
    

    plot_ponts = points_gpd.hvplot(
            geo=True,
            hovercols=["name"],
            size=points_param_size,
            # s = 300,
            c=points_param,
            alpha=0.7,
            color=helper.config["tech_colors"][points_param_carrier]
        ).opts(**graph_opts)

with col2:
    st.subheader("Network")
    line_option = st.selectbox(
            "Option", country_data["line_parameters"],
            key="line_option"
            
        )
    G=country_data["lines_edge_netwok"]
    pos=country_data["lines_edge_pos_dict"]
    scale = pd.Series(nx.get_edge_attributes(G,line_option )).max() / 10
    
    network_lines_plot=hvnx.draw_networkx_edges(G, pos=pos,edge_color=line_option,responsive=True,
            inspection_policy="edges",node_color='#A0C0E2',geo=True,edge_width=hv.dim(line_option)/scale ).opts(**graph_opts)



st.bokeh_chart(hv.render(plot_area*plot_ponts*network_lines_plot, backend='bokeh'), use_container_width=True)