# Multi-Planet Exoplanet Systems Dataset

## Pull info

| Field | Value |
|-------|-------|
| Pull date | 2026-04-27 |
| Source | NASA Exoplanet Archive |
| Table | `pscomppars` (composite parameters — one row per planet, best available values) |
| Filter | `sy_pnum >= 3` AND `pl_controv_flag = 0` (confirmed, non-controversial only) |
| Files | `multi_planet_systems.parquet`, `multi_planet_systems.csv` |

## Counts

- **336 systems**
- **1,182 planets**

| Planets per system | Systems |
|-------------------|---------|
| 3 | 216 |
| 4 | 82 |
| 5 | 25 |
| 6 | 11 |
| 7 | 1 (TRAPPIST-1) |
| 8 | 1 (KOI-351 / Kepler-90) |

## Columns

| Column | Description | Unit |
|--------|-------------|------|
| `pl_name` | Full planet name | — |
| `hostname` | Host star name | — |
| `pl_letter` | Planet letter (b, c, d, ...) | — |
| `sy_pnum` | Number of planets in system per archive | — |
| `pl_orbsmax` | Orbital semi-major axis | AU |
| `pl_orbsmaxerr1/2` | Upper/lower uncertainty on semi-major axis | AU |
| `pl_orbper` | Orbital period | days |
| `pl_orbpererr1/2` | Upper/lower uncertainty on period | days |
| `pl_orbeccen` | Orbital eccentricity | — |
| `pl_orbeccenerr1/2` | Upper/lower uncertainty on eccentricity | — |
| `pl_bmassj` | Best available planet mass (mass or msini) | M_Jupiter |
| `pl_bmassjerr1/2` | Upper/lower uncertainty on mass | M_Jupiter |
| `pl_bmassprov` | Mass provenance: `'Mass'` or `'Msini'` | — |
| `pl_radj` | Planet radius | R_Jupiter |
| `pl_radjerr1/2` | Upper/lower uncertainty on radius | R_Jupiter |
| `discoverymethod` | Detection method | — |
| `st_mass` | Host star mass | M_Sun |
| `st_masserr1/2` | Upper/lower uncertainty on stellar mass | M_Sun |
| `st_rad` | Host star radius | R_Sun |
| `st_raderr1/2` | Upper/lower uncertainty on stellar radius | R_Sun |
| `_pull_date` | Date this dataset was pulled | — |
| `_catalog` | Catalog source string | — |

## Notes on missing values

- Many planets have mass OR radius but not both — both columns are retained with NaN where unavailable.
- `pl_bmassj` uses true mass where available; falls back to msini. Check `pl_bmassprov` to distinguish.
- Eccentricity is frequently null for transit-discovered planets (not measurable from transit alone).

## Famous systems present

TRAPPIST-1 (7 planets), Kepler-11 (6), Kepler-20 (6), HD 10180 (6), TOI-178 (6),
Kepler-80 (6), 55 Cnc (5), Kepler-62 (5), Kepler-444 (5), HR 8799 (4), GJ 876 (4),
KOI-351 / Kepler-90 (8 planets — listed as KOI-351 in archive).

**Not present:** GJ 667 C and tau Cet do not appear — likely because their candidate
planets remain controversial or below the ≥3 confirmed threshold at time of pull.
Kepler-90 is present as KOI-351.

## Intended use

Data acquisition only. Downstream analysis targets:
- Mutual Hill spacing distributions
- Shell occupancy structure
- System architecture comparison across discovery methods
