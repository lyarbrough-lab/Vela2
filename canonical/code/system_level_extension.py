#!/usr/bin/env python3
"""Reproducibility extension for Yarbrough (2026) resonance analysis.

Runs matched system-level stability nulls for the full adopted ratio set and
for first-order commensurabilities only.  The archived source is not modified.
"""

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats


FULL_RATIOS = {
    "3:2": 3 / 2, "2:1": 2, "4:3": 4 / 3, "5:3": 5 / 3,
    "5:4": 5 / 4, "7:5": 7 / 5, "8:5": 8 / 5, "9:5": 9 / 5,
    "7:3": 7 / 3, "5:2": 5 / 2, "8:3": 8 / 3, "3:1": 3,
    "7:2": 7 / 2, "4:1": 4,
}
FIRST_ORDER_RATIOS = {"2:1": 2, "3:2": 3 / 2, "4:3": 4 / 3, "5:4": 5 / 4}
KEYS = ("M", "K", "G", "F")


def sf(value):
    try:
        return float(value) if str(value).strip() else math.nan
    except (TypeError, ValueError):
        return math.nan


def mass_bin(mass):
    if not np.isfinite(mass) or mass <= 0:
        return None
    if mass < 0.6:
        return "M"
    if mass < 0.9:
        return "K"
    if mass < 1.1:
        return "G"
    if mass < 1.6:
        return "F"
    return None


def is_bonded(period_ratio, ratios, tolerance=0.03):
    return any(abs(period_ratio / target - 1) <= tolerance for target in ratios.values())


def planet_mass_earth(row):
    mass_j = sf(row.get("pl_bmassj", ""))
    if np.isfinite(mass_j) and mass_j > 0.0001:
        return mass_j * 317.8
    radius_j = sf(row.get("pl_radj", ""))
    if np.isfinite(radius_j) and radius_j > 0:
        radius_e = radius_j * 11.21
        if radius_e <= 1.0:
            return radius_e ** 2.5
        if radius_e <= 1.5:
            return radius_e ** 2.0
        if radius_e <= 4.0:
            return radius_e ** 1.5
        if radius_e <= 8.0:
            return radius_e ** 1.2
        return radius_e
    return 5.0


def period_to_a(period_days, stellar_mass):
    return (((period_days / 365.25) ** 2) * stellar_mass) ** (1 / 3)


def load_systems(csv_path, require_three_valid=True, mass_strategy="first", transit_only=False):
    grouped = defaultdict(list)
    with open(csv_path, newline="") as handle:
        for row in csv.DictReader(handle):
            grouped[row["hostname"]].append(row)

    systems = []
    diagnostics = Counter()
    for host, rows in grouped.items():
        if len(rows) < 3:
            diagnostics["raw_lt3"] += 1
            continue
        masses = [sf(row.get("st_mass")) for row in rows]
        masses = [mass for mass in masses if np.isfinite(mass)]
        if not masses:
            diagnostics["missing_stellar_mass"] += 1
            continue
        stellar_mass = masses[0] if mass_strategy == "first" else float(np.median(masses))
        bin_name = mass_bin(stellar_mass)
        if bin_name is None:
            diagnostics["outside_mass_bins"] += 1
            continue
        valid = sorted(
            (sf(row.get("pl_orbper")), row)
            for row in rows
            if np.isfinite(sf(row.get("pl_orbper")))
            and 0.5 <= sf(row.get("pl_orbper")) <= 1e4
            and (not transit_only or row.get("discoverymethod") == "Transit")
        )
        if len(valid) < 3:
            diagnostics["valid_lt3"] += 1
            if require_three_valid:
                continue
        if len(valid) < 2:
            diagnostics["valid_lt2"] += 1
            continue
        periods = np.array([item[0] for item in valid], dtype=float)
        planets = [item[1] for item in valid]
        systems.append({
            "host": host,
            "mass": stellar_mass,
            "bin": bin_name,
            "periods": periods,
            "planet_masses": np.array([planet_mass_earth(row) for row in planets]),
        })
    return systems, diagnostics


def stable(periods, masses_earth, stellar_mass, min_hill):
    axes = np.array([period_to_a(period, stellar_mass) for period in periods])
    stellar_mass_earth = stellar_mass * 332946
    for i in range(len(periods) - 1):
        mean_axis = (axes[i] + axes[i + 1]) / 2
        hill = mean_axis * (
            (masses_earth[i] + masses_earth[i + 1]) / (3 * stellar_mass_earth)
        ) ** (1 / 3)
        if hill <= 0 or (axes[i + 1] - axes[i]) / hill < min_hill:
            return False
    return True


