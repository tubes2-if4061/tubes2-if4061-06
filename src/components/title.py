from dash import html

def title_component() -> html.Header:
    return html.Header(
        className="dashboard-header dashboard-header-center",
        children=[
            html.Div(
                className="title-block",
                children=[
                    html.H1("Migrasi Teror Global (1970-2017)", className="dashboard-title"),
                    html.P(
                        "Melacak pergeseran geografis dan evolusi serangan terorisme dari tahun 1970 hingga 2017",
                        className="dashboard-subtitle",
                    ),
                ],
            ),
        ],
    )
