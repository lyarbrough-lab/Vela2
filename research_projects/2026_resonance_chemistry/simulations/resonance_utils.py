#!/usr/bin/env python3
"""
resonance_utils.py — Shared helpers for the resonance chemistry analysis.

Used by stability_null_ensemble.py and generate_figures.py.
"""

import math, numpy as np
from scipy import stats as sp_stats

# ── Mass-bin limits ──
BIN_LIMS = [('M', 0, 0.6), ('K', 0.6, 0.9), ('G', 0.9, 1.1), ('F', 1.1, 1.6)]
KEYS = ['M', 'K', 'G', 'F']

# Resonance targets (all integer ratios used)
RES = {
    '3:2': 1.500, '2:1': 2.000, '4:3': 4/3,  '5:3': 5/3,
    '5:4': 1.250, '7:5': 1.400, '8:5': 1.600, '9:5': 1.800,
    '7:3': 7/3,   '5:2': 2.500, '8:3': 8/3,   '3:1': 3.000,
    '7:2': 3.500, '4:1': 4.000,
}
TOLERANCE = 0.03   # within 3% = bonded

# ── Helpers ──

def sf(v, default=float('nan')):
    """Safe float conversion."""
    try: return float(v) if v and str(v).strip() else default
    except: return default

def star_bin(m):
    """Classify stellar mass into bin label (M/K/G/F) or None."""
    if math.isnan(m) or m <= 0: return None
    if m < 0.6:   return 'M'
    if m < 0.9:   return 'K'
    if m < 1.1:   return 'G'
    if m < 1.6:   return 'F'
    return None

def classify(pr):
    """Nearest integer ratio within tolerance; returns (name, %deviation) or (None, None)."""
    best, bdev = None, float('inf')
    for name, exc in RES.items():
        dev = abs(pr / exc - 1)
        if dev < bdev:
            best, bdev = name, dev
    return (best, bdev * 100) if bdev <= TOLERANCE else (None, None)

def bootstrap_ci(arr, n=10000, ci=95):
    """Bootstrap 95% CI on the mean of arr."""
    if len(arr) < 2:
        return float(np.mean(arr)) if arr else 0, 0, 0
    boots = [np.mean(np.random.choice(arr, len(arr), replace=True)) for _ in range(n)]
    lo = np.percentile(boots, (100 - ci) / 2)
    hi = np.percentile(boots, 100 - (100 - ci) / 2)
    return float(np.mean(boots)), float(lo), float(hi)

def u_shape_permutation_test(bf_by_type, n_perm=100000, seed=42):
    """
    Strict U-ordering permutation test: M > K > G < F.
    Returns empirical p-value for observing the ordered pattern by chance.
    """
    nm, nk, ng, nf = [len(bf_by_type[t]) for t in KEYS]
    pool = np.concatenate([bf_by_type[t] for t in KEYS])
    count = 0
    np.random.seed(seed)
    for _ in range(n_perm):
        perm = np.random.permutation(pool)
        pm = np.mean(perm[:nm])
        pk = np.mean(perm[nm:nm+nk])
        pg = np.mean(perm[nm+nk:nm+nk+ng])
        pf = np.mean(perm[nm+nk+ng:])
        if pm > pk > pg and pf > pg:
            count += 1
    return (count + 1) / (n_perm + 1)

def quadratic_ubend_test(m_arr, b_arr):
    """
    One-tailed test for β₂ > 0 in b ~ β₀ + β₁m + β₂m².
    Returns (beta2, t_stat, p_value).
    """
    X = np.column_stack([np.ones_like(m_arr), m_arr, m_arr**2])
    betas = np.linalg.lstsq(X, b_arr, rcond=None)[0]
    resid = b_arr - X @ betas
    mse = np.sum(resid**2) / (len(b_arr) - 3)
    se_b2 = np.sqrt(mse * np.linalg.inv(X.T @ X)[2, 2])
    t_stat = betas[2] / se_b2
    p_val = float(1 - sp_stats.t.cdf(t_stat, len(b_arr) - 3))
    return float(betas[2]), float(t_stat), p_val

def period_to_a(P_days, M_sun):
    """Kepler: P[yr]² × M_sun = a[au]³"""
    return (((P_days / 365.25) ** 2) * M_sun) ** (1/3)

def planet_mass_earth(p):
    """Estimate planet mass in M_Earth — use bmassj if available, else radius-based."""
    m = sf(p.get('pl_bmassj', ''))
    if not math.isnan(m) and m > 0.0001:
        return m * 317.8
    r = sf(p.get('pl_radj', ''))
    if not math.isnan(r) and r > 0:
        R_e = r * 11.21
        if R_e <= 1.0:   return R_e ** 2.5
        if R_e <= 1.5:   return R_e ** 2.0
        if R_e <= 4.0:   return R_e ** 1.5
        if R_e <= 8.0:   return R_e ** 1.2
        return R_e ** 1.0
    return 5.0

def load_data(csv_path):
    """
    Load multi_planet_systems CSV, return list of system dicts with:
      host, mass, type, bond_frac, n_pairs, n_bonds, bonds, periods, vplanets
    """
    import csv
    from collections import defaultdict

    raw = defaultdict(list)
    with open(csv_path) as f:
        for r in csv.DictReader(f):
            raw[r['hostname']].append(r)

    systems = []
    for host, planets in raw.items():
        if len(planets) < 3: continue
        masses = [sf(p['st_mass']) for p in planets if not math.isnan(sf(p['st_mass']))]
        if not masses: continue
        bin_ = star_bin(masses[0])
        if not bin_: continue

        valid = sorted([
            (sf(p['pl_orbper']), p) for p in planets
            if not math.isnan(sf(p['pl_orbper'])) and 0.5 <= sf(p['pl_orbper']) <= 1e4
        ])
        periods = [v[0] for v in valid]
        vplanets = [v[1] for v in valid]
        if len(periods) < 2: continue

        bonds = []
        for i in range(len(periods) - 1):
            name, dev = classify(periods[i+1] / periods[i])
            if name: bonds.append((name, dev))

        n_pairs = len(periods) - 1
        systems.append({
            'host': host, 'mass': masses[0], 'type': bin_,
            'bond_frac': len(bonds) / n_pairs * 100,
            'n_pairs': n_pairs, 'n_bonds': len(bonds),
            'bonds': bonds, 'periods': periods, 'vplanets': vplanets,
        })

    return systems
