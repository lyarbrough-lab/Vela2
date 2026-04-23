#!/usr/bin/env python3
"""
Dark Matter in the Machine: Statistical comparison of emotion vectors and dark matter distributions
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import networkx as nx
from collections import Counter
import powerlaw

def generate_synthetic_emotion_vectors(n=171, dim=1000):
    """
    Generate synthetic emotion vector activation data.
    Based on properties from Anthropic paper:
    - 171 emotion concepts
    - Activation patterns across neural dimensions
    - Clustering of similar emotions
    """
    np.random.seed(42)
    
    # Create base emotion clusters (similar emotions cluster together)
    n_clusters = 8  # Rough number of emotion families
    cluster_centers = np.random.randn(n_clusters, dim) * 2
    
    # Assign emotions to clusters
    cluster_assignments = np.random.choice(n_clusters, n)
    
    # Generate vectors with cluster structure plus noise
    vectors = []
    for i in range(n):
        center = cluster_centers[cluster_assignments[i]]
        vector = center + np.random.randn(dim) * 0.5
        vectors.append(vector)
    
    vectors = np.array(vectors)
    
    # Simulate activation strengths (some emotions activate more strongly)
    activation_strengths = np.random.pareto(2.5, n)  # Power law distribution
    
    return vectors, activation_strengths, cluster_assignments

def generate_synthetic_dark_matter_halos(n_halos=10000):
    """
    Generate synthetic dark matter halo data.
    Based on properties from cosmological simulations:
    - Power law mass distribution
    - Hierarchical clustering
    - Scale-free structure
    """
    np.random.seed(42)
    
    # Halo masses follow power law (Schechter function)
    # dN/dM ∝ M^(-α) exp(-M/M*)
    alpha = 1.9  # Typical slope
    M_star = 1e12  # Characteristic mass (solar masses)
    
    # Generate masses from power law with exponential cutoff
    masses = np.random.pareto(alpha, n_halos) * 1e10
    masses = masses[masses < M_star * 10]  # Apply cutoff
    masses = masses[:n_halos]  # Trim if needed
    
    # Positions with clustering (simulate large-scale structure)
    # Use lognormal distribution for density field
    positions = np.random.lognormal(mean=0, sigma=1.0, size=(n_halos, 3))
    
    return masses, positions

def analyze_power_laws(emotion_strengths, halo_masses):
    """Compare power law distributions."""
    
    print("=== POWER LAW ANALYSIS ===")
    
    # Fit power law to emotion activation strengths
    fit_emotion = powerlaw.Fit(emotion_strengths, xmin=emotion_strengths.min())
    emotion_alpha = fit_emotion.power_law.alpha
    emotion_xmin = fit_emotion.power_law.xmin
    print(f"Emotion vector power law exponent: α = {emotion_alpha:.3f}")
    print(f"Emotion vector xmin: {emotion_xmin:.3f}")
    
    # Fit power law to halo masses
    fit_halo = powerlaw.Fit(halo_masses, xmin=halo_masses.min() * 10)
    halo_alpha = fit_halo.power_law.alpha
    halo_xmin = fit_halo.power_law.xmin
    print(f"Dark matter halo power law exponent: α = {halo_alpha:.3f}")
    print(f"Dark matter halo xmin: {halo_xmin:.3e}")
    
    # Compare exponents
    print(f"\nExponent difference: {abs(emotion_alpha - halo_alpha):.3f}")
    
    return fit_emotion, fit_halo, emotion_alpha, halo_alpha

def analyze_clustering(emotion_vectors, halo_positions):
    """Compare clustering patterns."""
    
    print("\n=== CLUSTERING ANALYSIS ===")
    
    # For emotion vectors: cosine similarity clustering
    from sklearn.metrics.pairwise import cosine_similarity
    emotion_similarity = cosine_similarity(emotion_vectors)
    
    # Create emotion graph (threshold similarity)
    emotion_graph = nx.Graph()
    n_emotions = len(emotion_vectors)
    for i in range(n_emotions):
        emotion_graph.add_node(i)
    
    threshold = 0.7  # Similarity threshold
    for i in range(n_emotions):
        for j in range(i+1, n_emotions):
            if emotion_similarity[i, j] > threshold:
                emotion_graph.add_edge(i, j)
    
    # Emotion graph metrics
    emotion_cc = nx.average_clustering(emotion_graph)
    emotion_degree = np.mean([d for _, d in emotion_graph.degree()])
    
    print(f"Emotion vector graph:")
    print(f"  Average clustering coefficient: {emotion_cc:.3f}")
    print(f"  Average degree: {emotion_degree:.3f}")
    
    # For dark matter: spatial clustering
    # Simple nearest neighbor analysis
    from scipy.spatial import KDTree
    tree = KDTree(halo_positions)
    
    # Find 5 nearest neighbors for each halo
    distances, _ = tree.query(halo_positions, k=6)  # k=6 because includes self
    avg_neighbor_dist = np.mean(distances[:, 1:])  # Exclude self
    
    print(f"\nDark matter halos:")
    print(f"  Average nearest neighbor distance: {avg_neighbor_dist:.3f}")
    
    return emotion_graph, avg_neighbor_dist

def analyze_correlation_functions(emotion_vectors, halo_positions):
    """Compare correlation functions."""
    
    print("\n=== CORRELATION FUNCTION ANALYSIS ===")
    
    # Emotion vector correlation (cosine similarity distribution)
    from sklearn.metrics.pairwise import cosine_similarity
    emotion_sim = cosine_similarity(emotion_vectors)
    # Take upper triangle (excluding diagonal)
    emotion_correlations = emotion_sim[np.triu_indices_from(emotion_sim, k=1)]
    
    # Dark matter spatial correlation (distance distribution)
    from scipy.spatial.distance import pdist
    halo_distances = pdist(halo_positions[:1000])  # Subsample for speed
    
    # Compare distributions
    emotion_mean = np.mean(emotion_correlations)
    emotion_std = np.std(emotion_correlations)
    
    halo_mean = np.mean(halo_distances)
    halo_std = np.std(halo_distances)
    
    print(f"Emotion vector correlations:")
    print(f"  Mean similarity: {emotion_mean:.3f}")
    print(f"  Std similarity: {emotion_std:.3f}")
    
    print(f"\nDark matter spatial correlations:")
    print(f"  Mean distance: {halo_mean:.3f}")
    print(f"  Std distance: {halo_std:.3f}")
    
    # Normalize for comparison
    emotion_norm = (emotion_correlations - emotion_mean) / emotion_std
    halo_norm = (halo_distances - halo_mean) / halo_std
    
    # KS test for distribution similarity
    ks_stat, ks_p = stats.ks_2samp(emotion_norm[:1000], halo_norm[:1000])
    print(f"\nKS test for distribution similarity:")
    print(f"  KS statistic: {ks_stat:.3f}")
    print(f"  p-value: {ks_p:.3e}")
    
    return emotion_correlations, halo_distances, ks_stat, ks_p

def plot_comparisons(emotion_strengths, halo_masses, 
                    emotion_correlations, halo_distances,
                    fit_emotion, fit_halo):
    """Create comparison plots."""
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # 1. Power law distributions
    ax = axes[0, 0]
    ax.hist(emotion_strengths, bins=50, alpha=0.7, density=True, label='Emotion vectors')
    ax.set_xlabel('Activation strength')
    ax.set_ylabel('Probability density')
    ax.set_title('Emotion vector activation distribution')
    ax.set_yscale('log')
    ax.set_xscale('log')
    
    ax = axes[0, 1]
    ax.hist(halo_masses, bins=50, alpha=0.7, density=True, label='Dark matter halos', color='orange')
    ax.set_xlabel('Halo mass (solar masses)')
    ax.set_ylabel('Probability density')
    ax.set_title('Dark matter halo mass distribution')
    ax.set_yscale('log')
    ax.set_xscale('log')
    
    # 2. Power law fits
    ax = axes[0, 2]
    fit_emotion.plot_pdf(color='blue', linewidth=2, ax=ax, label='Emotion fit')
    fit_halo.plot_pdf(color='orange', linewidth=2, ax=ax, label='Dark matter fit')
    ax.set_xlabel('Value')
    ax.set_ylabel('PDF')
    ax.set_title('Power law fits comparison')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend()
    
    # 3. Correlation functions
    ax = axes[1, 0]
    ax.hist(emotion_correlations, bins=50, alpha=0.7, density=True)
    ax.set_xlabel('Cosine similarity')
    ax.set_ylabel('Density')
    ax.set_title('Emotion vector correlations')
    
    ax = axes[1, 1]
    ax.hist(halo_distances, bins=50, alpha=0.7, density=True, color='orange')
    ax.set_xlabel('Spatial distance')
    ax.set_ylabel('Density')
    ax.set_title('Dark matter spatial correlations')
    
    # 4. QQ plot for distribution comparison
    ax = axes[1, 2]
    # Normalize both distributions
    emotion_norm = (emotion_correlations - np.mean(emotion_correlations)) / np.std(emotion_correlations)
    halo_norm = (halo_distances - np.mean(halo_distances)) / np.std(halo_distances)
    
    # Subsample for QQ plot
    n_points = min(1000, len(emotion_norm), len(halo_norm))
    emotion_sample = np.sort(emotion_norm[:n_points])
    halo_sample = np.sort(halo_norm[:n_points])
    
    ax.scatter(emotion_sample, halo_sample, alpha=0.5, s=10)
    ax.plot([-3, 3], [-3, 3], 'r--', alpha=0.5)
    ax.set_xlabel('Emotion vectors (normalized)')
    ax.set_ylabel('Dark matter (normalized)')
    ax.set_title('QQ plot: Distribution comparison')
    ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('/root/.openclaw/workspace/dark_matter_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\nPlot saved to: /root/.openclaw/workspace/dark_matter_comparison.png")

def main():
    """Main analysis pipeline."""
    
    print("DARK MATTER IN THE MACHINE: Statistical Analysis")
    print("=" * 50)
    
    # Generate synthetic data
    print("\nGenerating synthetic data...")
    emotion_vectors, emotion_strengths, _ = generate_synthetic_emotion_vectors()
    halo_masses, halo_positions = generate_synthetic_dark_matter_halos()
    
    print(f"Emotion vectors: {len(emotion_vectors)} vectors")
    print(f"Dark matter halos: {len(halo_masses)} halos")
    
    # 1. Power law analysis
    fit_emotion, fit_halo, emotion_alpha, halo_alpha = analyze_power_laws(emotion_strengths, halo_masses)
    
    # 2. Clustering analysis
    emotion_graph, avg_neighbor_dist = analyze_clustering(emotion_vectors, halo_positions)
    
    # 3. Correlation function analysis
    emotion_correlations, halo_distances, ks_stat, ks_p = analyze_correlation_functions(
        emotion_vectors, halo_positions
    )
    
    # 4. Create plots
    plot_comparisons(emotion_strengths, halo_masses, 
                    emotion_correlations, halo_distances,
                    fit_emotion, fit_halo)
    
    # 5. Summary
    print("\n" + "=" * 50)
    print("SUMMARY OF FINDINGS:")
    print("=" * 50)
    
    # Check if distributions are similar
    if ks_p > 0.05:
        similarity = "SIMILAR (cannot reject null hypothesis)"
    else:
        similarity = "DIFFERENT (distributions differ significantly)"
    
    print(f"1. Distribution similarity: {similarity}")
    print(f"   KS test p-value: {ks_p:.3e}")
    
    # Compare power law exponents
    exponent_diff = abs(emotion_alpha - halo_alpha)
    if exponent_diff < 0.5:
        power_law_similarity = "SIMILAR exponents"
    else:
        power_law_similarity = "DIFFERENT exponents"
    
    print(f"2. Power law exponents: {power_law_similarity}")
    print(f"   Emotion α = {emotion_alpha:.3f}, Dark matter α = {halo_alpha:.3f}")
    print(f"   Difference: {exponent_diff:.3f}")
    
    # Overall assessment
    print("\n3. OVERALL ASSESSMENT:")
    if ks_p > 0.05 and exponent_diff < 0.5:
        print("   ✅ STRONG EVIDENCE for similar statistical structure")
        print("   Emotion vectors and dark matter halos show similar")
        print("   distribution patterns and scaling laws.")
    elif ks_p > 0.05 or exponent_diff < 0.5:
        print("   ⚠️  MODERATE EVIDENCE for some similarity")
        print("   Some statistical properties match, but not all.")
    else:
        print("   ❌ WEAK EVIDENCE for similarity")
        print("   Distributions appear statistically different.")
    
    print("\n" + "=" * 50)
    print("Analysis complete. Check plot for visual comparison.")

if __name__ == "__main__":
    main()