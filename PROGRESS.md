# RPS Database — State Review Progress

Goal: Build a DSIRE-like backend for US RPS/CES and state procurement programs, verified
state by state. programs/STATE.yaml is the source of truth for program structure,
eligibility, targets, and unique requirements.

⚠️ SOURCE-OF-AUTHORITY POLICY (set 2026-06-23): LBNL data was only a quick starting point
to seed the database — it is NOT authoritative and is known to contain errors and omissions
(e.g. it omits CT Class III entirely). Now that we have a baseline, verify every state
against primary sources (state PUC/PURA sites, statutes, DSIRE). DO NOT run sanity checks
against LBNL or treat a mismatch with LBNL as a problem to reconcile. Where LBNL numbers are
still displayed, they should be replaced/overridden by verified values as each state is
reviewed.

To pick up a session: read this file, then open the next state marked 🔲 and begin.
To regenerate a state's HTML after editing its YAML:
  `python scripts/generate_state_summaries.py <STATE>`

YAML mechanisms for the numerical tables (per state):
- `targets_override:` — list of `{tier, source, values:{year:pct}}`. When present, these verified
  per-tier schedules FULLY REPLACE LBNL's target & demand figures for the state (demand = pct ×
  RPS-applicable sales). Include a `Total RPS` (and/or `Total CES`) tier for the totals row.
  Use this to make a reviewed state authoritative and independent of LBNL.
- `supplemental_data.targets:` — same shape; ADDITIVE tiers layered on top of LBNL (use for a
  standard LBNL omits entirely, e.g. CT Class III, MA APS). A Grand Total row is auto-added.
Page layout (CT template): targets + sales/demand at top, consolidated technology-eligibility
matrix (standards × techs, using concise `note_short` per eligibility entry) before program detail.

## Status Key
- ✅ Complete — YAML written, HTML generated, reviewed
- 🔄 In Progress — started but not finalized
- 🔲 Not Started — LBNL data only, no YAML yet

---

## Northeast

| State | Status | Programs Captured | Notes |
|---|---|---|---|
| MA | ✅ | Class I RPS, Class II RPS, CES, CES-E, APS | Full review. Class I schedule verified (+2%/yr→2024, +3%/yr 2025–29, 40% by 2030); LBNL figures accurate and retained. Added note_short fields. APS via supplemental_data. |
| CT | ✅ | Class I RPS, Class II RPS, Class III RPS, Zero-Carbon Procurement (Millstone) | Full review + revamp (template state). Class III (4% CHP/C&LM) added via supplemental_data and now in numerical tables. Class I note corrected for PA 23-102 (−7 pts 2026–2030). Class II = 4% confirmed via PURA. New page layout: targets/sales/demand at top, consolidated tech-eligibility matrix before program detail. |
| RI | 🔄 | RES, Long-Term Contracting Standard, REG Program | Initial build complete. RI calls it RES not RPS; 100% by 2033. Block Island Wind Farm mechanism captured. |
| NH | ✅ | Class I RPS, Class II RPS, Class III RPS, Class IV RPS | Full review. Split single collapsed program into 4 statutory classes (RSA 362-F); Class I notes the Thermal carve-out (2.2%). Targets driven by verified statutory schedule via targets_override — corrected LBNL Class III (1.0%→8.0% for 2024; total 24.3% 2024 / 25.2% 2025+). Admin PUC→DOE (2021). |
| ME | 🔄 | Class I/IA RPS, Class II RPS, Offshore Wind Procurement | Initial build complete. LD 1868 (2025) updated to 90% by 2040. DOER launched Sept 2025. NAR registry for northern ME. |
| VT | 🔄 | RES Tiers I/II/IV/V, RES Tier III (Energy Transformation), Standard Offer | Initial build complete. Five-tier structure post-Act 179 (2024). Tier III is demand-side/fossil-fuel savings, not generation. |
| NY | 🔲 | — | RPS + Tier 1/2 + offshore wind + ZEC (nuclear) |

## Mid-Atlantic

| State | Status | Programs Captured | Notes |
|---|---|---|---|
| NJ | 🔄 | RPS, Solar Carve-Out/SuSI, Offshore Wind OREC | Initial build complete. SuSI ADI/CSI structure captured. Uses PJM-GATS. |
| MD | 🔄 | RPS Tier 1, RPS Tier 2, Solar SREC, Offshore Wind OREC | Initial build complete. Brighter Tomorrow Act (2024) SREC multiplier captured. Uses PJM-GATS. |
| PA | 🔲 | — | AEPS (Alternative Energy Portfolio Standard), Tier I/II |
| DE | 🔲 | — | RPS |
| DC | 🔲 | — | RPS (among highest targets in US) |
| VA | 🔲 | — | RPS + offshore wind + storage mandates |

## Southeast

| State | Status | Programs Captured | Notes |
|---|---|---|---|
| NC | 🔲 | — | RPS (REPS) — utility and co-op obligations differ |

## Midwest

| State | Status | Programs Captured | Notes |
|---|---|---|---|
| IL | 🔲 | — | RPS + FEJA (long-term procurement, ZEC for nuclear) |
| MN | 🔲 | — | RPS + solar carve-out |
| MI | 🔲 | — | RPS (Clean Energy Plan) |
| WI | 🔲 | — | RPS |
| IA | 🔲 | — | RPS (oldest in US, 105 MW mandate — not %) |
| MO | 🔲 | — | RPS (MEEIA) |
| OH | 🔲 | — | RPS (reduced/altered by legislation) |
| KS | 🔲 | — | RPS (voluntary as of 2015 — verify current status) |
| ND | 🔲 | — | RPS (voluntary) |
| SD | 🔲 | — | RPS (voluntary) |

## West

| State | Status | Programs Captured | Notes |
|---|---|---|---|
| CA | 🔲 | — | RPS + CES + bundled power requirement + IRP procurement |
| OR | 🔲 | — | RPS + large utility 100% clean standard |
| WA | 🔲 | — | Clean Energy Transformation Act (100% by 2045) |
| NV | 🔲 | — | RPS |
| CO | 🔲 | — | RPS (IOU, Coop, Muni obligations differ) |
| NM | 🔲 | — | RPS + Energy Transition Act |
| AZ | 🔲 | — | RES (Renewable Energy Standard) |
| MT | 🔲 | — | RPS |
| HI | 🔲 | — | RPS (100% by 2045) |

## Texas

| State | Status | Programs Captured | Notes |
|---|---|---|---|
| TX | 🔲 | — | RPS (met and frozen; RECs still trade but no active mandate) |

---

## Known Gaps vs LBNL (log additions here as we find them)

| State | Program | Type | Note |
|---|---|---|---|
| MA | APS (Alternative Portfolio Standard) | APS | CHP, flywheel, DR — not in LBNL data |
| NJ | Solar procurement (TREC) | Procurement | State-level solar certificate program |
| MD | Offshore wind procurement | Procurement | State-contracted offshore wind |
| CA | IRP/CPUC procurement | Procurement | CPUC-directed long-term contracts |
| IL | ZEC (Zero Emission Credits) | ZEC | Nuclear support — Braidwood, Byron, Dresden, Quad Cities |
| NY | ZEC (Zero Emission Credits) | ZEC | Nuclear support for upstate plants |
| CT | ZEC (Zero Emission Credits) | ZEC | Millstone nuclear |
