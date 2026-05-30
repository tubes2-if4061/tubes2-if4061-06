from dash import dcc, html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Figure
from typing import List, Tuple

from ..ids import (
    COMPARE_MAPS_CONTAINER_ID,
    COMPARE_MAP_VIEW_TOGGLE_ID,
    SINGLE_MAPS_CONTAINER_ID,
    SINGLE_MAP_VIEW_TOGGLE_ID,
)


ATTACK_CATEGORY_COLORS = {
    "≥1000": "#cb181d",
    "100-999": "#fb6a4a",
    "10-99": "#fcae91",
    "<10": "#ffe5dc",
}
ATTACK_CATEGORY_ORDER = list(ATTACK_CATEGORY_COLORS.keys())
UNREGISTERED_COUNTRY_COLOR = "#e7e8e8"


def map_view_toggle(toggle_id: str, default_view: str) -> html.Div:
    return html.Div(
        className="map-view-control",
        children=[
            html.Span("Tampilan", className="map-view-control-label"),
            dcc.RadioItems(
                id=toggle_id,
                options=[
                    {"label": "Globe", "value": "globe"},
                    {"label": "Peta", "value": "choropleth"},
                ],
                value=default_view,
                className="map-view-toggle",
                inputClassName="map-view-input",
                labelClassName="map-view-option",
            ),
        ],
    )


def map_stage(
    container_id: str,
    toggle_id: str,
    default_view: str,
    show_toggle: bool = True,
) -> html.Div:
    return html.Div(
        className="maps-stage",
        children=[
            map_view_toggle(toggle_id, default_view) if show_toggle else None,
            html.Div(id=container_id, className="maps-container"),
        ],
    )


def single_map_component() -> html.Div:
    return html.Div(
        className="mode-map-panel single-map-section",
        children=[
            html.Div(
                className="section-heading map-heading-row",
                children=[
                    html.Div(
                        className="map-heading-copy",
                        children=[
                            html.H2("Globe Interaktif", className="section-title"),
                            html.P(
                                "Klik pada negara di peta untuk melihat detail",
                                className="section-subtitle map-click-hint",
                            ),
                        ],
                    ),
                    map_view_toggle(SINGLE_MAP_VIEW_TOGGLE_ID, "globe"),
                ],
            ),
            map_stage(
                SINGLE_MAPS_CONTAINER_ID,
                SINGLE_MAP_VIEW_TOGGLE_ID,
                "globe",
                show_toggle=False,
            ),
        ],
    )


def compare_map_component() -> html.Div:
    return html.Div(
        className="mode-map-panel compare-map-section",
        children=[
            html.Div(
                className="section-heading compare-map-heading-row",
                children=[
                    html.Div(
                        className="compare-map-heading-copy",
                        children=[
                            html.H2("Peta Perbandingan", className="section-title"),
                        ],
                    ),
                    map_view_toggle(COMPARE_MAP_VIEW_TOGGLE_ID, "choropleth"),
                ],
            ),
            map_stage(
                COMPARE_MAPS_CONTAINER_ID,
                COMPARE_MAP_VIEW_TOGGLE_ID,
                "choropleth",
                show_toggle=False,
            ),
        ],
    )


def attack_legend() -> html.Div:
    legend_items = [
        ("Tidak ada data", UNREGISTERED_COUNTRY_COLOR),
        *reversed(list(ATTACK_CATEGORY_COLORS.items())),
    ]

    return html.Div(
        className="map-legend",
        children=[
            html.Div("Kategori Jumlah Serangan", className="map-legend-title"),
            *[
                html.Div(
                    className="map-legend-item",
                    children=[
                        html.Span(
                            className="map-legend-swatch",
                            style={"backgroundColor": color},
                        ),
                        html.Span(label),
                    ],
                )
                for label, color in legend_items
            ],
        ],
    )


def attack_category(n_atk: int) -> str:
    if n_atk >= 1000:
        return "≥1000"
    if n_atk >= 100:
        return "100-999"
    if n_atk >= 10:
        return "10-99"
    return "<10"


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
        custom_data=["n_atk"],
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
    figure.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Total Serangan: %{customdata[0]:,}<extra></extra>",
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


