#!/usr/bin/env python3
"""
Generate publication-quality PDF plots for the paper.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from astropy.io import fits
from astropy.wcs import WCS
import os

# Use publication quality settings matching MC-BLOS pipeline
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'STIXGeneral', 'serif'],
    'mathtext.fontset': 'stix',
    'font.size': 14,
    'axes.labelsize': 16,
    'axes.titlesize': 16,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 12,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'text.usetex': False,
})

# Paths
base_dir = '/Users/halehhajizadeh/Desktop/MC-BLOS/MolecularClouds/FileOutput_ImprovedPlots/perseus'
final_data_dir = os.path.join(base_dir, 'FinalData')
plots_dir = os.path.join(base_dir, 'Plots')

# Load data
print("Loading data...")
blos_data = pd.read_csv(os.path.join(final_data_dir, 'BLOSPoints.csv'), sep='\t')
final_results = pd.read_csv(os.path.join(final_data_dir, 'FinalBLOSResults.csv'), sep='\t')
ref_data = pd.read_csv(os.path.join(final_data_dir, 'ReferenceData.csv'), sep='\t')
ref_points = pd.read_csv(os.path.join(final_data_dir, 'SelectedRefPoints.csv'), sep='\t')

# Merge uncertainties
blos_data['TotalUpperBUncertainty'] = final_results['TotalUpperBUncertainty']
blos_data['TotalLowerBUncertainty'] = final_results['TotalLowerBUncertainty']

# Get reference RM
ref_rm = ref_data['Reference RM'].values[0]
ref_rm_std = ref_data['Reference RM Std'].values[0]
ref_av = ref_data['Reference Extinction'].values[0]

print(f"Reference RM: {ref_rm:.2f} +/- {ref_rm_std:.2f} rad/m^2")
print(f"Total BLOS points: {len(blos_data)}")

# 1. Histogram of BLOS values
print("Creating BLOS histogram (PDF)...")
fig, ax = plt.subplots(figsize=(8, 6))
positive = blos_data[blos_data['Magnetic_Field(uG)'] > 0]['Magnetic_Field(uG)']
negative = blos_data[blos_data['Magnetic_Field(uG)'] < 0]['Magnetic_Field(uG)']

bins = np.linspace(-1000, 900, 40)
ax.hist(positive, bins=bins, alpha=0.7, color='blue', label=f'Positive (toward): {len(positive)} ({100*len(positive)/len(blos_data):.0f}%)', edgecolor='darkblue')
ax.hist(negative, bins=bins, alpha=0.7, color='red', label=f'Negative (away): {len(negative)} ({100*len(negative)/len(blos_data):.0f}%)', edgecolor='darkred')
ax.axvline(x=np.median(blos_data['Magnetic_Field(uG)']), color='green', linestyle='--', linewidth=2, label=f'Median: {np.median(blos_data["Magnetic_Field(uG)"]):.0f} $\mu$G')
ax.axvline(x=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
ax.set_xlabel(r'$B_\parallel$ ($\mu$G)')
ax.set_ylabel('Number of sight lines')
ax.legend(loc='upper right')
ax.set_xlim(-1000, 900)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'BLOS_histogram.pdf'), format='pdf')
plt.close()

# 2. BLOS vs Av
print("Creating BLOS vs Av plot (PDF)...")
fig, ax = plt.subplots(figsize=(8, 6))
pos_mask = blos_data['Magnetic_Field(uG)'] > 0
neg_mask = blos_data['Magnetic_Field(uG)'] < 0

ax.errorbar(blos_data.loc[pos_mask, 'Extinction'], blos_data.loc[pos_mask, 'Magnetic_Field(uG)'],
            yerr=[blos_data.loc[pos_mask, 'TotalLowerBUncertainty'], blos_data.loc[pos_mask, 'TotalUpperBUncertainty']],
            fmt='o', color='blue', alpha=0.6, markersize=5, label='Positive (toward)', elinewidth=0.5, capsize=0)
ax.errorbar(blos_data.loc[neg_mask, 'Extinction'], blos_data.loc[neg_mask, 'Magnetic_Field(uG)'],
            yerr=[blos_data.loc[neg_mask, 'TotalLowerBUncertainty'], blos_data.loc[neg_mask, 'TotalUpperBUncertainty']],
            fmt='o', color='red', alpha=0.6, markersize=5, label='Negative (away)', elinewidth=0.5, capsize=0)
ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
ax.axvline(x=ref_av, color='green', linestyle='--', linewidth=2, label=f'Reference $A_V$ = {ref_av:.2f} mag')
ax.set_xlabel(r'Visual Extinction $A_V$ (mag)')
ax.set_ylabel(r'$B_\parallel$ ($\mu$G)')
ax.legend(loc='upper right')
ax.set_xlim(0, 16)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'BLOS_vs_Av.pdf'), format='pdf')
plt.close()

# 3. RM observed vs cloud RM
print("Creating RM comparison plot (PDF)...")
blos_data['RM_cloud'] = blos_data['RM_Raw_Value'] - ref_rm

fig, ax = plt.subplots(figsize=(8, 6))
pos_rm = blos_data['RM_cloud'] > 0
neg_rm = blos_data['RM_cloud'] <= 0

ax.scatter(blos_data.loc[pos_rm, 'RM_Raw_Value'], blos_data.loc[pos_rm, 'RM_cloud'],
           c='blue', alpha=0.6, s=30, label='Positive cloud RM')
ax.scatter(blos_data.loc[neg_rm, 'RM_Raw_Value'], blos_data.loc[neg_rm, 'RM_cloud'],
           c='red', alpha=0.6, s=30, label='Negative cloud RM')
ax.axvline(x=ref_rm, color='green', linestyle='--', linewidth=2, label=f'Reference RM = {ref_rm:.1f} rad/m$^2$')
ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)

# Add diagonal reference line
rm_range = np.array([blos_data['RM_Raw_Value'].min(), blos_data['RM_Raw_Value'].max()])
ax.plot(rm_range, rm_range - ref_rm, 'k--', alpha=0.3, linewidth=1)

ax.set_xlabel(r'Observed RM (rad m$^{-2}$)')
ax.set_ylabel(r'Cloud RM (rad m$^{-2}$)')
ax.legend(loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'RM_observed_vs_cloud.pdf'), format='pdf')
plt.close()

# 4. |BLOS| vs Av (log scale)
print("Creating |BLOS| vs Av log plot (PDF)...")
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(blos_data.loc[pos_mask, 'Extinction'], np.abs(blos_data.loc[pos_mask, 'Magnetic_Field(uG)']),
           c='blue', alpha=0.6, s=30, label='Positive $B_\parallel$')
ax.scatter(blos_data.loc[neg_mask, 'Extinction'], np.abs(blos_data.loc[neg_mask, 'Magnetic_Field(uG)']),
           c='red', alpha=0.6, s=30, label='Negative $B_\parallel$')
ax.set_yscale('log')
ax.set_xlabel(r'Visual Extinction $A_V$ (mag)')
ax.set_ylabel(r'$|B_\parallel|$ ($\mu$G)')
ax.legend(loc='upper right')
ax.set_xlim(0, 16)
ax.set_ylim(1, 2000)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'BLOS_abs_vs_Av_log.pdf'), format='pdf')
plt.close()

# 5. Spatial distribution
print("Creating spatial distribution plot (PDF)...")
fig, ax = plt.subplots(figsize=(10, 8))

# Size proportional to |B|
sizes = np.abs(blos_data['Magnetic_Field(uG)']) / 10 + 20

scatter_pos = ax.scatter(blos_data.loc[pos_mask, 'Ra(deg)'], blos_data.loc[pos_mask, 'Dec(deg)'],
                         c='blue', s=sizes[pos_mask], alpha=0.6, label='Positive (toward)')
scatter_neg = ax.scatter(blos_data.loc[neg_mask, 'Ra(deg)'], blos_data.loc[neg_mask, 'Dec(deg)'],
                         c='red', s=sizes[neg_mask], alpha=0.6, label='Negative (away)')

# Add reference points
ax.scatter(ref_points['Ra(deg)'], ref_points['Dec(deg)'],
           c='green', s=100, marker='s', label='Reference points', zorder=10)

ax.set_xlabel('Right Ascension (deg)')
ax.set_ylabel('Declination (deg)')
ax.legend(loc='upper right')
ax.invert_xaxis()  # RA increases to the left
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'BLOS_spatial_distribution.pdf'), format='pdf')
plt.close()

print("\nAll PDF plots created successfully!")
print(f"Output directory: {plots_dir}")
