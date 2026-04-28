import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "RPS & CES Targets and Demand_August 2025.xlsx"


def find_skiprows(path, sheet, anchor_values):
    for skip in range(10, 40):
        df = pd.read_excel(path, sheet_name=sheet, skiprows=skip, nrows=1, header=None)
        row = [str(v).strip() for v in df.iloc[0]]
        if any(a in row for a in anchor_values):
            return skip
    raise ValueError(f"Could not locate header in sheet '{sheet}'")


def parse_sales(sheet, output_name):
    skip = find_skiprows(SOURCE, sheet, ["State"])
    df = pd.read_excel(SOURCE, sheet_name=sheet, skiprows=skip)

    cols = list(df.columns)
    df = df.rename(columns={cols[0]: "state"})
    df = df.dropna(how="all")
    df = df.dropna(subset=["state"])

    year_cols = [c for c in df.columns if isinstance(c, int)]

    melted = df.melt(id_vars=["state"], value_vars=year_cols, var_name="year", value_name="gwh")
    melted["gwh"] = pd.to_numeric(melted["gwh"], errors="coerce").astype("float32")
    melted["year"] = melted["year"].astype("int16")
    melted["is_projection"] = melted["year"] > 2025

    out = ROOT / "data" / f"{output_name}.parquet"
    out.parent.mkdir(exist_ok=True)
    melted.to_parquet(out, index=False)
    print(f"{output_name}: {len(melted):,} rows → {out}")


def parse_targets_pct():
    sheet = "RPS & CES Targets (%)"
    skip = find_skiprows(SOURCE, sheet, ["State", "RPS Tier or Carve Out"])
    df = pd.read_excel(SOURCE, sheet_name=sheet, skiprows=skip)

    cols = list(df.columns)
    rename = {cols[0]: "state", cols[1]: "program_notes", cols[2]: "tier"}
    df = df.rename(columns=rename)

    df = df.dropna(how="all")
    df["state"] = df["state"].ffill()
    df["tier"] = df["tier"].astype(str).str.strip()
    df["program_notes"] = df["program_notes"].where(df["program_notes"].notna(), None)

    year_cols = [c for c in df.columns if isinstance(c, int)]

    melted = df.melt(
        id_vars=["state", "program_notes", "tier"],
        value_vars=year_cols,
        var_name="year",
        value_name="target_pct",
    )
    melted["target_pct"] = pd.to_numeric(melted["target_pct"], errors="coerce").astype("float32")
    melted["year"] = melted["year"].astype("int16")
    melted["is_projection"] = melted["year"] > 2025
    melted = melted.dropna(subset=["state"])

    out = ROOT / "data" / "rps_targets_pct.parquet"
    melted.to_parquet(out, index=False)
    print(f"rps_targets_pct: {len(melted):,} rows → {out}")


def parse_demand_gwh():
    sheet = "RPS & CES Demand (GWh)"
    skip = find_skiprows(SOURCE, sheet, ["State", "RPS Tier or Carve Out"])
    df = pd.read_excel(SOURCE, sheet_name=sheet, skiprows=skip)

    cols = list(df.columns)
    rename = {cols[0]: "state", cols[1]: "program_notes", cols[2]: "tier"}
    df = df.rename(columns=rename)

    df = df.dropna(how="all")
    df["state"] = df["state"].ffill()
    df["tier"] = df["tier"].astype(str).str.strip()
    df["program_notes"] = df["program_notes"].where(df["program_notes"].notna(), None)

    # Drop the US Total aggregate row and any orphaned rows after it
    df = df[df["state"] != "Total"]
    df = df.dropna(subset=["state"])

    year_cols = [c for c in df.columns if isinstance(c, int)]

    melted = df.melt(
        id_vars=["state", "program_notes", "tier"],
        value_vars=year_cols,
        var_name="year",
        value_name="gwh",
    )
    melted["gwh"] = pd.to_numeric(melted["gwh"], errors="coerce").astype("float32")
    melted["year"] = melted["year"].astype("int16")
    melted["is_projection"] = melted["year"] > 2025

    out = ROOT / "data" / "rps_demand_gwh.parquet"
    melted.to_parquet(out, index=False)
    print(f"rps_demand_gwh: {len(melted):,} rows → {out}")


def parse():
    parse_sales("Statewide Sales", "statewide_sales")
    parse_sales("RPS-Applicable Sales", "rps_applicable_sales")
    parse_targets_pct()
    parse_demand_gwh()


if __name__ == "__main__":
    parse()
