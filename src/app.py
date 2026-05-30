from dash import Dash

from .callbacks import register_callbacks
from .config import REMOVE_BODY_MARGIN
from .layout import create_layout
from .utils.data_loader import load_terrorism_data

def create_app() -> Dash:
    app = Dash(__name__)
    data = load_terrorism_data()

    app.index_string = REMOVE_BODY_MARGIN
    app.layout = create_layout(data)
    register_callbacks(app, data)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8050,
        debug=True,
        dev_tools_hot_reload=True,
    )
