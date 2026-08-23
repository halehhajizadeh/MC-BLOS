"""
Publication-quality version of 02bRMMapping.py
Creates Figure 1 for the paper - all RM points in green (simple version)
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from LocalLibraries.RMCatalog import RMCatalog
from LocalLibraries.RegionOfInterest import Region
import LocalLibraries.config as config
import LocalLibraries.PlotTemplates as pt
import LocalLibraries.ConversionLibrary as cl

import os
import logging

# Set publication-quality fonts
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'Times'],
    'font.size': 14,
    'axes.labelsize': 16,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
})

# -------- CHOOSE THE REGION OF INTEREST --------
cloudName = config.cloud
regionOfInterest = Region(cloudName)
# -------- CHOOSE THE REGION OF INTEREST. --------

# Load all matched data
matched_data = pd.read_csv(config.MatchedRMExtinctionFile, sep=config.dataSeparator)

# -------- CREATE PUBLICATION-QUALITY FIGURE --------

# Create the base extinction plot
fig, ax = pt.extinctionPlot(regionOfInterest)

# Convert all RM points to pixel coordinates
x_all, y_all = cl.RADec2xy(list(matched_data['Ra(deg)']),
                            list(matched_data['Dec(deg)']),
                            regionOfInterest.wcs)

# Plot all RM points in green
ax.scatter(x_all, y_all, marker='o', s=30, facecolor='green',
           linewidth=0.5, edgecolors='black', alpha=0.8, zorder=3)

# Save publication figure as PNG
output_path = config.MatchedRMExtinctionPlotFile
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"Saved publication-quality PNG to: {output_path}")

# Also save as PDF
output_pdf = output_path.replace('.png', '.pdf')
plt.savefig(output_pdf, dpi=300, bbox_inches='tight', facecolor='white')
print(f"Saved PDF version to: {output_pdf}")

# Copy to figures directory
import shutil
os.makedirs('figures', exist_ok=True)
shutil.copy(output_path, 'figures/AllRMPtsInRegion.png')
shutil.copy(output_pdf, 'figures/AllRMPtsInRegion.pdf')
print(f"Copied to figures/ directory")

plt.close()

print(f"\nFigure statistics:")
print(f"  Total RM sources shown: {len(matched_data)}")
print(f"  Font: Times New Roman (serif) throughout")
print(f"  Font sizes: axis labels 16pt, tick labels 14pt, colorbar label 16pt")
