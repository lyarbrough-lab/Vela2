#!/usr/bin/env python3
"""
generate_figures.py — Generate all four paper figures from fresh data.

Usage:
    python3 generate_figures.py [--data ../data/multi_planet_systems.csv]

Output: fig1_ushape.png, fig2_tightness.png, fig3_stability_null.png,
        fig4_age_bond.png  (saved alongside this script).

Depends on resonance_utils.py (shared helpers) and the canonical CSV.
"""

import os, sys, math
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from scipy import stats as sp_stats

# Local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from resonance_utils import (
    sf, star_bin, classify, bootstrap_ci,
    u_shape_permutation_test, quadratic_ubend_test,
    period_to_a, planet_mass_earth, load_data,
    KEYS, RES, TOLERANCE,
)

# ── Plotting config ──
CB = {'M': '#0072B2', 'K': '#E69F00', 'G': '#CC79A7', 'F': '#009E73'}
HATCH = {'M': '', 'K': '///', 'G': '\\\\', 'F': '...'}
SHORT = {'M': 'M', 'K': 'K', 'G': 'G', 'F': 'F'}
LONG = {'M': 'M dwarf\n(<0.6 M☉)', 'K': 'K dwarf\n(0.6–0.9)',
        'G': 'G dwarf\n(0.9–1.1)', 'F': 'F dwarf\n(1.1–1.6)'}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = SCRIPT_DIR

def apply_hatch(bars, keys):
    """Apply hatch pattern per bar in a BarContainer."""
    for bar, k in zip(bars, keys):
        bar.set_hatch(HATCH[k])


# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL DATA: load + process + run null ensemble
# ══════════════════════════════════════════════════════════════════════════════

