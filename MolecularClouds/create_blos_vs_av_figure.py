#!/usr/bin/env python3
"""
Create BLOS vs Av scatter plot for Paper 2
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
sys.path.insert(0, 'LocalLibraries')
import PlotConfig as pc

# Font settings are applied globally by PlotConfig

# Read data
df = pd.read_csv('FileOutput/Perseus/FinalData/FinalBLOSResults.csv', sep='\t')

# Create figures directory if needed
os.makedirs('figures', exist_ok=True)

# Create figure with publication size
fig, ax = plt.subplots(figsize=(10, 7), dpi=pc.FIGURE_DPI)

# Separate by sign
positive = df[df['Magnetic_Field(uG)'] > 0]
negative = df[df['Magnetic_Field(uG)'] < 0]

# Plot with larger markers and better visibility
ax.scatter(positive['Extinction'], positive['Magnetic_Field(uG)'].abs(),
           c='#0066CC', alpha=0.7, s=50, label='Toward observer', edgecolors='black', linewidth=0.4)
ax.scatter(negative['Extinction'], negative['Magnetic_Field(uG)'].abs(),
           c='#CC0000', alpha=0.7, s=50, label='Away from observer', edgecolors='black', linewidth=0.4)

# Formatting with proper font sizes (uses global PlotConfig settings)
ax.set_xlabel(r'Visual Extinction $A_V$ (mag)')
ax.set_ylabel(r'$|B_{\parallel}|$ ($\mu$G)')
ax.set_xlim(0, df['Extinction'].max() * 1.05)
ax.set_ylim(0, df['Magnetic_Field(uG)'].abs().max() * 1.05)

# Place legend in upper right corner where there's no data
ax.legend(loc='upper right', framealpha=0.9, edgecolor='black', fancybox=False)
ax.grid(alpha=0.3, linestyle='--', linewidth=0.5)
ax.tick_params(width=1.2)

# Add statistics box directly below the legend in upper right
mean_blos = df['Magnetic_Field(uG)'].abs().mean()
median_blos = df['Magnetic_Field(uG)'].abs().median()
textstr = f'Mean $|B_\\parallel|$ = {mean_blos:.0f} $\\mu$G\nMedian $|B_\\parallel|$ = {median_blos:.0f} $\\mu$G\nN = {len(df)}'
ax.text(0.98, 0.78, textstr, transform=ax.transAxes,
        verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.6, edgecolor='black', linewidth=1))

plt.tight_layout()
plt.savefig('figures/BLOS_vs_Av.png', dpi=pc.FIGURE_DPI, bbox_inches='tight', facecolor='white')
print("Created figures/BLOS_vs_Av.png")
plt.close()

print(f"\nStatistics:")
print(f"  Total points: {len(df)}")
print(f"  Positive BLOS: {len(positive)} ({100*len(positive)/len(df):.1f}%)")
print(f"  Negative BLOS: {len(negative)} ({100*len(negative)/len(df):.1f}%)")
print(f"  Mean |BLOS|: {mean_blos:.1f} μG")
print(f"  Median |BLOS|: {median_blos:.1f} μG")
print(f"  Av range: {df['Extinction'].min():.2f} to {df['Extinction'].max():.2f} mag")
