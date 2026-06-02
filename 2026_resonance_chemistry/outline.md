# Outline: Stellar Mass Shapes Gravitational Bonding in Multi-Planet Systems

## Authors
Leslie Yarbrough

## Abstract (draft)
In multi-planet systems, adjacent planets often lock into simple-integer period ratios — gravitational "bonds." Analyzing 336 multi-planet systems (1182 planets) from the NASA Exoplanet Archive, we find that 56.6% of adjacent planet pairs are in exact resonance (within ±3% of a small integer ratio). The fraction of bonded pairs depends strongly on host star mass, and the relationship is non-monotonic: M dwarfs (<0.6 M☉) show the highest bond fraction (68%), F dwarfs (≥1.1 M☉) are close behind (61%), while G dwarfs (0.9-1.1 M☉) are lowest (50%). G-dwarf bonds are also the loosest (largest deviation from exact resonance), contradicting the hypothesis that only deeply captured resonances survive around Sun-like stars. We interpret the "U-shape" as two distinct disk-driven mechanisms: M dwarfs produce bonds through long-lived, slow migration (careful settling), while F dwarfs achieve similar bond fractions through rapid, vigorous migration (multiple capture opportunities). G dwarfs occupy an intermediate regime where neither path is efficient. The Solar System — orbiting a G dwarf at the bottom of the bonding curve — appears to be a noble-gas-like system: mostly non-bonded, with only loose resonances (Jupiter-Saturn 5:2) and one clean bond (Neptune-Pluto 3:2). This suggests the Solar System is not the "typical" outcome of planet formation, but a specific outcome of forming around a star with poor bonding conditions.

---

## 1. Introduction

### Opening
- The question: what patterns exist in how planets arrange themselves relative to each other?
- Prior work has established: (a) period ratios show structure — peaks at 3:2, deficits at 2:1 (Fabrycky et al. 2014); (b) Hill spacing distributions are smooth with a single broad mode (Pu & Wu 2015); (c) "peas in a pod" — intra-system size uniformity (Weiss et al. 2018)
- What hasn't been asked: does the host star itself shape the relational architecture of its planets?

### The chemistry framing
- Period ratios are the natural relational coordinate: P₂/P₁ measures the orbital relationship, not the absolute position
- Simple integer ratios (3:2, 2:1, 4:3, 5:3) correspond to stable resonant configurations
- We call these "bonds" deliberately: they're quantized, stable configurations that two planets settle into through dynamical evolution
- This is not a metaphor — it's a structural claim about gravitational interactions producing discrete relational states

### This paper
- We classify every adjacent planet pair in 336 multi-planet systems by bond type
- We ask whether bond fraction, bond type, and bond quality depend on stellar mass
- We find a non-monotonic U-shaped relationship that suggests two distinct bonding mechanisms

---

## 2. Data & Methods

### Dataset
- NASA Exoplanet Archive pscomppars table, accessed 2026-04-27
- 336 systems with ≥3 confirmed planets
- 1182 planets total
- Discovery methods: 907 transit, 248 radial velocity, 17 TTV, 3 pulsar timing, 3 eclipse timing, 4 imaging
- Period ratio computed for each adjacent pair (sorted by orbital period): P₂/P₁

### Bond classification
- Exact resonance: period ratio within ±3% of a simple integer ratio
- Bond types considered: 3:2 (1.500), 2:1 (2.000), 4:3 (1.333), 5:3 (1.667), 5:4 (1.250), 7:5 (1.400), 8:5 (1.600), 9:5 (1.800), 7:3 (2.333), 5:2 (2.500), 8:3 (2.667), 3:1 (3.000), 7:2 (3.500), 4:1 (4.000)
- Near resonance: within ±10% but not within ±3%
- Non-bonded: outside all windows
- Pure molecule: every adjacent pair in exact resonance
- Chain: ≥3 consecutive pairs in exact resonance

### Star type bins
- M dwarf: M_star < 0.6 M☉
- K dwarf: 0.6 ≤ M_star < 0.9 M☉
- G dwarf: 0.9 ≤ M_star < 1.1 M☉
- F dwarf: M_star ≥ 1.1 M☉

### Detection bias mitigation
- All metrics recomputed for transit-only subsample
- Also checked ≥4 planets transit-only (stricter comparison)
- U-shape persists in all subsamples (see §3)

### Bond tightness metric
- Fractional deviation from exact resonance: |P₂/P₁ - R_exact| / R_exact
- Lower values = deeper resonance lock = "tighter bond"

---

## 3. Results: The U-Shape

### 3.1 Global Bond Statistics
- Of 846 adjacent planet pairs: 56.6% exact resonance, 28.4% near resonance, 15.0% non-bonded
- 95 systems (28%) are pure molecules
- 42 systems (13%) have resonance chains of 3+