def run_null_ensemble(system_data):
    """Run stability-filtered null: 500 stable Hill-randomized draws/system.
    Returns (NULL, OBS_PW, DELTA_F) dicts keyed by mass bin."""
    N_DRAWS = 500
    MIN_HILL = 8

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
                if name: null_bonds_pw[bin_] += 1

    NULL = {}
    for t in KEYS:
        if null_pairs_pw[t] > 0:
            NULL[t] = null_bonds_pw[t] / null_pairs_pw[t] * 100
        else:
            NULL[t] = float('nan')

    # Observed pair-weighted
    td = defaultdict(list)
    for sd in system_data:
        td[sd['type']].append(sd)
    OBS_PW = {}
    for t in KEYS:
        tb = sum(sd['n_bonds'] for sd in td[t])
        tp = sum(sd['n_pairs'] for sd in td[t])
        OBS_PW[t] = tb / tp * 100 if tp > 0 else 0

    DELTA_F = {t: OBS_PW[t] - NULL[t] for t in KEYS}
    return NULL, OBS_PW, DELTA_F


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — U-shape
# ══════════════════════════════════════════════════════════════════════════════
def fig1(system_data, td):
    print("\n  Fig 1: U-shape …")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 4.8))

    x  = np.arange(4)
    mu = []; lo = []; hi = []; med = []; Ns = []
    for t in KEYS:
        bfs = [sd['bond_frac'] for sd in td[t]]
        m, l, h = bootstrap_ci(bfs)
        mu.append(m); lo.append(l); hi.append(h)
        med.append(float(np.median(bfs)))
        Ns.append(len(bfs))

    bars = ax1.bar(x, mu, 0.55, color=[CB[t] for t in KEYS],
                   alpha=0.85, edgecolor='black', linewidth=0.5)
    apply_hatch(bars, KEYS)
    ax1.errorbar(x, mu, yerr=[np.array(mu)-np.array(lo), np.array(hi)-np.array(mu)],
                 fmt='none', ecolor='black', capsize=3, capthick=1.5, zorder=5)
    ax1.scatter(x, med, marker='D', color='black', s=35, zorder=6, label='Median')

    for i, t in enumerate(KEYS):
        ax1.text(i, hi[i] + 2.5, f'{mu[i]:.0f}%\nN={Ns[i]}',
                 ha='center', fontsize=8, fontweight='bold')

    # U-shape permutation test
    bf_by_type = {t: [sd['bond_frac'] for sd in td[t]] for t in KEYS}
    p_perm = u_shape_permutation_test(bf_by_type)

    # Quadratic test
    m_arr  = np.array([sd['mass'] for sd in system_data])
    b_arr  = np.array([sd['bond_frac'] for sd in system_data])
    _, _, p_quad = quadratic_ubend_test(m_arr, b_arr)

    ax1.text(0.97, 0.97,
             f'U-shape tests:\nPermutation: p = {p_perm:.3f}\nQuadratic β₂ > 0: p = {p_quad:.3f}',
             transform=ax1.transAxes, fontsize=7.5, ha='right', va='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='wheat', alpha=0.4))
    ax1.annotate('G dwarfs near\ndynamical floor',
                 xy=(2, hi[2]), xytext=(2, 8), ha='center', fontsize=8, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='grey', lw=1.5),
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='grey', alpha=0.85))
    ax1.set_xticks(x); ax1.set_xticklabels([LONG[t] for t in KEYS], fontsize=8)
    ax1.set_ylabel('Bond fraction (%)', fontsize=11)
    ax1.set_title('(a) Bond fraction by stellar mass', fontsize=11)
    ax1.set_ylim(0, 90)
    ax1.legend(fontsize=8, loc='upper left')

    # panel (b) — detection filters
    all_sd      = system_data
    transit_3   = [sd for sd in system_data if sd.get('is_transit', False)]
    transit_4   = [sd for sd in system_data
                   if sd.get('is_transit', False) and len(sd['periods']) >= 4]
    # Add is_transit flag to load_data if needed
    # (we add it inline here for systems from load_data)
    if not transit_3:
        transit_3 = [sd for sd in system_data if any(
            'Transit' in str(p.get('discoverymethod', '')) for p in sd['vplanets'])]
        transit_4 = [sd for sd in system_data
                     if any('Transit' in str(p.get('discoverymethod', ''))
                            for p in sd['vplanets'])
                     and len(sd['periods']) >= 4]

    filter_sets = [all_sd, transit_3, transit_4]
    filter_lbl  = ['All\nplanets', 'Transit-only\n≥3 planets', 'Transit\n≥4 planets']
    xf = np.arange(3)
    w  = 0.18

    for i, t in enumerate(KEYS):
        vals = []; elo = []; ehi = []
        for fset in filter_sets:
            bfs = [sd['bond_frac'] for sd in fset if sd['type'] == t]
            if len(bfs) < 2:
                vals.append(0); elo.append(0); ehi.append(0)
            else:
                m, l, h = bootstrap_ci(bfs)
                vals.append(m); elo.append(m - l); ehi.append(h - m)
        off = (i - 1.5) * w
        bs  = ax2.bar(xf + off, vals, w, color=CB[t], alpha=0.85,
                       edgecolor='black', linewidth=0.3, label=SHORT[t])
        apply_hatch(bs, [t] * 3)
        ax2.errorbar(xf + off, vals, yerr=[elo, ehi],
                     fmt='none', ecolor='black', capsize=2, capthick=1, linewidth=0.8)
        for j, v in enumerate(vals):
            if v > 0:
                ax2.text(xf[j] + off, v + 1.5 + ehi[j], f'{v:.0f}%',
                         ha='center', fontsize=6.5)

    ax2.set_xticks(xf); ax2.set_xticklabels(filter_lbl, fontsize=8)
    ax2.set_ylabel('Bond fraction (%)', fontsize=11)
    ax2.set_title('(b) U-shape persists under detection filters', fontsize=11)
    ax2.legend(fontsize=7, loc='lower left', framealpha=0.8)
    ax2.set_ylim(0, 98)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig1_ushape.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print('    ✓ fig1_ushape.png')


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — Tightness
# ══════════════════════════════════════════════════════════════════════════════
def fig2(td):
    print("  Fig 2: Tightness …")
    fig, ax = plt.subplots(figsize=(7, 5.5))
    bond_types = ['3:2', '2:1', '5:3', '9:5']
    x = np.arange(4)
    w = 0.18

    all_devs = {}
    for i, t in enumerate(KEYS):
        vals = []; cnts = []; cis_lo = []; cis_hi = []
        for bt in bond_types:
            devs = [dev for sd in td[t] for nm, dev in sd['bonds'] if nm == bt]
            all_devs[(bt, t)] = devs
            cnts.append(len(devs))
            if devs:
                m, l, h = bootstrap_ci(devs)
                vals.append(m)
                cis_lo.append(m - l)
                cis_hi.append(h - m)
            else:
                vals.append(0); cis_lo.append(0); cis_hi.append(0)
        off  = (i - 1.5) * w
        bars = ax.bar(x + off, vals, w, color=CB[t], alpha=0.85,
                      edgecolor='black', linewidth=0.3, label=SHORT[t],
                      hatch=HATCH[t])
        ax.errorbar(x + off, vals, yerr=[cis_lo, cis_hi],
                    fmt='none', ecolor='black', capsize=2, capthick=1, linewidth=0.8, zorder=5)
        for j, (v, n) in enumerate(zip(vals, cnts)):
            if n == 0:
                ax.text(x[j] + off, 0.05, '—', ha='center', fontsize=8)
            else:
                dy = {0: 0.25, 1: 0.12, 2: 0.35, 3: 0.08}.get(i, 0.15)
                ax.text(x[j] + off, v + cis_hi[j] + dy, f'{v:.2f}%', ha='center', fontsize=6.5)

    ns_str = '  '.join(
        f'{SHORT[t]}: N={sum(len(all_devs.get((bt,t),[])) for bt in bond_types)}'
        for t in KEYS)
    ax.set_xticks(x); ax.set_xticklabels(bond_types, fontsize=10)
    ax.set_ylabel('Mean fractional deviation from\ncommensurability (%)', fontsize=10)
    ax.set_xlabel('Bond type', fontsize=10)
    ax.set_title('Bond tightness by stellar type (lower = tighter)', fontsize=11)
    ax.legend(fontsize=7, loc='upper right', framealpha=0.85)
    ax.set_ylim(0, 3.8)
    ax.text(0.5, -0.12, ns_str, transform=ax.transAxes, fontsize=7.5,
            ha='center', va='top', fontstyle='italic')
    ax.text(0.02, 0.98,
            'G dwarfs loosest or tied in 3:2 & 5:3;\nF dwarfs loosest in 2:1 & 9:5\nBootstrap 95% CI shown',
            transform=ax.transAxes, fontsize=7.5, va='top',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='grey', alpha=0.85))
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig2_tightness.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print('    ✓ fig2_tightness.png')


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Stability null
# ══════════════════════════════════════════════════════════════════════════════
def fig3(system_data, td, NULL, OBS_PW, DELTA_F):
    print("  Fig 3: Stability null …")
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    x = np.arange(4)
    w = 0.28

    obs  = [OBS_PW[t]  for t in KEYS]
    null = [NULL[t]    for t in KEYS]
    delf = [DELTA_F[t] for t in KEYS]

    obs_lo = []; obs_hi = []; p_vals = []
    for t in KEYS:
        sds  = td[t]
        boots = []
        for _ in range(5000):
            idx = np.random.choice(len(sds), len(sds), replace=True)
            tb  = sum(sds[i]['n_bonds'] for i in idx)
            tp  = sum(sds[i]['n_pairs'] for i in idx)
            boots.append(tb / tp * 100 if tp > 0 else 0)
        obs_lo.append(np.percentile(boots, 2.5))
        obs_hi.append(np.percentile(boots, 97.5))
        pws = [sd['n_bonds'] / sd['n_pairs'] * 100 for sd in sds if sd['n_pairs'] > 0]
        _, p = sp_stats.ttest_1samp(pws, NULL[t])
        p_vals.append(p)

    ax.bar(x - w/2, obs, w, color='#4D4D4D', alpha=0.65,
           edgecolor='black', linewidth=0.5, label='Observed',
           yerr=[[o - l for o, l in zip(obs, obs_lo)],
                 [h - o for h, o in zip(obs_hi, obs)]],
           capsize=3, error_kw={'linewidth': 1.0, 'ecolor': 'black'})
    ax.bar(x + w/2, null, w, color='lightgrey', alpha=0.85,
           edgecolor='black', linewidth=0.5,
           label='Null (stable random packing)', hatch='///')

    for i, (d, hi_, p) in enumerate(zip(delf, obs_hi, p_vals)):
        sign = '+' if d >= 0 else ''
        ax.text(i, hi_ + 4.5, f'Δf = {sign}{d:.1f}%\np = {p:.2f}',
                ha='center', fontsize=7.5, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white',
                          edgecolor='grey', alpha=0.75))

    ax.set_xticks(x)
    ax.set_xticklabels(['M dwarf\n(<0.6 M☉)', 'K dwarf\n(0.6–0.9)',
                        'G dwarf\n(0.9–1.1)', 'F dwarf\n(1.1–1.6)'], fontsize=8)
    ax.set_ylabel('Bond fraction (%)', fontsize=11)
    ax.set_title('Observed vs. stability-filtered null', fontsize=11)
    ax.legend(handles=[
        Patch(facecolor='#4D4D4D', alpha=0.65, edgecolor='black', label='Observed'),
        Patch(facecolor='lightgrey', hatch='///', edgecolor='black',
              label='Null (stable random packing)')
    ], fontsize=7.5, loc='upper left', framealpha=0.75)
    ax.set_ylim(0, 96)
    ax.annotate('G dwarfs at\nnull floor',
                xy=(2, null[2]), xytext=(2.6, 35), ha='center', fontsize=8, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='grey', lw=1.2),
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                          edgecolor='grey', alpha=0.75))
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig3_stability_null.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print('    ✓ fig3_stability_null.png')


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — Age vs bond fraction
# ══════════════════════════════════════════════════════════════════════════════
def fig4(td):
    print("  Fig 4: Age vs bond …")
    fig, axes = plt.subplots(1, 4, figsize=(7, 3.5))

    for i, t in enumerate(KEYS):
        ax = axes[i]
        pts = [(sd.get('age', float('nan')), sd['bond_frac']) for sd in td[t]
               if not math.isnan(sd.get('age', float('nan'))) and sd['age'] > 0]
        if len(pts) < 3:
            ax.text(0.5, 0.5, 'Insufficient\ndata', ha='center', va='center',
                    transform=ax.transAxes, fontsize=9)
            ax.set_title(f'{SHORT[t]}\n(N={len(pts)} sys)', fontsize=10)
            ax.set_xlim(0, 13); ax.set_ylim(15, 90)
            ax.set_xlabel('Age (Gyr)', fontsize=9)
            ax.set_ylabel('Bond fraction (%)', fontsize=9)
            continue

        a_arr = np.array([p[0] for p in pts])
        b_arr = np.array([p[1] for p in pts])
        n = len(pts)

        ax.scatter(a_arr, b_arr, c=CB[t], alpha=0.55, s=22,
                   edgecolors='black', linewidth=0.3, zorder=3)

        slope, intc, r, p, se = sp_stats.linregress(a_arr, b_arr)
        xf = np.linspace(0, 13, 100)
        yf = slope * xf + intc
        ax.plot(xf, yf, color=CB[t], linewidth=2, zorder=4)

        n_boot = 5000
        bs_slopes = []; bs_intcs = []
        for _ in range(n_boot):
            idx = np.random.choice(n, n)
            if len(np.unique(a_arr[idx])) < 2: continue
            s_, i_, _, _, _ = sp_stats.linregress(a_arr[idx], b_arr[idx])
            bs_slopes.append(s_); bs_intcs.append(i_)
        if bs_slopes:
            yfs = np.outer(bs_slopes, xf) + np.outer(bs_intcs, np.ones(100))
            ax.fill_between(xf, np.percentile(yfs, 2.5, 0),
                            np.percentile(yfs, 97.5, 0), color=CB[t], alpha=0.12)

        sig = ('**' if p < 0.0125 else '*' if p < 0.05 else '(n.s.)')
        ax.text(0.03, 0.97,
                f'Slope: {slope:+.2f}% Gyr$^{{-1}}$\nr = {r:.2f}\np = {p:.3f} {sig}',
                fontsize=7.5, transform=ax.transAxes, va='top',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                          edgecolor='grey', alpha=0.85, linewidth=0.5))

        ax.set_xlabel('Age (Gyr)', fontsize=9)
        ax.set_ylabel('Bond fraction (%)', fontsize=9)
        ax.set_title(f'{SHORT[t]}\n(N={n} sys)', fontsize=10)
        ax.set_xlim(0, 13); ax.set_ylim(15, 90)

    fig.text(0.5, 0.005, 'Bootstrap 95% CI shaded; Bonferroni threshold p < 0.0125',
             ha='center', fontsize=7, style='italic')
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(os.path.join(OUT, 'fig4_age_bond.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print('    ✓ fig4_age_bond.png')


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'multi_planet_systems.csv'
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), csv_path)

    print(f"Loading data from {csv_path} …")
    system_data = load_data(csv_path)
    td = defaultdict(list)
    for sd in system_data:
        td[sd['type']].append(sd)

    # Add is_transit flag for figure 1b
    for sd in system_data:
        sd['is_transit'] = any(
            'Transit' in str(p.get('discoverymethod', '')) for p in sd['vplanets'])

    print(f"  {len(system_data)} systems: " +
          ", ".join(f"{t}={len(td[t])}" for t in KEYS))

    # Run null ensemble
    import random
    np.random.seed(42)
    random.seed(42)
    NULL, OBS_PW, DELTA_F = run_null_ensemble(system_data)
    print(f"  Null: " + ", ".join(f"{t}={NULL[t]:.1f}%" for t in KEYS))
    print(f"  Obs:  " + ", ".join(f"{t}={OBS_PW[t]:.1f}%" for t in KEYS))
    print(f"  Δf:   " + ", ".join(f"{t}={DELTA_F[t]:+.1f}%" for t in KEYS))

    print("\nGenerating figures …")
    fig1(system_data, td)
    fig2(td)
    fig3(system_data, td, NULL, OBS_PW, DELTA_F)
    fig4(td)
    print("\nAll figures done ✓")
