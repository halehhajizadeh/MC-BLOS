#!/usr/bin/env python3
"""
Create BLOS map for Paper 2 (publication version - no title)
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

# Read BLOS data
blos_data = pd.read_csv('FileOutput/Perseus/FinalData/FinalBLOSResults.csv', sep='\t')

# Read selected reference points
selected_ref = pd.read_csv('FileOutput/Perseus/FinalData/SelectedRefPoints.csv', sep='\t')

# Reference values
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
x_blos, y_blos = ra_dec_to_pix(blos_data['Ra(deg)'], blos_data['Dec(deg)'], regionOfInterest.wcs)
x_ref, y_ref = ra_dec_to_pix(selected_ref['Ra(deg)'], selected_ref['Dec(deg)'], regionOfInterest.wcs)

# Separate positive and negative BLOS
positive = blos_data['Magnetic_Field(uG)'] > 0
negative = blos_data['Magnetic_Field(uG)'] < 0

# Calculate marker sizes (proportional to |BLOS|, scaled for visibility)
sizes = np.abs(blos_data['Magnetic_Field(uG)']) / 10  # Scale factor for visibility
sizes = np.clip(sizes, 10, 200)  # Clip to reasonable range

# Plot negative BLOS (away from observer) - red
ax.scatter(np.array(x_blos)[negative], np.array(y_blos)[negative],
          s=np.array(sizes)[negative], c='#CC0000', alpha=0.7,
          edgecolors='black', linewidth=0.5, label='Away from observer', zorder=3)

# Plot positive BLOS (toward observer) - blue
ax.scatter(np.array(x_blos)[positive], np.array(y_blos)[positive],
          s=np.array(sizes)[positive], c='#0066CC', alpha=0.7,
          edgecolors='black', linewidth=0.5, label='Toward observer', zorder=3)

# Plot reference points on top
ax.scatter(x_ref, y_ref, marker='o', s=120, c='green', edgecolors='black', linewidths=1.5,
           label='Off points', zorder=4)

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

# Create legend with size markers
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#CC0000',
           markersize=4, label='10 μG', markeredgecolor='black', markeredgewidth=0.5),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#CC0000',
           markersize=7, label='100 μG', markeredgecolor='black', markeredgewidth=0.5),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#CC0000',
           markersize=11, label='1000+ μG', markeredgecolor='black', markeredgewidth=0.5),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#CC0000',
           markersize=7, label='Away from us', markeredgecolor='black', markeredgewidth=0.5),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#0066CC',
           markersize=7, label='Towards us', markeredgecolor='black', markeredgewidth=0.5),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='green',
           markersize=8, label='Off points', markeredgecolor='black', markeredgewidth=0.5),
]
legend = ax.legend(handles=legend_elements, loc='lower left', fontsize=13,
                  ncol=2, framealpha=0.85, edgecolor='black')

# Add textbox for reference RM
textstr = f'RM$_{{\\rm Off}}$ = {rm_ref:+.1f} rad m$^{{-2}}$\n$A_V$ Off = {av_ref:+.2f} mag'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.85, edgecolor='black')
ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)

plt.tight_layout()

# Create figures directory if needed
os.makedirs('figures', exist_ok=True)

# Save
plt.savefig('figures/blos_map.png', dpi=pc.FIGURE_DPI, bbox_inches='tight', facecolor='white')
plt.savefig('figures/blos_map.pdf', bbox_inches='tight', facecolor='white')
print("Created figures/blos_map.png and .pdf")
plt.close()

print(f"\nBLOS map statistics:")
print(f"  Total BLOS measurements: {len(blos_data)}")
print(f"  Positive (toward observer): {positive.sum()} ({100*positive.sum()/len(blos_data):.1f}%)")
print(f"  Negative (away from observer): {negative.sum()} ({100*negative.sum()/len(blos_data):.1f}%)")
print(f"  Mean |BLOS|: {np.abs(blos_data['Magnetic_Field(uG)']).mean():.1f} μG")
print(f"  Median |BLOS|: {np.abs(blos_data['Magnetic_Field(uG)']).median():.1f} μG")
