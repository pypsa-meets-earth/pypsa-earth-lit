import streamlit as st
st.set_page_config(
    layout="wide"
)
import pathlib
import plotly.express as px
import app.pages.utils.tools as tools
import app.pages.utils.scenario_comparision_prerun as helper


def get_stat_unit(param):
    return tools.config["statistics_param_units"][param]

def main():
    st.title("Scenario comparison")

    network_map = tools.get_network_map()

    ###### first dropdown plotting n.statistics #####
    params = list(network_map.values())[0].statistics().columns
    option = st.selectbox(
        "Select your metric",
        params,
    )
    df = helper.get_df_for_parameter(
        network_map, option, helper.add_values_for_statistics, helper.get_stats_col_names
    )
    _, plot_col,_ = st.columns([1, 80, 1])
    with plot_col:
        if option == "Capacity Factor":
            st.plotly_chart(px.scatter(df, y=df.columns,
                # TODO Would be nice to adjust markers
                # size=[20],
                labels={
                    "value":get_stat_unit(option),
                    "index":"scenarios"
                }, title=option),use_cointainer_width=True
            )
        else:
            st.plotly_chart(px.bar(df, y=df.columns, 
                labels={
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
        co2_df = helper.get_df_for_parameter(
            network_map,
            "co2_emissions",
            helper.add_values_for_co2,
            helper.get_co2_col_names,
        )

        _,plot_col,_=st.columns([1,60,1])

        with plot_col:
            fig = px.bar(co2_df, y=co2_df.columns, title="CO2 emissions",labels={
            "value":tools.config["second_param_units"][option],
            "index":"scenarios"
        })
            st.plotly_chart(fig, use_container_width=True)

    elif option == "Optimal Capacity":
        gen_df = helper.get_df_for_parameter(
            network_map, None, helper.add_values_for_generators, helper.get_gen_col_names
        )

        _,plot_col,_=st.columns([1,80,1])

        with plot_col:
            fig = px.bar(gen_df, y=gen_df.columns, title="Optimal Capacity",labels={
            "value":tools.config["second_param_units"][option],
            "index":"scenarios"
        })
            st.plotly_chart(fig, use_container_width=True)


main()
