"""
Generate or update per-state RPS/CES HTML summaries.

Usage:
    python generate_state_summaries.py           # all states with a programs YAML
    python generate_state_summaries.py MA CA CO  # specific states
"""

import sys
import yaml
import pandas as pd
from pathlib import Path
from datetime import date
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
PROGRAMS_DIR = ROOT / "programs"
STATES_DIR = ROOT / "states"
TEMPLATES_DIR = ROOT / "templates"

STATE_NAMES = {
    "AZ": "Arizona", "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DC": "District of Columbia", "DE": "Delaware", "HI": "Hawaii", "IA": "Iowa",
    "IL": "Illinois", "IN": "Indiana", "KS": "Kansas", "MA": "Massachusetts",
    "MD": "Maryland", "ME": "Maine", "MI": "Michigan", "MN": "Minnesota",
    "MO": "Missouri", "MT": "Montana", "NC": "North Carolina", "ND": "North Dakota",
    "NE": "Nebraska", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NV": "Nevada", "NY": "New York", "OH": "Ohio", "OR": "Oregon",
    "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TX": "Texas", "UT": "Utah", "VA": "Virginia",
    "VT": "Vermont", "WA": "Washington", "WI": "Wisconsin", "WY": "Wyoming",
    "AK": "Alaska", "FL": "Florida", "GA": "Georgia", "ID": "Idaho",
    "KY": "Kentucky", "LA": "Louisiana", "MS": "Mississippi", "OK": "Oklahoma",
    "TN": "Tennessee", "WV": "West Virginia",
}

TECH_LABELS = {
    "solar_pv": "Solar PV",
    "wind": "Wind (Onshore)",
    "offshore_wind": "Offshore Wind",
    "hydro_run_of_river": "Hydro — Run of River",
    "hydro_large": "Hydro — Large / Conventional",
    "biomass_solid": "Biomass (Solid)",
    "biogas_lfg": "Biogas / Landfill Gas",
    "msw": "Municipal Solid Waste",
    "geothermal": "Geothermal",
    "storage": "Storage",
    "nuclear": "Nuclear / Zero-Carbon",
    "fuel_cell": "Fuel Cell",
    "chp": "Combined Heat & Power (CHP)",
    "conservation_load_mgmt": "Conservation & Load Mgmt",
    "waste_heat_recovery": "Waste-Heat Recovery",
    "demand_response": "Demand Response",
    "flywheel_storage": "Flywheel Storage",
}

# Compact column headers for the consolidated cross-program eligibility matrix,
# where horizontal space per technology is tight.
TECH_LABELS_SHORT = {
    "solar_pv": "Solar PV",
    "wind": "Wind",
    "offshore_wind": "Offshore Wind",
    "hydro_run_of_river": "Hydro (RoR)",
    "hydro_large": "Hydro (Large)",
    "biomass_solid": "Biomass",
    "biogas_lfg": "Biogas / LFG",
    "msw": "MSW",
    "geothermal": "Geothermal",
    "storage": "Storage",
    "nuclear": "Nuclear",
    "fuel_cell": "Fuel Cell",
    "chp": "CHP",
    "conservation_load_mgmt": "C&LM",
    "waste_heat_recovery": "Waste Heat",
    "demand_response": "Demand Resp.",
    "flywheel_storage": "Flywheel",
}


DEMAND_TOP_PREFIXES = ("Total RPS", "CES (incremental to RPS)")


def fmt_pct(v):
    return "—" if pd.isna(v) else f"{v:.1%}"


def fmt_gwh(v):
    return "—" if pd.isna(v) else f"{v:,.0f}"


def display_years(dfs):
    latest = int(dfs["targets"][~dfs["targets"]["is_projection"]]["year"].max())
    return list(range(latest - 1, latest + 5))


def _sum_row(pivot, tiers, available, fmt_fn):
    vals = []
    for y in available:
        total = sum(
            pivot.loc[t, y] for t in tiers
            if y in pivot.columns and not pd.isna(pivot.loc[t, y])
        )
        vals.append(fmt_fn(total) if total else "—")
    return vals


def grand_total_targets(pivot, available, supp_tiers):
    """
    Targets % grand total: use Total CES as base when it exists (it already subsumes
    Class I RPS via overlap), otherwise use Total RPS. Add supplemental tiers on top.
    Only emit a row when there are at least two independent programs.
    """
    def _active(tiers):
        # A tier is only a usable base if it carries at least one non-zero value;
        # some states (e.g. CT) include an all-zero "Total CES" placeholder.
        out = []
        for t in tiers:
            vals = [pivot.loc[t, y] for y in available
                    if y in pivot.columns and not pd.isna(pivot.loc[t, y])]
            if any(v for v in vals):
                out.append(t)
        return out

    ces = _active([t for t in pivot.index if t.startswith("Total CES")])
    rps = [t for t in pivot.index if t.startswith("Total RPS")]
    supp = [t for t in (supp_tiers or []) if t in pivot.index]

    base = ces if ces else rps  # CES subsumes RPS when both exist
    top = base + supp

    # Suppress if there's only one independent standard and no supplemental
    if len(top) < 2:
        return None

    return {"tier": "Grand Total", "vals": _sum_row(pivot, top, available, fmt_pct),
            "is_proj": False, "is_grand_total": True}


