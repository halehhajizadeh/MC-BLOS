#!/usr/bin/env python3
"""
Create stability trend figure for Paper 2 (publication version - no title)
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
sys.path.insert(0, 'LocalLibraries')
import PlotConfig as pc

# Read stability trend data
trend_data = pd.read_csv('FileOutput/Perseus/IntermediateData/TrendDataTable.csv', sep='\t', index_col=0)

# Number of reference points (columns)
n_ref_points = np.arange(1, len(trend_data.columns) + 1)

# Create figure
fig, ax = plt.subplots(figsize=(8, 6), dpi=pc.FIGURE_DPI)

# Plot each source's BLOS as a function of number of reference points
for idx in trend_data.index:
    blos_values = trend_data.loc[idx, :].values
    ax.plot(n_ref_points, blos_values, marker='o', markersize=3, alpha=0.6, linewidth=1)

# Add vertical line at the selected number of reference points (8)
ax.axvline(x=8, color='black', linestyle='--', linewidth=2, label='Selected: 8 reference points')

# Labels and formatting
ax.set_xlabel('Number of reference points', fontsize=18)
ax.set_ylabel(r'Calculated $B_{\parallel}$ ($\mu$G)', fontsize=18)
ax.tick_params(labelsize=16, width=1.2)
ax.legend(loc='upper left', fontsize=14, framealpha=0.9)
ax.grid(alpha=0.3, linestyle='--', linewidth=0.5)

# Set x-axis to show integer ticks
ax.set_xticks(n_ref_points)

plt.tight_layout()

# Create figures directory if needed
os.makedirs('figures', exist_ok=True)

# Save
plt.savefig('figures/stability_trend.png', dpi=pc.FIGURE_DPI, bbox_inches='tight', facecolor='white')
plt.savefig('figures/stability_trend.pdf', bbox_inches='tight', facecolor='white')
print("Created figures/stability_trend.png and .pdf")
plt.close()

# Print statistics
print(f"\nStability trend statistics:")
print(f"  Total sources tracked: {len(trend_data)}")
print(f"  Number of reference points tested: {len(n_ref_points)}")
print(f"  Selected number of reference points: 8")
print(f"  Mean |BLOS| at 8 ref points: {np.abs(trend_data.iloc[:, 7]).mean():.1f} μG")
