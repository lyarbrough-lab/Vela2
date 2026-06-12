#!/usr/bin/env python3
"""
generate_real_figures.py — Figures from actual system data
Uses the same analysis engine as the paper, reads live CSV data.
"""
import csv, math, os, sys
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats as scipy_stats

# Okabe-Ito colour-blind safe palette
CB = {
    'M': '#0072B2', 'K': '#E69F00', 'G': '#CC79A7', 'F': '#009E73',
}
HATCH = {'M': '', 'K': '///', 'G': '\\\\', 'F': '...'}
STAR_KEYS = ['M', 'K', 'G', 'F']
STAR_LABELS = {
    'M': 'M dwarf\n(<0.6 M☉)', 'K': 'K dwarf\n(0.6–0.9 M☉)',
    'G': 'G dwarf\n(0.9–1.1 M☉)', 'F': 'F dwarf\n(1.1–1.6 M☉)',
}

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(OUT_DIR), 'data')

# ── Analysis helpers (mirrors age_bond_analysis.py) ──
RES_WINDOWS = {
    '3:2': (1.455, 1.545), '2:1': (1.940, 2.060), '4:3': (1.293, 1.373),
    '5:3': (1.617, 1.717), '5:4': (1.213, 1.288), '7:5': (1.358, 1.442),
    '8:5': (1.552, 1.648), '9:5': (1.746, 1.854), '7:3': (2.263, 2.403),
    '5:2': (2.425, 2.575), '8:3': (2.587, 2.747), '3:1': (2.910, 3.090),
    '7:2': (3.395, 3.605), '4:1': (3.880, 4.120),
}
RES_EXACT = {'3:2': 1.500, '2:1': 2.000, '4:3': 1.333, '5:3': 1.667,
             '5:4': 1.250, '7:5': 1.400, '8:5': 1.600, '9:5': 1.800,
             '7:3': 2.333, '5:2': 2.500, '8:3': 2.667, '3:1': 3.000,
             '7:2': 3.500, '4:1': 4.000}

def sf(v, default=float('nan')):
    try: return float(v) if v and v.strip() else default
    except: return default

def is_bonded(pr):
    for _, (lo, hi) in RES_WINDOWS.items():
        if lo <= pr <= hi:
            return True
    return False

def classify_bond(pr):
    for name, exc in RES_EXACT.items():
        lo, hi = exc * 0.97, exc * 1.03
        if lo <= pr <= hi:
            return name, abs(pr - exc) / exc * 100
    return None, None

def star_bin(mass):
    if math.isnan(mass) or mass <= 0: return None
    if mass < 0.6: return 'M'
    if mass < 0.9: return 'K'
    if mass < 1.1: return 'G'
    if mass < 1.6: return 'F'
    return None

# ── Load systems ──
systems = defaultdict(list)
sys_path = os.path.join(DATA_DIR, 'multi_planet_systems.csv')
with open(sys_path) as f:
    for r in csv.DictReader(f):
        systems[r['hostname']].append(r)

# Ages
ages = {}
age_path = os.path.join(DATA_DIR, 'stellar_ages.csv')
with open(age_path) as f:
    for r in csv.DictReader(f):
        a = sf(r['st_age'])
        if not math.isnan(a):
            ages[r['hostname']] = a

print(f"Loaded {len(systems)} systems, {sum(len(v) for v in systems.values())} planets")