def build_country_sankey(
    data: pd.DataFrame,
    country_name: str | None,
    start_year: int,
    end_year: int,
    height: int = 500,
) -> Figure:
    range_start = min(start_year, end_year)
    range_end = max(start_year, end_year)

    def empty_sankey_figure(message: str) -> Figure:
        figure = go.Figure()
        figure.add_annotation(
            text=message,
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            align="center",
            font={"size": 15, "color": "#e0e0e0"},
        )
        figure.update_layout(
            font=dict(size=12, color="#f2f0ee"),
            paper_bgcolor="rgba(0, 0, 0, 0)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            height=height,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis={"visible": False},
            yaxis={"visible": False},
        )
        return figure

    filtered_data = data[
        (data["year"] >= range_start)
        & (data["year"] <= range_end)
    ]
    root_label = country_name or "Semua Negara"

    if country_name:
        country_data = filtered_data[filtered_data["country_txt"] == country_name]
    else:
        country_data = filtered_data

    if len(country_data) == 0:
        return empty_sankey_figure(
            f"Tidak ada data untuk {root_label}<br>pada periode {range_start}-{range_end}."
        )

    source = []
    target = []
    value = []

    if "attacktype1_txt" in country_data.columns and "targtype1_txt" in country_data.columns:
        sankey_data = country_data.groupby(["attacktype1_txt", "targtype1_txt"], as_index=False)["n_atk"].sum()
        attack_types = sankey_data["attacktype1_txt"].unique().tolist()
        target_types = sankey_data["targtype1_txt"].unique().tolist()

        nodes = [root_label] + attack_types + target_types

        for _, row in sankey_data.iterrows():
            source.append(nodes.index(root_label))
            target.append(nodes.index(row["attacktype1_txt"]))
            value.append(row["n_atk"])

        for _, row in sankey_data.iterrows():
            source.append(nodes.index(row["attacktype1_txt"]))
            target.append(nodes.index(row["targtype1_txt"]))
            value.append(row["n_atk"])
    else:
        
        attack_cols = [c for c in country_data.columns if c.startswith("attacktype_") and c.endswith("_cnt")]
        target_cols = [c for c in country_data.columns if c.startswith("targettype_") and c.endswith("_cnt")]

        attack_sums = country_data[attack_cols].sum() if attack_cols else pd.Series(dtype=float)
        target_sums = country_data[target_cols].sum() if target_cols else pd.Series(dtype=float)

        attack_labels = [c.replace("attacktype_", "").replace("_cnt", "").replace("_", " ").title() for c in attack_sums.index]
        target_labels = [c.replace("targettype_", "").replace("_cnt", "").replace("_", " ").title() for c in target_sums.index]

        attack_types = attack_labels
        target_types = target_labels

        nodes = [root_label] + attack_labels + target_labels

        total_attack = attack_sums.sum() if not attack_sums.empty else 0
        total_target = target_sums.sum() if not target_sums.empty else 0

        # country -> attack
        for idx, cnt in enumerate(attack_sums.values):
            if cnt <= 0:
                continue
            source.append(nodes.index(root_label))
            target.append(nodes.index(attack_labels[idx]))
            value.append(float(cnt))

        if total_target > 0 and total_attack > 0:
            for t_idx, t_cnt in enumerate(target_sums.values):
                for a_idx, a_cnt in enumerate(attack_sums.values):
                    if a_cnt <= 0:
                        continue
                    link_val = float(t_cnt) * (float(a_cnt) / float(total_attack))
                    if link_val > 0:
                        source.append(nodes.index(attack_labels[a_idx]))
                        target.append(nodes.index(target_labels[t_idx]))
                        value.append(link_val)
    
    sankey_dict = {}
    for s, t, v in zip(source, target, value):
        key = (s, t)
        sankey_dict[key] = sankey_dict.get(key, 0) + v
    
    source = [k[0] for k in sankey_dict.keys()]
    target = [k[1] for k in sankey_dict.keys()]
    value = list(sankey_dict.values())
    hover_value = [int(round(link_value)) for link_value in value]

    if not value:
        return empty_sankey_figure(
            f"Tidak ada data untuk {root_label}<br>pada periode {range_start}-{range_end}."
        )
    
    node_colors = []
    for node in nodes:
        if node == root_label:
            node_colors.append("rgba(203, 24, 29, 0.8)")  # Red for country
        elif node in attack_types:
            node_colors.append("rgba(251, 106, 74, 0.8)")  # Orange for attack types
        else:
            node_colors.append("rgba(252, 174, 145, 0.8)")  # Light orange for targets
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=nodes,
            color=node_colors,
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Total arus masuk: %{value:,}<br>"
                "Total arus keluar: %{value:,}"
                "<extra></extra>"
            ),
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color="rgba(200, 200, 200, 0.4)",
            customdata=hover_value,
            hovertemplate=(
                "<b>%{source.label}</b> ke <b>%{target.label}</b><br>"
                "Jumlah serangan: %{customdata:,}"
                "<extra></extra>"
            ),
        )
    )])
    
    fig.update_layout(
        title=f"Distribusi Serangan di {root_label}",
        font=dict(size=12, color="#f2f0ee"),
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        height=height,
        margin=dict(l=0, r=0, t=40, b=0),
    )
    
    return fig