def grand_total_demand(pivot, available, supp_tiers):
    """
    Demand GWh grand total: Total RPS + CES (incremental to RPS) + supplemental.
    LBNL's 'CES (incremental to RPS)' already strips the RPS/CES overlap.
    """
    top = [t for t in pivot.index if any(t.startswith(p) for p in DEMAND_TOP_PREFIXES)]
    top += [t for t in (supp_tiers or []) if t in pivot.index]
    if len(top) < 2:
        return None
    return {"tier": "Grand Total", "vals": _sum_row(pivot, top, available, fmt_gwh),
            "is_proj": False, "is_grand_total": True}


def build_targets_rows(df_state, years, supp_tiers=None):
    available = [y for y in years if y in df_state["year"].values]
    if not available or df_state.empty:
        return [], []
    pivot = (
        df_state[df_state["year"].isin(available)]
        .pivot_table(index="tier", columns="year", values="target_pct", aggfunc="first")
        .reindex(columns=available)
    )
    rows = []
    for tier, row in pivot.iterrows():
        rows.append({"tier": tier, "vals": [fmt_pct(row.get(y)) for y in available],
                     "is_proj": False, "is_grand_total": False})
    gt = grand_total_targets(pivot, available, supp_tiers)
    if gt:
        rows.append(gt)
    return rows, available


def build_sales_rows(ss, sr, years):
    rows = []
    for label, df_s in [("Statewide Sales", ss), ("RPS-Applicable Sales", sr)]:
        vals = []
        for y in years:
            r = df_s[df_s["year"] == y]
            vals.append(fmt_gwh(r["gwh"].iloc[0]) if not r.empty else "—")
        rows.append({"label": label, "vals": vals, "is_proj": False})
    return rows


def build_demand_rows(df_state, years, supp_tiers=None):
    available = [y for y in years if y in df_state["year"].values]
    if not available or df_state.empty:
        return []
    pivot = (
        df_state[df_state["year"].isin(available)]
        .pivot_table(index="tier", columns="year", values="gwh", aggfunc="first")
        .reindex(columns=available)
    )
    rows = []
    for tier, row in pivot.iterrows():
        rows.append({"tier": tier, "vals": [fmt_gwh(row.get(y)) for y in available],
                     "is_proj": False, "is_grand_total": False})
    gt = grand_total_demand(pivot, available, supp_tiers)
    if gt:
        rows.append(gt)
    return rows


def build_supplemental(supp, state, rps_applicable_df):
    """Build target and demand DataFrames from YAML supplemental_data block."""
    target_rows, demand_rows = [], []
    for item in supp.get("targets", []):
        tier = item["tier"]
        for year_raw, pct in item.get("values", {}).items():
            year = int(year_raw)
            is_proj = year > 2025
            target_rows.append({"state": state, "tier": tier, "year": year,
                                 "target_pct": float(pct), "is_projection": is_proj})
            row = rps_applicable_df[rps_applicable_df["year"] == year]
            if not row.empty:
                demand_rows.append({"state": state, "tier": tier, "year": year,
                                    "gwh": float(pct) * float(row["gwh"].iloc[0]),
                                    "is_projection": is_proj})
    t_df = pd.DataFrame(target_rows) if target_rows else pd.DataFrame()
    d_df = pd.DataFrame(demand_rows) if demand_rows else pd.DataFrame()
    return t_df, d_df


def program_eligibility(prog):
    """Merge a program's base `eligibility` with any `*_specific_eligibility` blocks
    (e.g. class3_specific_eligibility, aps_specific_eligibility) into one ordered dict."""
    merged = dict(prog.get("eligibility") or {})
    for key, val in prog.items():
        if key.endswith("_specific_eligibility") and isinstance(val, dict):
            merged.update(val)
    return merged


def _elig_status(info):
    """Normalize an eligibility entry to (status, note_short, condition)."""
    if isinstance(info, dict):
        elig = info.get("eligible")
        return elig, info.get("note_short"), info.get("condition")
    return info, None, None


