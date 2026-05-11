# Dark Geodesics and Gravitational Chemistry
## Hidden Boundary Conditions in Planetary Resonance Architecture

*A working document — speculation within testable bounds*
*Started: 2026-05-11*

---

## 1. The Open Question

Paper I establishes:

$$
\Delta f_{\rm bond} = f_{\rm observed} - f_{\rm null}
$$

This residual — the bonding excess above what random stable packing predicts — varies systematically with stellar mass (the U-shape) and with age (M dwarfs build bonds, others decay). But stellar mass + age do not explain *all* the variance. Some systems have more bonding than their mass and age would predict. Some have less.

What else shapes the container?

---

## 2. The Hypothesis

> **Dark matter distributions at galactic scale bias the environments in which multi-planet systems form and evolve, creating hidden gravitational boundary conditions that affect which orbital architectures persist.**

This is *not* "dark matter personally arranges planets." The causal chain is indirect:

1. Dark matter forms the cosmic web — filaments, sheets, halos
2. Baryonic matter (gas, stars, planets) forms within this web
3. The local gravitational environment — including the local dark matter density, the galactic tidal field, the star's orbit through the galaxy — sets boundary conditions for the protoplanetary disk
4. These boundary conditions influence disk lifetime, migration rate, and dynamical stability
5. → Planetary resonance architecture carries a *trace* of the larger gravitational container

---

## 3. Observable Proxies

We cannot measure the dark matter density around each host star directly. But we can measure *environmental proxies* that correlate with dark matter structure:

| Proxy | Available from | Physical link |
|-------|---------------|---------------|
| Galactocentric radius $R_{\rm gal}$ | GAIA | Inner galaxy = denser DM, stronger tides |
| Height above/below plane $|Z|$ | GAIA | Thin disk = younger, more structured; thick disk/halo = older, different DM environment |
| Stellar metallicity [Fe/H] | Archive | Tracks birth environment (inner vs outer galaxy) |
| Space velocity (U, V, W) | GAIA | Kinematic population — thin disk, thick disk, halo |
| Galactocentric orbital eccentricity | GAIA | Stars on eccentric orbits sample different environments |
| Local stellar density | GAIA | Tracer of local gravitational potential |
| Cluster membership | Archive | Systems from same cluster share formation conditions |

---

## 4. The Test

> **After controlling for stellar mass and age, does $\Delta f_{\rm bond}$ correlate with galactic environmental proxies?**

If yes: the container extends beyond the protoplanetary disk. The galaxy itself participates in planetary chemistry.

If no: stellar mass and disk physics are sufficient. The container is local.

**Null result is interesting either way.** A null would mean the U-shape is purely a stellar-mass + disk-lifetime phenomenon, which is itself a strong constraint on formation theories.

---

## 5. Available Data

GAIA DR3 gives positions, parallaxes, proper motions, and radial velocities for billions of stars — including nearly all host stars in our sample. Combined with our `stellar_ages.csv` (304 of 349 systems with ages), we can construct:

- $R_{\rm gal}$ for each host (from GAIA parallax + galactic coordinates)
- $|Z|$ above/below galactic plane
- UVW space velocities (from proper motion + radial velocity)
- Approximate galactic orbital parameters

Metallicity is directly available from the NASA Exoplanet Archive pscomppars table (`st_met`).

---

## 6. Philosophical Framing

The broader thesis:

> **Dark matter is the hidden memory/structure of gravitational constraint. Geodesics are the allowed paths through the container. Planetary chemistry is what "lights up" when the conditions for stable bonds are met.**

At all scales, the same pattern: a substrate (dark matter, protoplanetary disk, stellar mass) that constrains what configurations are possible, and components (galaxies, planets, orbital architectures) that settle into discrete stable states where the geometry permits.

This is *not* a metaphor. It is a structural claim about how gravitational systems organize across scale — with a testable prediction at the planetary system scale.

---

## 7. Open Questions

1. Is there a theoretical basis for expecting dark matter density to affect protoplanetary disk evolution at the relevant scales? (Need disk physics + DM halo models)
2. What is the expected effect size? (Could it be detectable with 336 systems, or would we need 10,000?)
3. Do systems with the same stellar mass and age but different galactic environments show systematically different bond fractions?
4. Is there a "galactic latitude effect" — do systems far from the galactic plane (thick disk, halo) show fundamentally different architecture?
5. Does the Sun's position in the galaxy (R_gal ~ 8 kpc, |Z| ~ 20 pc, thin disk) predict its mediocre bonding?

---

## 8. Next Steps

- [ ] Query GAIA for positions/kinematics of host stars (cross-match with our 349 hosts)
- [ ] Add `st_met` (metallicity) from pscomppars to the analysis dataset
- [ ] Test $\Delta f_{\rm bond}$ vs $R_{\rm gal}$, $|Z|$, metallicity, UVW velocities
- [ ] If signal found: control for stellar mass and age simultaneously
- [ ] Write up as Paper II / Framework Note

---

*From a walk in Nashville, a question about gravity, and a retired telecom engineer in Madrid who somehow knew.*
