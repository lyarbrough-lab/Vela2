#!/usr/bin/env python3
"""
Thickness sweep to find optimal layer thickness
"""

import numpy as np

class Material:
    def __init__(self, name, mu_total, photo_fraction, density):
        self.name = name
        self.mu_total = mu_total  # cm⁻¹
        self.photo_fraction = photo_fraction
        self.density = density  # g/cm³
        
    def interaction_occurs(self, thickness):
        prob = 1 - np.exp(-self.mu_total * thickness)
        return np.random.random() < prob
        
    def is_photoelectric(self):
        return np.random.random() < self.photo_fraction

def simulate_thickness(layer_thickness_cm, num_photons=2000, total_thickness_cm=2.6):
    """
    Simulate stack with given layer thickness
    Total stack thickness fixed at 2.6 cm
    """
    # Materials (same as before)
    lead = Material("Lead", mu_total=0.522, photo_fraction=0.05, density=11.34)
    copper = Material("Copper", mu_total=0.749, photo_fraction=0.35, density=8.96)
    
    # Create stack
    layers = []
    current_thickness = 0
    electron_range = 0.001  # 10 μm
    
    while current_thickness < total_thickness_cm:
        # Add lead layer
        layers.append((lead, layer_thickness_cm))
        current_thickness += layer_thickness_cm
        
        if current_thickness >= total_thickness_cm:
            break
            
        # Add copper layer  
        layers.append((copper, layer_thickness_cm))
        current_thickness += layer_thickness_cm
    
    # Trim last layer if needed
    if current_thickness > total_thickness_cm:
        excess = current_thickness - total_thickness_cm
        last_mat, last_thick = layers[-1]
        layers[-1] = (last_mat, last_thick - excess)
    
    # Simulation
    total_interactions = 0
    photo_interactions = 0
    collected_charge = 0.0
    
    for _ in range(num_photons):
        position = 0.0
        interacted = False
        
        for mat, thickness in layers:
            if mat.interaction_occurs(thickness):
                total_interactions += 1
                interacted = True
                
                if mat.is_photoelectric():
                    photo_interactions += 1
                    
                    # Random position within layer
                    interaction_pos = position + np.random.random() * thickness
                    
                    # Distance to nearest surface
                    dist_to_start = interaction_pos - position
                    dist_to_end = (position + thickness) - interaction_pos
                    dist_to_surface = min(dist_to_start, dist_to_end)
                    
                    if dist_to_surface <= electron_range:
                        collection_efficiency = 1 - (dist_to_surface / electron_range)
                        collected_charge += collection_efficiency
                
                break  # First interaction only
            
            position += thickness
    
    # Calculate metrics
    interaction_prob = total_interactions / num_photons * 100
    collection_eff = collected_charge / num_photons * 100
    num_layers = len(layers)
    
    return {
        'layer_thickness_cm': layer_thickness_cm,
        'layer_thickness_um': layer_thickness_cm * 10000,
        'num_layers': num_layers,
        'interaction_prob_%': interaction_prob,
        'photo_interactions': photo_interactions,
        'collection_eff_%': collection_eff,
        'total_thickness_cm': sum(thickness for _, thickness in layers)
    }

def main():
    print("=== Layer Thickness Optimization Sweep ===\n")
    print("Fixed total stack thickness: 2.6 cm (Pb/Cu alternating)")
    print("Electron range assumption: 10 μm\n")
    
    # Thicknesses to test (in cm)
    thicknesses_cm = [
        0.5,      # 5 mm
        0.2,      # 2 mm  
        0.1,      # 1 mm
        0.05,     # 500 μm
        0.02,     # 200 μm
        0.01,     # 100 μm
        0.005,    # 50 μm
        0.002,    # 20 μm
        0.001,    # 10 μm
        0.0005,   # 5 μm
    ]
    
    results = []
    
    print("Layer Thickness | Num Layers | Interaction % | Collection % | Improvement")
    print("-------------------------------------------------------------------------")
    
    baseline_eff = None
    
    for thickness_cm in thicknesses_cm:
        result = simulate_thickness(thickness_cm, num_photons=2000)
        results.append(result)
        
        if baseline_eff is None:
            baseline_eff = result['collection_eff_%']
            improvement = 1.0
        else:
            improvement = result['collection_eff_%'] / baseline_eff
        
        print(f"{result['layer_thickness_um']:6.0f} μm | "
              f"{result['num_layers']:10d} | "
              f"{result['interaction_prob_%']:12.1f}% | "
              f"{result['collection_eff_%']:12.3f}% | "
              f"{improvement:10.1f}x")
    
    # Find optimal
    best_result = max(results, key=lambda x: x['collection_eff_%'])
    
    print("\n=== OPTIMAL THICKNESS ===")
    print(f"Best thickness: {best_result['layer_thickness_um']:.0f} μm")
    print(f"Collection efficiency: {best_result['collection_eff_%']:.3f}%")
    print(f"Number of layers: {best_result['num_layers']}")
    print(f"Interaction probability: {best_result['interaction_prob_%']:.1f}%")
    
    # Analysis
    print("\n=== ANALYSIS ===")
    print("Trends observed:")
    
    # Calculate trends
    thick_results = [r for r in results if r['layer_thickness_um'] >= 1000]  # ≥1 mm
    medium_results = [r for r in results if 100 <= r['layer_thickness_um'] < 1000]
    thin_results = [r for r in results if r['layer_thickness_um'] < 100]
    
    if thick_results and thin_results:
        avg_thick = np.mean([r['collection_eff_%'] for r in thick_results])
        avg_thin = np.mean([r['collection_eff_%'] for r in thin_results])
        print(f"  Thick layers (≥1 mm): ~{avg_thick:.3f}% average")
        print(f"  Thin layers (<100 μm): ~{avg_thin:.3f}% average")
        print(f"  Improvement: {avg_thin/avg_thick:.1f}x")
    
    print("\nKey insight:")
    print("There's likely an optimal thickness where:")
    print("1. Layers are thin enough for good surface proximity")
    print("2. But thick enough for reasonable interaction probability per layer")
    print("3. And manufacturing constraints (can't make infinitely thin layers)")
    
    print("\n=== NEXT STEPS ===")
    print("1. Add Compton cascade (photons can have multiple interactions)")
    print("2. Include pair production → annihilation photons")
    print("3. Model electron transport more realistically")
    print("4. Consider manufacturing limits (what thickness is feasible?)")
    
    # Save results
    with open('/root/.openclaw/workspace/thickness_results.txt', 'w') as f:
        f.write("Layer Thickness (μm),Num Layers,Interaction %,Collection %\n")
        for r in results:
            f.write(f"{r['layer_thickness_um']:.1f},{r['num_layers']},"
                   f"{r['interaction_prob_%']:.2f},{r['collection_eff_%']:.4f}\n")
    
    print(f"\nResults saved to /root/.openclaw/workspace/thickness_results.txt")

if __name__ == "__main__":
    main()