#!/usr/bin/env python3
"""Query NASA Exoplanet Archive TAP for stellar ages of multi-planet host stars."""

import warnings
import pandas as pd
from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive

warnings.filterwarnings("ignore")

print("Querying NASA Exoplanet Archive TAP service for stellar ages...")
result = NasaExoplanetArchive.query_criteria(
    table="pscomppars",
    select="hostname, st_age, st_ageerr1, st_ageerr2, st_age_reflink",
    where="sy_pnum >= 3 AND pl_controv_flag = 0",
)

if result is None or len(result) == 0:
    print("ERROR: No results returned from TAP query.")
    exit(1)

# Convert to pandas DataFrame
df = result.to_pandas()

print(f"Raw rows returned: {len(df)}")

# Group by hostname, take first non-null age per system
# (all planets in a system should share the same stellar age)
def first_nonnull(series):
    valid = series.dropna()
    return valid.iloc[0] if len(valid) > 0 else None

grouped = df.groupby("hostname", as_index=False).agg({
    "st_age": first_nonnull,
    "st_ageerr1": first_nonnull,
    "st_ageerr2": first_nonnull,
    "st_age_reflink": first_nonnull,
})

print(f"Unique host stars (sy_pnum >= 3): {len(grouped)}")
stars_with_age = grouped['st_age'].notna().sum()
stars_without_age = grouped['st_age'].isna().sum()
print(f"Stars WITH age measurements: {stars_with_age} ({100*stars_with_age/len(grouped):.1f}%)")
print(f"Stars WITHOUT age measurements: {stars_without_age} ({100*stars_without_age/len(grouped):.1f}%)")

# Add pull date
from datetime import datetime, timezone
grouped["_pull_date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# Save to CSV
output_csv = "/root/vela2/datasets/exoplanets/stellar_ages.csv"
grouped.to_csv(output_csv, index=False)
print(f"\nSaved to {output_csv}")
print(f"\nPreview:")
print(grouped.head(10).to_string(index=False))