def bond_fraction(periods, ratios):
    flags = [is_bonded(periods[i + 1] / periods[i], ratios) for i in range(len(periods) - 1)]
    return 100 * np.mean(flags)


def minimum_log_period_gaps(masses_earth, stellar_mass, min_hill):
    """Exact adjacent log-period gaps implied by the circular mutual-Hill cut.

    With r=a2/a1 and h=Delta_min*((m1+m2)/(3Mstar))^(1/3),
    2(r-1)/(r+1) >= h, hence r >= (2+h)/(2-h).  Kepler then gives
    P2/P1=r^(3/2).
    """
    stellar_mass_earth = stellar_mass * 332946
    gaps = []
    for i in range(len(masses_earth) - 1):
        h = min_hill * (
            (masses_earth[i] + masses_earth[i + 1]) / (3 * stellar_mass_earth)
        ) ** (1 / 3)
        if h >= 2:
            return None
        axis_ratio = (2 + h) / (2 - h)
        gaps.append(1.5 * np.log(axis_ratio))
    return np.array(gaps)


def simulate_system(system, ratios, draws, min_hill, rng):
    periods = system["periods"]
    n_planets = len(periods)
    log_inner, log_outer = np.log(periods[[0, -1]])
    total_gap = log_outer - log_inner
    minimum_gaps = minimum_log_period_gaps(system["planet_masses"], system["mass"], min_hill)
    if minimum_gaps is None or minimum_gaps.sum() > total_gap + 1e-12:
        return np.array([]), 0

    # Ordered uniform interior points induce Dirichlet(1,...,1) gaps.
    # Conditioning on gap_i >= minimum_i translates the simplex by the
    # minimum gaps; the residual gaps remain uniformly Dirichlet.
    free_gap = max(0.0, total_gap - minimum_gaps.sum())
    accepted = []
    for _ in range(draws):
        extra_gaps = rng.dirichlet(np.ones(n_planets - 1)) * free_gap
        gaps = minimum_gaps + extra_gaps
        randomized = np.exp(np.concatenate(([log_inner], log_inner + np.cumsum(gaps))))
        accepted.append(bond_fraction(randomized, ratios))
    return np.array(accepted), draws


def bootstrap_mean_ci(values, rng, repetitions=20000):
    values = np.asarray(values, dtype=float)
    samples = rng.choice(values, size=(repetitions, len(values)), replace=True).mean(axis=1)
    return float(values.mean()), [float(x) for x in np.percentile(samples, [2.5, 97.5])]


def quadratic_test(masses, responses):
    masses = np.asarray(masses, dtype=float)
    responses = np.asarray(responses, dtype=float)
    design = np.column_stack((np.ones(len(masses)), masses, masses ** 2))
    beta = np.linalg.lstsq(design, responses, rcond=None)[0]
    residual = responses - design @ beta
    dof = len(responses) - design.shape[1]
    mse = np.sum(residual ** 2) / dof
    covariance = mse * np.linalg.inv(design.T @ design)
    standard_error = np.sqrt(covariance[2, 2])
    statistic = beta[2] / standard_error
    p_one_tailed = 1 - stats.t.cdf(statistic, dof)
    return {"beta2": float(beta[2]), "t": float(statistic), "p_one_tailed": float(p_one_tailed)}


def permutation_tests(records, rng, repetitions=20000):
    bins = np.array([record["bin"] for record in records])
    residuals = np.array([record["residual"] for record in records])
    masses = np.array([record["mass"] for record in records])
    observed_means = {key: residuals[bins == key].mean() for key in KEYS}
    observed_range = max(observed_means.values()) - min(observed_means.values())
    observed_quad = quadratic_test(masses, residuals)["beta2"]
    range_count = 0
    quad_count = 0
    for _ in range(repetitions):
        permuted = rng.permutation(residuals)
        means = {key: permuted[bins == key].mean() for key in KEYS}
        if max(means.values()) - min(means.values()) >= observed_range:
            range_count += 1
        if quadratic_test(masses, permuted)["beta2"] >= observed_quad:
            quad_count += 1
    return {
        "omnibus_bin_range_p": (range_count + 1) / (repetitions + 1),
        "quadratic_permutation_p": (quad_count + 1) / (repetitions + 1),
    }


