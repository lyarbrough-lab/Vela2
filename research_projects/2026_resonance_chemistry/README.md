# Resonance Chemistry: Gravitational Bonding in Multi-Planet Systems

## The Idea

What if gravity behaves like chemistry? Not metaphorically — structurally. The idea is that gravitational interactions in multi-planet systems produce discrete, quantized relational configurations that mirror chemical bonding. The key dimension is *period ratios*, not absolute distances. Simple-integer period ratios (3:2, 2:1, 4:3, 5:3...) are the gravitational equivalent of valence bonds.

## Key Findings

### 1. Period Ratios Are Lumpy (Hill Spacings Are Not)

**Hill spacing histogram:** Smooth, single broad peak at ~13 R_H, no substructure. The "shell occupancy" version of the chemistry analogy — planets occupying discrete preferred spacings — is not supported by the data at the population level.

**Period ratio histogram:** Strong peaks at simple-integer ratios. 3:2 is the dominant resonance (4.2× expected density). 2:1 shows a deficit at exact 2:00 with pile-up just wide (2.02-2.15). Clear forbidden zone below 1.15. The chemistry lives in *relational* coordinates, not absolute ones.

### 2. 56.6% of Adjacent Planet Pairs Are in Exact Resonance

Of 846 adjacent planet pairs across 336 multi-planet systems:
- **56.6%** in exact resonance (within ±3% of integer ratio)
- **28.4%** near resonance (within ±10%)
- **15.0%** non-bonded
- **95 systems (28%)** are "pure molecules" — every adjacent pair in exact resonance

### 3. Stellar Type Determines Bond Chemistry (The U-Shape)

| Star Type | Bond Fraction | Pure Molecules | Mean Chain Length |
|-----------|:------------:|:--------------:|:-----------------:|
| M dwarf   | **68%**      | **37%**        | **1.65**          |
| K dwarf   | 57%          | 27%            | 1.39              |
| G dwarf   | **50%**      | **23%**        | **1.20**          |
| F dwarf   | **61%**      | **35%**        | 1.41              |

**G dwarfs (Sun-like stars) are the worst chemists.** The U-shape survives every filter: all methods, transit-only, ≥4 planets. It's not a detection bias.

### 4. M Dwarfs Have the Tightest, Deepest Bonds

Contrary to prediction, G-dwarf bonds are the *loosest* (largest deviation from exact integer ratios). M-dwarf bonds are the tightest. This is consistent with **disk lifetime** driving post-capture dynamical settling: M dwarfs have the longest-lived protoplanetary disks (5-10 Myr), providing the most time for bonds to settle deeper into resonance after capture.

### 5. Bond Palette Varies by Star Type

- **M dwarfs**: Widest bond palette. Prefer 2:1, 5:3, 7:3, 8:3. Carbon-like chemistry — multiple bond types.
- **G dwarfs**: Narrow preferences. When they bond, prefer the tightest ratios (3:2, 5:4, 9:5, 5:2, 7:2). Halogen-like.
- **F dwarfs**: Similar to M dwarfs in bond fraction. Prefer 2:1, 8:5, 9:5.
- **3:2 is universal** — the hydrogen bond of the gravitational set. Deepest libration well, easiest to capture, hardest to disrupt.

## Notable Systems

- **TRAPPIST-1** (7 planets, M dwarf): Chain of 6 consecutive resonances. Heteropolymer — 8:5, 5:3, 3:2, 3:2, 4:3, 3:2.
- **HD 110067** (6 planets, K dwarf): Chain of 5. Near-uniform — 3:2, 3:2, 3:2, 4:3, 4:3. Regular crystal-like.
- **TOI-1136** (6 planets, G dwarf): Mixed bond chain including 2:1, 7:5, and 3:2s.
- **Solar System**: G-dwarf host. Jupiter-Saturn 5:2 (loose), Neptune-Pluto 3:2 (cleanest bond). Noble-gas-ish.

## Proposed Mechanism

**Disk lifetime drives both bond fraction and bond quality.** M dwarfs have the longest-lived, lowest-mass disks → slow migration → high capture probability → most post-capture settling time → most bonds, tightest bonds. G dwarfs have intermediate disks → moderate migration → moderate capture → less settling time → fewer bonds, looser bonds. F dwarfs have massive, short-lived disks → fast migration → multiple capture opportunities (different mechanism, same outcome) → many bonds.

Testable predictions:
1. Bond fraction should correlate with stellar age (older systems = more settling = tighter bonds)
2. Bond quality should correlate with system age within a stellar type
3. M-dwarf disks should produce more *high-order* resonances (7:3, 8:3) due to slower sweep speeds

## Methods

- Dataset: NASA Exoplanet Archive, 336 multi-planet systems with ≥3 confirmed planets
- 1182 planets, 907 transit, 248 RV, 17 TTV, 3 pulsar timing, 3 eclipse timing, 4 imaging
- Bond classification: ±3% of exact integer period ratio for "exact resonance"
- Hill spacing: R_H = a_mean * ((m1 + m2)/(3 * M_star))^(1/3)
- Star type bins: M (<0.6 M☉), K (0.6-0.9), G (0.9-1.1), F (≥1.1)

## Status

Exploratory analysis. Results documented. Ready for write-up.

## Files

- `README.md` — this file
- `data/` — extracted datasets
- `figures/` — (to add)
- `resonance_chemistry_analysis.py` — (to add)
