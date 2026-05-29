import argparse
from pathlib import Path

import pandas as pd

try:
    from scripts.unique import COUNTRY_ISO3_BY_NAME
    from scripts.preprocess_data import (
        remove_international,
        correct_country_names,
    )
except ModuleNotFoundError:
    from unique import COUNTRY_ISO3_BY_NAME
    from preprocess_data import (
        remove_international,
        correct_country_names,
    )


INPUT_COLUMNS = [
    "iyear",
    "country",
    "country_txt",
    "attacktype1_txt",
    "targtype1_txt",
]


def add_country_iso3_column(
    df: pd.DataFrame,
    country_col: str = "country_txt",
    iso_col: str = "country_iso_3",
) -> pd.DataFrame:
    mapped_df = df.copy()
    mapped_df[iso_col] = mapped_df[country_col].map(COUNTRY_ISO3_BY_NAME)

    missing_countries = sorted(
        mapped_df.loc[mapped_df[iso_col].isna(), country_col].dropna().unique()
    )

    if missing_countries:
        raise ValueError(
            "Missing ISO-3 mappings for countries: "
            + ", ".join(missing_countries)
        )

    return mapped_df


def build_sankey_data(df: pd.DataFrame) -> pd.DataFrame:
    sankey_df = (
        df.groupby(
            [
                "year",
                "country",
                "country_txt",
                "country_iso_3",
                "attacktype1_txt",
                "targtype1_txt",
            ],
            dropna=False,
        )
        .size()
        .reset_index(name="n_atk")
    )

    return sankey_df.sort_values(
        [
            "year",
            "country_txt",
            "attacktype1_txt",
            "targtype1_txt",
        ]
    ).reset_index(drop=True)


def process_sankey_data(
    file_path: str,
    output_path: str = "data/sankey_data.csv",
) -> pd.DataFrame:
    df = pd.read_csv(
        file_path,
        encoding="ISO-8859-1",
        low_memory=False,
        usecols=INPUT_COLUMNS,
    )

    df = df.rename(columns={"iyear": "year"})

    df = remove_international(df)
    df = correct_country_names(df)
    df = add_country_iso3_column(df)

    sankey_df = build_sankey_data(df)

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    sankey_df.to_csv(output_file, index=False)

    return sankey_df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preprocess GTD data for Sankey diagram visualization."
    )
    parser.add_argument(
        "--input",
        default="data/globalterrorism_1970_2017.csv",
        help="Path to the raw Global Terrorism Database CSV.",
    )
    parser.add_argument(
        "--output",
        default="data/sankey_data.csv",
        help="Path where the Sankey CSV will be written.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    processed_df = process_sankey_data(
        file_path=args.input,
        output_path=args.output,
    )

    print(
        f"Wrote {len(processed_df)} rows and "
        f"{len(processed_df.columns)} columns to {args.output}"
    )