#!/usr/bin/env python3
"""
Simplified simulator without plotting
"""

import numpy as np

class Material:
    def __init__(self, name: str, Z: int, density: float, 
                 mu_compton: float, mu_pair: float, mu_photo: float):
        self.name = name
        self.Z = Z
        self.density = density
        self.mu_compton = mu_compton
        self.mu_pair = mu_pair
        self.mu_photo = mu_photo
        self.mu_total = mu_compton + mu_pair + mu_photo
        
    def interaction_type(self) -> str:
        probs = np.array([self.mu_compton, self.mu_pair, self.mu_photo])
        probs = probs / probs.sum()
        return np.random.choice(['compton', 'pair', 'photo'], p=probs)

class ThinFoilStack:
    def __init__(self, materials, num_photons=5000, initial_energy=2.0):
        self.materials = materials
        self.num_photons = num_photons
        self.initial_energy = initial_energy
        self.electron_range = 0.001  # 10 μm
        
    def total_thickness(self):
        return sum(thickness for _, thickness in self.materials)
    
    def simulate_photon(self):
        energy = self.initial_energy
        position = 0.0
        collected_charge = 0.0
        deposited_heat = 0.0
        
        while energy > 0.001 and position < self.total_thickness():
            # Find current material
            current_pos = 0.0
            mat = None
            thickness = 0
            layer_start = 0
            for m, t in self.materials:
                if current_pos <= position < current_pos + t:
                    mat, thickness, layer_start = m, t, current_pos
                    break
                current_pos += t
            
            if mat is None:
                break
                
            dist_to_interface = layer_start + thickness - position
            interaction_prob = 1 - np.exp(-mat.mu_total * dist_to_interface)
            
            if np.random.random() < interaction_prob:
                interaction_type = mat.interaction_type()
                
                if interaction_type == 'photo':
                    electron_energy = energy * 1000  # keV
                    dist_to_surface = min(dist_to_interface, position - layer_start)
                    
                    if dist_to_surface <= self.electron_range:
                        collection_efficiency = 1 - (dist_to_surface / self.electron_range)
                        collected_charge += electron_energy * collection_efficiency
                        deposited_heat += electron_energy * (1 - collection_efficiency)
                    else:
                        deposited_heat += electron_energy
                    
                    energy = 0
                    break
                    
                elif interaction_type == 'compton':
                    energy *= 0.5
                    deposited_heat += 10
                    
                elif interaction_type == 'pair':
                    energy = 0.511
                    pair_energy = (self.initial_energy - 1.022) * 1000
                    deposited_heat += pair_energy
                    
                position += 0.001
            else:
                position += dist_to_interface + 0.001
        
        return collected_charge, deposited_heat
    
    def run_simulation(self):
        total_charge = 0.0
        total_heat = 0.0
        
        for i in range(self.num_photons):
            charge, heat = self.simulate_photon()
            total_charge += charge
            total_heat += heat
            
            if (i + 1) % 1000 == 0:
                print(f"  Processed {i+1}/{self.num_photons} photons")
        
        total_charge_mev = total_charge / 1000
        incident_energy_mev = self.num_photons * self.initial_energy
        efficiency = total_charge_mev / incident_energy_mev * 100
        
        return efficiency

def main():
    print("=== Thin Foil Gamma Harvesting Simulation ===\n")
    
    # Materials (linear attenuation coefficients in cm⁻¹ at ~2 MeV)
    # Rough estimates based on NIST data
    lead = Material("Lead", 82, 11.34, 0.365, 0.131, 0.026)
    copper = Material("Copper", 29, 8.96, 0.449, 0.037, 0.263)
    tungsten = Material("Tungsten", 74, 19.3, 0.400, 0.150, 0.020)
    
    # Thick stack
    print("1. Traditional Thick Stack (1.3 cm Pb + 1.3 cm Cu)")
    thick_stack = ThinFoilStack([(lead, 1.3), (copper, 1.3)], num_photons=2000)
    thick_eff = thick_stack.run_simulation()
    print(f"   Total thickness: {thick_stack.total_thickness():.2f} cm")
    print(f"   Efficiency: {thick_eff:.3f}%\n")
    
    # Thin stacks
    print("2. Thin Multilayer Stacks (W/Cu alternating, 0.01 cm each)")
    
    layer_pairs = [5, 15, 50, 150]  # Number of W/Cu pairs
    efficiencies = []
    
    for n in layer_pairs:
        print(f"   {n} layer pairs (total {2*n} layers)")
        materials = []
        for _ in range(n):
            materials.append((tungsten, 0.01))  # 100 μm tungsten
            materials.append((copper, 0.01))    # 100 μm copper
        
        thin_stack = ThinFoilStack(materials, num_photons=2000)
        eff = thin_stack.run_simulation()
        efficiencies.append(eff)
        print(f"     Total thickness: {thin_stack.total_thickness():.2f} cm")
        print(f"     Efficiency: {eff:.3f}%\n")
    
    # Results
    print("=== RESULTS ===")
    print(f"Thick stack efficiency: {thick_eff:.3f}%")
    print(f"Best thin stack efficiency: {max(efficiencies):.3f}%")
    improvement = max(efficiencies) / thick_eff if thick_eff > 0 else 0
    print(f"Improvement factor: {improvement:.1f}x")
    
    if improvement > 1.5:
        print("\n✅ HYPOTHESIS SUPPORTED: Thin layers improve charge collection")
        print(f"   Thin stack is {improvement:.1f}x more efficient than thick stack")
    else:
        print("\n❌ HYPOTHESIS NOT SUPPORTED: Thin layers don't significantly improve collection")
    
    # Key insight
    print("\n=== KEY INSIGHT ===")
    print("The improvement comes from:")
    print("1. More interfaces = more collection surfaces")
    print("2. Shorter distances for photoelectrons to reach surfaces")
    print("3. Multiple chances for photons to interact near surfaces")
    
    # Limitations of this simulation
    print("\n=== LIMITATIONS ===")
    print("This simulation simplifies:")
    print("- Photon energy spectrum (only 2 MeV)")
    print("- Exact cross-sections (rough estimates)")
    print("- Electron transport (simple range model)")
    print("- No secondary particle tracking")
    print("- No charge multiplication effects")
    
    print("\nNext step: Full Monte Carlo with proper cross-sections and electron transport")

if __name__ == "__main__":
    main()