def country_detail_component(
    country_name: str,
    total_attacks: int,
    total_kill: int,
    total_wound: int,
    organizations: List[Tuple[str, int]],
) -> html.Div:
    """Create a detail card showing country information"""
    total_organizations = len(organizations)
    metrics = [
        ("Total Serangan", total_attacks),
        ("Jumlah Kematian", total_kill),
        ("Jumlah Terluka", total_wound),
    ]

    return html.Div(
        className="country-detail-card",
        children=[
            html.Div(
                className="detail-header",
                children=[
                    html.Div(
                        children=[
                            html.Div("Negara", className="detail-eyebrow"),
                            html.H3(country_name, className="country-name"),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="detail-metric-row",
                children=[
                    html.Div(
                        className="detail-metric-card",
                        children=[
                            html.Span(label, className="detail-metric-label"),
                            html.Strong(f"{value:,}", className="detail-metric-value"),
                        ],
                    )
                    for label, value in metrics
                ],
            ),
            html.Div(
                className="detail-body",
                children=[
                    html.Div(
                        className="detail-section",
                        children=[
                            html.Div(
                                className="detail-section-header",
                                children=[
                                    html.H4(
                                        f"{total_organizations:,} Organisasi Teroris Terlibat",
                                        className="detail-section-title",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="org-list",
                                children=[
                                    html.Div(
                                        className="org-row",
                                        title=org,
                                        children=[
                                            html.Span(org, className="org-name"),
                                            html.Span(f"{count:,}", className="org-count"),
                                        ],
                                    )
                                    for org, count in organizations
                                ] or [
                                    html.Div(
                                        "Tidak ada data organisasi",
                                        className="empty-org-message",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def no_data_country_detail_component(
    country_name: str,
    start_year: int,
    end_year: int,
) -> html.Div:
    period_label = str(start_year) if start_year == end_year else f"{start_year}-{end_year}"

    return html.Div(
        className="country-detail-card country-detail-empty-card",
        children=[
            html.Div(
                className="detail-header",
                children=[
                    html.Div(
                        children=[
                            html.Div("Negara", className="detail-eyebrow"),
                            html.H3(country_name, className="country-name"),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="no-data-detail-panel",
                children=[
                    html.Div("Tidak ada data", className="no-data-detail-title"),
                    html.P(
                        f"Tidak ada serangan tercatat untuk periode {period_label}.",
                        className="no-data-detail-message",
                    ),
                ],
            ),
        ],
    )


def build_country_detail_content(
    data: pd.DataFrame,
    country_name: str,
    start_year: int,
    end_year: int,
) -> html.Div:
    """Build the country detail sidebar content."""
    start_year = int(start_year)
    end_year = int(end_year)
    range_start = min(start_year, end_year)
    range_end = max(start_year, end_year)
    
    # Get country data
    country_data = data[
        (data["country_txt"] == country_name)
        & (data["year"] >= range_start)
        & (data["year"] <= range_end)
    ]
    
    if len(country_data) == 0:
        return html.Div(
            className="graph2-content",
            children=[
                no_data_country_detail_component(
                    country_name,
                    range_start,
                    range_end,
                ),
            ],
        )
    
    total_attacks = int(country_data["n_atk"].sum())
    total_kill = int(country_data["n_kill"].sum()) if "n_kill" in country_data.columns else 0
    total_wound = int(country_data["n_wound"].sum()) if "n_wound" in country_data.columns else 0
    
    organizations: List[Tuple[str, int]] = []
    if "gname_concat" in country_data.columns:
        all_orgs = []
        for val in country_data["gname_concat"].dropna().astype(str):
            parts = [p.strip() for p in val.split(",") if p.strip()]
            all_orgs.extend(parts)
        if all_orgs:
            org_counts = pd.Series(all_orgs).value_counts()

            organizations = [(str(idx), int(val)) for idx, val in org_counts.items()]

    return html.Div(
        className="graph2-content",
        children=[
            country_detail_component(
                country_name,
                total_attacks,
                total_kill,
                total_wound,
                organizations,
            ),
        ],
    )


build_graph2_content = build_country_detail_content

def get_top_5_attack_types_data(
    data: pd.DataFrame,
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    range_start = min(start_year, end_year)
    range_end = max(start_year, end_year)

    filtered_data = data[
        (data["year"] >= range_start)
        & (data["year"] <= range_end)
    ]

    attack_cols = [col for col in data.columns if col.startswith("attacktype_")]

    yearly_data = filtered_data.groupby("year")[attack_cols].sum().reset_index()

    total_counts = yearly_data[attack_cols].sum().sort_values(ascending=False)
    top_5_cols = total_counts.head(5).index.tolist()

    plot_data = yearly_data[["year"] + top_5_cols]

    long_data = plot_data.melt(
        id_vars=["year"],
        value_vars=top_5_cols,
        var_name="Attack Type",
        value_name="n_atk"
    )

    long_data["Attack Type"] = (
        long_data["Attack Type"]
        .str.replace("attacktype_", "")
        .str.replace("_cnt", "")
        .str.replace("_", " ")
        .str.title()
    )
    
    return long_data


def line_chart_legend_layout(title: str, legend_below: bool) -> dict:
    if legend_below:
        return {
            "orientation": "h",
            "yanchor": "top",
            "y": -0.34,
            "xanchor": "left",
            "x": 0,
            "font": {"size": 11},
            "title": {"text": title},
        }

    return {
        "orientation": "v",
        "yanchor": "top",
        "y": 1,
        "xanchor": "left",
        "x": 1.02,
        "font": {"size": 11},
        "title": {"text": title},
    }


def line_chart_margin(legend_below: bool) -> dict:
    if legend_below:
        return {"l": 44, "r": 8, "t": 28, "b": 112}
    return {"l": 44, "r": 170, "t": 28, "b": 54}

def build_top_5_attack_type_line_graph(
    data: pd.DataFrame,
    year_ranges: list[tuple[int, int]],
    legend_below: bool = False,
) -> Figure:
    min_year = int(data["year"].min())
    max_year = int(data["year"].max())
    plot_data = get_top_5_attack_types_data(data, min_year, max_year)

    figure = px.line(
        plot_data,
        x="year",
        y="n_atk",
        color="Attack Type",
        labels={
            "n_atk": "Jumlah Serangan", 
            "year": "Tahun", 
            "Attack Type": "Jenis Serangan"
        },
    )

    figure.update_traces(
        hovertemplate="<b>%{y:,}</b> serangan<extra></extra>"
    )

    colors = ["rgba(255, 99, 132, 0.2)", "rgba(54, 162, 235, 0.2)", "rgba(255, 206, 86, 0.2)", "rgba(75, 192, 192, 0.2)"]

    for index, (start_year, end_year) in enumerate(year_ranges):
        if start_year == end_year:
            x_start = start_year - 0.4
            x_end = end_year + 0.4
        else:
            x_start = start_year
            x_end = end_year

        figure.add_vrect(
            x0=x_start, 
            x1=x_end, 
            fillcolor=colors[index % len(colors)],
            opacity=0.5, 
            layer="below", 
            line_width=1, 
            line_dash="dash",
            annotation_text=f"RANGE {index + 1}",
            annotation_position="top left"
        )

    if year_ranges:
        all_selected_years = [year for range_tuple in year_ranges for year in range_tuple]
        
        zoom_min = min(all_selected_years) - 2
        zoom_max = max(all_selected_years) + 2
        
        zoom_min = max(zoom_min, min_year)
        zoom_max = min(zoom_max, max_year)
    else:
        zoom_min = min_year
        zoom_max = max_year

    zoomed_data = plot_data[
        (plot_data["year"] >= zoom_min) & 
        (plot_data["year"] <= zoom_max)
    ]

    if not zoomed_data.empty:
        max_y_in_view = zoomed_data["n_atk"].max()
        y_axis_max = max_y_in_view * 1.10 
    else:
        y_axis_max = None

    window_size = zoom_max - zoom_min
    dynamic_dtick = 1 if window_size <= 20 else 2

    figure.update_layout(
        autosize=True,
        legend=line_chart_legend_layout("Jenis Serangan", legend_below),
        font={"family": "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif", "color": "#e0e0e0"},
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        margin=line_chart_margin(legend_below),
        xaxis={
            "range": [zoom_min, zoom_max],
            "showgrid": True,
            "gridcolor": "rgba(255, 255, 255, 0.05)",
            "gridwidth": 1,
            "griddash": "dot", 
            "dtick": dynamic_dtick, 
            "tickangle": -45,
            "automargin": True,
        },
        yaxis={"gridcolor": "rgba(255, 255, 255, 0.1)",
               "range": [0, y_axis_max],
               "zeroline": False,
               "automargin": True},
        hovermode="x unified", 
        hoverlabel={
            "bgcolor": "rgba(26, 26, 26, 0.85)",
            "bordercolor": "rgba(255, 255, 255, 0.2)",
            "font_size": 12,
            "font_family": "system-ui"
        }
    )

    return figure

def get_top_5_target_types_data(
    data: pd.DataFrame,
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    range_start = min(start_year, end_year)
    range_end = max(start_year, end_year)

    filtered_data = data[
        (data["year"] >= range_start)
        & (data["year"] <= range_end)
    ]

    target_cols = [col for col in data.columns if col.startswith("targettype_")]

    yearly_data = filtered_data.groupby("year")[target_cols].sum().reset_index()

    total_counts = yearly_data[target_cols].sum().sort_values(ascending=False)
    top_5_cols = total_counts.head(5).index.tolist()

    plot_data = yearly_data[["year"] + top_5_cols]

    long_data = plot_data.melt(
        id_vars=["year"],
        value_vars=top_5_cols,
        var_name="Target Type",
        value_name="n_atk"
    )

    long_data["Target Type"] = (
        long_data["Target Type"]
        .str.replace("targettype_", "")
        .str.replace("_cnt", "")
        .str.replace("_", " ")
        .str.title()
    )
    
    return long_data

def build_top_5_target_type_line_graph(
    data: pd.DataFrame,
    year_ranges: list[tuple[int, int]],
    legend_below: bool = False,
) -> Figure:
    min_year = int(data["year"].min())
    max_year = int(data["year"].max())
    plot_data = get_top_5_target_types_data(data, min_year, max_year)

    figure = px.line(
        plot_data,
        x="year",
        y="n_atk",
        color="Target Type",
        labels={
            "n_atk": "Jumlah Serangan", 
            "year": "Tahun", 
            "Target Type": "Jenis Target"
        },
    )

    figure.update_traces(
        hovertemplate="<b>%{y:,}</b> serangan<extra></extra>"
    )

    colors = ["rgba(255, 99, 132, 0.2)", "rgba(54, 162, 235, 0.2)", "rgba(255, 206, 86, 0.2)", "rgba(75, 192, 192, 0.2)"]

    for index, (start_year, end_year) in enumerate(year_ranges):
        if start_year == end_year:
            x_start = start_year - 0.4
            x_end = end_year + 0.4
        else:
            x_start = start_year
            x_end = end_year

        figure.add_vrect(
            x0=x_start, 
            x1=x_end, 
            fillcolor=colors[index % len(colors)],
            opacity=0.5, 
            layer="below", 
            line_width=1, 
            line_dash="dash",
            annotation_text=f"RANGE {index + 1}",
            annotation_position="top left"
        )

    if year_ranges:
        all_selected_years = [year for range_tuple in year_ranges for year in range_tuple]
        
        zoom_min = min(all_selected_years) - 2
        zoom_max = max(all_selected_years) + 2
        
        zoom_min = max(zoom_min, min_year)
        zoom_max = min(zoom_max, max_year)
    else:
        zoom_min = min_year
        zoom_max = max_year

    zoomed_data = plot_data[
        (plot_data["year"] >= zoom_min) & 
        (plot_data["year"] <= zoom_max)
    ]
    
    if not zoomed_data.empty:
        max_y_in_view = zoomed_data["n_atk"].max()
        y_axis_max = max_y_in_view * 1.10 
    else:
        y_axis_max = None

    window_size = zoom_max - zoom_min
    dynamic_dtick = 1 if window_size <= 20 else 2

    figure.update_layout(
        autosize=True,
        legend=line_chart_legend_layout("Jenis Target", legend_below),
        font={"family": "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif", "color": "#e0e0e0"},
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        margin=line_chart_margin(legend_below),
        xaxis={
            "range": [zoom_min, zoom_max],
            "showgrid": True,
            "gridcolor": "rgba(255, 255, 255, 0.05)",
            "gridwidth": 1,
            "griddash": "dot", 
            "dtick": dynamic_dtick, 
            "tickangle": -45,
            "automargin": True,
        },
        yaxis={"gridcolor": "rgba(255, 255, 255, 0.1)",
               "range": [0, y_axis_max],
               "zeroline": False,
               "automargin": True},
        hovermode="x unified", 
        hoverlabel={
            "bgcolor": "rgba(26, 26, 26, 0.85)",
            "bordercolor": "rgba(255, 255, 255, 0.2)",
            "font_size": 12,
            "font_family": "system-ui"
        }
    )

    return figure
