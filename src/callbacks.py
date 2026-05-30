from dash import Dash, Input, Output, dcc, html, no_update
from dash.exceptions import PreventUpdate
import pandas as pd
from typing import Optional, List, Tuple

from .components.filter import COMPARE_YEAR_DEFAULTS, COMPARE_YEAR_RANGE_DEFAULTS
from .components.map import (
    build_choropleth_map,
    build_graph2_content,
    build_country_sankey,
)
from .ids import (
    COMPARE_MAPS_CONTAINER_ID,
    COMPARE_MAP_VIEW_TOGGLE_ID,
    COMPARE_MODE_LAYOUT_ID,
    COMPARE_COUNT_FILTER_ID,
    COMPARE_YEAR_SLIDER_IDS,
    COMPARE_YEAR_SLIDER_ROW_IDS,
    GRAPH2_SECTION_ID,
    GRAPH3_SECTION_ID,
    MODE_LAYOUT_ID,
    MODE_FILTER_ID,
    PERIOD_CONTROLS_GRID_ID,
    SINGLE_MAPS_CONTAINER_ID,
    SINGLE_MAP_VIEW_TOGGLE_ID,
    SINGLE_MODE_LAYOUT_ID,
    SINGLE_YEAR_MODE_CONTROL_ID,
    SINGLE_YEAR_MODE_FILTER_ID,
    SINGLE_YEAR_SLIDER_ID,
    SINGLE_YEAR_SLIDER_ROW_ID,
    YEAR_RANGE_ERROR_ID,
    YEAR_RANGE_END_IDS,
    YEAR_RANGE_ROW_IDS,
    YEAR_RANGE_START_IDS,
    SINGLE_MAP_CLICK_DATA_ID,
    SINGLE_MAP_GRAPH_ID,
)


def visible_range_count(mode: str, compare_count: Optional[int]) -> int:
    if mode != "compare":
        return 1

    try:
        normalized_compare_count = int(compare_count)
    except (TypeError, ValueError):
        return 4

    if normalized_compare_count not in {2, 3, 4}:
        return 4
    return normalized_compare_count


def fallback_year(value: Optional[int], fallback: int) -> int:
    if value is None:
        return fallback
    return int(value)


def validate_year_ranges(
    year_ranges: List[Tuple[Optional[int], Optional[int]]],
    visible_count: int,
    min_year: int,
    max_year: int,
) -> Tuple[List[str], set, set]:
    order_invalid_labels = []
    bounds_invalid_labels = []
    invalid_start_indices = set()
    invalid_end_indices = set()

    for index, (start_year, end_year) in enumerate(year_ranges[:visible_count], start=1):
        zero_based_index = index - 1
        if start_year is not None:
            normalized_start_year = float(start_year)
            if normalized_start_year < min_year or normalized_start_year > max_year:
                invalid_start_indices.add(zero_based_index)
                bounds_invalid_labels.append(f"Range {index} start")

        if end_year is not None:
            normalized_end_year = float(end_year)
            if normalized_end_year < min_year or normalized_end_year > max_year:
                invalid_end_indices.add(zero_based_index)
                bounds_invalid_labels.append(f"Range {index} end")

        if start_year is None or end_year is None:
            continue

        if float(end_year) < float(start_year):
            order_invalid_labels.append(f"Range {index}")
            invalid_start_indices.add(zero_based_index)
            invalid_end_indices.add(zero_based_index)

    messages = []
    if bounds_invalid_labels:
        messages.append(
            f"{', '.join(bounds_invalid_labels)}: years must be between {min_year} and {max_year}."
        )
    if order_invalid_labels:
        messages.append(
            f"{', '.join(order_invalid_labels)}: end year must be greater than or equal to start year."
        )

    return messages, invalid_start_indices, invalid_end_indices


def year_input_class_names(
    invalid_start_indices: set,
    invalid_end_indices: set,
) -> List[str]:
    start_class_names = [
        "year-input year-input-invalid"
        if index in invalid_start_indices
        else "year-input"
        for index in range(len(YEAR_RANGE_START_IDS))
    ]
    end_class_names = [
        "year-input year-input-invalid"
        if index in invalid_end_indices
        else "year-input"
        for index in range(len(YEAR_RANGE_END_IDS))
    ]
    return [*start_class_names, *end_class_names]


def map_height(map_count: int) -> int:
    return {
        1: 400,
        2: 340,
        3: 310,
        4: 285,
    }.get(map_count, 430)


