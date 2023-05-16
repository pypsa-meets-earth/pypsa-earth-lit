import streamlit as st


st.title("Scenario comparison")

st.write("Scenario comparison plots will be added here.")

# import streamlit as st
# import utils.renders as renders
# import pypsa

# ng_model_location = "./results/NG/networks/elec_s_10_ec_lcopt_Co2L-4H.nc"
# big_model_location = "./results/BIG/networks/elec_s_10_ec_lcopt_Co2L-4H.nc"

# with st.sidebar:
#     st.title("PyPSA-Earth Sample Network Analysis")

#     genre = st.radio(
#     "Select a graph:",
#     ('no_oil', 'with_oil'))

# if(genre == 'no_oil'):
#     n = pypsa.Network(big_model_location)
# else:
#     n = pypsa.Network(ng_model_location)

# renders.plot_first_graph(n)
# renders.plot_second_graph(n)
# renders.plot_third_graph(n)