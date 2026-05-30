from dash import dcc, html
import pandas as pd
from typing import List, Dict

from ..ids import (
    COMPARE_COUNT_FILTER_ID,
    COMPARE_YEAR_SLIDER_IDS,
    COMPARE_YEAR_SLIDER_ROW_IDS,
    COMPARE_YEAR_SLIDER_VALUE_IDS,
    MODE_FILTER_ID,
    PERIOD_CONTROLS_GRID_ID,
    SINGLE_YEAR_MODE_CONTROL_ID,
    SINGLE_YEAR_MODE_FILTER_ID,
    SINGLE_YEAR_SLIDER_ID,
    SINGLE_YEAR_SLIDER_ROW_ID,
    SINGLE_YEAR_SLIDER_VALUE_ID,
    YEAR_RANGE_ERROR_ID,
    YEAR_RANGE_END_IDS,
    YEAR_RANGE_ROW_IDS,
    YEAR_RANGE_START_IDS,
)


DEFAULT_COMPARE_YEAR_RANGES = [
    (1970, 1979),
    (1980, 1989),
    (1990, 1999),
    (2000, 2017),
]
COMPARE_YEAR_RANGE_DEFAULTS = {
    2: [
        (1970, 1999),
        (2000, 2017),
        (1990, 1999),
        (2000, 2017),
    ],
    3: [
        (1970, 1984),
        (1985, 1999),
        (2000, 2017),
        (2000, 2017),
    ],
    4: DEFAULT_COMPARE_YEAR_RANGES,
}
COMPARE_YEAR_DEFAULTS = {
    compare_count: [start_year for start_year, _end_year in year_ranges]
    for compare_count, year_ranges in COMPARE_YEAR_RANGE_DEFAULTS.items()
}


def year_dropdown(dropdown_id: str, years: List[int], value: int) -> dcc.Input:
    return dcc.Input(
        id=dropdown_id,
        type="number",
        step=1,
        value=value,
        className="year-input",
    )


def year_range_row(
    row_index: int,
    years: List[int],
    default_start_year: int,
    default_end_year: int,
    is_visible: bool,
) -> html.Div:
    return html.Div(
        id=YEAR_RANGE_ROW_IDS[row_index],
        className="year-range-row",
        style={"display": "grid"} if is_visible else {"display": "none"},
        children=[
            html.Div(f"Rentang {row_index + 1}", className="range-label"),
            html.Label(
                className="field-label",
                children=[
                    "Awal",
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
                    "Akhir",
                    year_dropdown(
                        YEAR_RANGE_END_IDS[row_index],
                        years,
                        default_end_year,
                    ),
                ],
            ),
        ],
    )


def slider_marks(years: List[int]) -> Dict[int, str]:
    decade_marks = {
        int(year): str(year)
        for year in years
        if year == years[0] or year == years[-1] or year % 10 == 0
    }
    return decade_marks


def slider_percent(year: int, years: List[int]) -> str:
    return f"{((year - years[0]) / (years[-1] - years[0])) * 100}%"


def custom_year_slider(
    slider_id: str,
    value_id: str,
    years: List[int],
    default_year: int,
) -> html.Div:
    marks = slider_marks(years)

    return html.Div(
        className="custom-year-slider",
        children=[
            html.Div(
                className="custom-slider-shell",
                **{
                    "data-slider-min": years[0],
                    "data-slider-max": years[-1],
                    "data-slider-step": 1,
                    "data-slider-input-id": slider_id,
                },
                children=[
                    dcc.Input(
                        id=slider_id,
                        type="range",
                        min=years[0],
                        max=years[-1],
                        step=1,
                        value=default_year,
                        className="custom-slider-input",
                    ),
                    html.Div(
                        str(default_year),
                        id=value_id,
                        className="custom-slider-value",
                        style={"left": slider_percent(default_year, years)},
                    ),
                ],
            ),
            html.Div(
                className="custom-slider-marks",
                children=[
                    html.Span(
                        label,
                        className="custom-slider-mark",
                        style={
                            "left": (
                                f"{((year - years[0]) / (years[-1] - years[0])) * 100}%"
                            )
                        },
                    )
                    for year, label in marks.items()
                ],
            ),
        ],
    )


def single_year_slider_row(years: List[int], default_year: int) -> html.Div:
    return html.Div(
        id=SINGLE_YEAR_SLIDER_ROW_ID,
        className="year-slider-row single-year-slider-row",
        style={"display": "none"},
        children=[
            html.Div("Tahun", className="range-label"),
            html.Div(
                className="year-slider-wrap",
                children=[
                    custom_year_slider(
                        SINGLE_YEAR_SLIDER_ID,
                        SINGLE_YEAR_SLIDER_VALUE_ID,
                        years,
                        default_year,
                    ),
                ],
            ),
        ],
    )


def compare_year_slider_row(
    row_index: int,
    years: List[int],
    default_year: int,
) -> html.Div:
    return html.Div(
        id=COMPARE_YEAR_SLIDER_ROW_IDS[row_index],
        className="year-slider-row compare-year-slider-row",
        style={"display": "none"},
        children=[
            # html.Div(f"Map {row_index + 1}", className="range-label"),
            html.Div(
                className="year-slider-wrap",
                children=[
                    custom_year_slider(
                        COMPARE_YEAR_SLIDER_IDS[row_index],
                        COMPARE_YEAR_SLIDER_VALUE_IDS[row_index],
                        years,
                        default_year,
                    ),
                ],
            ),
        ],
    )


def filter_component(df: pd.DataFrame) -> html.Div:
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
                        style={"display": "grid"},
                        children=[
                            html.Label("JUMLAH PETA", className="filter-label"),
                            dcc.RadioItems(
                                id=COMPARE_COUNT_FILTER_ID,
                                options=[
                                    {"label": "2", "value": 2},
                                    {"label": "3", "value": 3},
                                    {"label": "4", "value": 4},
                                ],
                                value=4,
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
                            html.Label("PEMILIHAN TAHUN", className="filter-label"),
                            dcc.RadioItems(
                                id=SINGLE_YEAR_MODE_FILTER_ID,
                                options=[
                                    {"label": "Rentang", "value": "range"},
                                    {"label": "Slider", "value": "slider"},
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
        ],
    )


def period_controls_component(df: pd.DataFrame) -> html.Div:
    years = [int(year) for year in sorted(df["year"].unique())]
    default_start_year = years[0]

    return html.Div(
        className="period-controls",
        children=[
            html.Div(
                id=PERIOD_CONTROLS_GRID_ID,
                className="year-ranges period-controls-grid period-controls-grid-4",
                children=[
                    single_year_slider_row(years, default_start_year),
                    *[
                        compare_year_slider_row(
                            row_index,
                            years,
                            default_year,
                        )
                        for row_index, default_year in enumerate(
                            COMPARE_YEAR_DEFAULTS[4]
                        )
                    ],
                    *[
                        year_range_row(
                            row_index,
                            years,
                            start_year,
                            end_year,
                            is_visible=True,
                        )
                        for row_index, (start_year, end_year) in enumerate(
                            DEFAULT_COMPARE_YEAR_RANGES
                        )
                    ],
                ],
            ),
            html.Div(
                id=YEAR_RANGE_ERROR_ID,
                className="year-range-error",
                style={"display": "none"},
            ),
        ],
    )
