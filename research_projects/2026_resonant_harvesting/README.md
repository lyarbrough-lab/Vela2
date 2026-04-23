# Resonant Gamma Harvesting

**Project:** Paper III - Active research project (2026)  
**Status:** Technical draft in progress  
**Authors:** Leslie Yarbrough, Vela P

## Overview

While Paper I ("Eating the Fire") treats spent nuclear fuel as a broadband source, this project explores resonant absorption tuned to specific isotope emission lines (¹³⁷Cs 662 keV, ⁶⁰Co 1.17/1.33 MeV, etc.). Leveraging Mössbauer spectroscopy principles and nuclear resonance fluorescence, resonant cavities could achieve higher efficiency for matched isotopes at the cost of increased complexity and cryogenic operation.

## Project Structure

```
2026_resonant_harvesting/
├── paper_iii_expanded.md      # Technical draft with equations
├── paper_iii_resonant_harvesting.md  # Original outline
├── references/               # [To be added]
├── figures/                 # [To be added]
└── README.md                # This file
```

## Concept

### Resonant Advantage
Nuclear transitions offer exceptionally narrow linewidths (meV range) with correspondingly high quality factors (Q > 10⁶). While practical systems face Doppler broadening and other effects, resonant absorption cross-sections can exceed non-resonant processes by orders of magnitude.

### Target Isotopes
| Isotope | Half-life | Primary γ (keV) | Natural Width (eV) | Resonant σ (barns) |
|---------|-----------|-----------------|-------------------|-------------------|
| ¹³⁷Cs | 30.1 y | 662 | 7.5×10⁻⁹ | 1.2×10⁵ |
| ⁶⁰Co | 5.27 y | 1173 | 3.8×10⁻⁹ | 8.7×10⁴ |

### Proposed Architecture
1. **Isotope separation/staging:** Mechanical sorting by dominant emitter
2. **Resonant cavity design:** Bragg reflectors, photonic crystals, metamaterials
3. **Energy conversion layer:** Tailored medium for specific energy
4. **Cryogenic operation:** For significant recoil-free fraction

## Technical Details

### Mössbauer Effect
The Lamb-Mössbauer factor \( f \) gives the fraction of recoil-free events:
\[
f = \exp\left(-\frac{E_\gamma^2 \langle x^2 \rangle}{(\hbar c)^2}\right)
\]

For ¹³⁷Cs (662 keV), \( f \) is small at room temperature, requiring cryogenic operation for practical systems.

### Nuclear Resonance Fluorescence (NRF)
NRF cross-section for a pure nuclear transition:
\[
\sigma_{\text{NRF}} = \frac{2\pi}{k^2} \frac{2J_f + 1}{2J_i + 1} \frac{\Gamma_\gamma^2}{4(E - E_0)^2 + \Gamma^2}
\]

### Efficiency Projections
- **Resonant absorption:** η_abs ≈ 0.15 (with cryogenic enhancement)
- **Secondary emission:** η_sec ≈ 0.3 (typical scintillator)
- **Charge collection:** η_coll ≈ 0.5 (similar to Paper I)
- **System efficiency:** η_system ≈ 2.25% (optimistic)

## Comparison to Paper I

| Aspect | Paper I (Broadband) | Paper III (Resonant) |
|--------|-------------------|-------------------|
| Approach | Treats all isotopes simultaneously | Targets specific isotopes |
| Efficiency | 1-3% | 2-5% possible (matched isotopes) |
| Complexity | Moderate | High (cryogenic, separation) |
| Fabrication | Established thin-film tech | Nanoscale precision required |
| Thermal | Room temperature operation | Cryogenic operation needed |

## Files

### `paper_iii_expanded.md`
Complete technical draft including:
- Abstract and introduction
- Mössbauer and NRF theory
- Isotope tables and parameters
- Architecture proposals
- Efficiency projections
- Experimental pathway
- References

### `paper_iii_resonant_harvesting.md`
Original outline with:
- Title options and abstract concept
- Section breakdown
- Key research questions
- Connection to Paper I and IV

## Next Steps

1. **Literature review** on Mössbauer efficiency limits
2. **Cross-section calculations** for target isotopes
3. **Cavity design simulations**
4. **Experimental proposal** for proof-of-concept
5. **Conversion to LaTeX** manuscript format

## Related Projects

- **Paper I:** "Eating the Fire" - Broadband graded-Z approach
- **Paper IV:** Nuclear-Pumped Laser Stack - System integration
- **Hybrid approach:** Consider combining broadband front-end with resonant back-end

## References to Add

- Mössbauer, R.L. (1958). "Kernresonanzfluoreszenz von Gammastrahlung in Ir191"
- Collins et al. (2005). "Nuclear resonance fluorescence for isotope-specific detection"
- University of Colorado Denver (2025). "Quantum simulation of nuclear states"
- Improved Passive Gamma Emission Tomography (2022). Scientific Reports

---

*Active research project - draft stage, April 2026*