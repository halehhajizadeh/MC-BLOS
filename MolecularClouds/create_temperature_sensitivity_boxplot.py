#!/usr/bin/env python3
"""
Create box-and-whisker plot for temperature sensitivity analysis (Paper 2)
Shows the distribution of |B_parallel| at different T0 values
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
sys.path.insert(0, 'LocalLibraries')
import PlotConfig as pc

# Fiducial temperature
T0_fiducial = 12  # K

# Temperature variations to plot (percentage changes from fiducial)
# We'll use -20%, -10%, 0%, +10%, +20% which gives us approximately 9.6, 10.8, 12, 13.2, 14.4 K
temperature_variations = [
    (-20, 'T-20_n0.csv', 9.6),
    (-10, 'T-10_n0.csv', 10.8),
    (0, 'T0_n0.csv', 12.0),
    (+10, 'T+10_n0.csv', 13.2),
    (+20, 'T+20_n0.csv', 14.4),
]

# Read data for each temperature variation
data_list = []
labels = []
temperatures = []

base_dir = 'FileOutput/Perseus/TemperatureSensitivity'

for pct_change, filename, T0_value in temperature_variations:
    filepath = os.path.join(base_dir, f'B_Av_{filename}')
    if os.path.exists(filepath):
        df = pd.read_csv(filepath, sep='\t')
        # Extract absolute values of magnetic field
        b_values = np.abs(df['Magnetic_Field(uG)'].values)
        # Remove any NaN or inf values
        b_values = b_values[np.isfinite(b_values)]
        data_list.append(b_values)
        labels.append(f'{T0_value:.0f}')
        temperatures.append(T0_value)
        print(f"Loaded {len(b_values)} values for T0 = {T0_value:.1f} K (median: {np.median(b_values):.1f} μG)")
    else:
        print(f"Warning: {filepath} not found, skipping")

if len(data_list) == 0:
    print("Error: No temperature sensitivity data found")
    sys.exit(1)

# Create figure
fig, ax = plt.subplots(figsize=(10, 6), dpi=pc.FIGURE_DPI, facecolor='w')

# Create box plot
bp = ax.boxplot(data_list, labels=labels, patch_artist=True,
                widths=0.6,
                boxprops=dict(facecolor='lightgreen', edgecolor='black', linewidth=1.2),
                medianprops=dict(color='red', linewidth=2),
                whiskerprops=dict(color='black', linewidth=1.2),
                capprops=dict(color='black', linewidth=1.2),
                flierprops=dict(marker='o', markerfacecolor='gray', markersize=3,
                               alpha=0.3, markeredgecolor='none'))

# Highlight the fiducial model (T0 = 12 K)
fiducial_idx = labels.index('12')
bp['boxes'][fiducial_idx].set_facecolor('orange')
bp['boxes'][fiducial_idx].set_edgecolor('black')
bp['boxes'][fiducial_idx].set_linewidth(2)

# Labels and formatting
ax.set_xlabel('Gas kinetic temperature $T_0$ (K)', fontsize=pc.FONT_SIZE)
ax.set_ylabel('$|B_\\parallel|$ ($\mu$G)', fontsize=pc.FONT_SIZE)
ax.tick_params(axis='both', labelsize=pc.FONT_SIZE - 2, width=1.2, length=5)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='orange', edgecolor='black', linewidth=2, label=f'Fiducial ($T_0 = {T0_fiducial}$ K)'),
    Patch(facecolor='lightgreen', edgecolor='black', linewidth=1.2, label='Other values')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=pc.FONT_SIZE - 3, framealpha=0.9)

plt.tight_layout()

# Create figures directory if needed
os.makedirs('figures', exist_ok=True)

# Save
plt.savefig('figures/BTemperatureSensitivity.png', dpi=pc.FIGURE_DPI, bbox_inches='tight', facecolor='white')
plt.savefig('figures/BTemperatureSensitivity.pdf', bbox_inches='tight', facecolor='white')
print("\nCreated figures/BTemperatureSensitivity.png and .pdf")
plt.close()

# Print statistics
print(f"\nTemperature sensitivity statistics:")
for i, (label, data) in enumerate(zip(labels, data_list)):
    print(f"  T0 = {label} K: median |B∥| = {np.median(data):.1f} μG, "
          f"IQR = {np.percentile(data, 75) - np.percentile(data, 25):.1f} μG")
