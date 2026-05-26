from dash import Dash, Input, Output, State, dcc, html
import pandas as pd

from .components.map import (
    ATTACK_CATEGORY_COLORS,
    UNREGISTERED_COUNTRY_COLOR,
    build_choropleth_map,
)
from .ids import (
    APPLY_FILTERS_BUTTON_ID,
    COMPARE_COUNT_FILTER_ID,
    MAPS_CONTAINER_ID,
    MODE_FILTER_ID,
    YEAR_RANGE_END_IDS,
    YEAR_RANGE_ROW_IDS,
    YEAR_RANGE_START_IDS,
)


def visible_range_count(mode: str, compare_count: int | None) -> int:
    if mode != "compare":
        return 1

    try:
        normalized_compare_count = int(compare_count)
    except (TypeError, ValueError):
        return 2

    if normalized_compare_count not in {2, 3, 4}:
        return 2
    return normalized_compare_count


def fallback_year(value: int | None, fallback: int) -> int:
    if value is None:
        return fallback
    return int(value)


def format_year_range(start_year: int, end_year: int) -> str:
    range_start = min(start_year, end_year)
    range_end = max(start_year, end_year)
    if range_start == range_end:
        return str(range_start)
    return f"{range_start}-{range_end}"


def map_height(map_count: int) -> int:
    return {
        1: 470,
        2: 340,
        3: 310,
        4: 285,
    }.get(map_count, 430)


def attack_legend() -> html.Div:
    legend_items = [
        *ATTACK_CATEGORY_COLORS.items(),
        ("Not registered", UNREGISTERED_COUNTRY_COLOR),
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


def register_callbacks(app: Dash, data: pd.DataFrame) -> None:
    """Registers all callbacks for the Dash app."""
    min_year = int(data["year"].min())
    max_year = int(data["year"].max())

    @app.callback(
        [
            Output("compare-count-control", "style"),
            *[Output(row_id, "style") for row_id in YEAR_RANGE_ROW_IDS],
        ],
        [
            Input(MODE_FILTER_ID, "value"),
            Input(COMPARE_COUNT_FILTER_ID, "value"),
        ],
    )
    def update_year_range_visibility(
        selected_mode: str,
        compare_count: int,
    ) -> list[dict[str, str]]:
        visible_count = visible_range_count(selected_mode, compare_count)
        compare_count_style = (
            {"display": "grid"} if selected_mode == "compare" else {"display": "none"}
        )
        range_styles = [
            {"display": "grid"} if index < visible_count else {"display": "none"}
            for index in range(len(YEAR_RANGE_ROW_IDS))
        ]
        return [compare_count_style, *range_styles]

    @app.callback(
        Output(MAPS_CONTAINER_ID, "children"),
        Input(APPLY_FILTERS_BUTTON_ID, "n_clicks"),
        State(MODE_FILTER_ID, "value"),
        State(COMPARE_COUNT_FILTER_ID, "value"),
        State(YEAR_RANGE_START_IDS[0], "value"),
        State(YEAR_RANGE_END_IDS[0], "value"),
        State(YEAR_RANGE_START_IDS[1], "value"),
        State(YEAR_RANGE_END_IDS[1], "value"),
        State(YEAR_RANGE_START_IDS[2], "value"),
        State(YEAR_RANGE_END_IDS[2], "value"),
        State(YEAR_RANGE_START_IDS[3], "value"),
        State(YEAR_RANGE_END_IDS[3], "value"),
    )
    def update_maps(
        _n_clicks: int,
        selected_mode: str,
        compare_count: int,
        start_year_1: int,
        end_year_1: int,
        start_year_2: int,
        end_year_2: int,
        start_year_3: int,
        end_year_3: int,
        start_year_4: int,
        end_year_4: int,
    ) -> html.Div:
        visible_count = visible_range_count(selected_mode, compare_count)
        year_ranges = [
            (start_year_1, end_year_1),
            (start_year_2, end_year_2),
            (start_year_3, end_year_3),
            (start_year_4, end_year_4),
        ]

        apply_key = _n_clicks or 0
        graph_height = map_height(visible_count)
        maps = []
        for index, (start_year, end_year) in enumerate(year_ranges[:visible_count], start=1):
            normalized_start_year = fallback_year(start_year, min_year)
            normalized_end_year = fallback_year(end_year, max_year)
            figure = build_choropleth_map(
                data,
                normalized_start_year,
                normalized_end_year,
                graph_height,
            )
            maps.append(
                html.Div(
                    className="map-panel",
                    children=[
                        dcc.Graph(
                            id=f"choropleth-map-{apply_key}-{index}-{normalized_start_year}-{normalized_end_year}",
                            figure=figure,
                            className="choropleth-map",
                            config={"displayModeBar": False, "responsive": True},
                            style={"height": f"{graph_height}px", "width": "100%"},
                        ),
                        html.Div(
                            format_year_range(normalized_start_year, normalized_end_year),
                            className="map-caption",
                        ),
                    ],
                )
            )

        return html.Div(
            className="maps-section",
            children=[
                html.Div(
                    className=f"maps-grid maps-grid-{visible_count}",
                    children=maps,
                ),
                attack_legend(),
            ],
        )