def build_elig_matrix(programs):
    """Consolidated cross-program eligibility matrix.

    Rows are programs (portfolio standards), columns are technologies. Only technologies
    that are eligible or conditional in at least one program are shown, so the grid stays
    tight. Conditional/eligible cells carry the concise `note_short` (not the verbose
    `condition`, which is reserved for the per-program detail tables).
    """
    elig_by_prog = [(p, program_eligibility(p)) for p in programs]

    # Column order follows TECH_LABELS; keep only techs relevant to >=1 program.
    seen = list(TECH_LABELS.keys())
    for _, elig in elig_by_prog:
        for tech in elig:
            if tech not in seen:
                seen.append(tech)

    cols = []
    for tech in seen:
        relevant = any(
            _elig_status(elig.get(tech))[0] in (True, "conditional")
            for _, elig in elig_by_prog
            if tech in elig
        )
        if relevant:
            cols.append(tech)

    if not cols:
        return [], []

    rows = []
    for prog, elig in elig_by_prog:
        cells = []
        for tech in cols:
            status, note_short, _ = _elig_status(elig.get(tech))
            if status is True:
                cls, sym = "true", "✓"          # check
            elif status == "conditional":
                cls, sym = "conditional", "◐"   # half circle
            else:
                cls, sym = "false", "—"          # em dash
            cells.append({"cls": cls, "sym": sym,
                          "note": note_short if status in (True, "conditional") else None})
        rows.append({"name": prog.get("name", prog.get("id", "")), "cells": cells})

    headers = [{"key": t, "label": TECH_LABELS_SHORT.get(t, TECH_LABELS.get(t, t))}
               for t in cols]
    return headers, rows


def generate_state(state, dfs, years, env):
    yaml_path = PROGRAMS_DIR / f"{state}.yaml"
    programs = []
    last_reviewed = None

    admin_authority = None
    rec_registry = None
    compliance_reports = []
    supp_targets = pd.DataFrame()
    supp_demand = pd.DataFrame()
    ov_targets = pd.DataFrame()
    ov_demand = pd.DataFrame()

    if yaml_path.exists():
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        programs = data.get("programs", [])
        last_reviewed = data.get("last_reviewed")
        admin_authority = data.get("admin_authority")
        rec_registry = data.get("rec_registry")
        compliance_reports = data.get("compliance_reports", [])
        sr_all = dfs["rps_applicable"][dfs["rps_applicable"]["state"] == state]
        if "supplemental_data" in data:
            supp_targets, supp_demand = build_supplemental(
                data["supplemental_data"], state, sr_all)
        # targets_override: verified per-tier schedules that fully replace LBNL's
        # target and demand figures for this state (LBNL is a seed, not authoritative).
        if "targets_override" in data:
            ov_targets, ov_demand = build_supplemental(
                {"targets": data["targets_override"]}, state, sr_all)

    overriding = not ov_targets.empty
    if overriding:
        st = ov_targets
        sd = ov_demand
    else:
        st = dfs["targets"][dfs["targets"]["state"] == state]
        sd = dfs["demand"][dfs["demand"]["state"] == state]
    ss = dfs["statewide"][dfs["statewide"]["state"] == state]
    sr = dfs["rps_applicable"][dfs["rps_applicable"]["state"] == state]

    supp_tier_names = []
    if not supp_targets.empty:
        supp_tier_names = supp_targets["tier"].unique().tolist()
        st = pd.concat([st, supp_targets], ignore_index=True)
    if not supp_demand.empty:
        sd = pd.concat([sd, supp_demand], ignore_index=True)

    targets_rows, avail_years = build_targets_rows(st, years, supp_tier_names)
    sales_rows = build_sales_rows(ss, sr, avail_years)
    demand_rows = build_demand_rows(sd, avail_years, supp_tier_names)
    proj_start = next((y for y in avail_years if y > 2025), None)
    matrix_headers, matrix_rows = build_elig_matrix(programs)

    template = env.get_template("state.html")
    return template.render(
        state=state,
        state_name=STATE_NAMES.get(state, state),
        generated=date.today(),
        last_reviewed=last_reviewed,
        admin_authority=admin_authority,
        rec_registry=rec_registry,
        compliance_reports=compliance_reports,
        programs=programs,
        tech_labels=TECH_LABELS,
        years=avail_years,
        targets_rows=targets_rows,
        sales_rows=sales_rows,
        demand_rows=demand_rows,
        proj_start=proj_start,
        overriding=overriding,
        matrix_headers=matrix_headers,
        matrix_rows=matrix_rows,
    )


def load_dfs():
    return {
        "targets": pd.read_parquet(DATA / "rps_targets_pct.parquet"),
        "demand": pd.read_parquet(DATA / "rps_demand_gwh.parquet"),
        "statewide": pd.read_parquet(DATA / "statewide_sales.parquet"),
        "rps_applicable": pd.read_parquet(DATA / "rps_applicable_sales.parquet"),
    }


def generate(states=None):
    dfs = load_dfs()
    years = display_years(dfs)
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

    # States with a YAML file take priority; fall back to LBNL-only for others
    yaml_states = {p.stem for p in PROGRAMS_DIR.glob("*.yaml")}
    lbnl_states = set(dfs["targets"]["state"].dropna().unique())
    all_states = sorted(yaml_states | lbnl_states)

    targets = [s.upper() for s in states] if states else all_states
    STATES_DIR.mkdir(exist_ok=True)

    for state in targets:
        if state not in all_states:
            print(f"  WARNING: {state} not found, skipping")
            continue
        content = generate_state(state, dfs, years, env)
        (STATES_DIR / f"{state}.html").write_text(content)

    print(f"Updated {len(targets)} state file(s) → {STATES_DIR}/  [years: {years[0]}–{years[-1]}]")


if __name__ == "__main__":
    states = sys.argv[1:] or None
    generate(states)
