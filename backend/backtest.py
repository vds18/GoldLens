
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "processed" / "normalized_gold.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

TRADES_FILE = OUTPUT_DIR / "backtest_trades.csv"
REPORT_FILE = OUTPUT_DIR / "backtest_report.csv"
OPEN_POSITIONS_FILE = OUTPUT_DIR / "backtest_open_positions.csv"

# Configurable research parameters
WINDOW = 20
MIN_HISTORY = 15
ENTRY_Z = 2.0
EXIT_Z = 0.5

# Illustrative assumption only; validate real costs before interpreting results.
COST_BPS_PER_LEG = 10.0


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Missing {DATA_FILE}. Run normalize_gold.py first."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_FILE)

    required = [
        "Date",
        "Symbol",
        "Expiry Date",
        "NormalizedPrice10g",
    ]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Parse and validate the input.
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Expiry Date"] = pd.to_datetime(
        df["Expiry Date"], errors="coerce"
    )
    df["Symbol"] = df["Symbol"].astype("string").str.strip()
    df["NormalizedPrice10g"] = pd.to_numeric(
        df["NormalizedPrice10g"], errors="coerce"
    )

    df = df.dropna(
        subset=[
            "Date",
            "Expiry Date",
            "Symbol",
            "NormalizedPrice10g",
        ]
    )
    df = df[df["NormalizedPrice10g"] > 0]
    df = df.drop_duplicates(
        subset=["Date", "Symbol", "Expiry Date"],
        keep="last",
    )

    if df.empty:
        raise ValueError("No valid normalized historical prices found.")

    # Pair contracts only when both observation date and expiry match.
    columns = ["Date", "Expiry Date", "Symbol", "NormalizedPrice10g"]

    left = df[columns].rename(
        columns={
            "Symbol": "ContractA",
            "NormalizedPrice10g": "PriceA",
        }
    )
    right = df[columns].rename(
        columns={
            "Symbol": "ContractB",
            "NormalizedPrice10g": "PriceB",
        }
    )

    pairs = left.merge(
        right,
        on=["Date", "Expiry Date"],
        how="inner",
        validate="many_to_many",
    )
    pairs = pairs[pairs["ContractA"] < pairs["ContractB"]].copy()

    trade_columns = [
        "ContractA",
        "ContractB",
        "ExpiryDate",
        "EntryDate",
        "ExitDate",
        "EntrySpreadPercent",
        "ExitSpreadPercent",
        "EntryZScore",
        "ExitZScore",
        "GrossSpreadMoveProxyPct",
        "IllustrativeCostPct",
        "NetSpreadMoveProxyPct",
        "EntryMidpoint",
        "ExitMidpoint",
        "Interpretation",
    ]

    open_columns = [
        "ContractA",
        "ContractB",
        "ExpiryDate",
        "EntryDate",
        "EntrySpreadPercent",
        "EntryZScore",
        "Position",
        "Status",
    ]

    if pairs.empty:
        trades = pd.DataFrame(columns=trade_columns)
        open_positions = pd.DataFrame(columns=open_columns)

        trades.to_csv(TRADES_FILE, index=False)
        open_positions.to_csv(OPEN_POSITIONS_FILE, index=False)

        report = pd.DataFrame([{
            "Status": "No comparable same-expiry contract pairs",
            "TradingDates": df["Date"].nunique(),
            "PairObservations": 0,
            "CompletedTrades": 0,
            "OpenPositionsAtEnd": 0,
            "PositiveProxyTrades": 0,
            "NegativeOrZeroProxyTrades": 0,
            "MeanNetProxyPercent": np.nan,
            "MedianNetProxyPercent": np.nan,
            "TotalNetProxyPercent": np.nan,
            "EntryZThreshold": ENTRY_Z,
            "ExitZThreshold": EXIT_Z,
            "IllustrativeCostBpsPerLeg": COST_BPS_PER_LEG,
            "Note": "No performance conclusion is possible.",
        }])
        report.to_csv(REPORT_FILE, index=False)
        print(report.to_string(index=False))
        return

    midpoint = (pairs["PriceA"] + pairs["PriceB"]) / 2
    pairs["SpreadPercent"] = (
        (pairs["PriceA"] - pairs["PriceB"]) / midpoint * 100
    )

    pairs = pairs.sort_values(
        ["ContractA", "ContractB", "Expiry Date", "Date"]
    ).reset_index(drop=True)

    trade_records = []
    open_position_records = []

    # Each contract pair and expiry is evaluated independently.
    for (contract_a, contract_b, expiry), group in pairs.groupby(
        ["ContractA", "ContractB", "Expiry Date"],
        sort=True,
    ):
        group = group.sort_values("Date").copy()

        # Exclude the current observation from its own baseline.
        prior_spread = group["SpreadPercent"].shift(1)

        group["HistoricalMean"] = prior_spread.rolling(
            WINDOW, min_periods=MIN_HISTORY
        ).mean()
        group["HistoricalStd"] = prior_spread.rolling(
            WINDOW, min_periods=MIN_HISTORY
        ).std()

        valid_std = group["HistoricalStd"].where(
            group["HistoricalStd"] > 0
        )
        group["ZScore"] = (
            group["SpreadPercent"] - group["HistoricalMean"]
        ) / valid_std

        position = 0
        entry_date = None
        entry_spread = None
        entry_midpoint = None
        entry_z = None

        for _, row in group.iterrows():
            z = row["ZScore"]

            if pd.isna(z):
                continue

            if position == 0:
                # A positive Z-score: short the spread.
                if z >= ENTRY_Z:
                    position = -1
                # A negative Z-score: long the spread.
                elif z <= -ENTRY_Z:
                    position = 1

                if position != 0:
                    entry_date = row["Date"]
                    entry_spread = row["SpreadPercent"]
                    entry_midpoint = (
                        row["PriceA"] + row["PriceB"]
                    ) / 2
                    entry_z = z

            elif abs(z) <= EXIT_Z:
                exit_midpoint = (
                    row["PriceA"] + row["PriceB"]
                ) / 2

                # Research proxy only, not executable portfolio P&L.
                gross_proxy_pct = position * (
                    row["SpreadPercent"] - entry_spread
                )

                # Four leg executions: two legs to enter, two to exit.
                # Convert basis points to percentage points.
                estimated_cost_pct = (
                    4 * COST_BPS_PER_LEG / 100
                )

                trade_records.append({
                    "ContractA": contract_a,
                    "ContractB": contract_b,
                    "ExpiryDate": expiry,
                    "EntryDate": entry_date,
                    "ExitDate": row["Date"],
                    "EntrySpreadPercent": entry_spread,
                    "ExitSpreadPercent": row["SpreadPercent"],
                    "EntryZScore": entry_z,
                    "ExitZScore": z,
                    "GrossSpreadMoveProxyPct": gross_proxy_pct,
                    "IllustrativeCostPct": estimated_cost_pct,
                    "NetSpreadMoveProxyPct": (
                        gross_proxy_pct - estimated_cost_pct
                    ),
                    "EntryMidpoint": entry_midpoint,
                    "ExitMidpoint": exit_midpoint,
                    "Interpretation": (
                        "Research proxy only; not executable portfolio P&L"
                    ),
                })

                position = 0
                entry_date = None
                entry_spread = None
                entry_midpoint = None
                entry_z = None

        # Keep unclosed positions visible; do not count them as completed.
        if position != 0:
            open_position_records.append({
                "ContractA": contract_a,
                "ContractB": contract_b,
                "ExpiryDate": expiry,
                "EntryDate": entry_date,
                "EntrySpreadPercent": entry_spread,
                "EntryZScore": entry_z,
                "Position": position,
                "Status": "Open at end of available history",
            })

    trades = pd.DataFrame(trade_records, columns=trade_columns)
    open_positions = pd.DataFrame(
        open_position_records, columns=open_columns
    )

    trades.to_csv(TRADES_FILE, index=False)
    open_positions.to_csv(OPEN_POSITIONS_FILE, index=False)

    dates_count = df["Date"].nunique()
    pair_count = len(pairs)
    completed = len(trades)
    open_count = len(open_positions)

    report_data = {
        "Status": (
            "Exploratory backtest"
            if completed
            else "No completed trades"
        ),
        "TradingDates": dates_count,
        "PairObservations": pair_count,
        "CompletedTrades": completed,
        "OpenPositionsAtEnd": open_count,
        "PositiveProxyTrades": (
            int((trades["NetSpreadMoveProxyPct"] > 0).sum())
            if completed else 0
        ),
        "NegativeOrZeroProxyTrades": (
            int((trades["NetSpreadMoveProxyPct"] <= 0).sum())
            if completed else 0
        ),
        "MeanNetProxyPercent": (
            trades["NetSpreadMoveProxyPct"].mean()
            if completed else np.nan
        ),
        "MedianNetProxyPercent": (
            trades["NetSpreadMoveProxyPct"].median()
            if completed else np.nan
        ),
        "TotalNetProxyPercent": (
            trades["NetSpreadMoveProxyPct"].sum()
            if completed else np.nan
        ),
        "EntryZThreshold": ENTRY_Z,
        "ExitZThreshold": EXIT_Z,
        "IllustrativeCostBpsPerLeg": COST_BPS_PER_LEG,
        "Note": (
            "Spread-movement proxy only; not executable P&L, "
            "not annualized, and not evidence of profitability."
        ),
    }

    report = pd.DataFrame([report_data])
    report.to_csv(REPORT_FILE, index=False)

    print("\nGOLDLENS — EXPLORATORY BACKTEST")
    print("=" * 60)
    print(f"Trading dates: {dates_count}")
    print(f"Same-expiry pair observations: {pair_count}")
    print(f"Completed trades: {completed}")
    print(f"Open positions at end: {open_count}")
    print(f"Entry threshold: |Z| >= {ENTRY_Z}")
    print(f"Exit threshold: |Z| <= {EXIT_Z}")
    print(f"Illustrative cost: {COST_BPS_PER_LEG} bps per leg")

    if completed:
        print("\nSummary:")
        print(report.to_string(index=False))

    if open_count:
        print("\nOpen positions at end:")
        print(open_positions.to_string(index=False))

    print(f"\nTrades saved: {TRADES_FILE}")
    print(f"Open positions saved: {OPEN_POSITIONS_FILE}")
    print(f"Report saved: {REPORT_FILE}")
    print(
        "\nWARNING: These are spread-movement proxies, not executable "
        "returns. Real backtesting requires realistic contract quantities, "
        "liquidity, fees, slippage, and expiry rules."
    )


if __name__ == "__main__":
    main()
