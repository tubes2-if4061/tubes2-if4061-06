from dash import dcc, html
import pandas as pd

from .components.filter import filter_component
from .components.title import title_component
from .ids import MAPS_CONTAINER_ID, MAP_VIEW_TOGGLE_ID


def summary_cards(data: pd.DataFrame) -> html.Div:
    min_year = int(data["year"].min())
    max_year = int(data["year"].max())
    total_records = int(len(data))
    total_countries = int(data["country_txt"].nunique())
    total_attacks = int(data["n_atk"].sum())

    cards = [
        ("Years", f"{min_year}-{max_year}"),
        ("Records", f"{total_records:,}"),
        ("Countries", f"{total_countries:,}"),
        ("Total Attacks", f"{total_attacks:,}"),
    ]

    return html.Div(
        className="summary-row",
        children=[
            html.Div(
                className="summary-card",
                children=[
                    html.Div(value, className="summary-value"),
                    html.Div(label, className="summary-label"),
                ],
            )
            for label, value in cards
        ],
    )


def create_layout(data: pd.DataFrame) -> html.Div:
    return html.Div(
        className="app-shell",
        children=[
            html.Div(
                className="app-layout",
                children=[
                    html.Aside(
                        className="sidebar-nav",
                        children=[
                            html.Div("TG", className="sidebar-logo"),
                            html.Div("MAP", className="nav-item nav-item-active"),
                            html.Div("G2", className="nav-item"),
                            html.Div("G3", className="nav-item"),
                            html.Div("SET", className="nav-item"),
                        ],
                    ),
                    html.Div(
                        className="dashboard",
                        children=[
                            title_component(),
                            summary_cards(data),
                            html.Section(
                                className="content-grid",
                                children=[
                                    html.Div(
                                        className="visualization-section globe-section",
                                        children=[
                                            html.Div(
                                                className="section-heading",
                                                children=[
                                                    html.H2("Globe Interaktif", className="section-title"),
                                                ],
                                            ),
                                            filter_component(data),
                                            html.Div(
                                                className="maps-stage",
                                                children=[
                                                    dcc.RadioItems(
                                                        id=MAP_VIEW_TOGGLE_ID,
                                                        options=[
                                                            {"label": "Globe", "value": "globe"},
                                                            {"label": "Choropleth", "value": "choropleth"},
                                                        ],
                                                        value="globe",
                                                        className="map-view-toggle",
                                                        inputClassName="map-view-input",
                                                        labelClassName="map-view-option",
                                                    ),
                                                    html.Div(id=MAPS_CONTAINER_ID, className="maps-container"),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="right-stack",
                                        children=[
                                            html.Div(
                                                className="visualization-section graph2-section",
                                                children=[
                                                    html.Div(
                                                        className="section-heading",
                                                        children=[
                                                            html.H2("Graph 2", className="section-title"),
                                                        ],
                                                    ),
                                                    html.Div(
                                                        className="placeholder-card",
                                                        children=[
                                                            html.Div("Blank for now", className="placeholder-title"),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                className="visualization-section graph3-section",
                                                children=[
                                                    html.Div(
                                                        className="section-heading",
                                                        children=[
                                                            html.H2("Graph 3", className="section-title"),
                                                        ],
                                                    ),
                                                    html.Div(
                                                        className="placeholder-card graph3-card",
                                                        children=[
                                                            html.Div("Blank for now", className="placeholder-title"),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
