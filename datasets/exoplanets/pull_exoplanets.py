#!/usr/bin/env python3
"""
Pull confirmed multi-planet systems (>=3 planets) from NASA Exoplanet Archive.
Data acquisition only — no analysis.
"""

import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime, timezone
from pathlib import Path
from io import StringIO
import sys

# ── Config ────────────────────────────────────────────────────────────────────

OUT_DIR = Path(__file__).parent
TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
PULL_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")

COLUMNS = [
    # Planet identity
    "pl_name",           # planet name
    "hostname",          # host star name
    "pl_letter",         # planet letter (b, c, d, ...)
    "sy_pnum",           # number of planets in system

    # Orbital parameters
    "pl_orbsmax",        # semi-major axis (AU)
    "pl_orbsmaxerr1",
    "pl_orbsmaxerr2",
    "pl_orbper",         # orbital period (days)
    "pl_orbpererr1",
    "pl_orbpererr2",
    "pl_orbeccen",       # eccentricity
    "pl_orbeccenerr1",
    "pl_orbeccenerr2",

    # Planet physical
    "pl_bmassj",         # best mass (Jupiter masses; msini if mass unavailable)
    "pl_bmassjerr1",
    "pl_bmassjerr2",
    "pl_bmassprov",      # provenance: 'Mass' or 'Msini'
    "pl_radj",           # radius (Jupiter radii)
    "pl_radjerr1",
    "pl_radjerr2",

    # Discovery
    "discoverymethod",

    # Host star
    "st_mass",           # stellar mass (solar masses)
    "st_masserr1",
    "st_masserr2",
    "st_rad",            # stellar radius (solar radii)
    "st_raderr1",
    "st_raderr2",
]

# ── Query ─────────────────────────────────────────────────────────────────────

col_str = ",".join(COLUMNS)

query = f"""
SELECT {col_str}
FROM pscomppars
WHERE sy_pnum >= 3
AND pl_controv_flag = 0
ORDER BY hostname, pl_letter
"""

print("Querying NASA Exoplanet Archive TAP service...")
print(f"Table: pscomppars (composite parameters, one row per planet)")

resp = requests.get(TAP_URL, params={
    "query": query,
    "format": "csv",
    "lang": "ADQL",
})

if resp.status_code != 200:
    print(f"ERROR: HTTP {resp.status_code}")
    print(resp.text[:500])
    sys.exit(1)

print(f"Response received ({len(resp.content):,} bytes)")

df = pd.read_csv(StringIO(resp.text))
print(f"Rows pulled: {len(df):,}")

# ── Add metadata column ───────────────────────────────────────────────────────

df["_pull_date"] = PULL_DATE
df["_catalog"] = "NASA Exoplanet Archive — pscomppars"

# ── Verify filter ─────────────────────────────────────────────────────────────

# Re-verify: only systems where we actually have >=3 planets in the pull
# (some edge cases where sy_pnum is stale)
system_counts = df.groupby("hostname")["pl_name"].count()
valid_hosts = system_counts[system_counts >= 3].index
df = df[df["hostname"].isin(valid_hosts)].copy()

# ── Save ──────────────────────────────────────────────────────────────────────

OUT_DIR.mkdir(parents=True, exist_ok=True)

parquet_path = OUT_DIR / "multi_planet_systems.parquet"
csv_path = OUT_DIR / "multi_planet_systems.csv"

df.to_parquet(parquet_path, index=False)
df.to_csv(csv_path, index=False)

print(f"\nSaved:\n  {parquet_path}\n  {csv_path}")

# ── Summary ───────────────────────────────────────────────────────────────────

n_systems = df["hostname"].nunique()
n_planets = len(df)
size_dist = df.groupby("hostname")["pl_name"].count().value_counts().sort_index()

print(f"\n{'='*50}")
print(f"DATASET SUMMARY")
print(f"{'='*50}")
print(f"Pull date     : {PULL_DATE}")
print(f"Total systems : {n_systems:,}")
print(f"Total planets : {n_planets:,}")
print(f"\nSystem size distribution:")
for size, count in size_dist.items():
    bar = "█" * min(count // 2, 40)
    print(f"  {size} planets: {count:4d}  {bar}")

# Famous systems check
famous = [
    "TRAPPIST-1", "Kepler-90", "Kepler-11", "Kepler-20", "Kepler-62",
    "HR 8799", "55 Cnc", "GJ 667 C", "HD 10180", "TOI-178",
    "Kepler-80", "Kepler-444", "tau Cet", "GJ 876",
]
print(f"\nFamous systems check:")
for name in famous:
    match = df[df["hostname"].str.lower() == name.lower()]
    if len(match) > 0:
        n = len(match)
        print(f"  ✓ {name:<20} ({n} planets)")
    else:
        print(f"  ✗ {name:<20} (not found)")

# ── Verify loadable ───────────────────────────────────────────────────────────

print(f"\nVerifying parquet loads cleanly...")
check = pd.read_parquet(parquet_path)
assert len(check) == len(df), "Row count mismatch"
assert "hostname" in check.columns, "Missing hostname column"
print(f"  OK — {len(check):,} rows, {len(check.columns)} columns")

print(f"\nDone.")