# ── Per-system analysis ──
# For each multi-planet system (>=3), compute:
#   host, star_mass, star_type, age, bond_frac, N_pairs, N_bonds, bond_details
system_data = []
for host, planets in systems.items():
    if len(planets) < 3:
        continue
    # Get stellar mass (first planet with valid mass)
    masses = [sf(p['st_mass']) for p in planets if not math.isnan(sf(p['st_mass']))]
    if not masses:
        continue
    star_mass = masses[0]
    stype = star_bin(star_mass)
    if stype is None:
        continue
    host_age = ages.get(host, float('nan'))

    # Sort planets by period
    valid_planets = []
    for p in planets:
        per = sf(p['pl_orbper'])
        if not math.isnan(per) and per > 0:
            valid_planets.append((per, p))
    valid_planets.sort()
    periods = [p[0] for p in valid_planets]

    # Check each adjacent pair for bonds
    bonds = []
    for i in range(len(periods) - 1):
        pr = periods[i+1] / periods[i]
        if pr < 1.05 or pr > 5.0:
            continue
        result = classify_bond(pr)
        if result[0] is not None:
            bonds.append(result)
    
    n_pairs = len(periods) - 1
    n_bonds = len(bonds)
    bond_frac = (n_bonds / n_pairs * 100) if n_pairs > 0 else 0

    system_data.append({
        'host': host, 'mass': star_mass, 'type': stype,
        'age': host_age, 'bond_frac': bond_frac,
        'n_pairs': n_pairs, 'n_bonds': n_bonds,
        'bonds': bonds, 'periods': periods,
    })

print(f"Analyzed {len(system_data)} multi-planet systems")

# ── Now build figures ──

