import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure


ATTACK_CATEGORY_COLORS = {
    ">= 1000": "#cb181d",
    "100-999": "#fb6a4a",
    "10-99": "#fcae91",
    "< 10": "#ffe5dc",
}
ATTACK_CATEGORY_ORDER = list(ATTACK_CATEGORY_COLORS.keys())
UNREGISTERED_COUNTRY_COLOR = "#e7e8e8"


def attack_category(n_atk: int) -> str:
    if n_atk >= 1000:
        return ">= 1000"
    if n_atk >= 100:
        return "100-999"
    if n_atk >= 10:
        return "10-99"
    return "< 10"


def aggregate_attacks_by_country(
    data: pd.DataFrame,
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    range_start = min(start_year, end_year)
    range_end = max(start_year, end_year)

    countries = (
        data[["country_txt", "country_iso_3"]]
        .drop_duplicates()
        .sort_values("country_txt")
    )

    filtered_data = data[
        (data["year"] >= range_start)
        & (data["year"] <= range_end)
    ]

    attacks = (
        filtered_data.groupby(["country_txt", "country_iso_3"], as_index=False)["n_atk"]
        .sum()
    )

    map_data = countries.merge(
        attacks,
        on=["country_txt", "country_iso_3"],
        how="left",
    )
    map_data["n_atk"] = map_data["n_atk"].fillna(0).astype(int)
    map_data["attack_category"] = pd.Categorical(
        map_data["n_atk"].apply(attack_category),
        categories=ATTACK_CATEGORY_ORDER,
        ordered=True,
    )

    return map_data


def build_choropleth_map(
    data: pd.DataFrame,
    start_year: int,
    end_year: int,
    height: int,
    map_view: str = "globe",
) -> Figure:
    range_start = min(start_year, end_year)
    range_end = max(start_year, end_year)
    map_data = aggregate_attacks_by_country(data, range_start, range_end)

    figure = px.choropleth(
        map_data,
        locations="country_iso_3",
        locationmode="ISO-3",
        color="attack_category",
        color_discrete_map=ATTACK_CATEGORY_COLORS,
        category_orders={"attack_category": ATTACK_CATEGORY_ORDER},
        hover_name="country_txt",
        hover_data={
            "country_iso_3": False,
            "attack_category": False,
            "n_atk": ":,",
        },
        projection="orthographic" if map_view == "globe" else "natural earth",
    )

    geos_config = {
        "domain": {"x": [0, 1], "y": [0, 1]},
        "projection_rotation": {"lon": -25, "lat": 18, "roll": 0},
        "showframe": False,
        "showcoastlines": False,
        "showocean": True,
        "oceancolor": "#0b1220",
        "showlakes": True,
        "lakecolor": "#0b1220",
        "showland": True,
        "landcolor": UNREGISTERED_COUNTRY_COLOR,
        "showcountries": True,
        "countrycolor": "rgba(255, 255, 255, 0.18)",
        "bgcolor": "rgba(0, 0, 0, 0)",
    }

    if map_view == "globe":
        geos_config["projection_scale"] = 0.84
    else:
        geos_config["projection_rotation"] = {"lon": 0, "lat": 0, "roll": 0}
        geos_config["showcoastlines"] = True

    figure.update_geos(
        **geos_config,
    )
    figure.update_layout(
        autosize=True,
        height=height,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        showlegend=False,
        font={"family": "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif", "color": "#e0e0e0"},
    )

    return figure
