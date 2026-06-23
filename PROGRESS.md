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

## Status Key
- ✅ Complete — YAML written, HTML generated, reviewed
- 🔄 In Progress — started but not finalized
- 🔲 Not Started — LBNL data only, no YAML yet

---

## Northeast

| State | Status | Programs Captured | Notes |
|---|---|---|---|
| MA | 🔄 | Class I RPS, Class II RPS, CES, CES-E, APS | Initial build complete. Needs field verification. |
| CT | ✅ | Class I RPS, Class II RPS, Class III RPS, Zero-Carbon Procurement (Millstone) | Full review + revamp (template state). Class III (4% CHP/C&LM) added via supplemental_data and now in numerical tables. Class I note corrected for PA 23-102 (−7 pts 2026–2030). Class II = 4% confirmed via PURA. New page layout: targets/sales/demand at top, consolidated tech-eligibility matrix before program detail. |
| RI | 🔄 | RES, Long-Term Contracting Standard, REG Program | Initial build complete. RI calls it RES not RPS; 100% by 2033. Block Island Wind Farm mechanism captured. |
| NH | 🔄 | RPS (Class I, II, III, IV + Class I Thermal sub-class) | Initial build complete. Admin transferred PUC → NH DOE in 2021. Class I Thermal unique in New England. |
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