def interval_coverage(ratios, lower=1.0, upper=4.0, tolerance=0.03):
    intervals = sorted(
        (max(lower, value * (1 - tolerance)), min(upper, value * (1 + tolerance)))
        for value in ratios.values()
        if value * (1 + tolerance) >= lower and value * (1 - tolerance) <= upper
    )
    merged = []
    for start, end in intervals:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    linear = sum(end - start for start, end in merged) / (upper - lower)
    log = sum(np.log(end / start) for start, end in merged) / np.log(upper / lower)
    return {"domain": [lower, upper], "linear_fraction": linear, "log_fraction": log, "merged": merged}


def analyze(systems, ratios, draws, min_hill, seed):
    rng = np.random.default_rng(seed)
    records = []
    incomplete = []
    for index, system in enumerate(systems, 1):
        null, attempts = simulate_system(system, ratios, draws, min_hill, rng)
        if len(null) < draws:
            incomplete.append({"host": system["host"], "accepted": len(null), "attempts": attempts})
        if len(null) == 0:
            continue
        observed = bond_fraction(system["periods"], ratios)
        records.append({
            "host": system["host"], "mass": system["mass"], "bin": system["bin"],
            "n_planets": len(system["periods"]), "observed": observed,
            "null_mean": float(null.mean()), "null_sd": float(null.std(ddof=1)),
            "residual": observed - float(null.mean()), "accepted": len(null), "attempts": attempts,
        })

    summary = {}
    for key in KEYS:
        subset = [record for record in records if record["bin"] == key]
        residuals = [record["residual"] for record in subset]
        observed = [record["observed"] for record in subset]
        null_means = [record["null_mean"] for record in subset]
        mean_residual, residual_ci = bootstrap_mean_ci(residuals, rng)
        p_two_sided = stats.ttest_1samp(residuals, 0).pvalue
        summary[key] = {
            "n_systems": len(subset),
            "observed_system_mean": float(np.mean(observed)),
            "null_system_mean": float(np.mean(null_means)),
            "mean_residual": mean_residual,
            "residual_bootstrap_95ci": residual_ci,
            "residual_ttest_p_two_sided": float(p_two_sided),
        }
    qtest = quadratic_test([record["mass"] for record in records], [record["residual"] for record in records])
    ptests = permutation_tests(records, rng)
    return records, {"bins": summary, "quadratic": qtest, "permutation": ptests, "incomplete": incomplete}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--draws", type=int, default=2000)
    parser.add_argument("--hill", type=float, default=8)
    parser.add_argument("--seed", type=int, default=20260711)
    parser.add_argument("--mass-strategy", choices=("first", "median"), default="first")
    parser.add_argument("--transit-only", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("system_level_results.json"))
    args = parser.parse_args()

    systems, diagnostics = load_systems(
        args.csv, require_three_valid=True, mass_strategy=args.mass_strategy,
        transit_only=args.transit_only,
    )
    result = {
        "config": {"draws_per_system": args.draws, "min_hill": args.hill, "seed": args.seed,
                   "mass_strategy": args.mass_strategy, "transit_only": args.transit_only},
        "sample": {"systems": len(systems), "bins": Counter(s["bin"] for s in systems), "diagnostics": diagnostics},
        "coverage": {
            "full_1_to_4": interval_coverage(FULL_RATIOS),
            "first_order_1_to_4": interval_coverage(FIRST_ORDER_RATIOS),
        },
        "analyses": {},
    }
    all_records = {}
    for offset, (name, ratios) in enumerate((("full", FULL_RATIOS), ("first_order", FIRST_ORDER_RATIOS))):
        records, summary = analyze(systems, ratios, args.draws, args.hill, args.seed + offset)
        result["analyses"][name] = summary
        all_records[name] = records

    args.output.write_text(json.dumps(result, indent=2, default=lambda value: dict(value)))
    records_path = args.output.with_name(args.output.stem + "_systems.csv")
    with records_path.open("w", newline="") as handle:
        fieldnames = ["analysis"] + list(next(iter(all_records.values()))[0].keys())
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for analysis, records in all_records.items():
            for record in records:
                writer.writerow({"analysis": analysis, **record})
    print(json.dumps(result, indent=2, default=lambda value: dict(value)))


if __name__ == "__main__":
    main()
