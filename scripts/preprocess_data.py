import argparse
import re
from pathlib import Path

import pandas as pd
try:
    from scripts.unique import COUNTRY_ISO3_BY_NAME
except ModuleNotFoundError:
    from unique import COUNTRY_ISO3_BY_NAME


INPUT_COLUMNS = [
    "iyear",
    "country",
    "country_txt",
    "gname",
    "attacktype1_txt",
    "targtype1_txt",
]

GROUP_COLUMNS = ["year", "country", "country_txt"]

COUNTRY_ID_BY_NAME = {
    "Armenia": 12,
    "Azerbaijan": 16,
    "Belarus": 35,
    "Bosnia and Herzegovina": 28,
    "Cote d'Ivoire": 99,
    "Croatia": 50,
    "Czechia": 54,
    "Democratic Republic of the Congo": 229,
    "Eswatini": 197,
    "Estonia": 64,
    "Georgia": 74,
    "Germany": 75,
    "Kazakhstan": 103,
    "Kosovo": 1003,
    "Kyrgyzstan": 107,
    "Latvia": 109,
    "Lithuania": 115,
    "Moldova": 132,
    "Montenegro": 1002,
    "North Macedonia": 118,
    "Palestine": 155,
    "Republic of the Congo": 47,
    "Russia": 167,
    "Serbia": 1001,
    "Slovakia": 179,
    "Slovenia": 180,
    "Saint Kitts and Nevis": 189,
    "Saint Lucia": 190,
    "Tajikistan": 202,
    "Timor-Leste": 347,
    "Turkmenistan": 210,
    "Ukraine": 214,
    "Uzbekistan": 219,
    "Vanuatu": 220,
    "Vietnam": 223,
    "Yemen": 228,
    "Zimbabwe": 231,
}

ONE_TO_ONE_COUNTRY_RENAMES = {
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Czech Republic": "Czechia",
    "East Germany (GDR)": "Germany",
    "East Timor": "Timor-Leste",
    "Ivory Coast": "Cote d'Ivoire",
    "Macedonia": "North Macedonia",
    "New Hebrides": "Vanuatu",
    "North Yemen": "Yemen",
    "People's Republic of the Congo": "Republic of the Congo",
    "Rhodesia": "Zimbabwe",
    "Slovak Republic": "Slovakia",
    "South Vietnam": "Vietnam",
    "South Yemen": "Yemen",
    "St. Kitts and Nevis": "Saint Kitts and Nevis",
    "St. Lucia": "Saint Lucia",
    "Swaziland": "Eswatini",
    "West Bank and Gaza Strip": "Palestine",
    "West Germany (FRG)": "Germany",
    "Zaire": "Democratic Republic of the Congo",
}

ONE_TO_MANY_COUNTRY_SPLITS = {
    "Czechoslovakia": ["Czechia", "Slovakia"],
    "Serbia-Montenegro": ["Serbia", "Montenegro"],
    "Soviet Union": [
        "Russia",
        "Ukraine",
        "Belarus",
        "Estonia",
        "Latvia",
        "Lithuania",
        "Georgia",
        "Armenia",
        "Azerbaijan",
        "Kazakhstan",
        "Uzbekistan",
        "Turkmenistan",
        "Kyrgyzstan",
        "Tajikistan",
        "Moldova",
    ],
    "Yugoslavia": [
        "Serbia",
        "Croatia",
        "Slovenia",
        "Bosnia and Herzegovina",
        "Montenegro",
        "North Macedonia",
        "Kosovo",
    ],
}


def slugify(value: str) -> str:
    slug = value.lower().replace("&", "and")
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")


def unique_sorted_values(series: pd.Series) -> list[str]:
    values = series.dropna().astype(str).str.strip()
    values = values[values != ""]
    return sorted(values.unique())


def concat_unique_values(series: pd.Series) -> str:
    values = series.dropna().astype(str).str.strip()
    values = values[values != ""]
    values = values[~values.str.lower().isin({"unknown", "null"})]
    return ", ".join(pd.unique(values))


def remove_international(df: pd.DataFrame, country_col: str = "country_txt") -> pd.DataFrame:
    is_international = df[country_col].astype(str).str.strip().str.lower() == "international"
    return df.loc[~is_international].copy()


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


def set_country(df: pd.DataFrame, country_name: str, country_col: str) -> pd.DataFrame:
    df[country_col] = country_name
    df["country"] = COUNTRY_ID_BY_NAME[country_name]
    return df


