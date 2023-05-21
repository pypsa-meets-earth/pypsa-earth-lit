import os
import pathlib
import streamlit as st
import pandas as pd
import pypsa


def get_lines(n1):
    buses_map = {
        n1.buses.index[i]: {"x": n1.buses["x"][i], "y": n1.buses["y"][i]}
        for i in range(len(n1.buses))
    }

    line_df = pd.DataFrame()

    source_x_list = []
    source_y_list = []
    destination_x_list = []
    destination_y_list = []
    line_name = []
    total_capacity = []
    reinforcement = []
    original_capacity = []
    maximum_capacity = []
    technology = []
    length = []

    for i in range(len(n1.lines)):
        source_x_list.append(buses_map[n1.lines.bus0[i]]["x"])
        source_y_list.append(buses_map[n1.lines.bus0[i]]["y"])
        destination_x_list.append(buses_map[n1.lines.bus1[i]]["x"])
        destination_y_list.append(buses_map[n1.lines.bus1[i]]["y"])
        line_name.append(f"line_{n1.lines.index[i]}")
        total_capacity.append(n1.lines.s_nom_opt.clip(lower=1e-3)[i])
        reinforcement.append(
            n1.lines.s_nom_opt.clip(lower=1e-3)[i] - n1.lines.s_nom.clip(lower=1e-3)[i]
        )
        original_capacity.append(n1.lines.s_nom.clip(lower=1e-3)[i])
        maximum_capacity.append(n1.lines.s_nom_min.clip(lower=1e-3)[i])
        technology.append(n1.lines.carrier[i])
        length.append(n1.lines.length[i])

    line_df["source_x"] = source_x_list
    line_df["source_y"] = source_y_list
    line_df["destination_x"] = destination_x_list
    line_df["destination_y"] = destination_y_list
    line_df["index"] = line_name
    line_df["Total Capacity (GW)"] = total_capacity
    line_df["Reinforcement (GW)"] = reinforcement
    line_df["Original Capacity (GW)"] = original_capacity
    line_df["Maximum Capacity (GW)"] = maximum_capacity
    line_df["Technology"] = technology
    line_df["Length (km)"] = length
    return line_df


def get_sctter_points(n1):
    df = pd.DataFrame()
    df["x"] = n1.buses["x"]
    df["y"] = n1.buses["y"]
    df["name"] = n1.buses.index
    df["cost"] = n1.stores["marginal_cost"]
    df["size"] = (df["cost"] - (df["cost"].sum() / len(df))) * 1000

    dropped_indices = []
    for i in range(len(df)):
        if "battery" not in df["name"][i]:
            dropped_indices.append(df["name"][i])

    df.drop(index=dropped_indices, inplace=True)

    return df