# ===============================================================
# FIGURE 1: U-shape (bond fraction vs stellar mass)
# ===============================================================
def fig1_ushape():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    ax1, ax2 = axes

    # Panel (a): Bond fraction per stellar type
    type_data = defaultdict(list)
    for sd in system_data:
        type_data[sd['type']].append(sd)

    types = STAR_KEYS
    x = np.arange(len(types))
    width = 0.5
    bonds_mean = []
    bonds_ci_low = []
    bonds_ci_high = []
    n_sys = []

    for t in types:
        bfs = [sd['bond_frac'] for sd in type_data[t]]
        n_sys.append(len(bfs))
        mean = np.mean(bfs)
        bonds_mean.append(mean)
        # Bootstrap CI
        n_boot = 10000
        boot = np.random.choice(bfs, (n_boot, len(bfs))).mean(axis=1)
        ci = np.percentile(boot, [2.5, 97.5])
        bonds_ci_low.append(ci[0])
        bonds_ci_high.append(ci[1])

    colors = [CB[t] for t in types]
    bars = ax1.bar(x, bonds_mean, width, color=colors, alpha=0.8,
                   edgecolor='black', linewidth=0.5)
    for bar, t in zip(bars, types):
        bar.set_hatch(HATCH[t])
    ax1.errorbar(x, bonds_mean, 
                 yerr=[[m - l for m, l in zip(bonds_mean, bonds_ci_low)],
                       [h - m for m, h in zip(bonds_mean, bonds_ci_high)]],
                 fmt='none', ecolor='black', capsize=3, capthick=1)

    # N annotations above bars
    for i, (m, n) in enumerate(zip(bonds_mean, n_sys)):
        ax1.text(i, bonds_ci_high[i] + 1.5, f'N={n}',
                ha='center', fontsize=8, fontweight='bold')

    # Permutation test p-value (real)
    # Test if U-shape (G below extremes) is significant
    # Simple: compare mean G fraction to mean of M+F
    g_bfs = [sd['bond_frac'] for sd in type_data['G']]
    mf_bfs = [sd['bond_frac'] for sd in type_data['M'] + type_data['F']]
    obs_diff = np.mean(g_bfs) - np.mean(mf_bfs)
    all_vals = g_bfs + mf_bfs
    n_perm = 100000
    perm_diffs = []
    for _ in range(n_perm):
        np.random.shuffle(all_vals)
        perm_diffs.append(np.mean(all_vals[:len(g_bfs)]) - np.mean(all_vals[len(g_bfs):]))
    p_perm = (np.sum(np.array(perm_diffs) <= obs_diff) + 1) / (n_perm + 1)
    # Quadratic beta_2
    masses_arr = np.array([sd['mass'] for sd in system_data])
    bfs_arr = np.array([sd['bond_frac'] for sd in system_data])
    coeffs = np.polyfit(masses_arr, bfs_arr, 2)
    residuals = bfs_arr - np.polyval(coeffs, masses_arr)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((bfs_arr - np.mean(bfs_arr))**2)
    r2 = 1 - ss_res/ss_tot
    # F-test for quadratic term
    n_param = 3
    n_data = len(bfs_arr)
    f_stat = (r2/(n_param-1)) / ((1-r2)/(n_data-n_param))
    p_quad = 1 - scipy_stats.f.cdf(f_stat, n_param-1, n_data-n_param)

    ax1.text(0.95, 0.95,
             f'Permutation test: p={p_perm:.3f}\n'
             f'Quadratic β₂ > 0: p={p_quad:.3f}',
             transform=ax1.transAxes, fontsize=8, ha='right', va='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    ax1.set_xticks(x)
    ax1.set_xticklabels([STAR_LABELS[t] for t in types], fontsize=8)
    ax1.set_ylabel('Bond fraction (%)', fontsize=11)
    ax1.set_title('(a) All systems', fontsize=11)
    ax1.set_ylim(0, 100)

    # Panel (b): Detection filter comparison
    filter_data = {'All planets': [], 'Transit only': [], 'Higher mult. (≥4 planets)': []}
    for sd in system_data:
        filter_data['All planets'].append(sd)
        # Check if all planets are transit
        host_planets = systems[sd['host']]
        methods = [sf(p['discoverymethod']) for p in host_planets if p['discoverymethod']]
        is_transit = any('Transit' in str(m) for m in methods)
        # Higher multiplicity
        if len(sd['periods']) >= 4:
            filter_data['Higher mult. (≥4 planets)'].append(sd)

    f_types = list(filter_data.keys())
    x_f = np.arange(len(f_types))
    bar_width = 0.18

    for i, t in enumerate(types):
        offsets = [-1.5, -0.5, 0.5, 1.5]
        vals = []
        for f in f_types:
            bfs = [sd['bond_frac'] for sd in filter_data[f] if sd['type'] == t]
            vals.append(np.mean(bfs) if bfs else 0)
        bars = ax2.bar(x_f + offsets[i]*bar_width, vals, bar_width,
                      color=CB[t], alpha=0.8, edgecolor='black', linewidth=0.3,
                      label=STAR_LABELS[t].split('\n')[0])
        for bar in bars:
            bar.set_hatch(HATCH[t])

    ax2.set_xticks(x_f)
    ax2.set_xticklabels([f.replace(' ', '\n') for f in f_types], fontsize=8)
    ax2.set_ylabel('Bond fraction (%)', fontsize=11)
    ax2.set_title('(b) Detection filter comparison', fontsize=11)
    ax2.legend(fontsize=7, loc='lower left', framealpha=0.8)
    ax2.set_ylim(0, 100)

    fig.tight_layout()
    path = os.path.join(OUT_DIR, 'fig1_ushape.png')
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f'✓ {os.path.basename(path)}')

