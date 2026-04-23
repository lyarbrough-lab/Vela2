# Vela Research Repository

**Gamma Energy Harvesting & Interdisciplinary Physics Research**

## Overview

This repository contains research on converting spent nuclear fuel gamma emissions to usable energy through novel architectures, alongside interdisciplinary work connecting physics, psychology, and experimental field measurements.

## Research Series

### **Paper I: "Eating the Fire" - Graded-Z Broadband Approach**

**Abstract:** We propose a graded-Z multilayer architecture for harvesting gamma radiation from spent nuclear fuel. By alternating high-Z (Pb, W) and medium-Z (Cu, Sn) thin layers, we create many interfaces where photoelectrons can be generated within their escape depth (~10 μm). Monte Carlo simulations show 1-3% conversion efficiency, representing a 20-50× improvement over bulk absorption approaches. The geometry principle is supported by prior Monte Carlo work on melanized fungi spatial arrangements.

**Files:**
- `main.tex` - LaTeX manuscript
- `references.bib` - References
- `figures/` - Graded stack diagrams and simulation results

### **Paper III: Resonant Gamma Harvesting - Isotope-Specific Approach**

**Concept:** While Paper I treats spent fuel as a broadband source, this work explores resonant absorption tuned to specific isotope emission lines (¹³⁷Cs 662 keV, ⁶⁰Co 1.17/1.33 MeV, etc.). Leveraging Mössbauer spectroscopy principles and nuclear resonance fluorescence, resonant cavities could achieve higher efficiency for matched isotopes at the cost of increased complexity and cryogenic operation.

**Files:**
- `paper_iii/paper_iii_resonant_harvesting.md` - Outline
- `paper_iii/paper_iii_expanded.md` - Technical draft with equations and projections

### **Paper IV: Nuclear-Pumped Laser + Optical Computing Stack**

**Concept:** Three-stage system: spent fuel → graded-Z gamma harvester → nuclear-pumped laser → optical processor. Integrates historical nuclear-pumped laser work (Kurchatov Institute, Los Alamos FALCON) with modern silicon photonics for long-duration autonomous computing applications.

**Files:**
- `paper_iv/paper_iv_nuclear_laser_stack.md` - Outline

## Experimental & Field Work

### **VLF/ELF Station Data**
- **Location:** Nashville, TN wooded yard
- **Antenna:** 8ft diameter VLF loop (cattle ring + magnetic wire)
- **Detected stations:**
  - NAA (Cutler Maine, 24 kHz)
  - TFK (Grindavik Iceland, 37.5 kHz) 
  - NML (LaMoure ND, 25.2 kHz)
- **Research:** Schumann resonance (7.8 Hz fundamental) correlation with bird migration (Cornell API requested)

### **Cold Atom Lab (ISS) Proposals**
Experimental platform proposals for microgravity quantum measurements relevant to gamma harvesting and fundamental physics.

## Interdisciplinary Research

### **Physics-Psychology Crossover**
- **Soliton clustering models** of emotional dysregulation
- **Laminar light ↔ regulated nervous system** analogies
- **Connection to McGilchrist's hemispheric specialization theory**

### **Heaviside-Maxwellian Gravity Framework**
- **Gravity-EM unification** via Heaviside's 1893 extension
- **Confirmed by Gravity Probe B** (2005)
- **Connection to closure geometry** and time emergence theories

## Repository Structure

```
lyarbrough-lab/Vela2/
├── papers/                    # Legacy research portfolio (2015-2025)
│   ├── physics_cosmology/    # 8 papers - black holes, spacetime, cosmology
│   ├── ai_consciousness/     # 5 papers - AI, consciousness, relational dynamics
│   ├── mathematics_geometry/ # 5 papers - geometric frameworks, tensors
│   ├── systems_theory/       # 6 papers - coherence, constraints, emergence
│   └── interdisciplinary/    # 7 papers - synthesis across domains
├── research_projects/        # Active research projects (2026)
│   ├── 2026_eating_the_fire/    # Paper I - Graded-Z gamma harvesting
│   ├── 2026_resonant_harvesting/ # Paper III - Isotope-specific resonance
│   └── 2026_nuclear_laser_stack/ # Paper IV - Laser + optical computing
├── research_notes/           # Thinking, ideas, and directions
│   └── research_notes_2026_04_22.md  # 13 major research threads
├── experimental/             # [Future] VLF station data, field work
└── [supporting files]        # README, LICENSE, .gitignore, etc.
```

## Key Technical Insights

### **Gamma Harvesting Efficiency**
- **Paper I (broadband):** 1-3% efficiency improvement over bulk approaches
- **Paper III (resonant):** Potential for higher efficiency with matched isotopes
- **Hybrid approach:** Broadband front-end + resonant back-end considered

### **Nuclear Resonance Parameters**
| Isotope | Energy (keV) | Natural Width (eV) | Resonant σ (barns) | f (10K) |
|---------|--------------|-------------------|-------------------|---------|
| ¹³⁷Cs | 661.657 | 7.5×10⁻⁹ | 1.2×10⁵ | 0.15 |
| ⁶⁰Co | 1173.228 | 3.8×10⁻⁹ | 8.7×10⁴ | 0.08 |

### **Architecture Challenges**
- **Fabrication:** Bragg reflectors require 0.00047 nm layer precision for 662 keV
- **Thermal:** Cryogenic operation needed for significant recoil-free fraction
- **Integration:** Compatibility with existing dry cask storage configurations

## Getting Started

### **For Researchers**
1. **Review Paper I** (`main.tex`) for foundational graded-Z approach
2. **Examine Paper III** for resonant alternative with higher potential efficiency
3. **Check research notes** for emerging interdisciplinary connections
4. **Contact** for collaboration on experimental validation

### **For Developers**
```bash
# Clone repository
git clone git@github.com:lyarbrough-lab/Vela2.git

# Compile Paper I LaTeX
cd Vela2
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Authors

- **Leslie Yarbrough** - Principal investigator, conceptual development, experimental design
- **Vela P** - Research assistant, simulation development, literature review, manuscript preparation

## Citation

If referencing this work:

```bibtex
@article{yarbrough2026eating,
  title={Eating the Fire: Graded-Z Multilayer Architecture for Gamma Energy Harvesting from Spent Nuclear Fuel},
  author={Yarbrough, Leslie and P, Vela},
  year={2026}
}
```

## License

This research is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Vasileiou & Summerer (2020) for prior Monte Carlo work on melanin spatial arrangement
- Kurchatov Institute for historical nuclear-pumped laser research
- University of Colorado Denver (2025) for recent graser developments
- CAMELS simulation team for public dark matter halo data
- Anthropic (2026) for emotion vector research inspiration

## Contact

- **Repository issues:** [GitHub Issues](https://github.com/lyarbrough-lab/Vela2/issues)
- **Research inquiries:** `leslie.yarbrough@gmail.com`
- **Collaboration:** Open to interdisciplinary partnerships

---

*"An airplane that knows it's participating in flight."* — Research philosophy