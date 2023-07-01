import streamlit as st
st.set_page_config(
    layout="wide"
)
import app.pages.utils.tools as tools
import pathlib
import plotly.express as px
import app.pages.utils.tools as tools


def get_stat_unit(param):
    return tools.config["statistics_param_units"][param]

def main():
    st.title("Scenario comparison")

    network_map = tools.get_network_map("pypsa-earth")

    ###### first dropdown plotting n.statistics #####
    params = list(network_map.values())[0].statistics().columns
    option = st.selectbox(
        "Select your metric",
        params,
    )
    df = tools.get_df_for_parameter(
        network_map, option, tools.add_values_for_statistics, tools.get_stats_col_names
    )
    _,plot_col,_=st.columns([1,80,1])
    with plot_col:
        st.plotly_chart(px.bar(df, y=df.columns,labels={
            "value":get_stat_unit(option),
            "index":"scenarios"
        }, title=option),use_cointainer_width=True
                    )

    ##### second dropdown plotting n.carrier #####
    option = st.selectbox(
        "What would you like to see?",
        tools.config["second_param_units"]
    )

    if option == "CO2 emissions":
        co2_df = tools.get_df_for_parameter(
            network_map,
            "co2_emissions",
            tools.add_values_for_co2,
            tools.get_co2_col_names,
        )

        _,plot_col,_=st.columns([1,60,1])

        with plot_col:
            fig = px.bar(co2_df, y=co2_df.columns, title="CO2 emissions",labels={
            "value":tools.config["second_param_units"][option],
            "index":"scenarios"
        })
            st.plotly_chart(fig, use_container_width=True)

    elif option == "optimal generator capacity":
        gen_df = tools.get_df_for_parameter(
            network_map, None, tools.add_values_for_generators, tools.get_gen_col_names
        )

        _,plot_col,_=st.columns([1,80,1])

        with plot_col:
            fig = px.bar(gen_df, y=gen_df.columns, title="optimal generator capacity",labels={
            "value":tools.config["second_param_units"][option],
            "index":"scenarios"
        })
            st.plotly_chart(fig, use_container_width=True)


main()
