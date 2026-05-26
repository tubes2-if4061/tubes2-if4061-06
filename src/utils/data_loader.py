import pandas as pd


def load_terrorism_data(file_path: str = "data/data.csv") -> pd.DataFrame:
    return pd.read_csv(file_path)