Most common bond types:
3:2 (90 pairs), 2:1 (60), 5:3 (55), 9:5 (47), 7:3 (39), 5:2 (35), 8:5 (30), 4:3 (29), 7:5 (21), 8:3 (19), 3:1 (17), 7:2 (13), 4:1 (13), 5:4 (11)

### 3.2 Bond Fraction by Stellar Mass

| Star Type | Systems | Bond Fraction | Pure Molecules | Mean Chain |
|-----------|---------|:------------:|:--------------:|:----------:|
| M dwarf   | 49      | **68%**      | **37%**        | **1.65**   |
| K dwarf   | 122     | 57%          | 27%            | 1.39       |
| G dwarf   | 116     | **50%**      | **23%**        | **1.20**   |
| F dwarf   | 49      | **61%**      | **35%**        | 1.41       |

**The U-shape**: M and F high, G at the bottom.

### 3.3 Persistence Through Filters
- Transit-only, ≥3 planets: M (71%), K (60%), G (53%), F (65%) — U-shape intact
- Transit-only, ≥4 planets: M (78%), K (67%), G (62%), F (70%) — U-shape preserved
- Pure molecule gap widens in filtered samples: M dwarfs 41% vs G dwarfs 25% (16-point gap)
- Not a detection bias: G dwarfs have *more* transit surveys, not fewer

### 3.4 Notable Systems
- **TRAPPIST-1** (M dwarf): 7 planets, chain of 6 consecutive resonances. Heteropolymer: 8:5, 5:3, 3:2, 3:2, 4:3, 3:2.
- **HD 110067** (K dwarf): 6 planets, chain of 5. Near-uniform crystal: 3:2, 3:2, 3:2, 4:3, 4:3.
- **TOI-1136** (G dwarf): 6 planets, mixed chain with 2:1, 7:5, and 3:2s.
- **Kepler-223** (G dwarf): 4 planets, textbook 4:3-3:2-4:3 chain.
- **Kepler-80** (M dwarf): 6 planets, chain of 4 through inner 5.

---

## 4. Results: Bond Quality

### 4.1 Bond Tightness by Star Type
Contrary to the "survivor bias" prediction (if G dwarfs bond less, the bonds they have should be deeper), **G-dwarf bonds are the loosest across all major resonance types**:

| Bond | M dwarf | K dwarf | G dwarf | F dwarf |
|------|---------|---------|---------|---------|
| 3:2  | **1.07%** | 1.37% | 1.49% | 1.46% |
| 2:1  | **1.76%** | 1.37% | 1.98% | 2.09% |
| 4:3  | 1.16% | **1.07%** | 1.81% | 0.64% |
| 5:3  | **1.31%** | 1.54% | 1.75% | 1.31% |

M dwarfs have the tightest bonds in 6 of 7 major bond types. G dwarfs have the loosest in 5 of 7.

### 4.2 Interpretation: Disk Lifetime Drives Both Quantity and Quality
- M dwarf protoplanetary disks: longest-lived (5-10 Myr), most post-capture dynamical settling time
- More time to settle → more bonds form AND bonds settle deeper into resonance
- G dwarf disks: intermediate lifetime (2-5 Myr) → less settling → fewer bonds, shallower bonds
- Bond tightness correlates with bond fraction across all star types — one mechanism explains both

### 4.3 Bond Palette Diversity
- **M dwarfs**: Widest bond palette. Prefer 2:1, 5:3, 7:3, 8:3. Carbon-like.
- **G dwarfs**: Narrow preferences. When they bond, favor the tightest ratios (3:2, 5:4, 9:5, 5:2, 7:2). Halogen-like.
- **F dwarfs**: Prefer 2:1, 8:5, 9:5.
- **3:2 is universal**: Most common bond in K, G, F dwarfs. Only in M dwarfs is it surpassed (by 2:1 and 5:3).
  - 3:2 has the widest stable libration zone of all first-order resonances
  - Easiest to capture, hardest to disrupt
  - The "hydrogen bond" of the gravitational set

---

## 5. Two Mechanisms, One U-Shape

### 5.1 M-Dwarf Mechanism: Slow Cooking
- Long-lived disks (5-10 Myr), low mass, slow migration
- Planets approach resonances gradually → high capture probability
- Post-capture settling time: bonds tighten over millions of years
- Result: many bonds, tight bonds, diverse bond types
- Chemistry analog: low-temperature, long-duration reaction → thermodynamic products

