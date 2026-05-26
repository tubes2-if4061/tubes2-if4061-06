from dash import html
import pandas as pd

from .components.filter import filter_component
from .components.title import title_component
from .ids import MAPS_CONTAINER_ID


def create_layout(data: pd.DataFrame) -> html.Div:
    return html.Div(
        className="app-shell",
        children=[
            html.Div(
                className="dashboard",
                children=[
                    title_component(),
                    filter_component(data),
                    html.Div(id=MAPS_CONTAINER_ID, className="maps-container"),
                ],
            )
        ],
    )
