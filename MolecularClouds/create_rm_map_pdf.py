#!/usr/bin/env python3
"""
Create clean PDF version of RM map (no title, no legend, just green dots)
"""
import matplotlib.pyplot as plt
import pandas as pd
from LocalLibraries.RegionOfInterest import Region
import LocalLibraries.config as config
import LocalLibraries.PlotTemplates as pt
import LocalLibraries.ConversionLibrary as cl

# Load region
cloudName = config.cloud
regionOfInterest = Region(cloudName)

# Load matched data
matched_data = pd.read_csv(config.MatchedRMExtinctionFile, sep=config.dataSeparator)

# Create extinction plot (uses hot colormap, vmin=0 vmax=15, serif fonts)
fig, ax = pt.extinctionPlot(regionOfInterest)

# Convert RA/Dec to pixel coordinates
x, y = cl.RADec2xy(
    list(matched_data['Ra(deg)']),
    list(matched_data['Dec(deg)']),
    regionOfInterest.wcs
)

# Plot all points in green (simple, clean version)
ax.scatter(x, y, marker='o', facecolor='green', linewidth=0.5,
           edgecolors='black', s=30, alpha=0.8)

# Save as PDF (vector format for journal)
plt.savefig('figures/AllRMPtsInRegion.pdf',
            bbox_inches='tight',
            format='pdf',
            facecolor='white')
print("✅ Created clean PDF version: figures/AllRMPtsInRegion.pdf")
print("   (No title, no legend, green dots only)")
print("   (Hot colormap vmin=0 vmax=15, serif fonts, 300 DPI)")

plt.close()
