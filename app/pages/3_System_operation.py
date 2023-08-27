import streamlit as st
st.set_page_config(
    layout="wide"
)

import os
import pathlib
import app.pages.utils.system_operation_prerun as helper
import app.pages.utils.tools as tools

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
import datetime

# needed to change cursor mode of selectboxes from the default text mode
fix_cursor_css = '''
    <style>
        .stSelectbox:first-of-type > div[data-baseweb="select"] > div {
            cursor: pointer;      
        }            
    </style>
'''

non_empth_links_keys=[param for param in helper.config["links_t_parameter"]]
non_empth_loads_keys=[param for param in helper.config["loads_t_parameter"]]
non_empth_stores_keys=[param for param in helper.config["stores_t_parameter"]]

gen_df = helper.get_gen_t_dict()
storage_df = helper.get_storage_t_dict()
loads_df = helper.get_components_t_dict("loads_t", non_empth_loads_keys)
stores_df = helper.get_components_t_dict("stores_t", non_empth_stores_keys)

res_choices = helper.config["operation"]["resolution"]

kwargs = dict(
        stacked=True,
        line_width=0,
        xlabel="",
        width=800,
        height=550,
        hover=False,
        legend="right",
        alpha=0.8
    )
plot_font_dict = dict(
    title=18,
    legend=18,
    labels=18, 
    xticks=18, 
    yticks=18,
)

st.title("System operation")

_, main_col, _, suppl_col, _ = st.columns([1, 35, 1, 20, 1])

def scenario_formatter(scenario):
    return helper.config["scenario_names"][scenario]

def get_carrier_map():
    return helper.config["carrier"]

def get_colors_map():
    return helper.config["tech_colors"]  

carriers_map = get_carrier_map()
tech_map = dict(map(reversed, carriers_map.items()))
tech_colors = get_colors_map()

tools.add_logo()
with main_col:
    selected_network = st.selectbox(
        "Select which scenario's plot you want to see :",
        list(gen_df.keys()),
        format_func = scenario_formatter,
        help="You can choose between available scenarios"
    )
    st.markdown(fix_cursor_css, unsafe_allow_html=True)

# the finest available resolution depends on the model
finest_resolution = helper.get_meta_df(selected_network)["scenario"]["opts"][0].split("L-")[1]
finest_resolution_name = finest_resolution.split("H")[0] + "-hourly"
upd_dict = {finest_resolution: finest_resolution_name}
upd_dict.update(res_choices)

with suppl_col:
    choices = upd_dict
    res = st.selectbox(
        "Resolution",
        choices,
        format_func=lambda x: choices[x], 
        key="gen_res",
        help="You can choose a resolution for time aggregation applied for a plot"
    )
    st.markdown(fix_cursor_css, unsafe_allow_html=True) 


country_data=gen_df.get(selected_network)


##################### generators #####################
gen_df=country_data["p"].drop("Load", axis=1, errors="ignore")

_, date_range_param, _ = st.columns([1, 50, 1])
with date_range_param:
    min_index=gen_df.index[0]
    max_index=gen_df.index[-1]
    min_value = datetime.datetime(min_index.year, min_index.month, min_index.day)
    max_value = datetime.datetime(max_index.year, max_index.month, max_index.day)
    values = st.slider(
            "Select a range of values",
            min_value, max_value, (min_value, max_value),
            # step=datetime.timedelta(hours=int(res[:-1])),
            format="D MMM, HH:mm",
            label_visibility="hidden",
            key="gen_date"
        )

##################### demand #####################
loads_country_data=loads_df.get(selected_network)
stores_country_data=stores_df.get(selected_network)

loads_df = loads_country_data["p"]
stores_df = stores_country_data["p"]

# TODO Remove hard-coding
h2_cols = [col for col in stores_df.columns if "H2" in col]
battery_cols = [col for col in stores_df.columns if "battery" in col]

demand_df=pd.DataFrame({"load": loads_df.sum(axis=1)})
demand_df["H2"]=stores_df[h2_cols].sum(axis=1)
demand_df["battery"]=stores_df[battery_cols].sum(axis=1)

demand_df["load"] = demand_df["load"] * (-1)

demand_df["pbattery"] = 0
demand_df["nbattery"] = 0
demand_df.loc[demand_df['battery'] > 0, "pbattery"] = demand_df["battery"]
demand_df.loc[demand_df['battery'] < 0, "nbattery"] = demand_df["battery"]

demand_df["pH2"] = 0
demand_df["nH2"] = 0
demand_df.loc[demand_df['H2'] > 0, "pH2"] = demand_df["H2"]
demand_df.loc[demand_df['H2'] < 0, "nH2"] = demand_df["H2"]

##################### supply-demand balanse #####################

# ensure consistency of columns naming for generation and demand
gen_df.columns = [tech_map[c] for c in gen_df.columns]

balance_df = (
    pd.concat([gen_df, demand_df], axis=1)
    .drop("battery", axis=1)
    .drop("H2", axis=1)
    .drop("nH2", axis=1)
    .drop("load", axis=1)
)

dem_balance_df = (
    demand_df
    .drop("battery", axis=1)
    .drop("H2", axis=1)
    .drop("pH2", axis=1)
)

balance_aggr=balance_df.loc[values[0]:values[1]].resample(res).mean()
dem_balance_aggr=dem_balance_df.loc[values[0]:values[1]].resample(res).mean()

_, balanse_plot_col, _ = st.columns([1, 80, 1])

plot_color = [tech_colors[c] for c in balance_aggr.columns]
with balanse_plot_col:
    balanse_area_plot=balance_aggr.hvplot.area(
        **kwargs,
        ylabel="Supply [MW]",
        #group_label=helper.config["loads_t_parameter"]["p"]["legend_title"],
        color = plot_color
        )
    balanse_area_plot = balanse_area_plot.opts(
        fontsize=plot_font_dict
    )         
    s2=hv.render(balanse_area_plot, backend='bokeh')
    st.bokeh_chart(s2, use_container_width=True)

plot_color = [tech_colors[c] for c in dem_balance_aggr.columns]
with balanse_plot_col:
    dem_balanse_area_plot=dem_balance_aggr.hvplot.area(
        **kwargs,
        ylabel="Demand [MW]",
        #group_label=helper.config["loads_t_parameter"]["p"]["legend_title"],
        color = plot_color
        )
    dem_balanse_area_plot = dem_balanse_area_plot.opts(
        fontsize=plot_font_dict
    )         
    s2=hv.render(dem_balanse_area_plot, backend='bokeh')
    st.bokeh_chart(s2, use_container_width=True)