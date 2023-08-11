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
def get_onshore_regions():
    RESULTS_DIR=os.path.join("../pypsa-earth","resources")
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


def _get_gen_unique_names(network):
    gen_all_names=list(network.generators.index)
    for i in range(len(gen_all_names)):
        gen_all_names[i]=gen_all_names[i].split(" ")[2]

    gen_unique_names=list(set(gen_all_names))
    gen_unique_names.remove("load")
    return gen_unique_names

# TODO Add load and stores
selected_cols_gen = ["cf", "p_nom", "p_nom_opt", "marginal_cost", "capital_cost"]# "bus_load"]

def _get_gen_df(network,gpd_bus_regions):
    res_carriers_names = ["solar", "onwind", "offwind-ac", "offwind-dc", "hydro", "ror", "geothermal", "biomass"]
    network_carriers = list(network.generators.carrier.unique())#.remove("load")
    network_res_carriers = [x for x in res_carriers_names if x in network_carriers]
    # network_carriers replaced by network_res_carriers to focus on RES
    multi_index= pd.MultiIndex.from_product([network_res_carriers, selected_cols_gen],
    names=['carrier','parameter'])
    param_bus_value_df = pd.DataFrame( index=multi_index,columns=gpd_bus_regions.name)
    
    i_buses = network.buses_t.p.sum(axis=0).index
    load_df = pd.DataFrame({"bus_load": network.buses_t.p.sum(axis=0), "name": network.buses_t.p.columns})

    for carrier_in_unique in network_res_carriers:
        i_buses = network.buses_t.p.sum(axis=0).index

        generator_network=network.generators.copy()
        # carrier sorted value from generator_network
        i_carrier = generator_network["carrier"] == carrier_in_unique
        carrier_df = generator_network[i_carrier]
        # calculate capacity factors
        p_gen = network.generators_t.p[network.generators[i_carrier].index].mean(axis=0)
        # TODO since p_nom_opt can be zero, there may be a better way to calculate cf       
        carrier_df["cf"] = 100 * (p_gen / generator_network[i_carrier].p_nom_opt)

        # arranging according to geopandas bus regions
        temp_name_series = pd.Series([0]*len(gpd_bus_regions), index=gpd_bus_regions.name, name="bus")

        merged_gen_df = (
            carrier_df
            .merge(temp_name_series, left_on="bus", right_on="name", how="right")
            # TODO MultiIndex structure leads to identical load entries for each carrier - should be improved
            #.merge(load_df, left_on="bus_x", right_on="name", how="left")
        )
        # putting it in the param_bus_value_df for each carrier in generators
        for param in selected_cols_gen:
            param_bus_value_df.loc[(carrier_in_unique, param)]=list(merged_gen_df[param])

    param_bus_value_df.replace([np.inf, -np.inf, np.nan], 0, inplace=True)
    return param_bus_value_df

def _make_plot_lines_df(pypsa_network):
    nLines=pypsa_network.lines.copy()
    nLines["total_capacity"] = nLines.s_nom_opt.clip(lower=1e-3)
    nLines["reinforcement"] = nLines.s_nom_opt.clip(lower=1e-3) - nLines.s_nom.clip(lower=1e-3)
    nLines["original_capacity"] = nLines.s_nom.clip(lower=1e-3)
    # TODO What is the idea of using s_nom_min instead of s_nom_max?
    nLines["max_capacity"] = nLines.s_nom_min.clip(lower=1e-3)

    return nLines


##### add data to these df and define them in config #####

def get_spatial_values_df(pypsa_network,gpd_bus_regions):
    # this df is a multiindex df with carrier and parameter as index and bus regions as columns
    # add new row with index (carrier,parameter) and values as list of values for each bus region (in order)
    # what ever parameters are added to indexes in this df should be added to config "spatial_parameters" along with nice names
    base_df=_get_gen_df(pypsa_network,gpd_bus_regions)

    return base_df


def get_edges_df(pypsa_network):
    #  making base df for edges with lines 
    #  add other columns with data should be defined in config "network_parameters" along with nice names
    base_df=_make_plot_lines_df(pypsa_network)


    return base_df


# this function gives us the complete data in form of a dict
def make_dict_senario(pypsa_network,polygon_gpd):
    return_dict = {}

    ######### DATA FOR POINTS AND CHOLORPETH MAP #########

    return_dict["polygon_gpd"]=polygon_gpd

    # converting polygon geometry to points
    x=list(polygon_gpd["x"].values)
    y=list(polygon_gpd["y"].values)
    points = polygon_gpd.copy()
    points.geometry = gpd.points_from_xy(x, y, crs=4326)

    return_dict["nodes_gpd"]=points

    # base df with all values for all parameters
    return_dict["nodes_polygon_df"]=get_spatial_values_df(pypsa_network,polygon_gpd)

    
    ######### DATA FOR LINES  #########
    
    # getting df for edges and attributes from config
    edges_df=get_edges_df(pypsa_network)

    edges=list(config["network_parameters"].keys())

    # making network object in networkx
    G = nx.from_pandas_edgelist(edges_df, 'bus0', 'bus1',edge_attr=edges) # type: ignore

    return_dict["edge_netwok"]=G

    # addition dict with position of edge nodes reqired for plotting
    nodes_pos_dict={}
    for point in polygon_gpd.itertuples():
        nodes_pos_dict[point.name]=(point.x,point.y)

    return_dict["edge_pos_dict"]=nodes_pos_dict

    return return_dict


# making return dict for every scenario and complete data to plot that scenario
# @st.cache_resource
def make_return_dict():
    return_dict = {}

    pypsa_networks=tools.get_network_map()
    bus_region_gpd=get_onshore_regions()
    for k in pypsa_networks.keys():
          
        return_dict[k]=make_dict_senario(pypsa_networks.get(k),bus_region_gpd.get(k))

    return return_dict


