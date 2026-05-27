from dash import Dash, Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate
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
    SINGLE_YEAR_MODE_CONTROL_ID,
    SINGLE_YEAR_MODE_FILTER_ID,
    SINGLE_YEAR_SLIDER_ID,
    SINGLE_YEAR_SLIDER_ROW_ID,
    YEAR_RANGE_ERROR_ID,
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


def validate_year_ranges(
    year_ranges: list[tuple[int | None, int | None]],
    visible_count: int,
    min_year: int,
    max_year: int,
) -> tuple[list[str], set[int], set[int]]:
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
    invalid_start_indices: set[int],
    invalid_end_indices: set[int],
) -> list[str]:
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
            Output(SINGLE_YEAR_MODE_CONTROL_ID, "style"),
            Output(SINGLE_YEAR_SLIDER_ROW_ID, "style"),
            Output(APPLY_FILTERS_BUTTON_ID, "style"),
            Output(APPLY_FILTERS_BUTTON_ID, "disabled"),
            Output(APPLY_FILTERS_BUTTON_ID, "className"),
            Output(YEAR_RANGE_ERROR_ID, "children"),
            Output(YEAR_RANGE_ERROR_ID, "style"),
            *[
                Output(input_id, "className")
                for input_id in [*YEAR_RANGE_START_IDS, *YEAR_RANGE_END_IDS]
            ],
            *[Output(row_id, "style") for row_id in YEAR_RANGE_ROW_IDS],
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
    ) -> list[object]:
        visible_count = visible_range_count(selected_mode, compare_count)
        year_ranges = [
            (start_year_1, end_year_1),
            (start_year_2, end_year_2),
            (start_year_3, end_year_3),
            (start_year_4, end_year_4),
        ]
        range_validation_count = (
            0
            if selected_mode != "compare" and single_year_mode == "slider"
            else visible_count
        )
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
        single_year_mode_style = (
            {"display": "grid"} if selected_mode != "compare" else {"display": "none"}
        )
        slider_style = (
            {"display": "grid"}
            if selected_mode != "compare" and single_year_mode == "slider"
            else {"display": "none"}
        )
        apply_button_style = (
            {"display": "none"}
            if selected_mode != "compare" and single_year_mode == "slider"
            else {}
        )
        apply_button_class_name = (
            "apply-button apply-button-disabled"
            if has_invalid_ranges
            else "apply-button"
        )
        error_message = " ".join(validation_messages)
        error_style = {"display": "block"} if has_invalid_ranges else {"display": "none"}
        input_class_names = year_input_class_names(
            invalid_start_indices,
            invalid_end_indices,
        )
        range_styles = [
            {"display": "grid"}
            if (
                selected_mode == "compare"
                and index < visible_count
                or selected_mode != "compare"
                and single_year_mode != "slider"
                and index == 0
            )
            else {"display": "none"}
            for index in range(len(YEAR_RANGE_ROW_IDS))
        ]
        return [
            compare_count_style,
            single_year_mode_style,
            slider_style,
            apply_button_style,
            has_invalid_ranges,
            apply_button_class_name,
            error_message,
            error_style,
            *input_class_names,
            *range_styles,
        ]

    @app.callback(
        Output(MAPS_CONTAINER_ID, "children"),
        [
            Input(APPLY_FILTERS_BUTTON_ID, "n_clicks"),
            Input(SINGLE_YEAR_SLIDER_ID, "value"),
            Input(MODE_FILTER_ID, "value"),
            Input(SINGLE_YEAR_MODE_FILTER_ID, "value"),
        ],
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
        single_year: int,
        selected_mode: str,
        single_year_mode: str,
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
        slider_is_active = selected_mode != "compare" and single_year_mode == "slider"
        slider_triggers = {
            SINGLE_YEAR_SLIDER_ID,
            MODE_FILTER_ID,
            SINGLE_YEAR_MODE_FILTER_ID,
        }
        if ctx.triggered_id in slider_triggers and not slider_is_active:
            raise PreventUpdate

        visible_count = visible_range_count(selected_mode, compare_count)
        year_ranges = [
            (start_year_1, end_year_1),
            (start_year_2, end_year_2),
            (start_year_3, end_year_3),
            (start_year_4, end_year_4),
        ]
        if selected_mode != "compare" and single_year_mode == "slider":
            normalized_single_year = fallback_year(single_year, min_year)
            year_ranges = [(normalized_single_year, normalized_single_year)]
        else:
            validation_messages, _invalid_start_indices, _invalid_end_indices = (
                validate_year_ranges(year_ranges, visible_count, min_year, max_year)
            )
            if validation_messages:
                raise PreventUpdate

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