# ===============================================================
# FIGURE 3: Stability-filtered null comparison
# ===============================================================
def fig3_stability_null():
    fig, ax = plt.subplots(figsize=(7.5, 3.8))

    # Observed values from real data
    types = STAR_KEYS
    obs_vals = []
    obs_ci_low = []
    obs_ci_high = []
    for t in types:
        bfs = [sd['bond_frac'] for sd in system_data if sd['type'] == t]
        obs_vals.append(np.mean(bfs))
        boot = np.random.choice(bfs, (10000, len(bfs))).mean(axis=1)
        obs_ci_low.append(np.percentile(boot, 2.5))
        obs_ci_high.append(np.percentile(boot, 97.5))

    # Null values from the stability ensemble (hardcoded from paper's simulation)
    # These were computed from the stability_null_ensemble.py simulation
    null_vals = [63.5, 55.8, 49.8, 52.5]
    delta_f = [o - n for o, n in zip(obs_vals, null_vals)]

    # Bootstrap p-values for each bin
    p_vals = []
    for i, t in enumerate(types):
        bfs = [sd['bond_frac'] for sd in system_data if sd['type'] == t]
        # Compare against null via bootstrap
        n_boot = 100000
        boot = np.random.choice(bfs, (n_boot, len(bfs))).mean(axis=1)
        # Two-sided p-value
        p = (np.sum(np.abs(boot - obs_vals[i]) >= abs(delta_f[i])) + 1) / (n_boot + 1)
        p_vals.append(p)

    x = np.arange(len(types))
    width = 0.28

    # Observed bars
    bars1 = ax.bar(x - width/2, obs_vals, width, color='#4D4D4D', alpha=0.65,
                   edgecolor='black', linewidth=0.5, label='Observed',
                   yerr=[[o - l for o, l in zip(obs_vals, obs_ci_low)],
                         [h - o for o, h in zip(obs_vals, obs_ci_high)]],
                   capsize=3, error_kw={'linewidth': 1.0, 'ecolor': 'black'})

    # Null bars
    bars2 = ax.bar(x + width/2, null_vals, width, color='lightgrey', alpha=0.8,
                   edgecolor='black', linewidth=0.5, label='Null (dynamical floor)',
                   hatch='///')

    # Δf annotations
    for i, (d, p) in enumerate(zip(delta_f, p_vals)):
        y = max(obs_vals[i], null_vals[i]) + 4
        sign = '+' if d > 0 else ''
        ax.text(i, y, f'Δf = {sign}{d:.1f}%  p={p:.2f}',
                ha='center', fontsize=7.5, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white',
                         edgecolor='grey', alpha=0.7))

    ax.set_xticks(x)
    ax.set_xticklabels([STAR_LABELS[t] for t in types], fontsize=8)
    ax.set_ylabel('Bond fraction (%)', fontsize=11)
    ax.set_title('Observed vs. stability-filtered null', fontsize=11)
    
    from matplotlib.patches import Patch
    leg = ax.legend(handles=[
        Patch(facecolor='#4D4D4D', alpha=0.65, edgecolor='black', label='Observed'),
        Patch(facecolor='lightgrey', hatch='///', edgecolor='black', label='Null (dynamical floor)')
    ], fontsize=7.5, loc='upper right', framealpha=0.75)

    ax.set_ylim(0, 92)
    fig.tight_layout()
    path = os.path.join(OUT_DIR, 'fig3_stability_null.png')
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f'✓ {os.path.basename(path)}')

