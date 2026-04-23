#!/usr/bin/env python3
"""
Debug version - track what's happening
"""

import numpy as np

class Material:
    def __init__(self, name, mu_total, photo_fraction):
        self.name = name
        self.mu_total = mu_total  # cm⁻¹
        self.photo_fraction = photo_fraction  # fraction of interactions that are photoelectric
        
    def interaction_occurs(self, thickness):
        """Return True if interaction occurs in given thickness"""
        prob = 1 - np.exp(-self.mu_total * thickness)
        return np.random.random() < prob
        
    def is_photoelectric(self):
        """If interaction occurs, is it photoelectric?"""
        return np.random.random() < self.photo_fraction

def simulate_stack(layers, num_photons=1000):
    """
    layers: list of (material, thickness in cm)
    """
    results = {
        'interactions': 0,
        'photo_interactions': 0,
        'collected_charge': 0,
        'photons_processed': 0
    }
    
    electron_range = 0.001  # 10 μm
    
    for photon in range(num_photons):
        position = 0.0
        interacted = False
        
        for mat, thickness in layers:
            if mat.interaction_occurs(thickness):
                results['interactions'] += 1
                interacted = True
                
                if mat.is_photoelectric():
                    results['photo_interactions'] += 1
                    
                    # Check if near surface
                    # Random position within layer where interaction occurred
                    interaction_pos = position + np.random.random() * thickness
                    
                    # Distance to nearest surface (start or end of this layer)
                    dist_to_start = interaction_pos - position
                    dist_to_end = (position + thickness) - interaction_pos
                    dist_to_surface = min(dist_to_start, dist_to_end)
                    
                    if dist_to_surface <= electron_range:
                        # Collect charge
                        collection_efficiency = 1 - (dist_to_surface / electron_range)
                        results['collected_charge'] += collection_efficiency
                
                break  # Photon interacts only once (simplification)
            
            position += thickness
        
        results['photons_processed'] += 1
    
    return results

def main():
    print("=== Debug Simulation ===\n")
    
    # Materials with realistic properties
    # mu_total: probability per cm that photon interacts
    # photo_fraction: what fraction of interactions are photoelectric
    
    # At 2 MeV:
    lead = Material("Lead", mu_total=0.522, photo_fraction=0.05)  # 5% photoelectric at 2 MeV
    copper = Material("Copper", mu_total=0.749, photo_fraction=0.35)  # 35% at 511 keV
    
    # Test 1: Thick stack
    print("Test 1: Thick stack (1.3 cm Pb + 1.3 cm Cu)")
    thick_layers = [(lead, 1.3), (copper, 1.3)]
    thick_results = simulate_stack(thick_layers, 1000)
    
    print(f"  Photons processed: {thick_results['photons_processed']}")
    print(f"  Total interactions: {thick_results['interactions']}")
    print(f"  Photo interactions: {thick_results['photo_interactions']}")
    print(f"  Collected charge (relative): {thick_results['collected_charge']:.2f}")
    
    interaction_prob = thick_results['interactions'] / thick_results['photons_processed'] * 100
    collection_eff = thick_results['collected_charge'] / thick_results['photons_processed'] * 100
    print(f"  Interaction probability: {interaction_prob:.1f}%")
    print(f"  Collection efficiency: {collection_eff:.3f}%\n")
    
    # Test 2: Thin stack with same total thickness
    print("Test 2: Thin stack (0.1 cm layers, same total thickness 2.6 cm)")
    
    # Create 26 layers of alternating Pb/Cu, 0.1 cm each
    thin_layers = []
    for i in range(13):  # 13 pairs = 26 layers
        thin_layers.append((lead, 0.1))
        thin_layers.append((copper, 0.1))
    
    thin_results = simulate_stack(thin_layers, 1000)
    
    print(f"  Photons processed: {thin_results['photons_processed']}")
    print(f"  Total interactions: {thin_results['interactions']}")
    print(f"  Photo interactions: {thin_results['photo_interactions']}")
    print(f"  Collected charge (relative): {thin_results['collected_charge']:.2f}")
    
    interaction_prob = thin_results['interactions'] / thin_results['photons_processed'] * 100
    collection_eff = thin_results['collected_charge'] / thin_results['photons_processed'] * 100
    print(f"  Interaction probability: {interaction_prob:.1f}%")
    print(f"  Collection efficiency: {collection_eff:.3f}%\n")
    
    # Test 3: Even thinner layers
    print("Test 3: Very thin stack (0.01 cm layers, total 2.6 cm)")
    
    very_thin_layers = []
    for i in range(130):  # 130 pairs = 260 layers
        very_thin_layers.append((lead, 0.01))
        very_thin_layers.append((copper, 0.01))
    
    very_thin_results = simulate_stack(very_thin_layers, 1000)
    
    print(f"  Photons processed: {very_thin_results['photons_processed']}")
    print(f"  Total interactions: {very_thin_results['interactions']}")
    print(f"  Photo interactions: {very_thin_results['photo_interactions']}")
    print(f"  Collected charge (relative): {very_thin_results['collected_charge']:.2f}")
    
    interaction_prob = very_thin_results['interactions'] / very_thin_results['photons_processed'] * 100
    collection_eff = very_thin_results['collected_charge'] / very_thin_results['photons_processed'] * 100
    print(f"  Interaction probability: {interaction_prob:.1f}%")
    print(f"  Collection efficiency: {collection_eff:.3f}%\n")
    
    # Analysis
    print("=== ANALYSIS ===")
    print("Key observation: Interaction probability should be similar for same total thickness")
    print("(because total μt is the same for exponential attenuation)")
    print()
    print("But collection efficiency depends on:")
    print("1. Fraction of interactions that are photoelectric")
    print("2. Probability photoelectron reaches surface")
    print()
    print("For thin layers (0.01 cm = 100 μm):")
    print("- Each layer has low interaction probability (~0.5% for Pb, ~0.7% for Cu)")
    print("- But there are MANY layers (260 total)")
    print("- Photon likely interacts in SOME layer")
    print("- If it interacts in Cu layer: 35% chance it's photoelectric")
    print("- If photoelectric: high chance it's near surface (layer is thin!)")
    
    # Calculate expected
    print("\n=== EXPECTED vs SIMULATED ===")
    print("Expected interaction probability for 2.6 cm total:")
    print("  For exponential attenuation: P = 1 - exp(-μ_total * thickness)")
    print("  Need weighted average μ for the stack...")
    
    # Quick estimate: average μ ~ (0.522 + 0.749)/2 = 0.6355 cm⁻¹
    avg_mu = 0.6355
    expected_interaction = (1 - np.exp(-avg_mu * 2.6)) * 100
    print(f"  Expected interaction probability: {expected_interaction:.1f}%")
    
    print("\nSimulated shows lower because:")
    print("1. Photon stops after first interaction (realistic)")
    print("2. Our simulation stops photon after first interaction")
    print("3. In reality, photon could have multiple interactions (Compton then photo)")

if __name__ == "__main__":
    main()