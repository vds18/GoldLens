
from pathlib import Path

import pandas as pd

# --------------------------------------------------
# PATHS AND CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "historical_gold_download.csv"
OUTPUT_FILE = PROCESSED_DIR / "historical_gold.csv"

TARGET_SYMBOLS = {
    "GOLDM",
    "GOLDTEN",
    "GOLDGUINEA",
    "GOLDPETAL",
}

DATE_FORMATS = [
    "%d %b %Y",   # 13 Oct 2026
    "%d-%m-%Y",   # 13-10-2026
    "%Y-%m-%d",   # 2026-10-13
    "%d/%m/%Y",   # 13/10/2026
    "%d-%b-%Y",   # 13-Oct-2026
    "%d %B %Y",   # 13 October 2026
]

EXPIRY_FORMATS = [
    "%d%b%Y",     # 30OCT2026
    "%d %b %Y",
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%d-%b-%Y",
    "%d %B %Y",
]


# --------------------------------------------------
# DATE PARSING
# --------------------------------------------------

def parse_dates(series, formats):
    """Parse known date formats, then try pandas inference."""
    values = series.astype("string").str.strip()

    # Remove surrounding quotation marks, if present.
    values = values.str.strip('"').str.strip("'")

    parsed = pd.Series(
        pd.NaT,
        index=series.index,
        dtype="datetime64[ns]",
    )

    for fmt in formats:
        remaining = parsed.isna() & values.notna()

        if not remaining.any():
            break

        parsed.loc[remaining] = pd.to_datetime(
            values.loc[remaining],
            format=fmt,
            errors="coerce",
        )

    # Fallback for any additional date formats.
    remaining = parsed.isna() & values.notna()

    if remaining.any():
        parsed.loc[remaining] = pd.to_datetime(
            values.loc[remaining],
            errors="coerce",
            dayfirst=True,
        )

    return parsed


# --------------------------------------------------
# MAIN DATA CLEANING PIPELINE
# --------------------------------------------------

def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found:\n{INPUT_FILE}\n\n"
            "Run combine_bhavcopy.py first."
        )

    df = pd.read_csv(INPUT_FILE, low_memory=False)
    df.columns = df.columns.astype(str).str.strip()

    input_rows = len(df)

    print("\nGOLDLENS — HISTORICAL DATA PROCESSING")
    print("=" * 55)
    print(f"Input file: {INPUT_FILE}")
    print(f"Input rows: {input_rows:,}")

    # Validate required columns.
    required_columns = {
        "Date",
        "Instrument Name",
        "Symbol",
        "Expiry Date",
        "Close",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Normalize contract and instrument text.
    df["Symbol"] = (
        df["Symbol"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    df["Instrument Name"] = (
        df["Instrument Name"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    # Parse dates.
    df["Date"] = parse_dates(df["Date"], DATE_FORMATS)
    df["Expiry Date"] = parse_dates(
        df["Expiry Date"],
        EXPIRY_FORMATS,
    )

    # Filter the four target gold futures.
    df = df[
        (df["Instrument Name"] == "FUTCOM")
        & df["Symbol"].isin(TARGET_SYMBOLS)
    ].copy()

    if df.empty:
        raise ValueError(
            "No target gold futures were found. Check the instrument "
            "names and symbols in historical_gold_download.csv."
        )

    rows_after_filter = len(df)

    # Convert market fields to numeric.
    numeric_columns = [
        "Strike Price",
        "Open",
        "High",
        "Low",
        "Close",
        "Previous Close",
        "Volume(Lots)",
        "Volume(In 000's)",
        "Value(Lacs)",
        "Open Interest(Lots)",
    ]

    for column in numeric_columns:
        if column in df.columns:
            cleaned_values = (
                df[column]
                .astype("string")
                .str.replace(",", "", regex=False)
                .str.strip()
            )

            df[column] = pd.to_numeric(
                cleaned_values,
                errors="coerce",
            )

    # Count invalid values before removing invalid rows.
    invalid_dates = int(df["Date"].isna().sum())
    invalid_expiries = int(df["Expiry Date"].isna().sum())
    invalid_closes = int(df["Close"].isna().sum())

    # Remove records that cannot support time-series analysis.
    df = df.dropna(
        subset=["Date", "Expiry Date", "Close"]
    )

    df = df[df["Close"] > 0].copy()

    if df.empty:
        raise ValueError(
            "No valid rows remain after date and closing-price cleaning."
        )

    # Remove exact duplicate rows first.
    before_exact_dedup = len(df)
    df = df.drop_duplicates()
    exact_duplicates_removed = before_exact_dedup - len(df)

    # A contract record is identified by trading date, symbol and expiry.
    # If duplicates remain, keep the last source record.
    before_contract_dedup = len(df)

    df = df.drop_duplicates(
        subset=["Date", "Symbol", "Expiry Date"],
        keep="last",
    )

    contract_duplicates_removed = before_contract_dedup - len(df)

    # Sort chronologically.
    df = df.sort_values(
        ["Date", "Symbol", "Expiry Date"]
    ).reset_index(drop=True)

    if df.empty:
        raise ValueError("The cleaned dataset is empty.")

    # Save cleaned data without modifying source files.
    df.to_csv(
        OUTPUT_FILE,
        index=False,
        date_format="%Y-%m-%d",
    )

    # Validation statistics.
    valid_dates = sorted(
        df["Date"].dt.strftime("%Y-%m-%d").unique().tolist()
    )

    symbols_found = sorted(
        df["Symbol"].dropna().unique().tolist()
    )

    missing_symbols = sorted(
        TARGET_SYMBOLS - set(symbols_found)
    )

    # Report dates with the number of gold contract records.
    rows_per_date = (
        df.groupby(df["Date"].dt.strftime("%Y-%m-%d"))
        .size()
        .to_dict()
    )

    # --------------------------------------------------
    # VALIDATION REPORT
    # --------------------------------------------------

    print("\nGOLDLENS — HISTORICAL DATA REPORT")
    print("=" * 55)
    print(f"Input rows: {input_rows:,}")
    print(f"Gold rows after filtering: {rows_after_filter:,}")
    print(f"Valid gold futures rows: {len(df):,}")

    print(f"Exact duplicate rows removed: {exact_duplicates_removed:,}")
    print(
        "Duplicate date-symbol-expiry records removed: "
        f"{contract_duplicates_removed:,}"
    )

    print(f"Rows with invalid dates: {invalid_dates:,}")
    print(f"Rows with invalid expiries: {invalid_expiries:,}")
    print(f"Rows with invalid closes: {invalid_closes:,}")

    print(f"\nUnique trading dates: {len(valid_dates)}")

    if valid_dates:
        print(f"Date range: {valid_dates[0]} to {valid_dates[-1]}")

    print(f"Symbols found: {', '.join(symbols_found)}")

    if missing_symbols:
        print(f"Missing target symbols: {', '.join(missing_symbols)}")
    else:
        print("Missing target symbols: None")

    print("\nRows per trading date:")

    for trading_date, row_count in rows_per_date.items():
        print(f"  {trading_date}: {row_count} rows")

    print(f"\nSaved cleaned data to:\n{OUTPUT_FILE}")

    if len(valid_dates) < 30:
        print(
            "\nNOTICE: Fewer than 30 trading dates are available. "
            "Anomaly detection and backtesting should be considered "
            "preliminary."
        )

    if invalid_dates > 0:
        print(
            "\nCHECK REQUIRED: Some trading dates could not be parsed. "
            "Inspect the original Date values before trusting the "
            "historical date range."
        )


if __name__ == "__main__":
    main()
