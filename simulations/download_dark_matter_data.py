#!/usr/bin/env python3
"""
Download and analyze CAMELS dark matter halo data
"""

import numpy as np
import pandas as pd
import requests
from io import StringIO
import matplotlib.pyplot as plt
from scipy import stats
import powerlaw

def download_halo_catalog(simulation="LH_35", snapshot="5"):
    """Download a Rockstar halo catalog from CAMELS."""
    
    base_url = "https://users.flatironinstitute.org/~camels/Rockstar/CAMELS-SAM/LH"
    url = f"{base_url}/{simulation}/Rockstar/out_{snapshot}.list"
    
    print(f"Downloading: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse the data
        lines = response.text.split('\n')
        
        # Find header end and data start
        data_lines = []
        for line in lines:
            if line.startswith('#') or not line.strip():
                continue
            data_lines.append(line)
        
        # Column names from header
        columns = [
            'ID', 'DescID', 'Mvir', 'Vmax', 'Vrms', 'Rvir', 'Rs', 'Np',
            'X', 'Y', 'Z', 'VX', 'VY', 'VZ', 'JX', 'JY', 'JZ', 'Spin',
            'rs_klypin', 'Mvir_all', 'M200b', 'M200c', 'M500c', 'M2500c',
            'Xoff', 'Voff', 'spin_bullock', 'b_to_a', 'c_to_a',
            'A[x]', 'A[y]', 'A[z]', 'b_to_a(500c)', 'c_to_a(500c)',
            'A[x](500c)', 'A[y](500c)', 'A[z](500c)', 'T/|U|',
            'M_pe_Behroozi', 'M_pe_Diemer', 'Halfmass_Radius'
        ]
        
        # Parse data
        data = []
        for line in data_lines:
            if line.strip():
                values = line.split()
                if len(values) == len(columns):
                    data.append([float(v) for v in values])
        
        df = pd.DataFrame(data, columns=columns)
        print(f"Downloaded {len(df)} halos")
        return df
        
    except Exception as e:
        print(f"Error downloading data: {e}")
        return None

def analyze_halo_distribution(df):
    """Analyze dark matter halo distribution statistics."""
    
    print("\n=== DARK MATTER HALO ANALYSIS ===")
    
    # Extract masses
    masses = df['Mvir'].values
    print(f"Number of halos: {len(masses)}")
    print(f"Mass range: {masses.min():.2e} to {masses.max():.2e} Msun/h")
    print(f"Mean mass: {masses.mean():.2e} Msun/h")
    print(f"Median mass: {np.median(masses):.2e} Msun/h")
    
    # Power law fit
    print("\n--- Power Law Analysis ---")
    fit = powerlaw.Fit(masses, xmin=masses.min())
    alpha = fit.power_law.alpha
    xmin = fit.power_law.xmin
    print(f"Power law exponent α = {alpha:.3f}")
    print(f"Minimum cutoff xmin = {xmin:.2e}")
    
    # Mass function (dN/dM)
    log_masses = np.log10(masses)
    hist, bin_edges = np.histogram(log_masses, bins=30)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Fit linear slope in log-log space (power law)
    valid = hist > 0
    if np.sum(valid) > 2:
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            bin_centers[valid], np.log10(hist[valid])
        )
        print(f"Mass function slope: {slope:.3f} (R² = {r_value**2:.3f})")
    
    # Spatial distribution
    print("\n--- Spatial Distribution ---")
    positions = df[['X', 'Y', 'Z']].values
    
    # Mean inter-halo distance
    from scipy.spatial.distance import pdist
    if len(positions) > 1000:
        sample_positions = positions[:1000]  # Subsample for speed
    else:
        sample_positions = positions
    
    distances = pdist(sample_positions)
    print(f"Mean inter-halo distance: {distances.mean():.3f} Mpc/h")
    print(f"Distance std: {distances.std():.3f} Mpc/h")
    
    # Clustering (simple nearest neighbor)
    from scipy.spatial import KDTree
    tree = KDTree(positions)
    distances_nn, _ = tree.query(positions, k=2)  # k=2 because includes self
    avg_nearest_neighbor = np.mean(distances_nn[:, 1])  # Exclude self
    print(f"Average nearest neighbor distance: {avg_nearest_neighbor:.3f} Mpc/h")
    
    return {
        'masses': masses,
        'positions': positions,
        'alpha': alpha,
        'xmin': xmin,
        'mass_function_slope': slope if 'slope' in locals() else None
    }

