#!/usr/bin/env python3
"""
Create RM map for Paper 2 (publication version - no title)
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
cloudName = config.cloud
regionOfInterest = Region(cloudName)

# Read matched RM points
matched_rm = pd.read_csv('FileOutput/Perseus/FinalData/MatchedRMExtinction.csv', sep='\t')

# Read selected reference points
selected_ref = pd.read_csv('FileOutput/Perseus/FinalData/SelectedRefPoints.csv', sep='\t')

# Reference RM
rm_ref = 40.0
av_ref = 0.48

# Convert RA/Dec to pixel coordinates
def ra_dec_to_pix(ra, dec, wcs):
    x, y = [], []
    for r, d in zip(ra, dec):
        px, py = wcs.wcs_world2pix(r, d, 0)
        x.append(px)
        y.append(py)
    return x, y

# Create figure with WCS projection
fig = plt.figure(figsize=(10, 10), dpi=pc.FIGURE_DPI, facecolor='w')
ax = fig.add_subplot(111, projection=regionOfInterest.wcs)

# Plot extinction map
im = plt.imshow(regionOfInterest.hdu.data, origin='lower', cmap='hot', interpolation='nearest',
                vmin=0, vmax=15)

# Convert coordinates
x_all, y_all = ra_dec_to_pix(matched_rm['Ra(deg)'], matched_rm['Dec(deg)'], regionOfInterest.wcs)
x_ref, y_ref = ra_dec_to_pix(selected_ref['Ra(deg)'], selected_ref['Dec(deg)'], regionOfInterest.wcs)

# Plot all RM points (color-coded by RM value)
scatter = ax.scatter(x_all, y_all, c=matched_rm['Rotation_Measure(rad/m2)'],
                    cmap='RdBu_r', s=30, edgecolors='black', linewidth=0.5,
                    vmin=-50, vmax=90, zorder=3)

# Plot reference points on top
ax.scatter(x_ref, y_ref, marker='o', s=120, c='green', edgecolors='black', linewidths=1.5,
           label=f'Reference points (N={len(selected_ref)})', zorder=4)

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

# Add Av colorbar
from matplotlib.ticker import AutoLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.45, axes_class=plt.Axes)
cb = plt.colorbar(im, cax=cax)
cb.set_label('$A_V$', rotation=270, labelpad=25, fontsize=18)
cb.ax.tick_params(labelsize=16, width=1.2, length=5)
cb.ax.yaxis.set_major_locator(AutoLocator())

# Add textbox for reference RM
textstr = f'RM$_{{\\rm ref}}$ = {rm_ref:+.1f} rad m$^{{-2}}$\n$A_V$ ref = {av_ref:+.2f} mag'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.85, edgecolor='black')
ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)

plt.tight_layout()

# Create figures directory if needed
os.makedirs('figures', exist_ok=True)

# Save
plt.savefig('figures/rm_map.png', dpi=pc.FIGURE_DPI, bbox_inches='tight', facecolor='white')
plt.savefig('figures/rm_map.pdf', bbox_inches='tight', facecolor='white')
print("Created figures/rm_map.png and .pdf")
plt.close()

print(f"\nRM map statistics:")
print(f"  Total RM sources: {len(matched_rm)}")
print(f"  Reference points: {len(selected_ref)}")
print(f"  Reference RM: {rm_ref:.1f} ± 1.3 rad m^-2")
