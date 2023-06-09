# type: ignore
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
import streamlit as st
import typing


Store.add_style_opts(hv.Bars, ['level'], backend='bokeh')

@st.cache_resource
def get_network_map(pypsa_earth_path):
    RESULTS_DIR = pathlib.Path(pypsa_earth_path, "results")
    networks = {}
    for dir in os.listdir(RESULTS_DIR):
        entry = pathlib.Path(RESULTS_DIR, dir)
        if not entry.is_dir():
            continue

        for dir_child in os.listdir(pathlib.Path(entry, "networks")):
            if not dir_child.endswith(".nc"):
                continue
            networks[dir] = pypsa.Network(
                pathlib.Path(entry, "networks", dir_child)
            )
    return networks

###### for generators #####################

def get_unique_carriers(df):
    all_cols=df.columns
    split_cols= []
    for k in all_cols:
        split_cols.append(k.split(" ")[-1])
    return list(set(split_cols))



def get_gen_t_df(pypsa_network,gen_t_key):
    gen_t_df=pypsa_network.generators_t[gen_t_key]
    unique_carriers=get_unique_carriers(gen_t_df)
    resultant_df=pd.DataFrame(0,columns=unique_carriers,index=gen_t_df.index)

    for carrier in unique_carriers:
        for bus_carrier in gen_t_df.columns:
            if carrier in bus_carrier.split(" ") :
                resultant_df[carrier]+=gen_t_df[bus_carrier]

    return resultant_df
    

non_empth_df_gen_t=["p","p_max_pu"]

@st.cache_resource
def get_gen_t_dict():

    result={}
    pypsa_network_map=get_network_map("pypsa-earth")

    for network_key in pypsa_network_map.keys():
        network_dict={}
        network=pypsa_network_map.get(network_key)
        for non_empty_key in non_empth_df_gen_t:
            network_dict[non_empty_key]=get_gen_t_df(network,non_empty_key)
        
        result[network_key]=network_dict
    
    return result


########## for lines #####################

non_empty_df_lines_t=["p0","mu_upper","mu_lower"]
@st.cache_resource
def get_lines_t_dict():

    result={}
    pypsa_network_map=get_network_map("pypsa-earth")

    for network_key in pypsa_network_map.keys():
        network_dict={}
        network = pypsa_network_map.get(network_key)
        for non_empty_key in non_empty_df_lines_t:
            network_dict[non_empty_key]=network.lines_t[non_empty_key]
        
        result[network_key]=network_dict
    return result


############# for storage #####################

non_empty_storage_keys=["inflow","p","state_of_charge","spill"]

# @st.cache_resource
def get_storage_t_dict():
    
    result={}
    pypsa_network_map=get_network_map("pypsa-earth")

    for network_key in pypsa_network_map.keys():
        network_dict={}
        network = pypsa_network_map.get(network_key)
        for non_empty_key in non_empty_storage_keys:
            network_dict[non_empty_key]=network.storage_units_t[non_empty_key]
        
        result[network_key]=network_dict
    return result

############# for links #####################
def get_links_unique_cols(pypsa_network):
    all_cols=pypsa_network.links_t["p0"].columns
    split_cols= []
    for k in all_cols:
        split_cols.append(k.split(" ")[-1])
    return list(set(split_cols))

def get_links_df(pypsa_network,links_t_key):
    links_t_df=pypsa_network.links_t[links_t_key]
    unique_cols=get_links_unique_cols(pypsa_network)
    resultant_df=pd.DataFrame(0,columns=unique_cols,index=links_t_df.index)

    for carrier in unique_cols:
        for links_carrier in links_t_df.columns:
            if carrier in links_carrier.split(" ") :
                resultant_df[carrier]+=links_t_df[links_carrier]
    return resultant_df

non_empth_links_keys=["p0","mu_upper","mu_lower"]

@st.cache_resource
def get_links_t_dict():
    result={}
    pypsa_network_map=get_network_map("pypsa-earth")

    for network_key in pypsa_network_map.keys():
        network_dict={}
        network = pypsa_network_map.get(network_key)
        for non_empty_key in non_empth_links_keys:
            network_dict[non_empty_key]=get_links_df(network,non_empty_key)
        
        result[network_key]=network_dict
    return result