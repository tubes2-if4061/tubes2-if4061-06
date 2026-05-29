from dash import dcc, html
import pandas as pd

from ..ids import (
    APPLY_FILTERS_BUTTON_ID,
    COMPARE_COUNT_FILTER_ID,
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


def year_dropdown(dropdown_id: str, years: list[int], value: int) -> dcc.Input:
    return dcc.Input(
        id=dropdown_id,
        type="number",
        step=1,
        value=value,
        className="year-input",
    )


def year_range_row(
    row_index: int,
    years: list[int],
    default_start_year: int,
    default_end_year: int,
) -> html.Div:
    return html.Div(
        id=YEAR_RANGE_ROW_IDS[row_index],
        className="year-range-row",
        style={"display": "grid"} if row_index == 0 else {"display": "none"},
        children=[
            html.Div(f"Range {row_index + 1}", className="range-label"),
            html.Label(
                className="field-label",
                children=[
                    "Start",
                    year_dropdown(
                        YEAR_RANGE_START_IDS[row_index],
                        years,
                        default_start_year,
                    ),
                ],
            ),
            html.Label(
                className="field-label",
                children=[
                    "End",
                    year_dropdown(
                        YEAR_RANGE_END_IDS[row_index],
                        years,
                        default_end_year,
                    ),
                ],
            ),
        ],
    )


def slider_marks(years: list[int]) -> dict[int, str]:
    decade_marks = {
        int(year): str(year)
        for year in years
        if year == years[0] or year == years[-1] or year % 10 == 0
    }
    return decade_marks


def single_year_slider_row(years: list[int], default_year: int) -> html.Div:
    return html.Div(
        id=SINGLE_YEAR_SLIDER_ROW_ID,
        className="year-slider-row",
        style={"display": "none"},
        children=[
            html.Div("Year", className="range-label"),
            html.Div(
                className="year-slider-wrap",
                children=[
                    dcc.Slider(
                        id=SINGLE_YEAR_SLIDER_ID,
                        min=years[0],
                        max=years[-1],
                        step=1,
                        value=default_year,
                        marks=slider_marks(years),
                        included=False,
                        updatemode="drag",
                        tooltip={"placement": "bottom", "always_visible": False},
                        className="year-slider",
                    )
                ],
            ),
        ],
    )


def filter_component(df: pd.DataFrame) -> html.Div:
    years = [int(year) for year in sorted(df["year"].unique())]
    default_start_year = years[0]
    default_end_year = years[-1]

    return html.Div(
        className="filter-panel",
        children=[
            html.Div(
                className="mode-filter-wrap",
                children=[
                    html.Div(
                        className="mode-control",
                        children=[
                            html.Label("Mode", className="filter-label"),
                            dcc.RadioItems(
                                id=MODE_FILTER_ID,
                                options=[
                                    {"label": "Single", "value": "single"},
                                    {"label": "Compare", "value": "compare"},
                                ],
                                value="compare",
                                className="mode-filter",
                                inputClassName="mode-input",
                                labelClassName="mode-option",
                            ),
                        ],
                    ),
                    html.Div(
                        id="compare-count-control",
                        className="compare-count-control",
                        style={"display": "none"},
                        children=[
                            html.Label("Maps", className="filter-label"),
                            dcc.RadioItems(
                                id=COMPARE_COUNT_FILTER_ID,
                                options=[
                                    {"label": "2", "value": 2},
                                    {"label": "3", "value": 3},
                                    {"label": "4", "value": 4},
                                ],
                                value=3,
                                className="compare-count-filter",
                                inputClassName="compare-count-input",
                                labelClassName="compare-count-option",
                            ),
                        ],
                    ),
                    html.Div(
                        id=SINGLE_YEAR_MODE_CONTROL_ID,
                        className="single-year-mode-control",
                        children=[
                            html.Label("Year", className="filter-label"),
                            dcc.RadioItems(
                                id=SINGLE_YEAR_MODE_FILTER_ID,
                                options=[
                                    {"label": "Range", "value": "range"},
                                    {"label": "Single Year", "value": "slider"},
                                ],
                                value="range",
                                className="single-year-mode-filter",
                                inputClassName="single-year-mode-input",
                                labelClassName="single-year-mode-option",
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="year-ranges",
                children=[
                    single_year_slider_row(years, default_start_year),
                    *[
                        year_range_row(
                            row_index,
                            years,
                            default_start_year,
                            default_end_year,
                        )
                        for row_index in range(4)
                    ],
                ],
            ),
            html.Div(
                id=YEAR_RANGE_ERROR_ID,
                className="year-range-error",
                style={"display": "none"},
            ),
            html.Button(
                "Apply",
                id=APPLY_FILTERS_BUTTON_ID,
                n_clicks=0,
                className="apply-button",
            ),
        ],
    )
