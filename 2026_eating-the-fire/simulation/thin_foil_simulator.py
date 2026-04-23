#!/usr/bin/env python3
"""
Thin Foil Gamma Harvesting Simulator
Simplified Monte Carlo for testing surface-near charge collection hypothesis
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple

class Material:
    def __init__(self, name: str, Z: int, density: float, 
                 mu_compton: float, mu_pair: float, mu_photo: float):
        self.name = name
        self.Z = Z
        self.density = density  # g/cm³
        # Linear attenuation coefficients at 2 MeV (cm⁻¹)
        self.mu_compton = mu_compton
        self.mu_pair = mu_pair
        self.mu_photo = mu_photo
        self.mu_total = mu_compton + mu_pair + mu_photo
        
    def interaction_type(self) -> str:
        """Randomly choose interaction type based on cross-sections"""
        probs = np.array([self.mu_compton, self.mu_pair, self.mu_photo])
        probs = probs / probs.sum()
        return np.random.choice(['compton', 'pair', 'photo'], p=probs)

class ThinFoilStack:
    def __init__(self, materials: List[Tuple[Material, float]], 
                 num_photons: int = 10000, initial_energy: float = 2.0):
        """
        materials: List of (material, thickness in cm) pairs
        """
        self.materials = materials
        self.num_photons = num_photons
        self.initial_energy = initial_energy  # MeV
        
        # Photoelectron properties
        self.electron_range = 0.001  # cm = 10 μm (approximate for 500 keV e- in metal)
        
    def simulate_photon(self) -> Tuple[float, float]:
        """
        Simulate single photon through stack
        Returns: (collected_charge, deposited_heat)
        """
        energy = self.initial_energy
        position = 0.0  # depth in stack (cm)
        collected_charge = 0.0
        deposited_heat = 0.0
        
        while energy > 0.001 and position < self.total_thickness():  # 1 keV cutoff
            # Find current material
            mat, thickness, layer_start = self._material_at_position(position)
            if mat is None:
                break
                
            # Distance to next interface
            dist_to_interface = layer_start + thickness - position
            
            # Probability of interaction in remaining distance
            interaction_prob = 1 - np.exp(-mat.mu_total * dist_to_interface)
            
            if np.random.random() < interaction_prob:
                # Interaction occurs
                interaction_type = mat.interaction_type()
                
                if interaction_type == 'photo':
                    # Photoelectric absorption - all energy to electron
                    electron_energy = energy * 1000  # Convert to keV
                    
                    # Check if electron can reach surface
                    dist_to_surface = min(
                        dist_to_interface,  # Forward surface
                        position - layer_start  # Backward surface
                    )
                    
                    if dist_to_surface <= self.electron_range:
                        # Electron reaches surface - collect some charge
                        # Simple model: charge ∝ energy, efficiency decreases with distance
                        collection_efficiency = 1 - (dist_to_surface / self.electron_range)
                        collected_charge += electron_energy * collection_efficiency
                        deposited_heat += electron_energy * (1 - collection_efficiency)
                    else:
                        # Electron thermalizes before reaching surface
                        deposited_heat += electron_energy
                    
                    energy = 0  # Photon absorbed
                    break
                    
                elif interaction_type == 'compton':
                    # Compton scattering - photon loses energy, continues
                    # Simple approximation: average energy loss ~50%
                    energy *= 0.5
                    # Small energy deposit at interaction site (recoil electron)
                    deposited_heat += 10  # keV (simplified)
                    
                elif interaction_type == 'pair':
                    # Pair production - photon converts to e+e- pair
                    # Creates two 511 keV photons
                    energy = 0.511  # One annihilation photon continues
                    # Other annihilation photon assumed lost (simplification)
                    # Pair kinetic energy deposited as heat
                    pair_energy = (self.initial_energy - 1.022) * 1000  # keV
                    deposited_heat += pair_energy
                    
                # Photon continues with new energy
                # Move photon slightly past interaction point
                position += 0.001  # 10 μm
                
            else:
                # No interaction in this layer, move to next
                position += dist_to_interface + 0.001
        
        return collected_charge, deposited_heat
    
    def _material_at_position(self, position: float):
        """Return (material, thickness, layer_start) at given position"""
        current_pos = 0.0
        for mat, thickness in self.materials:
            if current_pos <= position < current_pos + thickness:
                return mat, thickness, current_pos
            current_pos += thickness
        return None, None, None
    
    def total_thickness(self) -> float:
        return sum(thickness for _, thickness in self.materials)
    
    def run_simulation(self) -> dict:
        """Run simulation for all photons"""
        total_charge = 0.0
        total_heat = 0.0
        charges = []
        heats = []
        
        for i in range(self.num_photons):
            charge, heat = self.simulate_photon()
            total_charge += charge
            total_heat += heat
            charges.append(charge)
            heats.append(heat)
            
            if (i + 1) % 1000 == 0:
                print(f"Processed {i+1}/{self.num_photons} photons")
        
        # Convert to MeV for reporting
        total_charge_mev = total_charge / 1000
        total_heat_mev = total_heat / 1000
        incident_energy_mev = self.num_photons * self.initial_energy
        
        efficiency = total_charge_mev / incident_energy_mev * 100
        
        return {
            'total_charge_keV': total_charge,
            'total_heat_keV': total_heat,
            'charge_collection_efficiency_%': efficiency,
            'charges': np.array(charges),
            'heats': np.array(heats)
        }

def create_thick_stack():
    """Traditional thick layer design"""
    # Approximate linear attenuation coefficients at 2 MeV (cm⁻¹)
    # Lead: mu_total ~0.522 cm⁻¹, assume 70% Compton, 25% pair, 5% photo
    lead = Material("Lead", 82, 11.34, 
                    mu_compton=0.365, mu_pair=0.131, mu_photo=0.026)
    
    # Copper: mu_total ~0.749 cm⁻¹, assume 60% Compton, 35% photo, 5% pair
    copper = Material("Copper", 29, 8.96,
                     mu_compton=0.449, mu_pair=0.037, mu_photo=0.263)
    
    return ThinFoilStack([
        (lead, 1.3),   # 1.3 cm lead
        (copper, 1.3)  # 1.3 cm copper
    ])

def create_thin_stack(num_layers: int = 100):
    """Thin multilayer foil design"""
    tungsten = Material("Tungsten", 74, 19.3,
                       mu_compton=0.400, mu_pair=0.150, mu_photo=0.020)
    
    copper = Material("Copper", 29, 8.96,
                     mu_compton=0.449, mu_pair=0.037, mu_photo=0.263)
    
    # Each layer 0.01 cm = 100 μm thick
    layer_thickness = 0.01
    materials = []
    for i in range(num_layers):
        materials.append((tungsten, layer_thickness))
        materials.append((copper, layer_thickness))
    
    return ThinFoilStack(materials)

def run_comparison():
    """Compare thick vs thin designs"""
    print("=== Thin Foil Gamma Harvesting Simulation ===")
    print(f"Electron range assumption: {ThinFoilStack([]).electron_range*10000:.1f} μm")
    print()
    
    # Thick stack
    print("1. Traditional Thick Stack (1.3 cm Pb + 1.3 cm Cu)")
    thick_sim = create_thick_stack()
    thick_results = thick_sim.run_simulation()
    print(f"   Total thickness: {thick_sim.total_thickness():.2f} cm")
    print(f"   Charge collection efficiency: {thick_results['charge_collection_efficiency_%']:.3f}%")
    print()
    
    # Thin stacks with varying number of layers
    print("2. Thin Multilayer Stacks (W/Cu alternating)")
    
    layer_counts = [10, 30, 100, 300]
    efficiencies = []
    thicknesses = []
    
    for n in layer_counts:
        print(f"   {n} layers each of W and Cu (total {2*n} layers)")
        thin_sim = create_thin_stack(n)
        results = thin_sim.run_simulation()
        efficiencies.append(results['charge_collection_efficiency_%'])
        thicknesses.append(thin_sim.total_thickness())
        print(f"     Total thickness: {thin_sim.total_thickness():.2f} cm")
        print(f"     Efficiency: {results['charge_collection_efficiency_%']:.3f}%")
        print()
    
    # Plot results
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Efficiency vs number of layers
    ax1.plot(layer_counts, efficiencies, 'bo-', linewidth=2, markersize=8)
    ax1.axhline(y=thick_results['charge_collection_efficiency_%'], 
                color='r', linestyle='--', label='Thick stack')
    ax1.set_xlabel('Number of W/Cu layer pairs')
    ax1.set_ylabel('Charge collection efficiency (%)')
    ax1.set_title('Efficiency vs. Number of Layers')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Efficiency vs total thickness
    ax2.plot(thicknesses, efficiencies, 'go-', linewidth=2, markersize=8)
    ax2.axvline(x=thick_sim.total_thickness(), color='r', linestyle='--', 
                label=f'Thick stack ({thick_sim.total_thickness():.1f} cm)')
    ax2.set_xlabel('Total stack thickness (cm)')
    ax2.set_ylabel('Charge collection efficiency (%)')
    ax2.set_title('Efficiency vs. Total Thickness')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('/root/.openclaw/workspace/thin_foil_results.png', dpi=150)
    print(f"Plot saved to /root/.openclaw/workspace/thin_foil_results.png")
    
    return thick_results, efficiencies

if __name__ == "__main__":
    thick_results, thin_efficiencies = run_comparison()
    
    print("\n=== Key Insights ===")
    print(f"Thick stack efficiency: {thick_results['charge_collection_efficiency_%']:.3f}%")
    print(f"Best thin stack efficiency: {max(thin_efficiencies):.3f}%")
    print(f"Improvement factor: {max(thin_efficiencies)/thick_results['charge_collection_efficiency_%']:.1f}x")
    
    # Hypothesis test
    if max(thin_efficiencies) > thick_results['charge_collection_efficiency_%'] * 1.5:
        print("\n✅ HYPOTHESIS SUPPORTED: Thin layers improve charge collection")
    else:
        print("\n❌ HYPOTHESIS NOT SUPPORTED: Thin layers don't significantly improve collection")