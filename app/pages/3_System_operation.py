import streamlit as st
st.set_page_config(
    layout="wide"
)

import os
import pathlib
import app.pages.utils.system_operation_prerun as helper

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


gen_df = helper.get_gen_t_dict()
storage_df = helper.get_storage_t_dict()
links_df = helper.get_links_t_dict()

res_choices = helper.config["operation"]["resolution"]

kwargs = dict(
        stacked=True,
        line_width=0,
        xlabel='Time',
        width=800,
        height=550,
        hover=False,
        legend='top'
    )

st.title("System operation")

_, main_col, _ = st.columns([1,90,1])

def scenario_formatter(scenario):
    return helper.config["scenario_names"][scenario]

with main_col:
    selected_network = st.selectbox(
        "Select which scenario's plot you want to see :",
        list(gen_df.keys()),
        format_func = scenario_formatter,
    )

country_data=gen_df.get(selected_network)


##################### generators #####################
st.subheader("Generators plot is here.")

def gen_formatter(gen):
    return helper.config["gen_t_parameter"][gen]["nice_name"]

_, gen_param_col,_,res_param_col,_,date_range_param, _ = st.columns([1,20,1,20,1,50,1])
_, gen_plot_col, _ = st.columns([1,80,1])

with gen_param_col:
    selected_gen = st.selectbox(
        "options",
        options=list(country_data.keys()),
        format_func=gen_formatter
    )

gen_df=country_data[selected_gen]

with res_param_col:
    choices = res_choices
    res = st.selectbox("Resolution", choices, format_func=lambda x: choices[x], key="gen_res")

with date_range_param:
    min_index=gen_df.index[0]
    max_index=gen_df.index[-1]
    min_value = datetime.datetime(min_index.year, min_index.month, min_index.day)
    max_value = datetime.datetime(max_index.year, max_index.month, max_index.day)
    values = st.slider(
            'Select a range of values',
            min_value, max_value, (min_value, max_value),
            # step=datetime.timedelta(hours=int(res[:-1])),
            format="D MMM, HH:mm",
            label_visibility='hidden',
            key="gen_date"
        )
    

gen_df = gen_df.loc[values[0]:values[1]].resample(res).mean()

ylab = helper.config["gen_t_parameter"][selected_gen]["nice_name"] + " ["+str(helper.config["gen_t_parameter"][selected_gen]["unit"] + "]")
# Not sure we really need a title, as there is still a header
gen_area_plot = gen_df.hvplot.area(**kwargs, group_label=helper.config["gen_t_parameter"][selected_gen]["legend_title"]) 
gen_area_plot = gen_area_plot.opts(xlabel="", ylabel=ylab)
s=hv.render(gen_area_plot, backend='bokeh')

with gen_plot_col:
    st.bokeh_chart(s, use_container_width=True)


##################### links #####################

st.subheader("Links plot is here.")
_, links_param_col,_,res_param_col,_,date_range_param, _ = st.columns([1,20,1,20,1,50,1])
_, links_plot_col, _ = st.columns([1,80,1])

links_country_data=links_df.get(selected_network)

def links_formatter(link):
    return helper.config["links_t_parameter"][link]["nice_name"] + " "+helper.config["links_t_parameter"][link]["unit"]

with links_param_col:
    selected_link = st.selectbox(
        "Select which link's plot you want to see :",
        list(links_country_data.keys()),
        format_func=links_formatter
    )

links_df=links_country_data[selected_link]

with res_param_col:
    choices = res_choices
    res = st.selectbox("Resolution", choices, format_func=lambda x: choices[x], key="links_res")

with date_range_param:
    min_index=links_df.index[0]
    max_index=links_df.index[-1]
    min_value = datetime.datetime(min_index.year, min_index.month, min_index.day,max_index.hour,max_index.minute)
    max_value = datetime.datetime(max_index.year, max_index.month, max_index.day,max_index.hour,max_index.minute)
    values = st.slider(
            'Select a range of values',
            min_value, max_value, (min_value, max_value),
            # step=datetime.timedelta(hours=int(res[:-1])),
            format="D MMM, HH:mm",
            label_visibility='hidden',
            key="links_date"
        )

links_df=links_df.loc[values[0]:values[1]].resample(res).mean()

with links_plot_col:
    supply_df=pd.DataFrame(index=links_df.index)
    demand_df=pd.DataFrame(index=links_df.index)
    supply_df["battery charger"]=links_df["battery charger"]
    supply_df["H2 Electrolysis"]=links_df["H2 Electrolysis"]
    demand_df["battery discharger"]=links_df["battery discharger"]
    demand_df["Fuel Cell"]=links_df["Fuel Cell"]
    supply_area_plot=supply_df.hvplot.area(**kwargs,ylabel=helper.config["links_t_parameter"][selected_link]["unit"],
    group_label=helper.config["links_t_parameter"][selected_link]["legend_title"])
    demand_area_plot=demand_df.hvplot.area(**kwargs,ylabel=helper.config["links_t_parameter"][selected_link]["unit"],
    group_label=helper.config["links_t_parameter"][selected_link]["legend_title"])  
    s=hv.render(supply_area_plot,backend='bokeh')
    s2=hv.render(demand_area_plot,backend='bokeh')
    st.subheader("Supply")
    st.bokeh_chart(s, use_container_width=True)
    st.subheader("Consumption")
    st.bokeh_chart(s2, use_container_width=True)



##################### storage #####################

st.subheader("Storage plot is here.")

_, storage_param_col,_,res_param_col,_,date_range_param, _ = st.columns([1,20,1,20,1,50,1])
_, storage_plot_col, _ = st.columns([1,80,1])

storage_country_data=storage_df.get(selected_network)

def storage_formatter(storage):
    return helper.config["storage_t_parameter"][storage]["nice_name"] + " "+helper.config["storage_t_parameter"][storage]["unit"]

with storage_param_col:
    selected_storage = st.selectbox(
        "options",
        list(storage_country_data.keys()),
        format_func=storage_formatter
    )

storage_df=storage_country_data[selected_storage]

with res_param_col:
    choices = res_choices
    res = st.selectbox("Resolution", choices, format_func=lambda x: choices[x],key="storage_res")

with date_range_param:
    min_index=storage_df.index[0]
    max_index=storage_df.index[-1]
    min_value = datetime.datetime(min_index.year, min_index.month, min_index.day,max_index.hour,max_index.minute)
    max_value = datetime.datetime(max_index.year, max_index.month, max_index.day,max_index.hour,max_index.minute)
    values = st.slider(
            'Select a range of values',
            min_value, max_value, (min_value, max_value),
            # step=datetime.timedelta(hours=int(res[:-1])),
            format="D MMM, HH:mm",
            label_visibility='hidden',
            key="storage_date"
        )

storage_df=storage_df.loc[values[0]:values[1]].resample(res).mean()

with storage_plot_col:
    storage_area_plot=storage_df.hvplot.area(**kwargs,
    ylabel=helper.config["storage_t_parameter"][selected_storage]["unit"],
    group_label=helper.config["storage_t_parameter"][selected_storage]["legend_title"])
    s=hv.render(storage_area_plot,backend='bokeh')
    st.bokeh_chart(s, use_container_width=True)
