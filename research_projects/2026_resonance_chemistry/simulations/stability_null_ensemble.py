#!/usr/bin/env python3
"""
stability_null_ensemble.py — §5.5 stability-filtered null ensemble (v4.0)

Produces a stability-filtered null distribution of near-commensurability
fractions by randomizing orbital periods within stable bounds (Hill
criterion > 8 R_H) while preserving observed inner/outer boundaries and
planet masses. Returns pair-weighted bond fractions for each mass bin,
used to compute Δf = observed − null for Figure 3.

Usage:
    python3 stability_null_ensemble.py

Output: prints observed, null, and Δf values per mass bin.
"""

import csv, math, random
from collections import defaultdict

random.seed(42)

# ── Config ──
DATA_PATH   = '/root/.openclaw/workspace/Vela2_ssh/research_projects/2026_resonance_chemistry/data/multi_planet_systems.csv'
N_DRAWS     = 500          # stable randomizations per system
MIN_HILL    = 8            # minimum mutual Hill radius separation
TOLERANCE   = 0.03         # ≤3% from exact commensurability = near-resonant

# Resonance targets
RES = {
    '3:2': 1.500, '2:1': 2.000, '4:3': 4/3,  '5:3': 5/3,
    '5:4': 1.250, '7:5': 1.400, '8:5': 1.600, '9:5': 1.800,
    '7:3': 7/3,   '5:2': 2.500, '8:3': 8/3,   '3:1': 3.000,
    '7:2': 3.500, '4:1': 4.000,
}
KEYS = ['M', 'K', 'G', 'F']  # mass bins

# ── Helpers ──
def sf(v):
    """Safe float conversion."""
    try: return float(v) if v and str(v).strip() else float('nan')
    except: return float('nan')

def star_bin(m):
    """Classify stellar mass into bin."""
    if math.isnan(m) or m <= 0: return None
    if m < 0.6:   return 'M'
    if m < 0.9:   return 'K'
    if m < 1.1:   return 'G'
    if m < 1.6:   return 'F'
    return None

def classify(pr):
    """Classify period ratio as nearest integer ratio within tolerance."""
    best, bdev = None, float('inf')
    for name, exc in RES.items():
        dev = abs(pr / exc - 1)
        if dev < bdev:
            best, bdev = name, dev
    return (best, bdev * 100) if bdev <= TOLERANCE else (None, None)

def period_to_a(P_days, M_sun):
    """Convert orbital period (days) to semimajor axis (au) via Kepler."""
    return (((P_days / 365.25) ** 2) * M_sun) ** (1/3)

def planet_mass_earth(p):
    """Estimate planet mass (M_E) — use bmassj if available, else radius-based."""
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
    return 5.0  # Earth-size fallback

# ── Load data ──
print(f"Loading data from {DATA_PATH} …")
raw = defaultdict(list)
with open(DATA_PATH) as f:
    for r in csv.DictReader(f):
        raw[r['hostname']].append(r)

print(f"  {len(raw)} host systems, {sum(len(v) for v in raw.values())} planets")

# ── Build system data ──
system_data = []
for host, planets in raw.items():
    if len(planets) < 3: continue
    masses = [sf(p['st_mass']) for p in planets if not math.isnan(sf(p['st_mass']))]
    if not masses: continue
    bin_ = star_bin(masses[0])
    if not bin_: continue
    star_mass = masses[0]

    valid = sorted([
        (sf(p['pl_orbper']), p) for p in planets
        if not math.isnan(sf(p['pl_orbper'])) and 0.5 <= sf(p['pl_orbper']) <= 1e4
    ])
    periods = [v[0] for v in valid]
    vplanets = [v[1] for v in valid]
    if len(periods) < 2: continue

    bonds = []
    for i in range(len(periods) - 1):
        pr = periods[i + 1] / periods[i]
        name, dev = classify(pr)
        if name: bonds.append((name, dev))

    n_pairs = len(periods) - 1
    system_data.append({
        'host': host, 'mass': star_mass, 'type': bin_,
        'bond_frac': len(bonds) / n_pairs * 100,
        'n_pairs': n_pairs, 'n_bonds': len(bonds),
        'bonds': bonds, 'periods': periods, 'vplanets': vplanets,
    })

