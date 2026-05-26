import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List unique countries from the processed terrorism dataset."
    )
    parser.add_argument(
        "--input",
        default="data/data.csv",
        help="Path to processed CSV file.",
    )
    parser.add_argument(
        "--column",
        default="country_txt",
        help="Country column name to use.",
    )
    return parser.parse_args()


def get_unique_countries(input_path: str, column_name: str) -> list[str]:
    df = pd.read_csv(input_path, usecols=[column_name])
    values = df[column_name].dropna().astype(str).str.strip()
    values = values[values != ""]
    return sorted(values.unique())


def main() -> None:
    args = parse_args()
    input_file = Path(args.input)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    unique_countries = get_unique_countries(str(input_file), args.column)

    print("Unique countries:")
    print("[")
    for i, country in enumerate(unique_countries):
        print(f'"{country}"', end="")
        if i == 0:
            print("\n", end="")
        else:
            print(",\n", end="")
    print("]")
    print(f"Total unique countries: {len(unique_countries)}")


if __name__ == "__main__":
    main()
