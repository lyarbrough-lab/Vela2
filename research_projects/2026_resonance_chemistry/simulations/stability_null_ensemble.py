#!/usr/bin/env python3
"""
stability_null_ensemble.py — §5.5 simulation

Build a stability-filtered null ensemble for the planetary chemistry dataset.
For each real system, randomize interior planet periods in log-period space while
preserving star mass, planet count, and orbital range. Reject systems that violate
basic Hill-stability thresholds. Measure bond fraction in the randomized ensemble
and compare to observed values.

Question: Does the U-shaped bonding curve (M/G/F) survive after controlling
for stability?
"""

import csv, math, random
from collections import defaultdict

random.seed(42)
N_RANDOMIZATIONS = 500  # per system

# ── Load dataset ──
rows = []
with open('/root/.openclaw/workspace/Vela2_ssh/datasets/exoplanets/multi_planet_systems.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

systems = defaultdict(list)
for r in rows:
    systems[r['hostname']].append(r)

print(f"Loaded {len(systems)} systems, {len(rows)} planets")

# ── Helpers ──
def sf(v):
    try: return float(v) if v else float('nan')
    except: return float('nan')

RESONANCES = {
    '3:2': 1.500, '2:1': 2.000, '4:3': 1.333, '5:3': 1.667,
    '5:4': 1.250, '7:5': 1.400, '8:5': 1.600, '9:5': 1.800,
    '7:3': 2.333, '5:2': 2.500, '8:3': 2.667, '3:1': 3.000,
    '7:2': 3.500, '4:1': 4.000,
}
RES_WINDOWS = {name: (exact * 0.97, exact * 1.03) for name, exact in RESONANCES.items()}

def classify_pair(pr):
    for name, (lo, hi) in RES_WINDOWS.items():
        if lo <= pr <= hi:
            return name
    return None

def is_bonded(pr):
    """Adjacent pair check: ±3% of any simple integer ratio"""
    return classify_pair(pr) is not None

def compute_mutual_hill(planets, M_star):
    """Compute all adjacent mutual Hill spacings."""
    rh_list = []
    for i in range(len(planets) - 1):
        p1, p2 = planets[i], planets[i+1]
        a1, a2 = sf(p1['pl_orbsmax']), sf(p2['pl_orbsmax'])
        m1, m2 = sf(p1['pl_bmassj']), sf(p2['pl_bmassj'])
        
        # Fallback: if no semi-major axis, estimate from period using M_star
        if math.isnan(a1):
            per1 = sf(p1['pl_orbper'])
            if not math.isnan(per1):
                per_days = per1
                au_per_year = 1.0  # Earth orbits at 1 AU/yr
                # From Kepler: a^3 = P^2 * M_star (in solar masses, years)
                per_years = per_days / 365.25
                a1 = (per_years ** 2 * M_star) ** (1/3)
            else:
                a1 = None
        if math.isnan(a2):
            per2 = sf(p2['pl_orbper'])
            if not math.isnan(per2):
                per_years = per2 / 365.25
                a2 = (per_years ** 2 * M_star) ** (1/3)
            else:
                a2 = None
        
        if a1 is None or a2 is None:
            continue
            
        a_mean = (a1 + a2) / 2
        m1_jup = 1 if (math.isnan(m1) or m1 <= 0) else m1
        m2_jup = 1 if (math.isnan(m2) or m2 <= 0) else m2
        # Convert Jupiter masses to Earth masses for Hill radius
        m1_earth = m1_jup * 317.8
        m2_earth = m2_jup * 317.8
        M_sun = M_star * 1047.56  # solar masses in Jupiter-mass-equivalent; convert properly
        # Mutual Hill radius
        R_H = a_mean * ((m1_earth + m2_earth) / (3 * M_star * 333000)) ** (1/3)
        # Interior planet mass also matters. Let's be precise.
        # R_H = (a1 + a2)/2 * ((m1 + m2)/(3*M_star))^(1/3)
        # Use Earth masses, solar mass
        m1_e = m1_jup * 317.8
        m2_e = m2_jup * 317.8
        R_H_exact = a_mean * ((m1_e + m2_e) / (3 * M_star * 332946)) ** (1/3)
        spacing = (a2 - a1) / R_H_exact
        rh_list.append(spacing)
    return rh_list

def stability_check(rh_list, min_hill=8):
    """Check if all adjacent Hill spacings exceed minimum."""
    return all(rh > min_hill for rh in rh_list)

def measure_bond_fraction(planets, M_star):
    """Compute bond fraction for a set of planets sorted by period."""
    planets_sorted = sorted(planets, key=lambda p: sf(p['pl_orbper']))
    total = 0
    bonded = 0
    for i in range(len(planets_sorted) - 1):
        p1, p2 = planets_sorted[i], planets_sorted[i+1]
        per1, per2 = sf(p1['pl_orbper']), sf(p2['pl_orbper'])
        if math.isnan(per1) or math.isnan(per2) or per2 <= per1:
            continue
        pr = per2 / per1
        total += 1
        if is_bonded(pr):
            bonded += 1
    return bonded, total

def randomize_system(planets, M_star):
    """Randomize interior planet periods in log period space.
    Preserve: host star mass, planet count, inner/outer periods, planet masses."""
    planets_sorted = sorted(planets, key=lambda p: sf(p['pl_orbper']))
    
    # Must have at least 3 planets
    if len(planets_sorted) < 3:
        return None
    
    # Get periods
    periods = [sf(p['pl_orbper']) for p in planets_sorted]
    if any(math.isnan(p) or p <= 0 for p in periods):
        return None
    
    # Preserve inner and outer periods
    P_inner = periods[0]
    P_outer = periods[-1]
    
    if P_outer <= P_inner:
        return None
    
    # Generate N-2 random interior periods in log space
    n_interior = len(periods) - 2
    log_inner = math.log(P_inner)
    log_outer = math.log(P_outer)
    
    if n_interior <= 0:
        return None
    
    randomized_logs = sorted([random.uniform(log_inner, log_outer) for _ in range(n_interior)])
    randomized_periods = [P_inner] + [math.exp(l) for l in randomized_logs] + [P_outer]
    
    # Create randomized planet entries (preserving all other fields)
    r_planets = []
    for i, p in enumerate(planets_sorted):
        rp = dict(p)
        rp['pl_orbper'] = str(randomized_periods[i])
        # Preserve masses for Hill calculation
        r_planets.append(rp)
    
    return r_planets

def estimate_mass_from_radius(radius_re):
    """Empirical mass-radius relation (simplified): 
    For Earth-to-Super-Earth: M ∝ R^2.0 (Lissauer+ 2011 style)
    """
    if radius_re <= 1.0:
        return radius_re ** 2.5  # rocky
    elif radius_re <= 1.5:
        return radius_re ** 2.0
    elif radius_re <= 4.0:
        return radius_re ** 1.5  # sub-Neptune
    else:
        return radius_re ** 1.2  # gas giant regime

# ═══════════════════════════════════════════════════════════════
# SIMULATION
# ═══════════════════════════════════════════════════════════════

# Collect stats by star type
star_stats = {
    'M dwarf': {'observed': [], 'null_bond': [], 'null_total': [], 'systems': 0},
    'K dwarf': {'observed': [], 'null_bond': [], 'null_total': [], 'systems': 0},
    'G dwarf': {'observed': [], 'null_bond': [], 'null_total': [], 'systems': 0},
    'F dwarf': {'observed': [], 'null_bond': [], 'null_total': [], 'systems': 0},
}

total_systems = 0
usable_systems = 0
skipped_no_mass = 0
skipped_insufficient = 0

for host, planets in systems.items():
    total_systems += 1
    p0 = planets[0]
    M_star = sf(p0['st_mass'])
    if math.isnan(M_star):
        continue
    
    if M_star < 0.6: star_type = 'M dwarf'
    elif M_star < 0.9: star_type = 'K dwarf'
    elif M_star < 1.1: star_type = 'G dwarf'
    else: star_type = 'F dwarf'
    
    # Measure observed bond fraction
    obs_bonded, obs_total = measure_bond_fraction(planets, M_star)
    if obs_total == 0:
        continue
    
    usable_systems += 1
    star_stats[star_type]['observed'].append(obs_bonded/obs_total)
    star_stats[star_type]['systems'] += 1
    
    # Randomize N_RANDOMIZATIONS times
    null_bonded_sum = 0
    null_total_sum = 0
    null_stable_count = 0
    
    for _ in range(N_RANDOMIZATIONS):
        r_planets = randomize_system(planets, M_star)
        if r_planets is None:
            continue
        
        # Hill stability check
        rh_list = compute_mutual_hill(r_planets, M_star)
        if not rh_list:
            continue
        
        # Reject unstable configurations (Hill spacing < 8)
        if not stability_check(rh_list):
            continue
        
        null_stable_count += 1
        n_bonded, n_total = measure_bond_fraction(r_planets, M_star)
        null_bonded_sum += n_bonded
        null_total_sum += n_total
    
    if null_stable_count > 10 and null_total_sum > 0:
        mean_null = null_bonded_sum / null_total_sum if null_total_sum > 0 else 0
        star_stats[star_type]['null_bond'].append(mean_null)
        star_stats[star_type]['null_total'].append(null_stable_count)

# ═══════════════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════════════

print()
print("=" * 72)
print("STABILITY-FILTERED NULL ENSEMBLE — Bond Fraction by Star Type")
print("=" * 72)
print()
print(f"{'Star Type':>12s} | {'N sys':>5s} | {'Obs f_bond':>10s} | {'Null f_bond':>11s} | {'Δf_bond':>8s} | {'σ (null)':>8s} | {'Signif':>7s}")
print("-" * 72)

for st in ['M dwarf', 'K dwarf', 'G dwarf', 'F dwarf']:
    stats = star_stats[st]
    if len(stats['observed']) < 2:
        continue
    
    obs_mean = 100 * sum(stats['observed']) / len(stats['observed'])
    
    if not stats['null_bond']:
        print(f"{st:>12s} | {stats['systems']:5d} | {obs_mean:8.2f}% | {'—':>11s} | {'—':>8s} | {'—':>8s} | {'—':>7s}")
        continue
    
    null_vals = stats['null_bond']
    null_mean = 100 * sum(null_vals) / len(null_vals)
    
    # Standard deviation of null mean across systems
    null_std = math.sqrt(sum((v - sum(null_vals)/len(null_vals))**2 for v in null_vals) / len(null_vals)) * 100 if len(null_vals) > 1 else 0
    
    delta = obs_mean - null_mean
    # Significance: delta / standard error
    se = null_std / math.sqrt(len(null_vals)) if len(null_vals) > 1 else 0
    z = delta / se if se > 0 else 0
    
    if z > 3: sig = '★★★'
    elif z > 2: sig = '★★'
    elif z > 1: sig = '★'
    else: sig = '—'
    
    print(f"{st:>12s} | {stats['systems']:5d} | {obs_mean:8.2f}% | {null_mean:9.2f}% | {delta:+7.2f}% | {obs_mean/null_mean:6.2f}x | {sig:>5s}")

print()
print("=" * 72)
print("PER-BOND-TYPE NULL ENSEMBLE")
print("(Compared to stability-filtered random systems)")
print("=" * 72)
print()

# Per-bond-type analysis: which resonances are genuinely enhanced?
bond_type_stats = defaultdict(lambda: {'obs': 0, 'null': 0, 'obs_total': 0, 'null_total': 0})

for host, planets in systems.items():
    p0 = planets[0]
    M_star = sf(p0['st_mass'])
    if math.isnan(M_star):
        continue
    
    # Observed bonds by type
    planets_sorted = sorted(planets, key=lambda p: sf(p['pl_orbper']))
    for i in range(len(planets_sorted) - 1):
        p1, p2 = planets_sorted[i], planets_sorted[i+1]
        per1, per2 = sf(p1['pl_orbper']), sf(p2['pl_orbper'])
        if math.isnan(per1) or math.isnan(per2) or per2 <= per1:
            continue
        pr = per2 / per1
        bond_type_stats['ALL']['obs_total'] += 1
        btype = classify_pair(pr)
        if btype:
            bond_type_stats[btype]['obs'] += 1
            bond_type_stats['ALL']['obs'] += 1
    
    # Null: randomize and collect bond types
    for _ in range(N_RANDOMIZATIONS // 4):
        r_planets = randomize_system(planets, M_star)
        if r_planets is None:
            continue
        rh_list = compute_mutual_hill(r_planets, M_star)
        if not rh_list or not stability_check(rh_list):
            continue
        
        r_sorted = sorted(r_planets, key=lambda p: sf(p['pl_orbper']))
        for i in range(len(r_sorted) - 1):
            p1, p2 = r_sorted[i], r_sorted[i+1]
            per1, per2 = sf(p1['pl_orbper']), sf(p2['pl_orbper'])
            if math.isnan(per1) or math.isnan(per2) or per2 <= per1:
                continue
            pr = per2 / per1
            bond_type_stats['ALL']['null_total'] += 1
            btype = classify_pair(pr)
            if btype:
                bond_type_stats[btype]['null'] += 1
                bond_type_stats['ALL']['null'] += 1

# Print per-bond-type comparison
total_obs = bond_type_stats['ALL']['obs']
total_null = bond_type_stats['ALL']['null']

print(f"{'Bond':>6s} | {'Obs count':>9s} | {'Obs frac':>9s} | {'Null count':>10s} | {'Null frac':>10s} | {'Enhance':>8s}")
print("-" * 60)

for bond in sorted(RESONANCES.keys()):
    bstats = bond_type_stats[bond]
    n_obs = bstats['obs']
    n_null = bstats['null']
    
    if n_obs == 0 and n_null == 0:
        continue
    
    frac_obs = 100 * n_obs / total_obs if total_obs > 0 else 0
    frac_null = 100 * n_null / total_null if total_null > 0 else 0
    enhance = (n_obs / total_obs) / (n_null / total_null) if n_null > 0 and total_null > 0 and total_obs > 0 else float('inf')
    
    bar = '█' * min(40, int(enhance * 5)) if enhance < float('inf') else '∞'
    print(f"  {bond:>4s} | {n_obs:9d} | {frac_obs:7.2f}% | {n_null:10d} | {frac_null:7.2f}% | {enhance:6.1f}x {bar}")

total_obs_frac = 100 * total_obs / bond_type_stats['ALL']['obs_total'] if bond_type_stats['ALL']['obs_total'] > 0 else 0
total_null_frac = 100 * total_null / bond_type_stats['ALL']['null_total'] if bond_type_stats['ALL']['null_total'] > 0 else 0
print(f"  {'ALL':>4s} | {total_obs:9d} | {total_obs_frac:7.2f}% | {total_null:10d} | {total_null_frac:7.2f}% |")

print()
print(f"Observed systems analyzed: {usable_systems}/{total_systems}")
print(f"Randomizations per system: {N_RANDOMIZATIONS}")

# ═══════════════════════════════════════════════════════════════
# NOTE
print()
print("Note: Hill stability threshold of 8 R_H is conservative for 10^8 yr stability.")
print("Systems with K2, K3, K4 (amplitudes for first few terms in the Hamiltonian)")
print("may be stable below 8 R_H for short-term. The main test is: does the observed")
print("bonding pattern survive control for random placement within stable bounds?")
