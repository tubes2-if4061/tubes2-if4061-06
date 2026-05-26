from dash import Dash, Input, Output
import pandas as pd

from .components.map import build_choropleth_map
from .ids import CHOROPLETH_MAP_ID, YEAR_DROPDOWN_ID


def register_callbacks(app: Dash, data: pd.DataFrame) -> None:
    @app.callback(
        Output(CHOROPLETH_MAP_ID, "figure"),
        Input(YEAR_DROPDOWN_ID, "value"),
    )
    def update_map(selected_year: int):
        return build_choropleth_map(data, selected_year)