def correct_country_names(df: pd.DataFrame, country_col: str = "country_txt") -> pd.DataFrame:
    corrected_df = df.copy()

    for old_country, new_country in ONE_TO_ONE_COUNTRY_RENAMES.items():
        mask = corrected_df[country_col] == old_country
        if mask.any():
            corrected_df.loc[mask, country_col] = new_country
            corrected_df.loc[mask, "country"] = COUNTRY_ID_BY_NAME[new_country]

    split_rows = []
    for old_country, new_countries in ONE_TO_MANY_COUNTRY_SPLITS.items():
        mask = corrected_df[country_col] == old_country
        if not mask.any():
            continue

        base_rows = corrected_df.loc[mask]
        corrected_df = corrected_df.loc[~mask]

        for new_country in new_countries:
            new_rows = set_country(base_rows.copy(), new_country, country_col)
            split_rows.append(new_rows)

    if split_rows:
        corrected_df = pd.concat([corrected_df, *split_rows], ignore_index=True)

    corrected_df["country"] = corrected_df["country"].astype("int64")
    return corrected_df


def build_category_columns(
    df: pd.DataFrame,
    category_col: str,
    category_values: list[str],
    prefix: str,
) -> pd.DataFrame:
    counts = (
        df.groupby([*GROUP_COLUMNS, category_col])
        .size()
        .unstack(category_col, fill_value=0)
    )

    for category_value in category_values:
        if category_value not in counts.columns:
            counts[category_value] = 0

    counts = counts[category_values].reset_index()

    category_df = counts[GROUP_COLUMNS].copy()
    count_columns = {}

    for category_value in category_values:
        column_slug = slugify(category_value)
        count_columns[f"{prefix}_{column_slug}_cnt"] = counts[category_value].astype("int64")

    return pd.concat(
        [
            category_df,
            pd.DataFrame(count_columns, index=counts.index),
        ],
        axis=1,
    )


def aggregate_data(df: pd.DataFrame) -> pd.DataFrame:
    attack_type_values = unique_sorted_values(df["attacktype1_txt"])
    target_type_values = unique_sorted_values(df["targtype1_txt"])

    base = (
        df.groupby(GROUP_COLUMNS)
        .agg(
            n_atk=("year", "size"),
            gname_concat=("gname", concat_unique_values),
        )
        .reset_index()
    )

    attack_type_df = build_category_columns(
        df,
        category_col="attacktype1_txt",
        category_values=attack_type_values,
        prefix="attacktype",
    )
    target_type_df = build_category_columns(
        df,
        category_col="targtype1_txt",
        category_values=target_type_values,
        prefix="targettype",
    )

    aggregated_df = base.merge(attack_type_df, on=GROUP_COLUMNS, how="left")
    aggregated_df = aggregated_df.merge(target_type_df, on=GROUP_COLUMNS, how="left")

    count_columns = [column for column in aggregated_df.columns if column.endswith("_cnt")]
    aggregated_df[count_columns] = aggregated_df[count_columns].fillna(0).astype("int64")

    return aggregated_df.sort_values(GROUP_COLUMNS).reset_index(drop=True)


def process_data(file_path: str, output_path: str = "data/data.csv") -> pd.DataFrame:
    df = pd.read_csv(
        file_path,
        encoding="ISO-8859-1",
        low_memory=False,
        usecols=INPUT_COLUMNS,
    )
    df = df.rename(columns={"iyear": "year"})

    df = remove_international(df)
    df = correct_country_names(df)
    aggregated_df = aggregate_data(df)
    aggregated_df = add_country_iso3_column(aggregated_df)

    front_columns = ["year", "country", "country_txt", "country_iso_3", "n_atk", "gname_concat"]
    other_columns = [column for column in aggregated_df.columns if column not in front_columns]
    aggregated_df = aggregated_df[front_columns + other_columns]

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    aggregated_df.to_csv(output_file, index=False)

    return aggregated_df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preprocess the Global Terrorism Database for visualization."
    )
    parser.add_argument(
        "--input",
        default="data/globalterrorism_1970_2017.csv",
        help="Path to the raw Global Terrorism Database CSV.",
    )
    parser.add_argument(
        "--output",
        default="data/data.csv",
        help="Path where the preprocessed CSV will be written.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    RAW_DATA_PATH = "data/globalterrorism_1970_2017.csv"
    OUTPUT_DATA_PATH = "data/data.csv"
    processed_df = process_data(RAW_DATA_PATH, OUTPUT_DATA_PATH)
    print(f"Wrote {len(processed_df)} rows and {len(processed_df.columns)} columns to {OUTPUT_DATA_PATH}")
