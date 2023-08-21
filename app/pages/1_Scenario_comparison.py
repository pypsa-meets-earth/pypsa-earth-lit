import streamlit as st
st.set_page_config(
    layout="wide"
)
import pathlib
import plotly.express as px
import app.pages.utils.tools as tools
import app.pages.utils.scenario_comparision_prerun as helper

data_color = "#1B1212"
# needed to change cursor mode of selectboxes from the default text mode
fix_cursor_css = '''
    <style>
        .stSelectbox:first-of-type > div[data-baseweb="select"] > div {
            cursor: pointer;      
        }            
    </style>
'''

def get_stat_unit(param):
    return tools.config["statistics_param_units"][param]

def get_carrier_map():
    return tools.config["carrier"]

def get_colors_map():
    return tools.config["tech_colors"]

def scenario_formatter(scenario):
    return tools.config["scenario_names"][scenario]

def main():
    st.title("Scenario comparison")

    network_map = tools.get_network_map()
    carriers_map = get_carrier_map()
    tech_map = dict(map(reversed, carriers_map.items()))

    ###### first dropdown plotting n.statistics #####
    params = list(network_map.values())[0].statistics().columns
    st.header("Statistics plot")
    _, select_col, _ = st.columns([2,60,20])


    with select_col: 
        option = st.selectbox(
            "Select metric",
            params,
            help="You can select any parameter from PyPSA Network Statistics table"
        )
        st.markdown(fix_cursor_css, unsafe_allow_html=True)

    df = helper.get_df_for_parameter(
        network_map, option, helper.add_values_for_statistics, helper.get_stats_col_names
    )

    df_techs = [tech_map[c] for c in df.columns]
    tech_colors = get_colors_map()
    plot_color = [tech_colors[c] for c in df_techs]

    # needed to control markers size for the scatter
    _, plot_col,_ = st.columns([1,80,1])
    with plot_col:
        if option == "Capacity Factor":
            df["dummy_size"] = 1
            fig = px.scatter(df, y=df.columns,
                size="dummy_size",
                size_max=25,
                opacity=0.9,
                color_discrete_sequence=plot_color,
                labels={
                    "value":get_stat_unit(option),
                    "index":" ",
                    "variable": "carriers"
                },
                title=" ")
            helper.adjust_plot_appearance(current_fig=fig)
            st.plotly_chart(fig,
                use_cointainer_width=True
            )
        else:
            fig = px.bar(df, y=df.columns,
                color_discrete_sequence=plot_color,                    
                labels={
                    "value":get_stat_unit(option),
                    "index":" ",
                    "variable": "carriers"
                }, 
                title=" ")
            helper.adjust_plot_appearance(current_fig=fig)
            st.plotly_chart(fig,
                use_cointainer_width=True
            )            

    st.header("Network statistics")
    _, table_col, _ = st.columns([2,60,20])
    with table_col:
        scenario = st.selectbox(
            "Select scenario:",
            list(network_map.keys()),
            format_func=scenario_formatter,
            help="You can choose between available scenarios"
        )
    st.markdown(fix_cursor_css, unsafe_allow_html=True)
    stat_table = helper.add_statistics(network_map[scenario])

    th_props = [
        ("font-size", "18px"),
        ("color", data_color),
        ("font-weight", "bold"),
        ("text-align", "left")
    ]
    td_props = [
        ("font-size", "18px"),
        ("color", data_color)
    ]    
    styles = [
        dict(selector="th", props=th_props),
        dict(selector="td", props=td_props)
    ]

    df = (
        stat_table.style
        .format(precision=2, thousands=" ", decimal=".")
        .set_properties().set_table_styles(styles)
        )

    with table_col:
        # st.dataframe(stat_table.style.format(precision=2, thousands=" ", decimal="."))
        st.table(df)     

    ##### second dropdown plotting n.carrier #####
    st.header("Operation plots")    
    _, table_col, _ = st.columns([2,60,20])
    with table_col:    
        option = st.selectbox(
            "Which plot would you like to see?",
            tools.config["second_param_units"],
            help="Currently, you can choose between CO2 emissions and Optimal Capacity plots. More options will follow soon"
        )
    st.markdown(fix_cursor_css, unsafe_allow_html=True)    
    if option == "CO2 emissions":
        co2_df = helper.get_df_for_parameter(
            network_map,
            "co2_emissions",
            helper.add_values_for_co2,
            helper.get_co2_col_names,
        ).drop("Load", axis=1)

        df_techs = [tech_map[c] for c in co2_df.columns]
        tech_colors = get_colors_map()
        plot_color = [tech_colors[c] for c in df_techs]

        _, plot_col, _ = st.columns([1,60,1])

        with plot_col:
            fig = px.bar(co2_df, y=co2_df.columns, 
                title=" ",
                color_discrete_sequence=plot_color,
                labels={
                    "value": tools.config["second_param_units"][option],
                    "index":" ",
                    "variable": "carriers"
                }
            )
            helper.adjust_plot_appearance(current_fig=fig)
            st.plotly_chart(fig, use_container_width=True)

    elif option == "Optimal Capacity":
        gen_df = helper.get_df_for_parameter(
            network_map, None, helper.add_values_for_generators, helper.get_gen_col_names
        )

        df_techs = [tech_map[c] for c in gen_df.columns]
        tech_colors = get_colors_map()
        plot_color = [tech_colors[c] for c in df_techs]

        _,plot_col,_=st.columns([1,80,1])

        with plot_col:
            fig = px.bar(
                gen_df, 
                y=gen_df.columns, 
                title=" ",
                color_discrete_sequence=plot_color,
                labels={
                    "value": tools.config["second_param_units"][option],
                    "index":" ",
                    "variable": "carriers"
                }  
            )
            helper.adjust_plot_appearance(current_fig=fig) 
            st.plotly_chart(fig, use_container_width=True)


main()
