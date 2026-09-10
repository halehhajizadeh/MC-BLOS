"""
Additional BLOS plot that highlights overlapping reference points in a separate color.
"""
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- Set global font style to match publication quality
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'STIXGeneral', 'serif']
plt.rcParams['mathtext.fontset'] = 'stix'

from LocalLibraries.RegionOfInterest import Region
from LocalLibraries.CalculateB import CalculateB
import LocalLibraries.MatchedRMExtinctionFunctions as MREF
import LocalLibraries.config as config
import LocalLibraries.PlotUtils as putil

# -------- SETUP --------
cloudName = config.cloud
regionOfInterest = Region(cloudName)

# Input Files
ChosenRefPointFile = config.ChosenRefPointFile
ChosenRefDataFile = config.ChosenRefDataFile
MatchedRMExtinctFile = config.MatchedRMExtinctionFile

# Output file for this special plot
OutputPlotFile = config.BLOSPointsPlot.replace('.png', '_RefOverlap.png')
OutputPlotFilePDF = OutputPlotFile.replace('.png', '.pdf')

# -------- READ DATA --------
MatchedRMExtinctTable = pd.read_csv(MatchedRMExtinctFile, sep=config.dataSeparator)
RefPointTable = pd.read_csv(ChosenRefPointFile, sep=config.dataSeparator)
RefData = pd.read_csv(ChosenRefDataFile, sep=config.dataSeparator)

fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction = MREF.unpackRefData(RefData)
RemainingPointTable = MREF.rmMatchingPts(MatchedRMExtinctTable, RefPointTable)
ExtLimit = config.onPtsExtMultipleThreshold * fiducialExtinction
RemainingPointTable = MREF.rmLowExtPts(RemainingPointTable, ExtLimit)

# -------- CALCULATE BLOS --------
BLOSData = CalculateB(regionOfInterest.AvFilePath, RemainingPointTable, fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction, NegativeExtinctionEntriesChange=config.negScaledExtOption)

# -------- IDENTIFY OVERLAPPING REFERENCE POINTS --------
# Find reference points that are very close to each other (within 0.02 degrees)
RefRa = np.array(RefPointTable['Ra(deg)'])
RefDec = np.array(RefPointTable['Dec(deg)'])
RefIDs = np.array(RefPointTable['ID#'])

overlap_threshold = 0.02  # degrees
overlap_indices = set()

for i in range(len(RefRa)):
    for j in range(i+1, len(RefRa)):
        dist = np.sqrt((RefRa[i] - RefRa[j])**2 + (RefDec[i] - RefDec[j])**2)
        if dist < overlap_threshold:
            overlap_indices.add(i)
            overlap_indices.add(j)

overlap_indices = list(overlap_indices)
non_overlap_indices = [i for i in range(len(RefRa)) if i not in overlap_indices]

print(f"Found {len(overlap_indices)} overlapping reference points: IDs {[RefIDs[i] for i in overlap_indices]}")

# -------- PREPARE PLOT DATA --------
n = list(BLOSData['ID#'])
Ra = list(BLOSData['Ra(deg)'])
Dec = list(BLOSData['Dec(deg)'])
BLOS = list(BLOSData['Magnetic_Field(uG)'])

# Reference point BLOS
RefBLOSData = CalculateB(regionOfInterest.AvFilePath, RefPointTable, fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction, NegativeExtinctionEntriesChange="None")
RefBLOS = list(RefBLOSData['Magnetic_Field(uG)'])

# -------- CREATE FIGURE --------
fig = plt.figure(figsize=(10, 10), dpi=300, facecolor='w', edgecolor='k')
ax = fig.add_subplot(111, projection=regionOfInterest.wcs)

im = plt.imshow(regionOfInterest.hdu.data, origin='lower', cmap='BrBG', interpolation='nearest',
                vmin=0, vmax=15)

# ---- Plot BLOS points (red/blue)
x = []
y = []
for i in range(len(Ra)):
    pixelRow, pixelColumn = regionOfInterest.wcs.wcs_world2pix(Ra[i], Dec[i], 0)
    x.append(pixelRow)
    y.append(pixelColumn)

color, size = putil.p2RGB(BLOS, size_cap=1000, scale_factor=0.5, alpha=0.7)
plt.scatter(x, y, s=size, facecolor=color, marker='o', linewidth=0.8, edgecolors='black')

# ---- Plot NON-overlapping reference points (green)
xRef_non = []
yRef_non = []
sizeRef_non = []
for i in non_overlap_indices:
    pixelRow, pixelColumn = regionOfInterest.wcs.wcs_world2pix(RefRa[i], RefDec[i], 0)
    xRef_non.append(pixelRow)
    yRef_non.append(pixelColumn)
    sizeRef_non.append(abs(RefBLOS[i])*0.5 if abs(RefBLOS[i]) < 1000 else 500)

colorRef_non = [(0, 1, 0, 0.7) for _ in non_overlap_indices]
plt.scatter(xRef_non, yRef_non, s=sizeRef_non, facecolor=colorRef_non, marker='o', linewidth=1.5, edgecolors='darkgreen')

