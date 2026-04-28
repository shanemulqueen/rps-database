import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "Historical RPS & CES Capacity Additions_August 2025.xlsx"
OUTPUT = ROOT / "data" / "capacity_additions.parquet"

SHEET = "RPS & CES Capacity Additions"
ID_VARS = ["region", "technology", "off_taker", "rps_related"]


def find_skiprows(path, sheet):
    """Scan rows until we find the header by looking for 'Region' or 'Technology' in col 1."""
    for skip in range(25, 40):
        df = pd.read_excel(path, sheet_name=sheet, skiprows=skip, nrows=1, header=None)
        row = [str(v).strip() for v in df.iloc[0]]
        if any(v in ("Region", "Technology", "Annual Capacity Additions (MW-AC)") for v in row):
            return skip
    raise ValueError(f"Could not locate header row in {sheet}")


def parse():
    skip = find_skiprows(SOURCE, SHEET)
    df = pd.read_excel(SOURCE, sheet_name=SHEET, skiprows=skip)

    # Normalize column names
    df.columns = [
        str(c).strip().lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
        for c in df.columns
    ]

    # Drop fully-empty rows and trailing aggregate rows
    df = df.dropna(how="all")

    # Rename the pre-2000 string column (may appear as 'pre_2000' or similar after normalization)
    pre_col = [c for c in df.columns if "pre" in c and "2000" in c]
    if pre_col:
        df = df.rename(columns={pre_col[0]: "pre_2000"})

    # Detect dimension and year columns
    # After normalization, ID cols are non-numeric strings; year cols are int-like
    all_cols = list(df.columns)

    # First 4 non-numeric columns are dimensions
    dim_cols = []
    for c in all_cols:
        if len(dim_cols) < 4:
            dim_cols.append(c)

    year_cols = [c for c in all_cols if c not in dim_cols]

    # Rename dimension columns to standard names
    rename_map = dict(zip(dim_cols, ID_VARS))
    df = df.rename(columns=rename_map)

    # Melt to long format
    melted = df.melt(id_vars=ID_VARS, value_vars=year_cols, var_name="year", value_name="mw_ac")
    melted["mw_ac"] = pd.to_numeric(melted["mw_ac"], errors="coerce").astype("float32")

    # Drop rows where all dimension values are NaN
    melted = melted.dropna(subset=["region"])

    OUTPUT.parent.mkdir(exist_ok=True)
    melted.to_parquet(OUTPUT, index=False)
    print(f"capacity_additions: {len(melted):,} rows → {OUTPUT}")


if __name__ == "__main__":
    parse()