def plot_distributions(df, results):
    """Create plots of dark matter halo distributions."""
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # 1. Mass distribution
    ax = axes[0, 0]
    ax.hist(np.log10(results['masses']), bins=50, alpha=0.7, density=True)
    ax.set_xlabel('log10(Mass [Msun/h])')
    ax.set_ylabel('Probability density')
    ax.set_title('Dark Matter Halo Mass Distribution')
    
    # 2. Mass function (dN/dM)
    ax = axes[0, 1]
    log_masses = np.log10(results['masses'])
    hist, bin_edges = np.histogram(log_masses, bins=30)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    ax.plot(bin_centers, hist, 'o-', alpha=0.7)
    ax.set_xlabel('log10(Mass [Msun/h])')
    ax.set_ylabel('Number of halos')
    ax.set_title('Halo Mass Function')
    ax.set_yscale('log')
    
    # 3. Power law fit
    ax = axes[0, 2]
    fit = powerlaw.Fit(results['masses'], xmin=results['masses'].min())
    fit.plot_pdf(color='blue', linewidth=2, ax=ax, label='Power law fit')
    ax.set_xlabel('Mass [Msun/h]')
    ax.set_ylabel('PDF')
    ax.set_title('Power Law Fit')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend()
    
    # 4. Spatial distribution (2D projection)
    ax = axes[1, 0]
    if len(results['positions']) > 1000:
        sample_pos = results['positions'][:1000]
    else:
        sample_pos = results['positions']
    
    ax.scatter(sample_pos[:, 0], sample_pos[:, 1], alpha=0.5, s=1)
    ax.set_xlabel('X [Mpc/h]')
    ax.set_ylabel('Y [Mpc/h]')
    ax.set_title('Spatial Distribution (XY projection)')
    ax.set_aspect('equal')
    
    # 5. Nearest neighbor distance distribution
    ax = axes[1, 1]
    from scipy.spatial import KDTree
    tree = KDTree(results['positions'])
    distances_nn, _ = tree.query(results['positions'], k=2)
    nn_distances = distances_nn[:, 1]
    
    ax.hist(nn_distances, bins=50, alpha=0.7, density=True)
    ax.set_xlabel('Nearest neighbor distance [Mpc/h]')
    ax.set_ylabel('Probability density')
    ax.set_title('Nearest Neighbor Distribution')
    
    # 6. Correlation function (simple 2-point)
    ax = axes[1, 2]
    from scipy.spatial.distance import pdist
    if len(results['positions']) > 1000:
        sample = results['positions'][:1000]
        distances = pdist(sample)
    else:
        distances = pdist(results['positions'])
    
    ax.hist(distances, bins=50, alpha=0.7, density=True)
    ax.set_xlabel('Pairwise distance [Mpc/h]')
    ax.set_ylabel('Probability density')
    ax.set_title('Pair Distance Distribution')
    
    plt.tight_layout()
    plt.savefig('/root/.openclaw/workspace/dark_matter_halo_analysis.png', 
                dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\nPlot saved to: /root/.openclaw/workspace/dark_matter_halo_analysis.png")

def compare_with_emotion_vectors(halo_results, emotion_alpha=1.135):
    """Compare dark matter statistics with emotion vector statistics."""
    
    print("\n=== COMPARISON WITH EMOTION VECTORS ===")
    print(f"Dark matter power law exponent: α = {halo_results['alpha']:.3f}")
    print(f"Emotion vector power law exponent: α = {emotion_alpha:.3f}")
    
    exponent_diff = abs(halo_results['alpha'] - emotion_alpha)
    print(f"Exponent difference: {exponent_diff:.3f}")
    
    if exponent_diff < 0.3:
        print("✅ SIMILAR: Power law exponents are close (< 0.3 difference)")
    elif exponent_diff < 0.5:
        print("⚠️ MODERATELY SIMILAR: Exponents somewhat similar (< 0.5 difference)")
    else:
        print("❌ DIFFERENT: Exponents differ significantly")
    
    # Additional comparison metrics could be added here
    # when we have emotion vector data
    
    return exponent_diff

def main():
    """Main analysis pipeline."""
    
    print("CAMELS DARK MATTER HALO DATA ANALYSIS")
    print("=" * 50)
    
    # Download data
    df = download_halo_catalog(simulation="LH_35", snapshot="5")
    
    if df is None or len(df) == 0:
        print("Failed to download data. Trying alternative...")
        # Try a different snapshot
        df = download_halo_catalog(simulation="LH_35", snapshot="6")
    
    if df is None or len(df) == 0:
        print("Could not download data. Exiting.")
        return
    
    # Analyze dark matter distribution
    halo_results = analyze_halo_distribution(df)
    
    # Create plots
    plot_distributions(df, halo_results)
    
    # Compare with emotion vectors (using synthetic exponent for now)
    # When we get real emotion vector data, we'll update this
    compare_with_emotion_vectors(halo_results, emotion_alpha=1.135)
    
    # Save results
    results_summary = {
        'n_halos': len(df),
        'mass_mean': float(np.mean(halo_results['masses'])),
        'mass_median': float(np.median(halo_results['masses'])),
        'power_law_alpha': float(halo_results['alpha']),
        'power_law_xmin': float(halo_results['xmin']),
        'mass_function_slope': float(halo_results['mass_function_slope']) if halo_results['mass_function_slope'] else None
    }
    
    print("\n" + "=" * 50)
    print("ANALYSIS COMPLETE")
    print("=" * 50)
    for key, value in results_summary.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()