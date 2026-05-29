from dash import html
import pandas as pd

from .components.filter import filter_component, period_controls_component
from .components.map import attack_legend, compare_map_component, single_map_component
from .components.title import title_component
from .ids import (
    COMPARE_MODE_LAYOUT_ID,
    GRAPH2_SECTION_ID,
    GRAPH3_SECTION_ID,
    MODE_LAYOUT_ID,
    SINGLE_MODE_LAYOUT_ID,
)


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


def graph_placeholder(
    title: str,
    section_class_name: str,
    card_class_name: str = "placeholder-card",
    section_id: str | None = None,
    style: dict[str, str] | None = None,
) -> html.Div:
    return html.Div(
        id=section_id,
        className=f"visualization-section {section_class_name}",
        style=style,
        children=[
            html.Div(
                className="section-heading",
                children=[
                    html.H2(title, className="section-title"),
                ],
            ),
            html.Div(
                className=card_class_name,
                children=[
                    html.Div("Blank for now", className="placeholder-title"),
                ],
            ),
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
                            html.Div(
                                className="dashboard-controls",
                                children=filter_component(data),
                            ),
                            html.Section(
                                id=MODE_LAYOUT_ID,
                                className="mode-layout compare-mode-layout",
                                children=[
                                    html.Div(
                                        className="visualization-section map-workspace",
                                        children=[
                                            html.Div(
                                                id=SINGLE_MODE_LAYOUT_ID,
                                                style={"display": "none"},
                                                children=single_map_component(),
                                            ),
                                            html.Div(
                                                id=COMPARE_MODE_LAYOUT_ID,
                                                style={"display": "grid"},
                                                children=compare_map_component(),
                                            ),
                                            period_controls_component(data),
                                            attack_legend(),
                                        ],
                                    ),
                                    graph_placeholder(
                                        "Graph 2",
                                        "graph2-section",
                                        section_id=GRAPH2_SECTION_ID,
                                        style={"display": "none"},
                                    ),
                                    graph_placeholder(
                                        "Graph 3",
                                        "graph3-section",
                                        "placeholder-card graph3-card",
                                        section_id=GRAPH3_SECTION_ID,
                                        style={"display": "grid"},
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
