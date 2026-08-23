#!/usr/bin/env python3
"""
Create reference points classification figure for Paper 2 (publication version - no title)
Shows all potential reference points, which were kept, and which were rejected (with reasons)
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
sys.path.insert(0, 'LocalLibraries')
import PlotConfig as pc
from LocalLibraries.RegionOfInterest import Region
import LocalLibraries.config as config

# Read data
selected_ref = pd.read_csv('FileOutput/Perseus/FinalData/SelectedRefPoints.csv', sep='\t')
all_potential = pd.read_csv('FileOutput/Perseus/FinalData/AllPotentialRefPoints.csv', sep='\t')
near_high_rej = pd.read_csv('FileOutput/Perseus/IntermediateData/NearHighExtRej.csv', sep='\t')
far_high_rej = pd.read_csv('FileOutput/Perseus/IntermediateData/FarHighExtRej.csv', sep='\t')
anom_rej = pd.read_csv('FileOutput/Perseus/IntermediateData/AnomRej.csv', sep='\t')

# Load region
cloudName = config.cloud
regionOfInterest = Region(cloudName)

# Create figure with WCS projection
fig = plt.figure(figsize=(10, 10), dpi=pc.FIGURE_DPI, facecolor='w')
ax = fig.add_subplot(111, projection=regionOfInterest.wcs)

# Plot extinction map
im = plt.imshow(regionOfInterest.hdu.data, origin='lower', cmap='hot', interpolation='nearest',
                vmin=0, vmax=15)

# Convert coordinates to pixels
def ra_dec_to_pix(ra, dec, wcs):
    x, y = [], []
    for r, d in zip(ra, dec):
        px, py = wcs.wcs_world2pix(r, d, 0)
        x.append(px)
        y.append(py)
    return x, y

# Plot rejected points (near high extinction) - red X
if len(near_high_rej) > 0:
    x, y = ra_dec_to_pix(near_high_rej['Ra(deg)'], near_high_rej['Dec(deg)'], regionOfInterest.wcs)
    ax.scatter(x, y, marker='x', s=150, c='red', linewidths=2, label=f'Rejected: Near cloud ({len(near_high_rej)})', zorder=5)

# Plot rejected points (far from high extinction) - orange X
if len(far_high_rej) > 0:
    x, y = ra_dec_to_pix(far_high_rej['Ra(deg)'], far_high_rej['Dec(deg)'], regionOfInterest.wcs)
    ax.scatter(x, y, marker='x', s=150, c='orange', linewidths=2, label=f'Rejected: Far from cloud ({len(far_high_rej)})', zorder=5)

# Plot rejected points (anomalous RM) - purple X
if len(anom_rej) > 0:
    x, y = ra_dec_to_pix(anom_rej['Ra(deg)'], anom_rej['Dec(deg)'], regionOfInterest.wcs)
    ax.scatter(x, y, marker='x', s=150, c='purple', linewidths=2, label=f'Rejected: Anomalous RM ({len(anom_rej)})', zorder=5)

# Plot remaining potential reference points (not selected by stability) - yellow circles
# These are points in all_potential but not in selected_ref and not rejected
selected_ids = set(selected_ref['ID#'])
rejected_ids = set()
if len(near_high_rej) > 0:
    rejected_ids.update(near_high_rej['ID#'])
if len(far_high_rej) > 0:
    rejected_ids.update(far_high_rej['ID#'])
if len(anom_rej) > 0:
    rejected_ids.update(anom_rej['ID#'])

remaining = all_potential[~all_potential['ID#'].isin(selected_ids) & ~all_potential['ID#'].isin(rejected_ids)]
if len(remaining) > 0:
    x, y = ra_dec_to_pix(remaining['Ra(deg)'], remaining['Dec(deg)'], regionOfInterest.wcs)
    ax.scatter(x, y, marker='o', s=100, facecolors='none', edgecolors='yellow', linewidths=2,
               label=f'Not selected ({len(remaining)})', zorder=4)

# Plot selected reference points - green circles (on top)
x, y = ra_dec_to_pix(selected_ref['Ra(deg)'], selected_ref['Dec(deg)'], regionOfInterest.wcs)
ax.scatter(x, y, marker='o', s=120, c='green', edgecolors='black', linewidths=1.5,
           label=f'Selected ({len(selected_ref)})', zorder=6)

# Set bounds
if not np.isnan(regionOfInterest.xmax) and not np.isnan(regionOfInterest.xmin):
    ax.set_xlim(regionOfInterest.xmin, regionOfInterest.xmax)
if not np.isnan(regionOfInterest.ymax) and not np.isnan(regionOfInterest.ymin):
    ax.set_ylim(regionOfInterest.ymin, regionOfInterest.ymax)

# Style axes
ra = ax.coords[0]
dec = ax.coords[1]
ra.set_major_formatter('d')
dec.set_major_formatter('d')
ra.set_axislabel('RA (degree)', fontsize=18)
dec.set_axislabel('Dec (degree)', fontsize=18)
dec.set_ticks(number=8)
ra.set_ticks(number=12)
ra.display_minor_ticks(True)
dec.display_minor_ticks(True)
ra.set_minor_frequency(5)
ra.set_ticklabel(size=16)
dec.set_ticklabel(size=16)
ra.grid(color='white', alpha=0.5, linestyle='solid')
dec.grid(color='white', alpha=0.5, linestyle='solid')

# Style galactic overlay
overlay = ax.get_coords_overlay('galactic')
overlay[0].set_axislabel('Longitude', fontsize=16, color='grey')
overlay[1].set_axislabel('Latitude', fontsize=16, minpad=-1)
ax.text(1.02, 0.55, 'Latitude', fontsize=16, color='grey',
        rotation=270, transform=ax.transAxes,
        verticalalignment='center', horizontalalignment='left')
overlay[1].set_axislabel('')
overlay[0].set_ticks(color='grey', number=12)
overlay[1].set_ticks(color='grey', number=8)
overlay[0].set_ticklabel(size=14, color='grey')
overlay[1].set_ticklabel(size=14, color='grey')
overlay.grid(color='grey', linestyle='dashed', alpha=0.5)

# Add colorbar
from matplotlib.ticker import AutoLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.45, axes_class=plt.Axes)
cb = plt.colorbar(im, cax=cax)
cb.set_label('$A_V$', rotation=270, labelpad=25, fontsize=18)
cb.ax.tick_params(labelsize=16, width=1.2, length=5)
cb.ax.yaxis.set_major_locator(AutoLocator())

# Legend (upper left, outside the main data)
ax.legend(loc='upper left', fontsize=12, framealpha=0.9, edgecolor='black')

plt.tight_layout()

# Create figures directory if needed
os.makedirs('figures', exist_ok=True)

# Save
plt.savefig('figures/reference_classification.png', dpi=pc.FIGURE_DPI, bbox_inches='tight', facecolor='white')
plt.savefig('figures/reference_classification.pdf', bbox_inches='tight', facecolor='white')
print("Created figures/reference_classification.png and .pdf")
plt.close()

# Print statistics
print(f"\nReference point classification statistics:")
print(f"  Total potential reference points: {len(all_potential)}")
print(f"  Rejected (near high extinction): {len(near_high_rej)}")
print(f"  Rejected (far from high extinction): {len(far_high_rej)}")
print(f"  Rejected (anomalous RM): {len(anom_rej)}")
print(f"  Not selected by stability trend: {len(remaining)}")
print(f"  Final selected reference points: {len(selected_ref)}")
