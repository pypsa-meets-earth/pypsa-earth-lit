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
import app.pages.utils.tools as tools
import typing



config=tools.config
pypsa_network_map=tools.get_network_map()

###### for generators #####################

def get_unique_carriers(df):
    all_cols=df.columns
    split_cols= []
    for k in all_cols:
        split_cols.append(k.split(" ")[-1])

    return list(set(split_cols))

def get_meta_df(network_key):
    network=pypsa_network_map.get(network_key)
    return network.meta

def get_gen_t_df(pypsa_network, gen_t_key):
    gen_t_df = pypsa_network.generators_t[gen_t_key]
    unique_carriers = get_unique_carriers(gen_t_df)
    unique_carriers_nice_names = [config["carrier"][carrier] for carrier in unique_carriers]
    resultant_df = pd.DataFrame(0,columns=unique_carriers_nice_names, index=gen_t_df.index)

    for carrier in unique_carriers:
        for bus_carrier in gen_t_df.columns:
            if carrier in bus_carrier.split(" ") :
                nice_name = config["carrier"][carrier]
                resultant_df[nice_name] += gen_t_df[bus_carrier]
    
    return resultant_df
    

non_empth_df_gen_t=[param for param in config["gen_t_parameter"]]

# @st.cache_resource
def get_gen_t_dict():

    result={}
    

    for network_key in pypsa_network_map.keys():
        network_dict={}
        network=pypsa_network_map.get(network_key)
        for non_empty_key in non_empth_df_gen_t:
            network_dict[non_empty_key]=get_gen_t_df(network,non_empty_key)
        
        result[network_key]=network_dict
    
    return result



############# for storage #####################

non_empty_storage_keys=[param for param in config["storage_t_parameter"]]

def get_renamed_column(column_name):
    split_arr=column_name.split(" ")
    last=split_arr.pop(-1)
    split_arr.append(config["carrier"][last])
    return " ".join(split_arr)

def rename_final_df(df):
    for column_name in df.columns:
        df=df.rename(columns={column_name:get_renamed_column(column_name)})
    return df


# @st.cache_resource
def get_storage_t_dict():
    
    result={}

    for network_key in pypsa_network_map.keys():
        network_dict={}
        network = pypsa_network_map.get(network_key)
        for non_empty_key in non_empty_storage_keys:
            df=network.storage_units_t[non_empty_key].copy()
            network_dict[non_empty_key]=  rename_final_df(df)
        
        result[network_key]=network_dict
    return result

############# for links #####################
def get_links_unique_cols(pypsa_network, pypsa_component, col_name):
    #all_cols=pypsa_network.links_t["p0"].columns
    all_cols=getattr(pypsa_network, pypsa_component)[col_name].columns
    split_cols= []
    for k in all_cols:
        split_cols.append(k.split(" ")[-2]+" "+k.split(" ")[-1])
    return list(set(split_cols))

def get_links_df(pypsa_network, pypsa_component, component_key):
    #links_t_df=pypsa_network.links_t[links_t_key]
    pypsa_df = getattr(pypsa_network, pypsa_component)[component_key]
    unique_cols=get_links_unique_cols(pypsa_network, pypsa_component, component_key)
    resultant_df=pd.DataFrame(0,columns=unique_cols, index=pypsa_df.index)

    for carrier in unique_cols:
        for links_carrier in pypsa_df.columns:
            if carrier.split(" ")[-1] in links_carrier.split(" ") :
                resultant_df[carrier]+=pypsa_df[links_carrier]
    
    return resultant_df

#non_empth_links_keys=[param for param in config["links_t_parameter"]]
#non_empth_loads_keys=[param for param in config["loads_t_parameter"]]
#non_empth_stores_keys=[param for param in config["stores_t_parameter"]]

# @st.cache_resource
def get_components_t_dict(component_key, component_keys):
    result={}

    for network_key in pypsa_network_map.keys():
        network_dict={}
        network = pypsa_network_map.get(network_key)
        for non_empty_key in component_keys:
            network_dict[non_empty_key]=get_links_df(network, component_key, non_empty_key)
        
        result[network_key]=network_dict
    return result