import streamlit as st
import app.pages.utils.spatial_configuration_helper as helper
import app.pages.utils.tools as tools
import plotly.express as px
import plotly.graph_objects as go


def main():
    network_map = tools.get_network_map("pypsa-earth")

    name_network_map = {}

    for name, file_name in network_map.keys():
        name_network_map[name] = network_map[(name, file_name)]

    st.title("Spatial configuration")

    selected_network = st.selectbox(
        "Select your metric",
        list(name_network_map.keys()),
    )

    n = name_network_map[selected_network]

    options = st.multiselect(
        "select features", ["lines", "generators"], default=["generators"]
    )

    df = helper.get_sctter_points(n)

    line_df = helper.get_lines(n)

    fig = px.scatter_mapbox(
        df,
        lat="y",
        lon="x",
        hover_name="name",
        size="size",
        color="size",
        opacity=1 if options.__contains__("generators") else 0,
    )

    if options.__contains__("lines"):
        for i in range(len(line_df)):
            s_nom = line_df["width"][i]
            fig.add_trace(
                go.Scattermapbox(
                    lon=[line_df["source_x"][i], line_df["destination_x"][i]],
                    lat=[line_df["source_y"][i], line_df["destination_y"][i]],
                    mode="lines",
                    line=dict(width=line_df["width"][i] / 800),
                    hovertemplate=f"s_nom: {s_nom:.2f},   name: {line_df['index'][i]}",
                    hovertext=line_df["width"][i],
                    name=line_df["index"][i],
                    hoverinfo="all",
                    showlegend=False,
                )
            )

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=4.5,
        mapbox_center={"lat": sum(df["y"]) / len(df), "lon": sum(df["x"]) / len(df)},
    )

    st.plotly_chart(fig, use_container_width=False, theme="streamlit")


main()
