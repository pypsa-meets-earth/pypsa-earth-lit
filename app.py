import streamlit as st
import pandas as pd
import numpy as np
import xarray as xr
import yaml
import plotly.graph_objects as go
from matplotlib.colors import to_rgba
import plotly.express as px


import matplotlib.pyplot as plt

import pypsa

n = pypsa.Network("data/results.nc")


st.line_chart(n.loads_t.p_set.sum(axis=1))

st.write("the capital expendture for various generators:")
fig=px.bar(n.statistics()["Capital Expenditure"].loc["Generator"])
st.plotly_chart(fig, use_container_width=True)


# 
# https://github.com/pypsa-meets-earth/documentation/blob/main/notebooks/validation/validation_namibia.ipynb
# 
st.write("installed generation by type vs USAID 2020")

nigeria_generators = n.generators.filter(regex="NG *", axis=0)
total_cap = 0
load_cap = 0

capacity_per_carrier = nigeria_generators.groupby(by="carrier")["p_nom"].sum()

if "load" in capacity_per_carrier.index:
        load_cap = capacity_per_carrier["load"]

for c, group in nigeria_generators.groupby(by="carrier"):
    total_cap=total_cap + group["p_nom"].sum()
print( " \n Total  Capacity", total_cap-load_cap , "MW")

df = pd.DataFrame(
     {
         "carrier": pd.Series(dtype="str"),
          "Installed capacity [MW]": pd.Series(dtype="float"),
           "sources": pd.Series(dtype="str")
            })
            
carrier_list = nigeria_generators.carrier.unique()
for i in range(0, len(carrier_list)):
    if carrier_list[i] != "load":
        df.loc[i] = [
            carrier_list[i],
            round(
                nigeria_generators.p_nom.filter(like=carrier_list[i]).sum()
                ,
                2,
                    ), "pypsa 2020"
                    ] # MWh to GWh

usaid_cap = pd.DataFrame()

usaid_cap['carrier'] = ["coal" ,"oil", "onwind", "ror", "solar"]
usaid_cap['Installed capacity [MW]'] = [22, 10, 10, 62, 7]
usaid_cap['sources'] = "USAID 2020"


all_cap = pd.concat([df, usaid_cap], ignore_index=True)

fig=px.bar(df,x='carrier', y='Installed capacity [MW]', color='carrier', title="PYPSA")
st.plotly_chart(fig, use_container_width=True)

fig=px.bar(usaid_cap,x='carrier', y='Installed capacity [MW]', color='carrier', title="USAID 2020")
st.plotly_chart(fig, use_container_width=True)


# 
# 
# ###


st.area_chart(n.generators_t.p_max_pu.loc["2013-03"])



# https://github.com/pypsa-meets-earth/documentation/blob/main/notebooks/add_electricity.ipynb

st.write("Maximal available wind profile (as p.u.)")

fig = px.bar(n.generators_t.p_max_pu.iloc[:, 0])
st.plotly_chart(fig, use_container_width=True)




with st.sidebar:
    st.title("PyPSA-Earth Sample Network Analysis")

    


