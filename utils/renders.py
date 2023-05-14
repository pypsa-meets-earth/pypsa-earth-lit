import plotly.express as px
import streamlit as st
from . import tools
import plotly.graph_objects as go
import math

def get_third_graph(n):
    option = st.selectbox(
'What would you like to see?',
('CO2 emissions', 'optimal generator capacity', 'transmission line expansion'))
    st.write(option)
    if(option == 'CO2 emissions'):
        fig=px.bar(n.carriers[n.carriers["co2_emissions"]!=0]["co2_emissions"],color='value')
        st.plotly_chart(fig, use_container_width=True)

    elif(option == 'optimal generator capacity'):
        fig=px.bar(n.generators.groupby(by="carrier")["p_nom"].sum().drop("load", errors='ignore'),color='value')
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig=px.bar(n.lines.s_nom - n.lines.s_nom_opt,color='value') 
        st.plotly_chart(fig, use_container_width=True)

def get_map(n):
    
    options = st.multiselect(
    'select features',
    ['lines', 'generators'], default=["generators"])

    df=tools.get_sctter_points(n)

    line_df = tools.get_lines(n)

    fig = px.scatter_mapbox(df, lat="y", lon="x", hover_name="name",size="size" ,color="size", opacity=1 if options.__contains__("generators") else 0)

    if(options.__contains__("lines")):
        for i in range(len(line_df)):
            s_nom = line_df["width"][i]
            fig.add_trace(
                go.Scattermapbox(
                    lon=[line_df["source_x"][i], line_df["destination_x"][i]],
                    lat=[line_df["source_y"][i], line_df["destination_y"][i]],
                    mode="lines",
                    line=dict(width=line_df["width"][i]/800),
                    hovertemplate=f"s_nom: {s_nom:.2f},   name: {line_df['index'][i]}",
                    hovertext=line_df["width"][i],
                    name=line_df["index"][i],
                    hoverinfo ="all",
                    showlegend=False,
                )
            )

    fig.update_layout(mapbox_style="carto-positron", mapbox_zoom=4.5, mapbox_center={"lat": sum(df["y"])/len(df), "lon": sum(df["x"])/len(df)})

    st.plotly_chart(fig, use_container_width=False, theme="streamlit")


def get_first_graph(n):
    option = st.selectbox(
    'Select your metric',
    ('Capital Expenditure', 'Installed Capacity', 'Operational Expenditure','Revenue','Optimal Capacity'))

    st.write(option)


    ylabel=""
    if(option == 'Capital Expenditure'or option == 'Operational Expenditure' or option == 'Revenue'):
        ylabel = "Euro"
    else:
        ylabel = "MW"

    fig=px.bar(n.statistics()[[x != 0 and not math.isnan(x) for x in n.statistics()[option]]][option].loc
    ['Generator'].drop('load', errors='ignore'),color='value',
        labels={
                    "carrier": "type of generator",
                    "value": ylabel,
                    })
    st.plotly_chart(fig, use_container_width=True)

