#!/usr/bin/env python3
"""
Create publication-quality Figure 1 for the paper:
Spatial distribution of RM sources with reference points highlighted
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
from astropy.wcs import WCS

from LocalLibraries.RegionOfInterest import Region
import LocalLibraries.config as config
import LocalLibraries.ConversionLibrary as cl

# Set publication-quality font and style
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 11,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'text.usetex': False,  # Set to True if you have LaTeX installed
    'axes.linewidth': 1.0,
    'grid.alpha': 0.3,
    'grid.linewidth': 0.5
})

# Load the region
cloudName = config.cloud
regionOfInterest = Region(cloudName)

# Load the data
matched_data = pd.read_csv(config.MatchedRMExtinctionFile, sep=config.dataSeparator)
ref_points = pd.read_csv('FileOutput/Perseus/FinalData/SelectedRefPoints.csv', sep='\t')

# Classify ON points by B_parallel sign
blos_data = pd.read_csv('FileOutput/Perseus/FinalData/FinalBLOSResults.csv', sep='\t')

# Create figure with WCS projection
wcs = WCS(regionOfInterest.hdu.header)
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection=wcs)

# Plot extinction map
im = ax.imshow(regionOfInterest.hdu.data, origin='lower', cmap='BrBG',
               interpolation='nearest', aspect='auto')

# Style the axes with equatorial coordinates
ra = ax.coords[0]
dec = ax.coords[1]
ra.set_major_formatter('d')
dec.set_major_formatter('d')
ra.set_axislabel('RA (degrees)', fontsize=14)
dec.set_axislabel('Dec (degrees)', fontsize=14)

dec.set_ticks(number=8)
ra.set_ticks(number=12)
ra.display_minor_ticks(True)
dec.display_minor_ticks(True)
ra.set_minor_frequency(5)

ra.grid(color='white', alpha=0.3, linestyle='solid', linewidth=0.5)
dec.grid(color='white', alpha=0.3, linestyle='solid', linewidth=0.5)

# Overlay galactic coordinates
overlay = ax.get_coords_overlay('galactic')
overlay[0].set_axislabel('Longitude', fontsize=14)
overlay[1].set_axislabel('Latitude', fontsize=14, minpad=0.8)
overlay[0].set_ticks(color='grey', number=12)
overlay[1].set_ticks(color='grey', number=8)
overlay.grid(color='grey', linestyle='--', alpha=0.25, linewidth=0.5)

# Plot ON points (cloud sight lines) - color by B_parallel sign
on_points = matched_data[~matched_data['ID#'].isin(ref_points['ID#'])]

# Merge with BLOS data to get signs
on_with_blos = on_points.merge(blos_data[['ID#', 'Magnetic_Field(uG)']], on='ID#', how='left')

# Convert coordinates to pixels
x_on, y_on = cl.RADec2xy(list(on_with_blos['Ra(deg)']),
                          list(on_with_blos['Dec(deg)']),
                          regionOfInterest.wcs)

# Separate by sign
positive_mask = on_with_blos['Magnetic_Field(uG)'] > 0
negative_mask = on_with_blos['Magnetic_Field(uG)'] < 0

# Plot positive B_parallel (toward observer) in blue
if positive_mask.sum() > 0:
    ax.scatter(np.array(x_on)[positive_mask], np.array(y_on)[positive_mask],
               marker='o', s=30, facecolor='#0066CC', linewidth=0.5,
               edgecolors='black', alpha=0.8, label='Positive $B_\\parallel$', zorder=3)

# Plot negative B_parallel (away from observer) in red
if negative_mask.sum() > 0:
    ax.scatter(np.array(x_on)[negative_mask], np.array(y_on)[negative_mask],
               marker='o', s=30, facecolor='#CC0000', linewidth=0.5,
               edgecolors='black', alpha=0.8, label='Negative $B_\\parallel$', zorder=3)

# Plot reference (OFF) points in green
x_ref, y_ref = cl.RADec2xy(list(ref_points['Ra(deg)']),
                            list(ref_points['Dec(deg)']),
                            regionOfInterest.wcs)

ax.scatter(x_ref, y_ref, marker='o', s=80, facecolor='#00CC00',
           linewidth=1.0, edgecolors='black', alpha=0.9,
           label='Reference (OFF) points', zorder=4)

# Set bounds
if np.isfinite(regionOfInterest.xmin) and np.isfinite(regionOfInterest.xmax):
    ax.set_xlim(regionOfInterest.xmin, regionOfInterest.xmax)
if np.isfinite(regionOfInterest.ymin) and np.isfinite(regionOfInterest.ymax):
    ax.set_ylim(regionOfInterest.ymin, regionOfInterest.ymax)

# Add colorbar
cbar = plt.colorbar(im, ax=ax, pad=0.12, fraction=0.046)
cbar.set_label(r'$A_V$ (mag)', fontsize=14, rotation=270, labelpad=20)
cbar.ax.tick_params(labelsize=12)

# Add legend
legend = ax.legend(loc='upper right', framealpha=0.9, edgecolor='black',
                   fancybox=False, shadow=False, fontsize=11)

# Tight layout to minimize white space
plt.tight_layout()

# Save figure
output_path = 'figures/AllRMPtsInRegion.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"Saved publication-quality Figure 1 to: {output_path}")

# Also save as PDF for LaTeX
output_pdf = 'figures/AllRMPtsInRegion.pdf'
plt.savefig(output_pdf, dpi=300, bbox_inches='tight', facecolor='white')
print(f"Saved PDF version to: {output_pdf}")

plt.close()

# Print statistics
print(f"\nFigure statistics:")
print(f"  Total matched sources: {len(matched_data)}")
print(f"  Reference (OFF) points: {len(ref_points)}")
print(f"  ON points: {len(on_points)}")
print(f"  Positive B_parallel: {positive_mask.sum()}")
print(f"  Negative B_parallel: {negative_mask.sum()}")
