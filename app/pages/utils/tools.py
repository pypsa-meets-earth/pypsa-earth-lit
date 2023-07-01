import os
import pathlib
import streamlit as st
import pandas as pd
import pypsa
import yaml

# @st.cache_resource
def return_color_from_yaml(config_file):
    with open(config_file, "r") as f:
       config = yaml.safe_load(f)
    return config

config=return_color_from_yaml("app/pages/utils/config.yaml")


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
    print(networks)
    return networks



def get_df_for_parameter(network_map, parameter, get_values_fn, get_cols_fn):
    all_column_names = _get_all_columns(network_map, get_cols_fn)
    all_column_names.discard("load")
    all_column_names = list(all_column_names)
    df_array = []
    for n in network_map.values():
        avilable_cols = get_cols_fn(n)
        child_arr = []
        for col_name in all_column_names:
            if col_name in avilable_cols:
                child_arr.append(get_values_fn(n, parameter, col_name))
            else:
                child_arr.append(0)
        df_array.append(child_arr)

    indices = network_map.keys()
    indices = [config["scenario_names"][i] for i in indices]
    nice_col_name=[]
    for col_name in all_column_names:
        if col_name in list(config["carrier"]):
            nice_col_name.append(config["carrier"][col_name])
        else:
            nice_col_name.append(col_name)
    
    wide_form_df = pd.DataFrame(df_array, columns=nice_col_name, index=indices)
    return wide_form_df


#############
def add_values_for_statistics(n, parameter, col_name):
    return n.statistics()[parameter].loc["Generator"][col_name]


def add_values_for_co2(n, parameter, col_name):
    return n.carriers[parameter].get(col_name, default=0)


def add_values_for_generators(n, _parameter, col_name):
    return (
        n.generators.groupby(by="carrier")["p_nom"]
        .sum()
        .drop("load", errors="ignore")
        .get(col_name, default=0)
    )


################
def get_stats_col_names(n):
    return n.statistics()["Curtailment"].loc["Generator"].index


def get_co2_col_names(n):
    return n.carriers.index.array


def get_gen_col_names(n):
    return n.generators.groupby(by="carrier")["p_nom"].sum().index.array


def _get_all_columns(network_map, get_cols_fn):
    names = set()
    for n in network_map.values():
        names = names | set(get_cols_fn(n))
    return names