def build_maps_section(
    data: pd.DataFrame,
    year_ranges: List[Tuple[Optional[int], Optional[int]]],
    graph_height: int,
    selected_map_view: str,
    graph_id_prefix: str,
    min_year: int,
    max_year: int,
) -> html.Div:
    map_count = len(year_ranges)
    maps = []
    for index, (start_year, end_year) in enumerate(year_ranges, start=1):
        normalized_start_year = fallback_year(start_year, min_year)
        normalized_end_year = fallback_year(end_year, max_year)
        figure = build_choropleth_map(
            data,
            normalized_start_year,
            normalized_end_year,
            graph_height,
            selected_map_view,
        )
        maps.append(
            html.Div(
                className="map-panel",
                children=[
                    dcc.Graph(
                        id=f"{graph_id_prefix}-{index}",
                        figure=figure,
                        className="choropleth-map",
                        config={"displayModeBar": True, "displaylogo": False, "responsive": True},
                        style={"height": f"{graph_height}px", "width": "100%"},
                    ),
                ],
            )
        )

    return html.Div(
        className=f"maps-grid maps-grid-{map_count}",
        children=maps,
    )


def register_callbacks(app: Dash, data: pd.DataFrame) -> None:
    """Registers all callbacks for the Dash app."""
    min_year = int(data["year"].min())
    max_year = int(data["year"].max())

    @app.callback(
        [
            Output(MODE_LAYOUT_ID, "className"),
            Output(SINGLE_MODE_LAYOUT_ID, "style"),
            Output(COMPARE_MODE_LAYOUT_ID, "style"),
            Output(GRAPH2_SECTION_ID, "style"),
            Output(GRAPH3_SECTION_ID, "style"),
        ],
        Input(MODE_FILTER_ID, "value"),
    )
    def update_mode_layout(selected_mode: str) -> List[object]:
        if selected_mode == "compare":
            return [
                "mode-layout compare-mode-layout",
                {"display": "none"},
                {"display": "grid"},
                {"display": "none"},
                {"display": "grid"},
            ]
        return [
            "mode-layout single-mode-layout",
            {"display": "grid"},
            {"display": "none"},
            {"display": "grid"},
            {"display": "none"},
        ]

    @app.callback(
        [
            *[Output(input_id, "value") for input_id in YEAR_RANGE_START_IDS],
            *[Output(input_id, "value") for input_id in YEAR_RANGE_END_IDS],
            *[Output(slider_id, "value") for slider_id in COMPARE_YEAR_SLIDER_IDS],
        ],
        [
            Input(MODE_FILTER_ID, "value"),
            Input(COMPARE_COUNT_FILTER_ID, "value"),
        ],
    )
    def sync_compare_default_ranges(
        selected_mode: str,
        compare_count: int,
    ) -> List:
        if selected_mode != "compare":
            return [no_update] * (
                len(YEAR_RANGE_START_IDS)
                + len(YEAR_RANGE_END_IDS)
                + len(COMPARE_YEAR_SLIDER_IDS)
            )

        defaults = COMPARE_YEAR_RANGE_DEFAULTS.get(
            visible_range_count(selected_mode, compare_count),
            COMPARE_YEAR_RANGE_DEFAULTS[4],
        )
        single_year_defaults = COMPARE_YEAR_DEFAULTS.get(
            visible_range_count(selected_mode, compare_count),
            COMPARE_YEAR_DEFAULTS[4],
        )
        return [
            *[start_year for start_year, _end_year in defaults],
            *[end_year for _start_year, end_year in defaults],
            *single_year_defaults,
        ]

    @app.callback(
        [
            Output("compare-count-control", "style"),
            Output(SINGLE_YEAR_MODE_CONTROL_ID, "style"),
            Output(SINGLE_YEAR_SLIDER_ROW_ID, "style"),
            Output(YEAR_RANGE_ERROR_ID, "children"),
            Output(YEAR_RANGE_ERROR_ID, "style"),
            Output(PERIOD_CONTROLS_GRID_ID, "className"),
            *[
                Output(input_id, "className")
                for input_id in [*YEAR_RANGE_START_IDS, *YEAR_RANGE_END_IDS]
            ],
            *[Output(row_id, "style") for row_id in YEAR_RANGE_ROW_IDS],
            *[Output(row_id, "style") for row_id in COMPARE_YEAR_SLIDER_ROW_IDS],
        ],
        [
            Input(MODE_FILTER_ID, "value"),
            Input(COMPARE_COUNT_FILTER_ID, "value"),
            Input(SINGLE_YEAR_MODE_FILTER_ID, "value"),
            Input(YEAR_RANGE_START_IDS[0], "value"),
            Input(YEAR_RANGE_END_IDS[0], "value"),
            Input(YEAR_RANGE_START_IDS[1], "value"),
            Input(YEAR_RANGE_END_IDS[1], "value"),
            Input(YEAR_RANGE_START_IDS[2], "value"),
            Input(YEAR_RANGE_END_IDS[2], "value"),
            Input(YEAR_RANGE_START_IDS[3], "value"),
            Input(YEAR_RANGE_END_IDS[3], "value"),
        ],
    )
    def update_year_range_visibility(
        selected_mode: str,
        compare_count: int,
        single_year_mode: str,
        start_year_1: int,
        end_year_1: int,
        start_year_2: int,
        end_year_2: int,
        start_year_3: int,
        end_year_3: int,
        start_year_4: int,
        end_year_4: int,
    ) -> List[object]:
        visible_count = visible_range_count(selected_mode, compare_count)
        year_ranges = [
            (start_year_1, end_year_1),
            (start_year_2, end_year_2),
            (start_year_3, end_year_3),
            (start_year_4, end_year_4),
        ]
        range_validation_count = 0 if single_year_mode == "slider" else visible_count
        (
            validation_messages,
            invalid_start_indices,
            invalid_end_indices,
        ) = validate_year_ranges(
            year_ranges,
            range_validation_count,
            min_year,
            max_year,
        )
        has_invalid_ranges = len(validation_messages) > 0
        compare_count_style = (
            {"display": "grid"} if selected_mode == "compare" else {"display": "none"}
        )
        single_year_mode_style = {"display": "grid"}
        slider_style = (
            {"display": "grid"}
            if selected_mode != "compare" and single_year_mode == "slider"
            else {"display": "none"}
        )
        error_message = " ".join(validation_messages)
        error_style = {"display": "block"} if has_invalid_ranges else {"display": "none"}
        period_controls_grid_class_name = (
            "year-ranges period-controls-grid "
            f"period-controls-grid-{visible_count if selected_mode == 'compare' else 1}"
        )
        input_class_names = year_input_class_names(
            invalid_start_indices,
            invalid_end_indices,
        )
        range_styles = [
            {"display": "grid"}
            if (
                selected_mode == "compare"
                and single_year_mode != "slider"
                and index < visible_count
                or selected_mode != "compare"
                and single_year_mode != "slider"
                and index == 0
            )
            else {"display": "none"}
            for index in range(len(YEAR_RANGE_ROW_IDS))
        ]
        compare_slider_styles = [
            {"display": "grid"}
            if (
                selected_mode == "compare"
                and single_year_mode == "slider"
                and index < visible_count
            )
            else {"display": "none"}
            for index in range(len(COMPARE_YEAR_SLIDER_ROW_IDS))
        ]
        return [
            compare_count_style,
            single_year_mode_style,
            slider_style,
            error_message,
            error_style,
            period_controls_grid_class_name,
            *input_class_names,
            *range_styles,
            *compare_slider_styles,
        ]

    @app.callback(
        Output(SINGLE_MAPS_CONTAINER_ID, "children"),
        [
            Input(SINGLE_YEAR_SLIDER_ID, "value"),
            Input(MODE_FILTER_ID, "value"),
            Input(SINGLE_YEAR_MODE_FILTER_ID, "value"),
            Input(SINGLE_MAP_VIEW_TOGGLE_ID, "value"),
            Input(YEAR_RANGE_START_IDS[0], "value"),
            Input(YEAR_RANGE_END_IDS[0], "value"),
        ],
    )
    def update_single_map(
        single_year: int,
        selected_mode: str,
        single_year_mode: str,
        selected_map_view: str,
        start_year: int,
        end_year: int,
    ) -> html.Div:
        if selected_mode == "compare":
            raise PreventUpdate

        slider_is_active = single_year_mode == "slider"

        if slider_is_active:
            normalized_single_year = fallback_year(single_year, min_year)
            year_ranges = [(normalized_single_year, normalized_single_year)]
        else:
            year_ranges = [(start_year, end_year)]
            validation_messages, _invalid_start_indices, _invalid_end_indices = (
                validate_year_ranges(year_ranges, 1, min_year, max_year)
            )
            if validation_messages:
                raise PreventUpdate

        return build_maps_section(
            data,
            year_ranges,
            map_height(1),
            selected_map_view or "globe",
            "single-map",
            min_year,
            max_year,
        )

    @app.callback(
        Output(COMPARE_MAPS_CONTAINER_ID, "children"),
        [
            Input(MODE_FILTER_ID, "value"),
            Input(COMPARE_COUNT_FILTER_ID, "value"),
            Input(SINGLE_YEAR_MODE_FILTER_ID, "value"),
            Input(COMPARE_MAP_VIEW_TOGGLE_ID, "value"),
            *[Input(slider_id, "value") for slider_id in COMPARE_YEAR_SLIDER_IDS],
            Input(YEAR_RANGE_START_IDS[0], "value"),
            Input(YEAR_RANGE_END_IDS[0], "value"),
            Input(YEAR_RANGE_START_IDS[1], "value"),
            Input(YEAR_RANGE_END_IDS[1], "value"),
            Input(YEAR_RANGE_START_IDS[2], "value"),
            Input(YEAR_RANGE_END_IDS[2], "value"),
            Input(YEAR_RANGE_START_IDS[3], "value"),
            Input(YEAR_RANGE_END_IDS[3], "value"),
        ],
    )
    def update_compare_maps(
        selected_mode: str,
        compare_count: int,
        single_year_mode: str,
        selected_map_view: str,
        compare_year_1: int,
        compare_year_2: int,
        compare_year_3: int,
        compare_year_4: int,
        start_year_1: int,
        end_year_1: int,
        start_year_2: int,
        end_year_2: int,
        start_year_3: int,
        end_year_3: int,
        start_year_4: int,
        end_year_4: int,
    ) -> html.Div:
        if selected_mode != "compare":
            raise PreventUpdate

        visible_count = visible_range_count(selected_mode, compare_count)
        if single_year_mode == "slider":
            year_ranges = [
                (fallback_year(compare_year_1, min_year), fallback_year(compare_year_1, min_year)),
                (fallback_year(compare_year_2, min_year), fallback_year(compare_year_2, min_year)),
                (fallback_year(compare_year_3, min_year), fallback_year(compare_year_3, min_year)),
                (fallback_year(compare_year_4, min_year), fallback_year(compare_year_4, min_year)),
            ]
        else:
            year_ranges = [
                (start_year_1, end_year_1),
                (start_year_2, end_year_2),
                (start_year_3, end_year_3),
                (start_year_4, end_year_4),
            ]
            validation_messages, _invalid_start_indices, _invalid_end_indices = (
                validate_year_ranges(year_ranges, visible_count, min_year, max_year)
            )
            if validation_messages:
                raise PreventUpdate

        return build_maps_section(
            data,
            year_ranges[:visible_count],
            map_height(visible_count),
            selected_map_view or "choropleth",
            "compare-map",
            min_year,
            max_year,
        )

    @app.callback(
        Output("graph2-content-container", "children"),
        [
            Input(f"{SINGLE_MAP_GRAPH_ID}", "clickData"),
            Input(SINGLE_YEAR_SLIDER_ID, "value"),
            Input(SINGLE_YEAR_MODE_FILTER_ID, "value"),
            Input(YEAR_RANGE_START_IDS[0], "value"),
            Input(YEAR_RANGE_END_IDS[0], "value"),
        ],
    )
    def update_graph2_on_country_click(
        click_data,
        single_year,
        single_year_mode,
        range_start,
        range_end,
    ):
        """Update Graph2 when a country is clicked on the map"""
        if click_data is None or not click_data.get("points"):
            raise PreventUpdate
      
        clicked_point = click_data["points"][0]
        country_name = clicked_point.get("hovertext") or clicked_point.get("customdata")

        if not country_name:
            iso3 = clicked_point.get("location")
            if iso3:
                row = data[data["country_iso_3"] == iso3]
                if not row.empty:
                    country_name = row.iloc[0]["country_txt"]

        if not country_name:
            raise PreventUpdate
        
        # Determine year range
        if single_year_mode == "slider":
            start_year = single_year
            end_year = single_year
        else:
            start_year = range_start or min_year
            end_year = range_end or max_year
        
        try:
            content = build_graph2_content(data, country_name, start_year, end_year)
            return content
        except Exception as e:
            error_msg = html.Div(f"Error: {str(e)}", className="error-message")
            return error_msg
