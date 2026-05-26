from dash import dcc, html
import pandas as pd

from .components.filter import filter_component
from .components.title import title_component
from .ids import CHOROPLETH_MAP_ID


def create_layout(data: pd.DataFrame) -> html.Div:
    return html.Div(
        children=[
            html.Div(
                children=[
                    title_component(),
                    filter_component(data),
                    dcc.Graph(id=CHOROPLETH_MAP_ID),
                ],
                style={
                    "padding": "0px",
                },
            )
        ],
        style={
            "backgroundColor": "#ffffff",
        },
    )