cnt_str = ', '.join(f"{t}={sum(1 for sd in system_data if sd['type']==t)}" for t in KEYS)
print(f'  {len(system_data)} selected systems ({cnt_str})')

# Group by type
td = defaultdict(list)
for sd in system_data:
    td[sd['type']].append(sd)

# ── Observed (pair-weighted) ──
OBS_PW = {}
for t in KEYS:
    tb = sum(sd['n_bonds'] for sd in td[t])
    tp = sum(sd['n_pairs'] for sd in td[t])
    OBS_PW[t] = tb / tp * 100 if tp > 0 else 0

print("\nObserved pair-weighted bond fractions:")
for t in KEYS:
    print(f"  {t}: {OBS_PW[t]:.1f}%")

# ── Stability-filtered null ensemble ──
print(f"\nRunning null ensemble ({N_DRAWS} stable draws/system, Hill > {MIN_HILL} R_H) …")

null_bonds_pw = defaultdict(int)
null_pairs_pw = defaultdict(int)

for sd in system_data:
    bin_   = sd['type']
    M_sun  = sd['mass']
    perds  = sd['periods']
    vps    = sd['vplanets']
    n_pl   = len(perds)
    if n_pl < 3: continue

    P_in, P_out = perds[0], perds[-1]
    if P_out <= P_in: continue
    log_in, log_out = math.log(P_in), math.log(P_out)

    planet_masses = [planet_mass_earth(p) for p in vps]
    M_sun_earth   = M_sun * 332946

    stable_count = 0
    attempts     = 0
    max_attempts = N_DRAWS * 8

    while stable_count < N_DRAWS and attempts < max_attempts:
        attempts += 1
        interior = sorted(random.uniform(log_in, log_out) for _ in range(n_pl - 2))
        rand_p   = [P_in] + [math.exp(x) for x in interior] + [P_out]
        rand_a   = [period_to_a(p, M_sun) for p in rand_p]

        ok = True
        for i in range(n_pl - 1):
            a_mean = (rand_a[i] + rand_a[i + 1]) / 2
            R_H = a_mean * (
                (planet_masses[i] + planet_masses[i + 1]) / (3 * M_sun_earth)
            ) ** (1/3)
            if R_H <= 0 or (rand_a[i + 1] - rand_a[i]) / R_H < MIN_HILL:
                ok = False
                break
        if not ok: continue

        stable_count += 1
        for i in range(n_pl - 1):
            null_pairs_pw[bin_] += 1
            name, _ = classify(rand_p[i + 1] / rand_p[i])
            if name:
                null_bonds_pw[bin_] += 1

NULL = {}
for t in KEYS:
    if null_pairs_pw[t] > 0:
        NULL[t] = null_bonds_pw[t] / null_pairs_pw[t] * 100
    else:
        NULL[t] = float('nan')

DELTA_F = {t: OBS_PW[t] - NULL[t] for t in KEYS}

# ── Results ──
print("\n" + "=" * 65)
print("  STABILITY-FILTERED NULL ENSEMBLE RESULTS")
print("=" * 65)
print(f"  {'Type':>4}  {'Obs PW%':>7}  {'Null%':>6}  {'Δf%':>5}")
for t in KEYS:
    print(f"  {t:>4}  {OBS_PW[t]:>6.1f}%  {NULL[t]:>5.1f}%  {DELTA_F[t]:>+4.1f}")
print("=" * 65)
print(f"\nNull computed from {N_DRAWS} stable draws/system, Hill > {MIN_HILL} R_H.")
print("Bond fractions are pair-weighted (not system-averaged).")
print("Near-commensurability = ≤3% of exact integer ratio.\n")
