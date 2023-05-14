import streamlit as st

import sys
sys.path.insert(0, "..")
from utils import renders


import pypsa

ng_model_location = "./results/NG/networks/elec_s_10_ec_lcopt_Co2L-4H.nc"
big_model_location = "./results/BIG/networks/elec_s_10_ec_lcopt_Co2L-4H.nc"

with st.sidebar:
    st.title("PyPSA-Earth Sample Network Analysis")

    genre = st.radio(
    "Select a graph:",
    ('no_oil', 'with_oil'))

if(genre == 'no_oil'):
    n = pypsa.Network(big_model_location)
else:
    n = pypsa.Network(ng_model_location)

renders.get_first_graph(n)


# #######
renders.get_map(n)

# create line traces to figure


# #######


renders.get_third_graph(n)