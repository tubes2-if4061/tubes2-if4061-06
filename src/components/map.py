from dash import dcc, html
import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure

from ..ids import (
    COMPARE_MAPS_CONTAINER_ID,
    COMPARE_MAP_VIEW_TOGGLE_ID,
    SINGLE_MAPS_CONTAINER_ID,
    SINGLE_MAP_VIEW_TOGGLE_ID,
)


ATTACK_CATEGORY_COLORS = {
    ">= 1000": "#cb181d",
    "100-999": "#fb6a4a",
    "10-99": "#fcae91",
    "< 10": "#ffe5dc",
}
ATTACK_CATEGORY_ORDER = list(ATTACK_CATEGORY_COLORS.keys())
UNREGISTERED_COUNTRY_COLOR = "#e7e8e8"


def map_view_toggle(toggle_id: str, default_view: str) -> dcc.RadioItems:
    return dcc.RadioItems(
        id=toggle_id,
        options=[
            {"label": "Globe", "value": "globe"},
            {"label": "Choropleth", "value": "choropleth"},
        ],
        value=default_view,
        className="map-view-toggle",
        inputClassName="map-view-input",
        labelClassName="map-view-option",
    )


def map_stage(container_id: str, toggle_id: str, default_view: str) -> html.Div:
    return html.Div(
        className="maps-stage",
        children=[
            map_view_toggle(toggle_id, default_view),
            html.Div(id=container_id, className="maps-container"),
        ],
    )


def single_map_component() -> html.Div:
    return html.Div(
        className="mode-map-panel single-map-section",
        children=[
            html.Div(
                className="section-heading",
                children=[
                    html.H2("Globe Interaktif", className="section-title"),
                ],
            ),
            map_stage(
                SINGLE_MAPS_CONTAINER_ID,
                SINGLE_MAP_VIEW_TOGGLE_ID,
                "globe",
            ),
        ],
    )


def compare_map_component() -> html.Div:
    return html.Div(
        className="mode-map-panel compare-map-section",
        children=[
            html.Div(
                className="section-heading",
                children=[
                    html.H2("Peta Perbandingan", className="section-title"),
                ],
            ),
            map_stage(
                COMPARE_MAPS_CONTAINER_ID,
                COMPARE_MAP_VIEW_TOGGLE_ID,
                "choropleth",
            ),
        ],
    )


def attack_legend() -> html.Div:
    legend_items = [
        ("Not registered", UNREGISTERED_COUNTRY_COLOR),
        *reversed(list(ATTACK_CATEGORY_COLORS.items())),
    ]

    return html.Div(
        className="map-legend",
        children=[
            html.Div("Attacks", className="map-legend-title"),
            *[
                html.Div(
                    className="map-legend-item",
                    children=[
                        html.Span(
                            className="map-legend-swatch",
                            style={"backgroundColor": color},
                        ),
                        html.Span(label),
                    ],
                )
                for label, color in legend_items
            ],
        ],
    )


def attack_category(n_atk: int) -> str:
    if n_atk >= 1000:
        return ">= 1000"
    if n_atk >= 100:
        return "100-999"
    if n_atk >= 10:
        return "10-99"
    return "< 10"