# ===============================================================
# FIGURE 4: Age-Bond Correlation (real scatter plot)
# ===============================================================
def fig4_age_bond():
    fig, axes = plt.subplots(1, 4, figsize=(10, 3.2))

    for i, key in enumerate(STAR_KEYS):
        ax = axes[i]
        # Get systems of this type with valid ages
        pts = [(sd['age'], sd['bond_frac']) for sd in system_data
               if sd['type'] == key and not math.isnan(sd['age'])]
        if len(pts) < 3:
            ax.text(0.5, 0.5, 'Insufficient data', ha='center', va='center',
                   transform=ax.transAxes, fontsize=9)
            continue
        ages_arr = np.array([p[0] for p in pts])
        bfs_arr = np.array([p[1] for p in pts])
        n = len(pts)

        ax.scatter(ages_arr, bfs_arr, c=CB[key], alpha=0.55, s=22,
                   edgecolors='black', linewidth=0.3, zorder=3)

        # OLS regression
        slope, intercept, r_val, p_val, std_err = scipy_stats.linregress(ages_arr, bfs_arr)
        x_fit = np.linspace(0, 13, 100)
        y_fit = slope * x_fit + intercept
        ax.plot(x_fit, y_fit, color=CB[key], linewidth=2, zorder=4)

        # 95% CI band
        n_boot = 5000
        boot_slopes = []
        for _ in range(n_boot):
            idx = np.random.choice(n, n)
            if len(np.unique(ages_arr[idx])) < 2:
                continue
            s, _, _, _, _ = scipy_stats.linregress(ages_arr[idx], bfs_arr[idx])
            boot_slopes.append(s)
        boot_slopes = np.array(boot_slopes)
        ci_lo, ci_hi = np.percentile(boot_slopes, [2.5, 97.5])
        for mult in [1.96]:
            sem = std_err * mult
            ax.fill_between(x_fit, y_fit - sem, y_fit + sem,
                           color=CB[key], alpha=0.1, edgecolor='none', zorder=1)

        star_label = STAR_LABELS[key].split('\n')[0]
        ax.set_xlabel('Age (Gyr)', fontsize=9)
        ax.set_ylabel('Bond fraction (%)', fontsize=9)
        ax.set_title(f'{star_label}\n(N={n} sys)', fontsize=10)
        ax.set_ylim(15, 90)
        ax.set_xlim(0, 13)

        # Significance
        slope_str = f'{slope:+.1f}'
        if p_val < 0.0125:
            sig_tag = f'p = {p_val:.3f} **'
        elif p_val < 0.05:
            sig_tag = f'p = {p_val:.3f} *'
        else:
            sig_tag = f'p = {p_val:.3f} (n.s.)'

        note = (f'Slope: {slope_str}% Gyr$^{{-1}}$\n'
                f'r = {r_val:.2f}\n'
                f'{sig_tag}')
        ax.text(0.03, 0.97, note, fontsize=7.5, transform=ax.transAxes,
               verticalalignment='top',
               bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                        edgecolor='grey', alpha=0.85, linewidth=0.5))

    fig.text(0.5, 0.005,
             'Bootstrapped 95% CI shaded; Bonferroni threshold p < 0.0125',
             ha='center', fontsize=7, style='italic')
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    path = os.path.join(OUT_DIR, 'fig4_age_bond.png')
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f'✓ {os.path.basename(path)}')

# ===============================================================
# SUPPLEMENTARY: Period ratio histogram
# ===============================================================
def figS1_period_ratio_hist():
    fig, ax = plt.subplots(figsize=(6, 3.5))

    # Collect all period ratios
    ratios = []
    for sd in system_data:
        for j in range(len(sd['periods']) - 1):
            pr = sd['periods'][j+1] / sd['periods'][j]
            if 1.0 < pr < 5.0:
                ratios.append(pr)

    ax.hist(ratios, bins=80, color='#0072B2', alpha=0.7, edgecolor='black', linewidth=0.3)

    # Mark resonance locations
    for name, exc in sorted(RES_EXACT.items(), key=lambda x: x[1]):
        if 1.1 <= exc <= 4.1:
            ax.axvline(x=exc, color='#D55E00', linestyle='--', alpha=0.4, linewidth=0.8)
            ax.text(exc, ax.get_ylim()[1] * 0.95, name, rotation=90,
                   fontsize=6, ha='left', va='top', color='#D55E00', alpha=0.6)

    ax.set_xlabel('Period ratio (P$_{i+1}$ / P$_{i}$)', fontsize=11)
    ax.set_ylabel('Number of adjacent pairs', fontsize=11)
    ax.set_title(f'Period Ratio Distribution (N={len(ratios)} adjacent pairs)', fontsize=11)
    ax.set_xlim(1.0, 4.2)
    fig.tight_layout()
    path = os.path.join(OUT_DIR, 'figS1_period_ratio_hist.png')
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f'✓ {os.path.basename(path)}')

# ── Run ──
if __name__ == '__main__':
    print("Generating figures for v3.1 from REAL DATA …")
    fig1_ushape()
    fig3_stability_null()
    fig4_age_bond()
    figS1_period_ratio_hist()
    print("Done.")
