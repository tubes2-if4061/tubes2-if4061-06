from dash import dcc, html
import pandas as pd
from typing import Optional, Dict

from .components.filter import filter_component, period_controls_component
from .components.map import attack_legend, compare_map_component, single_map_component
from .components.title import title_component
from .ids import (
    COMPARE_MODE_LAYOUT_ID,
    COMPARE_DETAIL_TRANSFER_STORE_ID,
    COUNTRY_DETAIL_CLOSE_BUTTON_ID,
    COUNTRY_SANKEY_ID,
    COUNTRY_SANKEY_SECTION_ID,
    GRAPH2_SECTION_ID,
    LINE_GRAPH_WORKSPACE_ID,
    MODE_LAYOUT_ID,
    MODE_RESTORE_STORE_ID,
    MODE_STATE_STORE_ID,
    SINGLE_MODE_LAYOUT_ID,
    SINGLE_MAP_CLICK_DATA_ID,
    TOP_5_ATTACK_TYPE_GRAPH_ID,
    TOP_5_TARGET_TYPE_GRAPH_ID,
    VIEWPORT_WIDTH_INTERVAL_ID,
    VIEWPORT_WIDTH_STORE_ID,
)


def summary_cards(data: pd.DataFrame) -> html.Div:
    min_year = int(data["year"].min())
    max_year = int(data["year"].max())
    total_records = int(len(data))
    total_countries = int(data["country_txt"].nunique())
    total_attacks = int(data["n_atk"].sum())

    cards = [
        ("Tahun Tersedia (kecuali 1993)", f"{min_year}-{max_year}"),
        ("Baris Data", f"{total_records:,}"),
        ("Negara", f"{total_countries:,}"),
        ("Total Serangan", f"{total_attacks:,}"),
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
    section_id: Optional[str] = None,
    style: Optional[Dict[str, str]] = None,
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
                                    html.Section(
                                        id=COUNTRY_SANKEY_SECTION_ID,
                                        className="visualization-section sankey-section",
                                        style={"display": "none"},
                                        children=[
                                            html.Div(
                                                className="section-heading",
                                                children=[
                                                    html.H2(
                                                        "Alur Jenis Serangan dan Target",
                                                        className="section-title",
                                                    ),
                                                ],
                                            ),
                                            dcc.Graph(
                                                id=COUNTRY_SANKEY_ID,
                                                className="country-sankey-chart",
                                                config={
                                                    "displayModeBar": True,
                                                    "displaylogo": False,
                                                    "responsive": True,
                                                },
                                                style={"height": "500px", "width": "100%"},
                                            ),
                                        ],
                                    ),
                                    html.Section(
                                        id=GRAPH2_SECTION_ID,
                                        className="graph2-section",
                                        style={"display": "none"},
                                        children=[
                                            html.Button(
                                                "Tutup",
                                                id=COUNTRY_DETAIL_CLOSE_BUTTON_ID,
                                                className="detail-close-button",
                                                n_clicks=0,
                                                type="button",
                                            ),
                                            html.Div(
                                                id="graph2-content-container",
                                                className="graph2-content-container",
                                            ),
                                        ],
                                    ),
                                    dcc.Store(id=SINGLE_MAP_CLICK_DATA_ID),
                                    dcc.Store(id=VIEWPORT_WIDTH_STORE_ID),
                                    dcc.Store(id=MODE_STATE_STORE_ID, storage_type="memory"),
                                    dcc.Store(id=MODE_RESTORE_STORE_ID, storage_type="memory"),
                                    dcc.Store(id=COMPARE_DETAIL_TRANSFER_STORE_ID, storage_type="memory"),
                                    dcc.Interval(
                                        id=VIEWPORT_WIDTH_INTERVAL_ID,
                                        interval=1000,
                                        n_intervals=0,
                                        max_intervals=1,
                                    ),
                            html.Div(
                                id=LINE_GRAPH_WORKSPACE_ID,
                                className="visualization-section line-graph-workspace",
                                children=[
                                    html.Div(
                                        className="graph-card",
                                        children=[
                                            html.H3("Top 5 Jenis Serangan", className="graph-title"),
                                            dcc.Graph(
                                                id=TOP_5_ATTACK_TYPE_GRAPH_ID,
                                                className="line-graph",
                                                config={
                                                    "displayModeBar": False,
                                                    "responsive": True,
                                                },
                                                responsive=True,
                                                style={"height": "350px", "width": "100%"},
                                            )
                                        ],
                                    ),
                                    html.Div(
                                        className="graph-card",
                                        children=[
                                            html.H3("Top 5 Target Serangan", className="graph-title"),
                                            dcc.Graph(
                                                id=TOP_5_TARGET_TYPE_GRAPH_ID,
                                                className="line-graph",
                                                config={
                                                    "displayModeBar": False,
                                                    "responsive": True,
                                                },
                                                responsive=True,
                                                style={"height": "350px", "width": "100%"},
                                            )
                                        ],
                                    ),
                                ]
                            )
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