def aggregate_attacks_by_country(
    data: pd.DataFrame,
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    range_start = min(start_year, end_year)
    range_end = max(start_year, end_year)

    countries = (
        data[["country_txt", "country_iso_3"]]
        .drop_duplicates()
        .sort_values("country_txt")
    )

    filtered_data = data[
        (data["year"] >= range_start)
        & (data["year"] <= range_end)
    ]

    attacks = (
        filtered_data.groupby(["country_txt", "country_iso_3"], as_index=False)["n_atk"]
        .sum()
    )

    map_data = countries.merge(
        attacks,
        on=["country_txt", "country_iso_3"],
        how="left",
    )
    map_data["n_atk"] = map_data["n_atk"].fillna(0).astype(int)
    map_data["attack_category"] = pd.Categorical(
        map_data["n_atk"].apply(attack_category),
        categories=ATTACK_CATEGORY_ORDER,
        ordered=True,
    )

    return map_data


def build_choropleth_map(
    data: pd.DataFrame,
    start_year: int,
    end_year: int,
    height: int,
    map_view: str = "globe",
) -> Figure:
    range_start = min(start_year, end_year)
    range_end = max(start_year, end_year)
    map_data = aggregate_attacks_by_country(data, range_start, range_end)

    figure = px.choropleth(
        map_data,
        locations="country_iso_3",
        locationmode="ISO-3",
        color="attack_category",
        color_discrete_map=ATTACK_CATEGORY_COLORS,
        category_orders={"attack_category": ATTACK_CATEGORY_ORDER},
        hover_name="country_txt",
        hover_data={
            "country_iso_3": False,
            "attack_category": False,
            "n_atk": ":,",
        },
        projection="orthographic" if map_view == "globe" else "natural earth",
    )

    geos_config = {
        "domain": {"x": [0, 1], "y": [0, 1]},
        "projection_rotation": {"lon": -25, "lat": 18, "roll": 0},
        "showframe": False,
        "showcoastlines": False,
        "showocean": True,
        "oceancolor": "#0b1220",
        "showlakes": True,
        "lakecolor": "#0b1220",
        "showland": True,
        "landcolor": UNREGISTERED_COUNTRY_COLOR,
        "showcountries": True,
        "countrycolor": "rgba(255, 255, 255, 0.18)",
        "bgcolor": "rgba(0, 0, 0, 0)",
    }

    if map_view == "globe":
        geos_config["projection_scale"] = 0.84
    else:
        geos_config["projection_rotation"] = {"lon": 0, "lat": 0, "roll": 0}
        geos_config["showcoastlines"] = True

    figure.update_geos(
        **geos_config,
    )
    figure.update_layout(
        autosize=True,
        height=height,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        showlegend=False,
        font={"family": "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif", "color": "#e0e0e0"},
    )

    return figure

def get_top_5_attack_types_data(
    data: pd.DataFrame,
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    range_start = min(start_year, end_year)
    range_end = max(start_year, end_year)

    filtered_data = data[
        (data["year"] >= range_start)
        & (data["year"] <= range_end)
    ]

    attack_cols = [col for col in data.columns if col.startswith("attacktype_")]

    yearly_data = filtered_data.groupby("year")[attack_cols].sum().reset_index()

    total_counts = yearly_data[attack_cols].sum().sort_values(ascending=False)
    top_5_cols = total_counts.head(5).index.tolist()

    plot_data = yearly_data[["year"] + top_5_cols]

    long_data = plot_data.melt(
        id_vars=["year"],
        value_vars=top_5_cols,
        var_name="Attack Type",
        value_name="n_atk"
    )

    long_data["Attack Type"] = (
        long_data["Attack Type"]
        .str.replace("attacktype_", "")
        .str.replace("_cnt", "")
        .str.replace("_", " ")
        .str.title()
    )
    
    return long_data

def build_top_5_attack_type_line_graph(
    data: pd.DataFrame,
    year_ranges: list[tuple[int, int]],
) -> Figure:
    min_year = int(data["year"].min())
    max_year = int(data["year"].max())
    plot_data = get_top_5_attack_types_data(data, min_year, max_year)

    figure = px.line(
        plot_data,
        x="year",
        y="n_atk",
        color="Attack Type",
        labels={
            "n_atk": "Number of Attacks", 
            "year": "Year", 
            "Attack Type": "Attack Type"
        },
    )

    figure.update_traces(
        hovertemplate="<b>%{y:,}</b> serangan<extra></extra>"
    )

    colors = ["rgba(255, 99, 132, 0.2)", "rgba(54, 162, 235, 0.2)", "rgba(255, 206, 86, 0.2)", "rgba(75, 192, 192, 0.2)"]

    for index, (start_year, end_year) in enumerate(year_ranges):
        if start_year == end_year:
            x_start = start_year - 0.4
            x_end = end_year + 0.4
        else:
            x_start = start_year
            x_end = end_year

        figure.add_vrect(
            x0=x_start, 
            x1=x_end, 
            fillcolor=colors[index % len(colors)],
            opacity=0.5, 
            layer="below", 
            line_width=1, 
            line_dash="dash",
            annotation_text=f"RANGE {index + 1}",
            annotation_position="top left"
        )

    if year_ranges:
        all_selected_years = [year for range_tuple in year_ranges for year in range_tuple]
        
        zoom_min = min(all_selected_years) - 2
        zoom_max = max(all_selected_years) + 2
        
        zoom_min = max(zoom_min, min_year)
        zoom_max = min(zoom_max, max_year)
    else:
        zoom_min = min_year
        zoom_max = max_year

    zoomed_data = plot_data[
        (plot_data["year"] >= zoom_min) & 
        (plot_data["year"] <= zoom_max)
    ]

    if not zoomed_data.empty:
        max_y_in_view = zoomed_data["n_atk"].max()
        y_axis_max = max_y_in_view * 1.10 
    else:
        y_axis_max = None

    window_size = zoom_max - zoom_min
    dynamic_dtick = 1 if window_size <= 20 else 2

    figure.update_layout(
        legend_title_text="Attack Type",
        font={"family": "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif", "color": "#e0e0e0"},
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        margin={"l": 40, "r": 20, "t": 40, "b": 40},
        xaxis={
            "range": [zoom_min, zoom_max],
            "showgrid": True,
            "gridcolor": "rgba(255, 255, 255, 0.05)",
            "gridwidth": 1,
            "griddash": "dot", 
            "dtick": dynamic_dtick, 
            "tickangle": -45,
        },
        yaxis={"gridcolor": "rgba(255, 255, 255, 0.1)",
               "range": [0, y_axis_max],
               "zeroline": False},
        hovermode="x unified", 
        hoverlabel={
            "bgcolor": "rgba(26, 26, 26, 0.85)",
            "bordercolor": "rgba(255, 255, 255, 0.2)",
            "font_size": 12,
            "font_family": "system-ui"
        }
    )

    return figure

def get_top_5_target_types_data(
    data: pd.DataFrame,
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    range_start = min(start_year, end_year)
    range_end = max(start_year, end_year)

    filtered_data = data[
        (data["year"] >= range_start)
        & (data["year"] <= range_end)
    ]

    target_cols = [col for col in data.columns if col.startswith("targettype_")]

    yearly_data = filtered_data.groupby("year")[target_cols].sum().reset_index()

    total_counts = yearly_data[target_cols].sum().sort_values(ascending=False)
    top_5_cols = total_counts.head(5).index.tolist()

    plot_data = yearly_data[["year"] + top_5_cols]

    long_data = plot_data.melt(
        id_vars=["year"],
        value_vars=top_5_cols,
        var_name="Target Type",
        value_name="n_atk"
    )

    long_data["Target Type"] = (
        long_data["Target Type"]
        .str.replace("targettype_", "")
        .str.replace("_cnt", "")
        .str.replace("_", " ")
        .str.title()
    )
    
    return long_data

def build_top_5_target_type_line_graph(
    data: pd.DataFrame,
    year_ranges: list[tuple[int, int]],
) -> Figure:
    min_year = int(data["year"].min())
    max_year = int(data["year"].max())
    plot_data = get_top_5_target_types_data(data, min_year, max_year)

    figure = px.line(
        plot_data,
        x="year",
        y="n_atk",
        color="Target Type",
        labels={
            "n_atk": "Number of Attacks", 
            "year": "Year", 
            "Target Type": "Target Type"
        },
    )

    figure.update_traces(
        hovertemplate="<b>%{y:,}</b> serangan<extra></extra>"
    )

    colors = ["rgba(255, 99, 132, 0.2)", "rgba(54, 162, 235, 0.2)", "rgba(255, 206, 86, 0.2)", "rgba(75, 192, 192, 0.2)"]

    for index, (start_year, end_year) in enumerate(year_ranges):
        if start_year == end_year:
            x_start = start_year - 0.4
            x_end = end_year + 0.4
        else:
            x_start = start_year
            x_end = end_year

        figure.add_vrect(
            x0=x_start, 
            x1=x_end, 
            fillcolor=colors[index % len(colors)],
            opacity=0.5, 
            layer="below", 
            line_width=1, 
            line_dash="dash",
            annotation_text=f"RANGE {index + 1}",
            annotation_position="top left"
        )

    if year_ranges:
        all_selected_years = [year for range_tuple in year_ranges for year in range_tuple]
        
        zoom_min = min(all_selected_years) - 2
        zoom_max = max(all_selected_years) + 2
        
        zoom_min = max(zoom_min, min_year)
        zoom_max = min(zoom_max, max_year)
    else:
        zoom_min = min_year
        zoom_max = max_year

    zoomed_data = plot_data[
        (plot_data["year"] >= zoom_min) & 
        (plot_data["year"] <= zoom_max)
    ]
    
    if not zoomed_data.empty:
        max_y_in_view = zoomed_data["n_atk"].max()
        y_axis_max = max_y_in_view * 1.10 
    else:
        y_axis_max = None

    window_size = zoom_max - zoom_min
    dynamic_dtick = 1 if window_size <= 20 else 2

    figure.update_layout(
        legend_title_text="Target Type",
        font={"family": "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif", "color": "#e0e0e0"},
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        margin={"l": 40, "r": 20, "t": 40, "b": 40},
        xaxis={
            "range": [zoom_min, zoom_max],
            "showgrid": True,
            "gridcolor": "rgba(255, 255, 255, 0.05)",
            "gridwidth": 1,
            "griddash": "dot", 
            "dtick": dynamic_dtick, 
            "tickangle": -45,
        },
        yaxis={"gridcolor": "rgba(255, 255, 255, 0.1)",
               "range": [0, y_axis_max],
               "zeroline": False},
        hovermode="x unified", 
        hoverlabel={
            "bgcolor": "rgba(26, 26, 26, 0.85)",
            "bordercolor": "rgba(255, 255, 255, 0.2)",
            "font_size": 12,
            "font_family": "system-ui"
        }
    )

    return figure