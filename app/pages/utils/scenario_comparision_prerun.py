import app.pages.utils.tools as tools
import pandas as pd

data_color = "#1B1212"

def get_df_for_parameter(network_map, parameter, get_values_fn, get_cols_fn):
    all_column_names = _get_all_columns(network_map, get_cols_fn)
    all_column_names.discard("load")
    all_column_names = list(all_column_names)
    df_array = []
    for n in network_map.values():
        avilable_cols = get_cols_fn(n)
        child_arr = []
        for col_name in all_column_names:
            if col_name in avilable_cols:
                child_arr.append(get_values_fn(n, parameter, col_name))
            else:
                child_arr.append(0)
        df_array.append(child_arr)

    indices = network_map.keys()
    indices = [tools.config["scenario_names"][i] for i in indices]
    nice_col_name=[]
    for col_name in all_column_names:
        if col_name in list(tools.config["carrier"]):
            nice_col_name.append(tools.config["carrier"][col_name])
        else:
            nice_col_name.append(col_name)
    
    wide_form_df = pd.DataFrame(df_array, columns=nice_col_name, index=indices)
    return wide_form_df


#############
def add_values_for_statistics(n, parameter, col_name):
    return n.statistics()[parameter].loc["Generator"][col_name]

def add_statistics(n):
    return n.statistics()


def add_values_for_co2(n, parameter, col_name):
    # https://github.com/PyPSA/PyPSA/issues/520
    # n.generators_t.p / n.generators.efficiency * n.generators.carrier.map(n.carriers.co2_emissions)
    df_p = n.generators_t.p
    df_p.drop(df_p.columns[df_p.columns.str.contains("load")], axis=1, inplace=True)
    df_gen = n.generators[~n.generators.index.str.contains("load")]
    co2 = (n.generators_t.p.mean(axis=0) / df_gen.efficiency ) * df_gen.carrier.map(n.carriers[parameter])
    if co2[co2.index.str.contains(col_name)].empty:
        return(0)
    else:
        return(co2[co2.index.str.contains(col_name)].iloc[0])


def add_values_for_generators(n, _parameter, col_name):
    return (
        n.generators.groupby(by="carrier")["p_nom_opt"]
        .sum()
        .drop("load", errors="ignore")
        .get(col_name, default=0)
    )


################
def get_stats_col_names(n):
    return n.statistics()["Curtailment"].loc["Generator"].index


def get_co2_col_names(n):
    return n.carriers.index.array


def get_gen_col_names(n):
    return n.generators.groupby(by="carrier")["p_nom"].sum().index.array

################
def _get_all_columns(network_map, get_cols_fn):
    names = set()
    for n in network_map.values():
        names = names | set(get_cols_fn(n))
    return names

def adjust_plot_appearance(current_fig):
    current_fig.update_layout(
        font=dict(
            family="PT Sans Narrow",
            size=18
        ),              
        legend_font_color=data_color,
        legend_font_size=18,
        legend_title_font_color=data_color,
        legend_title_font_size=18,
        font_color=data_color
    )
    current_fig.update_xaxes(
        tickangle=270,
        tickfont=dict(
            family="PT Sans Narrow",
            color=data_color,
            size=18
        )
    )
    current_fig.update_yaxes(
        title_font=dict(
            family="PT Sans Narrow",
            color=data_color,
            size=18                    
        ),
        tickfont=dict(
            family="PT Sans Narrow",
            color=data_color,
            size=18
        )
    )
    return(current_fig)   