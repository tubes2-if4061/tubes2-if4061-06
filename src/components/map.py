import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure


def build_choropleth_map(data: pd.DataFrame, selected_year: int) -> Figure:
    filtered_data = data[data["year"] == selected_year]

    return px.choropleth(
        filtered_data,
        locations="iso_alpha",
        color="pop",
        hover_name="country",
        projection="natural earth",
        title=f"Contoh Choropleth Tahun {selected_year}",
    )
