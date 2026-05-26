import pandas as pd
import plotly.express as px


def load_gapminder_data() -> pd.DataFrame:
    return px.data.gapminder()
