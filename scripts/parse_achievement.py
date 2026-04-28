import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "Historical RPS & CES Target Achievement and Compliance Costs_August 2025.xlsx"


def find_skiprows(path, sheet, anchor_values):
    """Scan rows to find the header by matching expected values in the first few cols."""
    for skip in range(20, 40):
        df = pd.read_excel(path, sheet_name=sheet, skiprows=skip, nrows=1, header=None)
        row = [str(v).strip() for v in df.iloc[0]]
        if any(a in row for a in anchor_values):
            return skip
    raise ValueError(f"Could not locate header in sheet '{sheet}'")


def parse_target_achievement():
    sheet = "Target Achievement"
    skip = find_skiprows(SOURCE, sheet, ["RPS States", "Annual RPS"])
    df = pd.read_excel(SOURCE, sheet_name=sheet, skiprows=skip)

    # First col = state, second = notes, third = data source, fourth = tier, rest = years
    cols = list(df.columns)
    rename = {cols[0]: "state", cols[1]: "notes", cols[2]: "data_source", cols[3]: "tier"}
    df = df.rename(columns=rename)

    df = df.dropna(how="all")
    df["state"] = df["state"].ffill()
    df["tier"] = df["tier"].astype(str).str.strip()

    # Year cols: integer-typed columns
    year_cols = [c for c in df.columns if isinstance(c, int)]

    melted = df.melt(
        id_vars=["state", "tier"],
        value_vars=year_cols,
        var_name="year",
        value_name="achievement_pct",
    )
    melted["achievement_pct"] = pd.to_numeric(melted["achievement_pct"], errors="coerce").astype("float32")
    melted["year"] = melted["year"].astype("int16")
    melted = melted.dropna(subset=["state"])

    out = ROOT / "data" / "target_achievement.parquet"
    out.parent.mkdir(exist_ok=True)
    melted.to_parquet(out, index=False)
    print(f"target_achievement: {len(melted):,} rows → {out}")


def parse_compliance_costs():
    sheet = "Compliance Costs"
    skip = find_skiprows(SOURCE, sheet, ["States", "CO", "Total RPS"])
    df = pd.read_excel(SOURCE, sheet_name=sheet, skiprows=skip)

    cols = list(df.columns)
    rename = {cols[0]: "state", cols[1]: "tier"}
    df = df.rename(columns=rename)

    df = df.dropna(how="all")
    df["state"] = df["state"].ffill()
    df["tier"] = df["tier"].astype(str).str.strip()

    year_cols = [c for c in df.columns if isinstance(c, int)]

    melted = df.melt(
        id_vars=["state", "tier"],
        value_vars=year_cols,
        var_name="year",
        value_name="cost_pct_retail_bill",
    )
    melted["cost_pct_retail_bill"] = pd.to_numeric(melted["cost_pct_retail_bill"], errors="coerce").astype("float32")
    melted["year"] = melted["year"].astype("int16")
    melted = melted.dropna(subset=["state"])

    out = ROOT / "data" / "compliance_costs.parquet"
    melted.to_parquet(out, index=False)
    print(f"compliance_costs: {len(melted):,} rows → {out}")


def parse():
    parse_target_achievement()
    parse_compliance_costs()


if __name__ == "__main__":
    parse()
