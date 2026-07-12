#!/usr/bin/env python3
import csv, json, sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).parent
CANONICAL = ROOT.parent
sys.path.insert(0, str(CANONICAL / "code"))
import system_level_extension as ext

COLORS = {"M": "#0072B2", "K": "#E69F00", "G": "#CC79A7", "F": "#009E73"}
KEYS = "MKGF"
LABELS = ["M-mass\n<0.6", "K-mass\n0.6--0.9", "G-mass\n0.9--1.1", "F-mass\n1.1--1.6"]


def load():
    data = json.load(open(CANONICAL / "results/canonical_results.json"))
    rows = list(csv.DictReader(open(CANONICAL / "results/canonical_systems.csv")))
    return data, rows


def bootstrap_ci(values, seed, n=30000):
    rng = np.random.default_rng(seed)
    values = np.asarray(values, float)
    means = rng.choice(values, (n, len(values)), replace=True).mean(axis=1)
    return np.percentile(means, [2.5, 97.5])


def figure_residuals(data):
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.35), sharey=True)
    for ax, analysis, title in zip(
        axes, ("full", "first_order"),
        ("(a) Fourteen-ratio classifier", "(b) First-order ratios only")
    ):
        vals, lo, hi = [], [], []
        for key in KEYS:
            item = data["analyses"][analysis]["bins"][key]
            vals.append(item["mean_residual"])
            lo.append(item["residual_bootstrap_95ci"][0])
            hi.append(item["residual_bootstrap_95ci"][1])
        x = np.arange(4)
        bars = ax.bar(x, vals, color=[COLORS[k] for k in KEYS], edgecolor="black", lw=.5)
        ax.errorbar(x, vals, yerr=[np.array(vals)-lo, np.array(hi)-vals], fmt="none",
                    ecolor="black", capsize=3, lw=1.1)
        ax.axhline(0, color="black", lw=.8, ls="--")
        for bar, value in zip(bars, vals):
            ax.text(bar.get_x()+bar.get_width()/2, value + (0.7 if value >= 0 else -1.2),
                    f"{value:+.1f}", ha="center", va="center", fontsize=8, fontweight="bold")
        ax.set_xticks(x, LABELS, fontsize=8)
        ax.set_title(title, fontsize=10)
        ax.set_ylim(-17, 17)
        ax.grid(axis="y", alpha=.2)
    axes[0].set_ylabel("Observed minus matched-null fraction\n(percentage points)", fontsize=9)
    fig.tight_layout()
    fig.savefig(ROOT / "fig1_residuals.png", dpi=320, bbox_inches="tight")
    fig.savefig(ROOT / "fig1_residuals.pdf", bbox_inches="tight")
    plt.close(fig)


def classify_populations():
    csv_path = ROOT.parents[3] / "datasets/exoplanets/multi_planet_systems.csv"
    systems, _ = ext.load_systems(csv_path, require_three_valid=True, mass_strategy="first")
    feasible, infeasible = [], []
    for system in systems:
        gaps = ext.minimum_log_period_gaps(system["planet_masses"], system["mass"], 8)
        extent = np.log(system["periods"][-1] / system["periods"][0])
        (infeasible if gaps is None or gaps.sum() > extent + 1e-12 else feasible).append(system)
    return feasible, infeasible


def figure_feasibility():
    feasible, infeasible = classify_populations()
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.4), sharey=True)
    width = .34
    for ax, ratios, title in zip(
        axes, (ext.FULL_RATIOS, ext.FIRST_ORDER_RATIOS),
        ("(a) Fourteen-ratio classifier", "(b) First-order ratios only")
    ):
        x = np.arange(4)
        for offset, population, label, alpha in (
            (-width/2, feasible, "Null-feasible", .9),
            (width/2, infeasible, "Null-infeasible", .45),
        ):
            means, los, his, ns = [], [], [], []
            for index, key in enumerate(KEYS):
                values = [ext.bond_fraction(s["periods"], ratios) for s in population if s["bin"] == key]
                ns.append(len(values)); means.append(np.mean(values))
                low, high = bootstrap_ci(values, 5000 + index + (0 if label == "Null-feasible" else 20))
                los.append(low); his.append(high)
            bars = ax.bar(x+offset, means, width, color=[COLORS[k] for k in KEYS], alpha=alpha,
                          edgecolor="black", lw=.5, hatch="" if label == "Null-feasible" else "///",
                          label=label)
            ax.errorbar(x+offset, means, yerr=[np.array(means)-los, np.array(his)-means],
                        fmt="none", ecolor="black", capsize=2, lw=.8)
        ax.set_xticks(x, LABELS, fontsize=8)
        ax.set_title(title, fontsize=10)
        ax.set_ylim(0, 105)
        ax.grid(axis="y", alpha=.2)
    axes[0].set_ylabel("Observed near-commensurability fraction (%)", fontsize=9)
    axes[1].legend(fontsize=7, loc="lower right")
    fig.text(.5, .01, "Error bars are bootstrap 95% intervals; subgroup sizes are reported in Table 2.",
             ha="center", fontsize=7)
    fig.tight_layout(rect=(0, .035, 1, 1))
    fig.savefig(ROOT / "fig2_feasibility.png", dpi=320, bbox_inches="tight")
    fig.savefig(ROOT / "fig2_feasibility.pdf", bbox_inches="tight")
    plt.close(fig)


def figure_ratio_distribution():
    feasible, infeasible = classify_populations()
    fig, ax = plt.subplots(figsize=(7.1, 3.1))
    bins = np.linspace(1, 4, 61)
    for population, label, color, linestyle in (
        (feasible, "Null-feasible", "#4C78A8", "-"),
        (infeasible, "Null-infeasible", "#E45756", "--"),
    ):
        ratios = [s["periods"][i+1]/s["periods"][i] for s in population
                  for i in range(len(s["periods"])-1)
                  if 1 <= s["periods"][i+1]/s["periods"][i] <= 4]
        ax.hist(ratios, bins=bins, density=True, histtype="step", lw=1.8,
                linestyle=linestyle, label=f"{label} (N={len(ratios)} pairs)", color=color)
    for name, value in ext.FIRST_ORDER_RATIOS.items():
        ax.axvline(value, color="black", alpha=.35, lw=.8)
        ax.text(value, ax.get_ylim()[1]*.9, name, rotation=90, ha="center", va="top", fontsize=7)
    ax.set_xlabel("Adjacent period ratio")
    ax.set_ylabel("Density")
    ax.set_xlim(1, 4)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(ROOT / "fig3_ratio_distribution.png", dpi=320, bbox_inches="tight")
    fig.savefig(ROOT / "fig3_ratio_distribution.pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    d, _ = load()
    figure_residuals(d)
    figure_feasibility()
    figure_ratio_distribution()
