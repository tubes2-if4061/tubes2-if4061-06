from dash import dcc, html
import pandas as pd

from ..ids import (
    APPLY_FILTERS_BUTTON_ID,
    COMPARE_COUNT_FILTER_ID,
    MODE_FILTER_ID,
    YEAR_RANGE_END_IDS,
    YEAR_RANGE_ROW_IDS,
    YEAR_RANGE_START_IDS,
)


def year_dropdown(dropdown_id: str, years: list[int], value: int) -> dcc.Input:
    return dcc.Input(
        id=dropdown_id,
        type="number",
        min=years[0],
        max=years[-1],
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


def filter_component(df: pd.DataFrame) -> html.Div:
    years = sorted(df["year"].unique())
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
                                value="single",
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
                                value=2,
                                className="compare-count-filter",
                                inputClassName="compare-count-input",
                                labelClassName="compare-count-option",
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="year-ranges",
                children=[
                    year_range_row(
                        row_index,
                        years,
                        default_start_year,
                        default_end_year,
                    )
                    for row_index in range(4)
                ],
            ),
            html.Button(
                "Apply",
                id=APPLY_FILTERS_BUTTON_ID,
                n_clicks=0,
                className="apply-button",
            ),
        ],
    )
