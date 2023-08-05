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
    RESULTS_DIR = pathlib.Path("../pypsa-earth", "results")
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