# ---- Plot OVERLAPPING reference points (yellow/gold) at original location
xRef_over = []
yRef_over = []
sizeRef_over = []
for idx, i in enumerate(overlap_indices):
    pixelRow, pixelColumn = regionOfInterest.wcs.wcs_world2pix(RefRa[i], RefDec[i], 0)
    xRef_over.append(pixelRow)
    yRef_over.append(pixelColumn)
    sizeRef_over.append(abs(RefBLOS[i])*0.5 if abs(RefBLOS[i]) < 1000 else 500)

colorRef_over = [(1, 0.8, 0, 0.85) for _ in overlap_indices]  # Gold/yellow color
plt.scatter(xRef_over, yRef_over, s=sizeRef_over, facecolor=colorRef_over, marker='o', linewidth=2, edgecolors='darkorange', zorder=10)

# ---- Style axes
if not math.isnan(regionOfInterest.xmax) and not math.isnan(regionOfInterest.xmin):
    ax.set_xlim(regionOfInterest.xmin, regionOfInterest.xmax)
if not math.isnan(regionOfInterest.ymax) and not math.isnan(regionOfInterest.ymin):
    ax.set_ylim(regionOfInterest.ymin, regionOfInterest.ymax)

ra = ax.coords[0]
dec = ax.coords[1]
ra.set_major_formatter('d')
dec.set_major_formatter('d')
ra.set_axislabel('RA (degree)', fontsize=16)
dec.set_axislabel('Dec (degree)', fontsize=16)

dec.set_ticks(number=8)
ra.set_ticks(number=12)
ra.display_minor_ticks(True)
dec.display_minor_ticks(True)
ra.set_minor_frequency(5)

ra.set_ticklabel(size=14)
dec.set_ticklabel(size=14)

dec.set_ticks_position('l')
dec.set_ticklabel_position('l')
dec.set_axislabel_position('l')

ra.grid(color='white', alpha=0.5, linestyle='solid')
dec.grid(color='white', alpha=0.5, linestyle='solid')

# ---- Overlay galactic coordinates
overlay = ax.get_coords_overlay('galactic')
overlay[0].set_axislabel('Longitude', fontsize=14, color='grey')
overlay[1].set_axislabel('Latitude', fontsize=14, minpad=-1)
ax.text(1.02, 0.60, 'Latitude', fontsize=14, color='grey',
        rotation=270, transform=ax.transAxes,
        verticalalignment='center', horizontalalignment='left')
overlay[1].set_axislabel('')
overlay[0].set_ticks(color='grey', number=12)
overlay[1].set_ticks(color='grey', number=8)
overlay[0].set_ticklabel(size=12, color='grey')
overlay[1].set_ticklabel(size=12, color='grey')
overlay.grid(color='grey', linestyle='dashed', alpha=0.5)

# ---- Colorbar
from matplotlib.ticker import AutoLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable

divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.48, axes_class=plt.Axes)
cb = plt.colorbar(im, cax=cax)
cb.set_label('$A_V$', rotation=270, labelpad=25, fontsize=14)
cb.ax.tick_params(labelsize=12, width=1.2, length=5)
cb.ax.yaxis.set_major_locator(AutoLocator())

# ---- Legend with overlapping points highlighted
marker1 = plt.scatter([], [], s=10/2, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker2 = plt.scatter([], [], s=100/2, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker4 = plt.scatter([], [], s=1000/2, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker5 = plt.scatter([], [], s=100, facecolor=(1, 0, 0, 0.7), edgecolor='black', linewidth=0.8)
marker6 = plt.scatter([], [], s=100, facecolor=(0, 0, 1, 0.7), edgecolor='black', linewidth=0.8)
marker7 = plt.scatter([], [], s=100, facecolor=(0, 1, 0, 0.7), edgecolor='darkgreen', linewidth=1.5)
marker8 = plt.scatter([], [], s=100, facecolor=(1, 0.8, 0, 0.85), edgecolor='darkorange', linewidth=2)

legend_markers = [marker1, marker2, marker4, marker5, marker6, marker7, marker8]
labels = [
    r'$10\,\mu G$',
    r'$100\,\mu G$',
    r'$1000+\,\mu G$',
    'Away from us',
    'Towards us',
    'Off points',
    'Overlapping Off pts'
]

legend = ax.legend(handles=legend_markers, labels=labels, scatterpoints=1, ncol=2, loc='lower left', fontsize=10)
frame = legend.get_frame()
frame.set_facecolor('1')
frame.set_alpha(0.4)

# ---- Textbox
offPointsText = r"$\mathrm{RM}_{\mathrm{Off}}$: " + "{:+.1f}".format(fiducialRM) + r" rad/m$^2$" + "\n" + r"$A_V$ Off: " + "{:+.2f}".format(fiducialExtinction) + " mag"
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
ax.text(0.02, 0.98, offPointsText, transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=props)

# ---- Save
plt.savefig(OutputPlotFile, bbox_inches='tight')
plt.savefig(OutputPlotFilePDF, bbox_inches='tight', format='pdf')
plt.close()

print(f"Saved overlap-highlighted plot to {OutputPlotFile} and {OutputPlotFilePDF}")
