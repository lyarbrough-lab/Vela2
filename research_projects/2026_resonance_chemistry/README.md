# Planetary Near-Commensurability by Dynamical Order

This directory contains the canonical, reproducible analysis for the manuscript
**“Host-Mass Dependence of Planetary Near-Commensurability Varies with Dynamical Order.”**

The earlier rejection-sampling analysis and its “resonance chemistry” interpretation
are superseded. Proximity to a nominal integer period ratio is called
*near-commensurability* here; it is not treated as proof of resonance without
resonant-angle libration.

## Canonical result

The frozen 2026-04-27 NASA Exoplanet Archive catalog contains 336 hosts and
1182 planets. After the documented cuts, 326 systems (1150 planets; 824 adjacent
pairs) remain. The eight-mutual-Hill-radius null is geometrically feasible for
300 systems and infeasible for 26.

- Broad 14-ratio classifier, G-host residual: **−5.46 percentage points**,
  nominal 95% bootstrap interval **[−10.81, −0.15]**.
- First-order-only classifier (2:1, 3:2, 4:3, 5:4), G-host residual:
  **+0.09 points**, interval **[−4.44, +4.69]**.
- Global quadratic host-mass tests are not significant for either definition.
- The broad classifier covers about 56% of the ratio domain from 1 to 4.
- The 26 null-infeasible compact systems are more commensurable than the
  feasible population and are reported separately.

The defensible interpretation is conditional: among systems for which a stable
randomized eight-Hill architecture exists, the marginal G-host deficit depends
on the selected dynamical orders and vanishes for first-order ratios alone.

## Canonical files

| Path | Purpose |
|---|---|
| `../../datasets/exoplanets/multi_planet_systems.csv` | Frozen 2026-04-27 input catalog (repository-wide canonical dataset) |
| `canonical/code/system_level_extension.py` | Exact conditional Dirichlet sampler and statistical tests |
| `canonical/results/canonical_results.json` | Canonical summary output; seed 20260711 |
| `canonical/results/canonical_systems.csv` | Per-system observed/null output |
| `canonical/manuscript/main.tex` | AJ AASTeX manuscript source |
| `canonical/manuscript/references.bib` | Verified bibliography |
| `canonical/figures/make_figures.py` | Figure-generation code |

Running `canonical/figures/make_figures.py` regenerates the manuscript's three
vector PDF figures from the canonical outputs.

## Reproduction

From this directory:

```bash
python canonical/code/system_level_extension.py \
  ../../datasets/exoplanets/multi_planet_systems.csv \
  --output canonical/results/reproduced_results.json \
  --draws 2000 --hill 8 --seed 20260711
```

The canonical run uses NumPy PCG64 seed `20260711`, 2000 draws per feasible
system, and requires every included system to receive exactly 2000 draws.

## Versioning and archive

The files under `canonical/` supersede the rejection-sampling outputs associated
with the earlier repository release. The corrected `v5.0.0` release is archived
at Zenodo as [10.5281/zenodo.21326602](https://doi.org/10.5281/zenodo.21326602).

## License and citation

See the repository-level license and the Zenodo record linked from the release.
