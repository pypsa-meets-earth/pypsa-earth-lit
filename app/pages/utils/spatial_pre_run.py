import os
import pathlib
import streamlit as st
import pandas as pd
import pypsa
import geopandas as gpd
import numpy as np
import networkx as nx
import app.pages.utils.tools as tools
import yaml


config=tools.config

@st.cache_resource
def get_onshore_regions(pypsa_earth_path):
    RESULTS_DIR=os.path.join(pypsa_earth_path,"resources")
    name_geo_dict = {}
    for dir in os.listdir(RESULTS_DIR):
        entry = pathlib.Path(RESULTS_DIR, dir)
        if not entry.is_dir():
             continue

        for dir_child in os.listdir(pathlib.Path(entry, "bus_regions")):
            if not dir_child.endswith(".geojson"):
                continue
            else:
                dir_child_words=dir_child.split(".")[0].split("_")
                if "onshore" in dir_child_words and len(dir_child_words)==5:
                    gdf = gpd.read_file(pathlib.Path(entry, "bus_regions", dir_child))
                    gdf.geometry = gdf.to_crs(3035).geometry.simplify(1000).to_crs(4326)
                    name_geo_dict[dir] = gdf
    return name_geo_dict


def get_gen_unique_names(network):
    gen_all_names=list(network.generators.index)
    for i in range(len(gen_all_names)):
        gen_all_names[i]=gen_all_names[i].split(" ")[2]

    gen_unique_names=list(set(gen_all_names))
    gen_unique_names.remove("load")
    return gen_unique_names

selected_cols = [param for param in config["gen_spatial_parameters"]]


def get_spatial_values_df(gen_unique_names,selected_cols,network,gpd_bus_regions):
    multi_index= pd.MultiIndex.from_product([gen_unique_names, selected_cols],
    names=['carrier','parameter'])
    param_bus_value_df = pd.DataFrame( index=multi_index,columns=gpd_bus_regions.name)

    for carrier_in_unique in gen_unique_names:
        generator_network=network.generators.copy()
        # carrier sorted value from generator_network
        carrier_df=generator_network[generator_network["carrier"] == carrier_in_unique]
        # arranging according to geopandas bus regions
        temp_name_series = pd.Series([0]*len(gpd_bus_regions), index=gpd_bus_regions.name, name="bus")
        # merging both to get all params df
        merged_gen_df=carrier_df.merge(temp_name_series, left_on="bus", right_on="name", how="right")
        # putting it in the param_bus_value_df 
        for param in selected_cols:
            param_bus_value_df.loc[(carrier_in_unique, param)]=list(merged_gen_df[param])

    param_bus_value_df.replace([np.inf, -np.inf,np.nan], 0, inplace=True)
    return param_bus_value_df


def make_dict_senario(pypsa_network,polygon_gpd):
    return_dict = {}

    ######### DATA FOR POINTS AND CHOLORPETH MAP #########
    return_dict["polygon_gpd"]=polygon_gpd

    # converting polygon geometry with just x and y
    x=list(polygon_gpd["x"].values)
    y=list(polygon_gpd["y"].values)
    points = polygon_gpd.copy()
    points.geometry = gpd.points_from_xy(x, y, crs=4326)
    return_dict["nodes_gpd"]=points

    # add values to nodes_polygon_df
    return_dict["nodes_polygon_df"]=get_spatial_values_df(get_gen_unique_names(pypsa_network),selected_cols,pypsa_network,polygon_gpd)

    ######### DATA FOR LINES  #########

    # adding values to n.lines copy
    nLines=pypsa_network.lines.copy()
    nLines["Total Capacity (GW)"] = nLines.s_nom_opt.clip(lower=1e-3)
    nLines["Reinforcement (GW)"] = nLines.s_nom.clip(lower=1e-3)- nLines.s_nom_opt.clip(lower=1e-3)
    nLines["Original Capacity (GW)"] = nLines.s_nom.clip(lower=1e-3)
    nLines["Maximum Capacity (GW)"] = nLines.s_nom_min.clip(lower=1e-3)
    nLines["Line Length (km)"] = nLines.length
    
    return_dict["lines_df"]=nLines

    # making network object in networkx
    edges= ["Total Capacity (GW)", "Reinforcement (GW)", "Original Capacity (GW)", "Maximum Capacity (GW)","Line Length (km)"]
    G = nx.from_pandas_edgelist(nLines, 'bus0', 'bus1',edge_attr=edges) # type: ignore
    return_dict["lines_edge_netwok"]=G

    
    nodes_pos_dict={}
    for point in polygon_gpd.itertuples():
        nodes_pos_dict[point.name]=(point.x,point.y)
    return_dict["lines_edge_pos_dict"]=nodes_pos_dict

    ######### PARAMETERS  #########

    return_dict["gen_unique_names"]=get_gen_unique_names(pypsa_network)
    return_dict["line_parameters"]=edges

    return return_dict

@st.cache_resource
def make_return_dict():
    return_dict = {}

    pypsa_networks=tools.get_network_map("pypsa-earth")
    bus_region_gpd=get_onshore_regions("pypsa-earth")
    for k in pypsa_networks.keys():
        
        return_dict[k]=make_dict_senario(pypsa_networks.get(k),bus_region_gpd.get(k))

    return return_dict


