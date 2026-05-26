from dash import dcc
import pandas as pd

from ..ids import YEAR_DROPDOWN_ID


def filter_component(df: pd.DataFrame) -> dcc.Dropdown:
    years = sorted(df["year"].unique())
    default_year = 2007 if 2007 in years else years[-1]

    return dcc.Dropdown(
        id=YEAR_DROPDOWN_ID,
        options=[{"label": year, "value": year} for year in years],
        value=default_year,
    )
