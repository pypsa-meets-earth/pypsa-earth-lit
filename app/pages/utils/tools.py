import os
import pathlib
import streamlit as st
import pypsa
import yaml

# @st.cache_resource
def open_yaml_file(config_file):
    with open(config_file, "r") as f:
       config = yaml.safe_load(f)
    return config

config=open_yaml_file("app/pages/utils/config.yaml")


@st.cache_resource
def get_network_map():
    
    networks = {}
    scenario_names = config["scenario_names"].keys()

    for scenario in scenario_names:
        for dir_child in os.listdir(pathlib.Path("../pypsa-earth" ,"results",scenario, "networks")):
            if not dir_child.endswith(".nc"):
                continue
            networks[scenario] = pypsa.Network(
                pathlib.Path("../pypsa-earth" ,"results",scenario, "networks", dir_child))

    return networks