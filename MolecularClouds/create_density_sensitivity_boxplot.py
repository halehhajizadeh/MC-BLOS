#!/usr/bin/env python3
"""
Create box-and-whisker plot for density sensitivity analysis (Paper 2)
Shows the distribution of |B_parallel| at different n0 values
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
sys.path.insert(0, 'LocalLibraries')
import PlotConfig as pc

# Fiducial density
n0_fiducial = 1000  # cm^-3

# Density variations to plot (percentage changes from fiducial)
# We'll use -50%, -20%, 0%, +20%, +50% which gives us 500, 800, 1000, 1200, 1500 cm^-3
density_variations = [
    (-50, 'n-50.csv', 500),
    (-20, 'n-20.csv', 800),
    (0, 'n0.csv', 1000),
    (+20, 'n+20.csv', 1200),
    (+50, 'n+50.csv', 1500),
]

# Read data for each density variation
data_list = []
labels = []
densities = []

base_dir = 'FileOutput/Perseus/DensitySensitivity'

for pct_change, filename, n0_value in density_variations:
    filepath = os.path.join(base_dir, f'B_Av_T0_{filename}')
    if os.path.exists(filepath):
        df = pd.read_csv(filepath, sep='\t')
        # Extract absolute values of magnetic field
        b_values = np.abs(df['Magnetic_Field(uG)'].values)
        # Remove any NaN or inf values
        b_values = b_values[np.isfinite(b_values)]
        data_list.append(b_values)
        labels.append(f'{n0_value}')
        densities.append(n0_value)
        print(f"Loaded {len(b_values)} values for n0 = {n0_value} cm^-3 (median: {np.median(b_values):.1f} μG)")
    else:
        print(f"Warning: {filepath} not found, skipping")

if len(data_list) == 0:
    print("Error: No density sensitivity data found")
    sys.exit(1)

# Create figure
fig, ax = plt.subplots(figsize=(10, 6), dpi=pc.FIGURE_DPI, facecolor='w')

# Create box plot
bp = ax.boxplot(data_list, labels=labels, patch_artist=True,
                widths=0.6,
                boxprops=dict(facecolor='lightblue', edgecolor='black', linewidth=1.2),
                medianprops=dict(color='red', linewidth=2),
                whiskerprops=dict(color='black', linewidth=1.2),
                capprops=dict(color='black', linewidth=1.2),
                flierprops=dict(marker='o', markerfacecolor='gray', markersize=3,
                               alpha=0.3, markeredgecolor='none'))

# Highlight the fiducial model (n0 = 1000)
fiducial_idx = densities.index(1000)
bp['boxes'][fiducial_idx].set_facecolor('orange')
bp['boxes'][fiducial_idx].set_edgecolor('black')
bp['boxes'][fiducial_idx].set_linewidth(2)

# Labels and formatting
ax.set_xlabel('Initial gas density $n_0$ (cm$^{-3}$)', fontsize=pc.FONT_SIZE)
ax.set_ylabel('$|B_\\parallel|$ ($\mu$G)', fontsize=pc.FONT_SIZE)
ax.tick_params(axis='both', labelsize=pc.FONT_SIZE - 2, width=1.2, length=5)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='orange', edgecolor='black', linewidth=2, label=f'Fiducial ($n_0 = {n0_fiducial}$ cm$^{{-3}}$)'),
    Patch(facecolor='lightblue', edgecolor='black', linewidth=1.2, label='Other values')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=pc.FONT_SIZE - 3, framealpha=0.9)

plt.tight_layout()

# Create figures directory if needed
os.makedirs('figures', exist_ok=True)

# Save
plt.savefig('figures/BDensitySensitivity.png', dpi=pc.FIGURE_DPI, bbox_inches='tight', facecolor='white')
plt.savefig('figures/BDensitySensitivity.pdf', bbox_inches='tight', facecolor='white')
print("\nCreated figures/BDensitySensitivity.png and .pdf")
plt.close()

# Print statistics
print(f"\nDensity sensitivity statistics:")
for i, (label, data) in enumerate(zip(labels, data_list)):
    print(f"  n0 = {label} cm^-3: median |B∥| = {np.median(data):.1f} μG, "
          f"IQR = {np.percentile(data, 75) - np.percentile(data, 25):.1f} μG")
