import streamlit as st
import pandas as pd
import numpy as np
import xarray as xr
import yaml
import plotly.graph_objects as go
from matplotlib.colors import to_rgba

import matplotlib.pyplot as plt

import pypsa

n = pypsa.Network("data/results.nc")


st.line_chart(n.loads_t.p_set.sum(axis=1))

st.bar_chart(n.statistics()["Capital Expenditure"].loc["Generator"])

st.area_chart(n.generators_t.p_max_pu.loc["2013-03"])


with st.sidebar:
    st.title("PyPSA-Earth Sample Network Analysis")

    


