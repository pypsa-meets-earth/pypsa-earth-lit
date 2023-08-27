import streamlit as st
st.set_page_config(
    layout="wide"
)


import app.pages.utils.spatial_pre_run as helper
import app.pages.utils.tools as tools

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

# needed to change cursor mode of selectboxes from the default text mode
fix_cursor_css = '''
    <style>
        .stSelectbox:first-of-type > div[data-baseweb="select"] > div {
            cursor: pointer;      
        }            
    </style>
'''

data=helper.make_return_dict()
tools.add_logo()
st.title("Spatial configuration")


_, main_col, _ = st.columns([1,90,1])

def scenario_formatter(scenario):
    return helper.config["scenario_names"][scenario]

with main_col:
    selected_network = st.selectbox(
        "Select which scenario's plot you want to see :",
        list(data.keys()),
        format_func=scenario_formatter,
        help="You can choose between available scenarios"
    )
st.markdown(fix_cursor_css, unsafe_allow_html=True)    

country_data=data.get(selected_network)

_, col1, col2, col3, _ = st.columns([1,30,30,30,1])

graph_opts = dict(
        xaxis=None,
        yaxis=None,
        active_tools=['pan', 'wheel_zoom'],
    )


polygon_gpd=country_data["polygon_gpd"]
points_gpd=country_data["nodes_gpd"]
map_points_df=country_data["nodes_polygon_df"]


def spatial_param_formatter(param):
    if(param=="Nothing"):
        return param
    param_name=param.split("___")
    carrier=param_name[0]
    param=param_name[1]
    return helper.config["carrier"][carrier]+" - "+helper.config["spatial_parameters"][param]["nice_name"]+" "+helper.config["spatial_parameters"][param]["unit"]


colorpeth_nodes_param = []
for i in map_points_df.index:
    colorpeth_nodes_param.append(f"{i[0]}___{i[1]}")


with col1:
    colorpeth_nodes_param.insert(0,"Nothing")

    colorpeth_param = st.selectbox(
            "Regions", colorpeth_nodes_param, 
            format_func = spatial_param_formatter,
            key="colorpeth_param_carrier",
            help="You can pick a parameter to be shown for each bus region of the model"

        )
    st.markdown(fix_cursor_css, unsafe_allow_html=True)
    
    if(colorpeth_param=="Nothing"):
        plot_area=polygon_gpd.hvplot(
        geo=True,
        tiles="StamenWatercolor",
        color="white",
        alpha=0.8, 
        width=800, height=800).opts(**graph_opts)
    
    else:
        colorpeth_param_carrier=colorpeth_param.split("___")[0]
        colorpeth_param_value=colorpeth_param.split("___")[1]

        # adding data from values df to polygon_gpd
        if(colorpeth_param not in polygon_gpd.columns):
            selecter_col_data=map_points_df.loc[
            (colorpeth_param_carrier, colorpeth_param_value)].values.tolist()
            polygon_gpd.insert(loc=0, column=colorpeth_param, value=selecter_col_data)


        kargs=dict(
            # hover_cols=['name'],
            c=colorpeth_param,
            cmap=helper.config["carrier_colors"][colorpeth_param_carrier],
            clabel=spatial_param_formatter(colorpeth_param)
        )

        plot_area=polygon_gpd.hvplot(
        geo=True,
        tiles="StamenWatercolor",
        alpha=0.8, 
        width=800, height=800,
        **kargs).opts(**graph_opts)
    
with col3:
    points_param = st.selectbox(
            "Nodes", colorpeth_nodes_param,
            format_func = spatial_param_formatter,
            key="points_param_carrier",
            help="You can pick a parameter to be shown for each node of the model"
        )
    st.markdown(fix_cursor_css, unsafe_allow_html=True)
   

    if(points_param=="Nothing"):
        plot_ponts = points_gpd.hvplot(
            geo=True,
            alpha=0,
            color="white"
        ).opts(**graph_opts)

    else:
        points_param_size=f"{points_param}___size"
        points_param_carrier=points_param.split("___")[0]
        points_param_value=points_param.split("___")[1]
        # adding data from values df to points_gpd
        if(points_param not in points_gpd.columns):
            # adding values
            selecter_col_data=map_points_df.loc[
            (points_param_carrier
            ,points_param_value) ].values.tolist()
            points_gpd.insert(loc=0, column=points_param, value=selecter_col_data)
            # adding size factor
            scale = pd.Series(points_gpd[points_param]).max() 
            temp_size=pd.DataFrame()
            temp_size["scale"]=(2+points_gpd[points_param]/scale)*500
            points_gpd.insert(loc=0,column=points_param_size, value=temp_size["scale"].values.tolist())

        plot_ponts = points_gpd.hvplot(
                geo=True,
                # hovercols=["name"],
                size=points_param_size,
                # s = 300,
                c=points_param,
                alpha=0.7,
                color=helper.config["tech_colors"][points_param_carrier]
            ).opts(**graph_opts)
    
###### networkx edges plot ######

G=country_data["edge_netwok"]
pos=country_data["edge_pos_dict"]

edge_params = helper.config["network_parameters"].keys()
edge_params=list(edge_params)
edge_params.insert(0,"Nothing")

def line_param_formatter(param):
    if(param=="Nothing"):
        return param
    return helper.config["network_parameters"][param]

with col2:

    line_option = st.selectbox(
            "Network", edge_params,
            format_func = line_param_formatter,
            key="line_option",
            help="You can pick a parameter to be shown for each line of the model"            
        )
    st.markdown(fix_cursor_css, unsafe_allow_html=True)

    if(line_option!="Nothing"):
        scale = pd.Series(nx.get_edge_attributes(G,line_option )).max() / 10
    
        network_lines_plot=hvnx.draw_networkx_edges(G, pos=pos, edge_color=line_option, responsive=True,
            inspection_policy="edges", node_color='#A0C0E2'
            ,geo=True
            ,edge_width=hv.dim(line_option)/scale ).opts(**graph_opts)


if (line_option=="Nothing"):
    combined_plot=hv.render(plot_area*plot_ponts, backend='bokeh')
else:
    combined_plot=hv.render(plot_area*plot_ponts*network_lines_plot, backend='bokeh')    

st.bokeh_chart(combined_plot, use_container_width=True)