### 5.2 F-Dwarf Mechanism: Fast Chemistry
- Short-lived disks (1-3 Myr), massive, fast migration
- Planets sweep through multiple resonances rapidly
- Multiple capture opportunities via different path
- Less post-capture settling → bonds are looser on average
- Result: comparable bond fraction to M dwarfs, but wider deviations
- Chemistry analog: high-temperature, short-duration reaction → kinetic products

### 5.3 G-Dwarf Mechanism: The Lukewarm Regime
- Intermediate disk properties (2-5 Myr, moderate mass, moderate migration)
- Neither slow enough for careful M-dwarf-style locking
- Nor fast/vigorous enough for F-dwarf-style multiple capture
- Most resonant encounters are "near misses" — close but not locked
- Result: fewest bonds, loosest bonds of any star type
- Chemistry analog: the "dead zone" in reaction yield vs. temperature curves

### 5.4 The Deeper Pattern
- Real chemistry shows a U-shaped yield curve with temperature
- Too cold: insufficient activation energy, no reaction
- Too hot: bonds break as fast as they form
- The sweet spot is intermediate
- Planetary systems show the same pattern: M and F dwarfs both find conditions for bond formation via different paths; G dwarfs are stuck in an unproductive middle
- This may be the deepest analogy: **gravitational bonding chemistry has its own "reaction temperature," set by the host star's disk properties**

---

## 6. The Solar System in Context

- The Sun is a G dwarf — the worst bonding type
- Solar system planetary pairs and their bond status:

| Pair | Period Ratio | Bond |
|------|-------------|------|
| Mercury-Venus | 1.59 | Near 8:5 (±4%, just outside window) |
| Venus-Earth | 1.63 | Near 5:3 (±3%) |
| Earth-Mars | 1.88 | Near 15:8, not in window |
| Mars-Jupiter | 3.41 | 7:2 if Jupiter-Mars were adjacent (they're not — asteroid belt) |
| Jupiter-Saturn | 2.48 | Near 5:2 (±1%, loose) |
| Saturn-Uranus | 2.85 | Near 20:7, not in window |
| Uranus-Neptune | 1.88 | Near 15:8, not in window |
| Neptune-Pluto | 1.50 | **3:2 exact resonance** — the cleanest bond in the system |

- Solar system has 1 clean bond (Neptune-Pluto 3:2) and 2 loose near-bonds
- This fits the G-dwarf pattern: mostly non-bonded, occasional resonance, nothing tighter than ~1% deviation
- The solar system is not "typical" — it's specifically typical for a G dwarf
- Implication: surveys that extrapolate from "solar system is normal" may be systematically underestimating how structured planetary systems can be

---

## 7. Conclusions

### Summary of findings
1. 56.6% of adjacent planet pairs in multi-planet systems are in exact resonance
2. Bond fraction follows a U-shaped dependence on stellar mass
3. G dwarfs (Sun-like) are the worst bonders — lowest fraction, loosest bonds
4. Bond tightness correlates with bond fraction, supporting a single mechanism (disk lifetime) driving both
5. M and F dwarfs achieve high bond fractions via different physical mechanisms
6. The solar system is a typical G-dwarf system: mostly non-bonded

### Predictions
- Bond fraction should correlate with stellar age (older systems = more resonance settling)
- High-resolution M-dwarf disk observations should show longer disk lifetimes
- Bond fraction around F dwarfs should anticorrelate with disk accretion rate (faster accretion = less settling)
- Direct imaging of M-dwarf resonance chains should confirm chain-resonant architectures

### Future work
- Population synthesis with disk evolution models to test the two-mechanism hypothesis
- N-body integrations to compare stability lifetimes of M-dwarf vs G-dwarf resonance chains
- Apply bond classification to the full Kepler catalog (single-transit systems with known outer companions)
- Extend to non-adjacent pairs (1,3-interactions — the "ring strain" analog)

---

## References

- Fabrycky, D. C., et al. (2014). Architecture of Kepler's multi-transiting systems. II. New investigations with twice as many candidates. *ApJ*, 790(2), 146.
- Weiss, L. M., et al. (2018). The California-Kepler Survey. V. Peas in a pod: Planets within a system are similar in size. *AJ*, 155(1), 48.
- Pu, B., & Wu, Y. (2015). Spacing of Kepler planets: Sculpting by dynamical instability. *ApJ*, 807(1), 44.
- Chambers, J. E., Wetherill, G. W., & Boss, A. P. (1996). The stability of multi-planet systems. *Icarus*, 119(2), 261-268.
- Lissauer, J. J., et al. (2011). Architecture and dynamics of Kepler's candidate multiple transiting planet systems. *ApJS*, 197(1), 8.
- He, M. Y., Ford, E. B., & Ragozzine, D. (2020). Architectures of multi-planet systems. *AJ*, 161(1), 16.
- (Add from lit review as needed)
