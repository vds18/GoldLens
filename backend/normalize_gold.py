
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "historical_gold.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

# Initial specifications from the hackathon problem statement.
# Verify quotation bases against official MCX specifications.

CONTRACTS = {
    "GOLDM": {
        "quoted_grams": 10,
        "purity": 995
    },
    "GOLDTEN": {
        "quoted_grams": 10,
        "purity": 999
    },
    "GOLDGUINEA": {
        "quoted_grams": 8,
        "purity": 999
    },
    "GOLDPETAL": {
        "quoted_grams": 1,
        "purity": 999
    },
}


REFERENCE_GRAMS = 10
REFERENCE_PURITY = 999


def normalize_price(price, quoted_grams, purity):
    """Convert a quoted price to a 10g, 999-purity reference."""
    if pd.isna(price) or price <= 0:
        return float("nan")

    price_per_gram = price / quoted_grams

    return (
        price_per_gram
        * REFERENCE_GRAMS
        * REFERENCE_PURITY
        / purity
    )


def main():
    if not INPUT_FILE.exists():
        print("Gold data not found. Run filter_gold.py first.")
        return

    df = pd.read_csv(INPUT_FILE)

    for col in ["Symbol", "Close"]:
        if col not in df.columns:
            print(f"Required column missing: {col}")
            return

    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

    df["QuotedGrams"] = df["Symbol"].map(
        {symbol: spec["quoted_grams"]
         for symbol, spec in CONTRACTS.items()}
    )

    df["ContractPurity"] = df["Symbol"].map(
        {symbol: spec["purity"]
         for symbol, spec in CONTRACTS.items()}
    )

    df["NormalizedPrice10g"] = df.apply(
        lambda row: normalize_price(
            row["Close"],
            row["QuotedGrams"],
            row["ContractPurity"]
        ),
        axis=1
    )

    df["NormalizationStatus"] = "Needs validation against MCX specs"

    columns = [
        "Date", "Symbol", "Expiry Date", "Close",
        "QuotedGrams", "ContractPurity",
        "NormalizedPrice10g", "NormalizationStatus"
    ]

    result = df[columns].sort_values(
        ["Date", "Symbol", "Expiry Date"]
    )   

    output_file = OUTPUT_DIR / "normalized_gold.csv"
    result.to_csv(output_file, index=False)

    print("\nNormalized gold contract prices:")
    print(result.to_string(index=False))

    print(f"\nSaved to: {output_file}")
    print(
        "\nIMPORTANT: These are provisional normalized values. "
        "Verify each contract's quotation basis before comparing "
        "prices or generating signals."
    )


if __name__ == "__main__":
    main()
