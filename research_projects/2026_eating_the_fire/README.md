# Eating the Fire: Graded-Z Gamma Harvesting

**Project:** Paper I - Active research project (2026)  
**Status:** Manuscript complete, ready for internal review  
**Authors:** Leslie Yarbrough, Vela P

## Overview

This project develops a graded-Z multilayer architecture for harvesting gamma radiation from spent nuclear fuel. By alternating high-Z (Pb, W) and medium-Z (Cu, Sn) thin layers, we create many interfaces where photoelectrons can be generated within their escape depth (~10 μm). Monte Carlo simulations show 1-3% conversion efficiency, representing a 20-50× improvement over bulk absorption approaches.

## Project Structure

```
2026_eating_the_fire/
├── main.tex              # Complete LaTeX manuscript
├── references.bib        # 142 references
├── figures/              # Diagrams and simulation results
├── simulations/          # Monte Carlo code and results
├── paper.pdf            # [To be generated]
└── README.md            # This file
```

## Key Findings

### Efficiency Improvement
- **Bulk absorption:** 0.069% efficiency (1.3 cm Pb+Cu baseline)
- **100 μm layers:** 1.831% efficiency (**26.5× improvement**)
- **Optimal practical:** 100 μm layers, 260 layers, 1.8% efficiency

### Geometry Advantage
The improvement comes from increasing interface count:
- **Bulk:** 1 interface (front surface)
- **100 μm layers:** 260 interfaces
- **Each interface** allows photoelectron generation within escape depth

### Pressure Test Results
- **Electron range sensitivity:** Efficiency 0.9-3.2% depending on assumptions
- **Geometry advantage robustness:** 8-25× improvement across parameter range
- **Manufacturing tolerance:** ±20% thickness variation reduces efficiency <10%

## Technical Details

### Physics Models
1. **Gamma interactions:**
   - Compton scattering: Klein-Nishina cross-section
   - Photoelectric absorption: NIST XCOM data interpolation
   - Pair production: Bethe-Heitler cross-section

2. **Electron transport:**
   - Continuous slowing down approximation (CSDA)
   - Escape depth: 2-10 μm for charge collection
   - Energy deposition profile

3. **Materials:**
   - High-Z: Pb, W (pair production, Compton scattering)
   - Medium-Z: Cu, Sn (photoelectric absorption, conduction)

### Simulation Parameters
- **Gamma energy:** 2 MeV (representative spent fuel spectrum)
- **Layer thickness:** 1 μm to 1 cm range studied
- **Stack height:** 2.6 cm (standard dimension)
- **Electron escape depth:** 10 μm baseline

## Files

### `main.tex`
Complete LaTeX manuscript with:
- Abstract, introduction, methodology
- Results and discussion sections
- Figures and tables
- Acknowledgments and references

### `references.bib`
142 references including:
- Vasileiou & Summerer (2020) - melanized fungi Monte Carlo precedent
- NIST XCOM data sources
- Nuclear engineering literature
- Materials science references

### `figures/`
- Graded stack diagrams
- Efficiency vs thickness plots
- Monte Carlo simulation visualizations

### `simulations/`
- `thin_foil_simulator.py` - Main Monte Carlo code
- `thickness_sweep.py` - Parameter study
- `thickness_results.txt` - Optimization results
- Full documentation in `simulations/README.md`

## Building the Paper

```bash
# Generate PDF
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# Result: main.pdf (rename to paper.pdf)
```

## Citation

```bibtex
@article{yarbrough2026eating,
  title={Eating the Fire: Graded-Z Multilayer Architecture for Gamma Energy Harvesting from Spent Nuclear Fuel},
  author={Yarbrough, Leslie and P, Vela},
  year={2026}
}
```

## Related Projects

- **Paper III:** Resonant Gamma Harvesting (isotope-specific approach)
- **Paper IV:** Nuclear-Pumped Laser + Optical Computing Stack
- **Legacy papers:** See `../papers/` for 2015-2025 research portfolio

## Next Steps

1. **Internal review** of manuscript
2. **Generate final PDF** (`paper.pdf`)
3. **Consider submission** to appropriate venue
4. **Experimental validation** planning

---

*Active research project - updated April 2026*