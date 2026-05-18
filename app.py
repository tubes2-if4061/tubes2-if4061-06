from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)

df = px.data.gapminder()

app.layout = html.Div(
    children=[
        html.H1("Migrasi Teror Global Dashboard"),

        dcc.Dropdown(
            id="year-dropdown",
            options=[{"label": year, "value": year} for year in sorted(df["year"].unique())],
            value=2007,
        ),

        dcc.Graph(id="choropleth-map"),
    ],
    style={"padding": "24px"},
)

@app.callback(
    Output("choropleth-map", "figure"),
    Input("year-dropdown", "value"),
)
def update_map(selected_year):
    filtered_df = df[df["year"] == selected_year]

    fig = px.choropleth(
        filtered_df,
        locations="iso_alpha",
        color="pop",
        hover_name="country",
        projection="natural earth",
        title=f"Contoh Choropleth Tahun {selected_year}",
    )

    return fig

if __name__ == "__main__":
    app.run(debug=True)