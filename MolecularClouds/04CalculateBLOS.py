"""
This is the fourth stage of the BLOSMapping method where the BLOS values are calculated using the reference points selected in
the previous stage.  This file also produces a scatter plot of BLOS points.
"""
import math
import pandas as pd

import matplotlib.pyplot as plt
from LocalLibraries.RegionOfInterest import Region
from LocalLibraries.CalculateB import CalculateB

import LocalLibraries.MatchedRMExtinctionFunctions as MREF
import LocalLibraries.config as config
import LocalLibraries.PlotTemplates as pt
import LocalLibraries.PlotUtils as putil

import logging

# Import PlotConfig for consistent styling (fonts set globally)
import LocalLibraries.PlotConfig as pc

# -------- CHOOSE THE REGION OF INTEREST --------
cloudName = config.cloud
regionOfInterest = Region(cloudName)
# -------- CHOOSE THE REGION OF INTEREST. --------

# -------- DEFINE FILES AND PATHS --------
#Input Files
ChosenRefPointFile = config.ChosenRefPointFile #Matched RM-Extinction points chosen as reference points - point data
ChosenRefDataFile = config.ChosenRefDataFile #Matched RM-Extinction points chosen as reference points - summary statistics such as average extinction, RM, etc.
MatchedRMExtinctFile = config.MatchedRMExtinctionFile

#Output Files
BLOSPointsFile = config.BLOSPointsFile
BLOSPointsPlotFile = config.BLOSPointsPlot
LogFile = config.Script04File
# -------- DEFINE FILES AND PATHS. --------

# -------- CONFIGURE LOGGING --------
logging.basicConfig(filename=LogFile, filemode='w', format=config.logFormat, level=logging.INFO)
# -------- CONFIGURE LOGGING --------

# -------- READ REFERENCE POINT TABLE --------
MatchedRMExtinctTable = pd.read_csv(MatchedRMExtinctFile, sep=config.dataSeparator)
RefPointTable = pd.read_csv(ChosenRefPointFile, sep=config.dataSeparator)
RefData = pd.read_csv(ChosenRefDataFile, sep=config.dataSeparator)
# -------- READ REFERENCE POINT TABLE. --------

# -------- DETERMINE REMAINING POINTS AFTER FILTERING --------
fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction = MREF.unpackRefData(RefData)
RemainingPointTable = MREF.rmMatchingPts(MatchedRMExtinctTable, RefPointTable)
ExtLimit = config.onPtsExtMultipleThreshold * fiducialExtinction
RemainingPointTable = MREF.rmLowExtPts(RemainingPointTable, ExtLimit)
# -------- DETERMINE REMAINING POINTS AFTER FILTERING --------
# =====================================================================================================================

# -------- CALCULATE BLOS --------
BLOSData = CalculateB(regionOfInterest.AvFilePath, RemainingPointTable, fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction, NegativeExtinctionEntriesChange = config.negScaledExtOption)
BLOSData.to_csv(BLOSPointsFile, index=False, na_rep=config.missingDataRep, sep=config.dataSeparator)

message = 'Saving calculated magnetic field values to ' + BLOSPointsFile
logging.info(message)
print(message)
# -------- CALCULATE BLOS. --------

# =====================================================================================================================

# -------- PREPARE TO PLOT BLOS POINTS --------
n = list(BLOSData['ID#'])
Ra = list(BLOSData['Ra(deg)'])
Dec = list(BLOSData['Dec(deg)'])
BLOS = list(BLOSData['Magnetic_Field(uG)'])
# -------- PREPARE TO PLOT BLOS POINTS. --------
#
# -------- CREATE A FIGURE - BLOS POINT MAP --------
fig = plt.figure(figsize=(8, 8), dpi=300, facecolor='w', edgecolor='k')
ax = fig.add_subplot(111, projection=regionOfInterest.wcs)

# No title for publication version
# Use hot colormap with fixed vmin/vmax for extinction background
im = plt.imshow(regionOfInterest.hdu.data, origin='lower', cmap='hot', interpolation='nearest',
                vmin=0, vmax=15)

# ---- Convert Ra and Dec of points into pixel values of the fits file
x = []  # x pixel coordinate
y = []  # y pixel coordinate
for i in range(len(Ra)):
    pixelRow, pixelColumn = regionOfInterest.wcs.wcs_world2pix(Ra[i], Dec[i], 0)
    x.append(pixelRow)
    y.append(pixelColumn)
# ---- Convert Ra and Dec of points into pixel values of the fits file.
color, size = putil.p2RGB(BLOS, size_cap=1000, scale_factor=0.3)
plt.scatter(x, y, s=size, facecolor=color, marker='o', linewidth=.5, edgecolors='black')

# ---- Annotate the BLOS Points - DISABLED for publication version
# pt.labelPoints(ax, n, x, y, textFix = config.textFix)
# ---- Annotate the BLOS Points.

# -------- PREPARE TO PLOT REF BLOS POINTS --------
# ---- CALCULATE REF POINT BLOS.
#Utilized only for the plot which includes the reference points used to find the BLOS
RefBLOSData = CalculateB(regionOfInterest.AvFilePath, RefPointTable, fiducialRM, fiducialRMAvgErr, fiducialRMStd, fiducialExtinction, NegativeExtinctionEntriesChange="None")
# ---- CALCULATE REF POINT BLOS.

Refn = list(RefBLOSData['ID#'])
RefRa = list(RefBLOSData['Ra(deg)'])
RefDec = list(RefBLOSData['Dec(deg)'])
RefBLOS = list(RefBLOSData['Magnetic_Field(uG)'])

# -------- PREPARE TO PLOT REF BLOS POINTS. --------
# ---- Convert Ra and Dec of points into pixel values of the fits file
xRef = []  # x pixel coordinate
yRef = []  # y pixel coordinate
for i in range(len(RefRa)):
    pixelRow, pixelColumn = regionOfInterest.wcs.wcs_world2pix(RefRa[i], RefDec[i], 0)
    xRef.append(pixelRow)
    yRef.append(pixelColumn)
# ---- Convert Ra and Dec of points into pixel values of the fits file.
colorRef, sizeRef = putil.p2C(RefBLOS, colour=(0, 1, 0), size_cap=1000, scale_factor=0.3)
plt.scatter(xRef, yRef, s=sizeRef, facecolor=colorRef, marker='o', linewidth=.5, edgecolors='black')

# ---- Annotate the BLOS Points - DISABLED for publication version
# pt.labelPoints(ax, Refn, xRef, yRef, color = 'magenta', textFix=config.textFix)
# ---- Annotate the BLOS Points.

# ---- Style the main axes and their grid
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

# Set tick label sizes
ra.set_ticklabel(size=14)
dec.set_ticklabel(size=14)

ra.grid(color='white', alpha=0.5, linestyle='solid')
dec.grid(color='white', alpha=0.5, linestyle='solid')
# ---- Style the main axes and their grid.

# ---- Style the overlay and its grid
overlay = ax.get_coords_overlay('galactic')

overlay[0].set_axislabel('Longitude', fontsize=14, color='grey')
overlay[1].set_axislabel('Latitude', fontsize=14, minpad=-1)

# Manually position the Latitude label - adjust y-value to move it vertically
ax.text(1.02, 0.55, 'Latitude', fontsize=14, color='grey',
        rotation=270, transform=ax.transAxes,
        verticalalignment='center', horizontalalignment='left')
overlay[1].set_axislabel('')  # Hide the default label

overlay[0].set_ticks(color='grey', number=12)
overlay[1].set_ticks(color='grey', number=8)

# Set tick label properties
overlay[0].set_ticklabel(size=12, color='grey')
overlay[1].set_ticklabel(size=12, color='grey')

overlay.grid(color='grey', linestyle='dashed', alpha=0.5)
# ---- Style the overlay and its grid.

# ---- Style the colour bar (match RM map style)
from matplotlib.ticker import AutoLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable

if regionOfInterest.fitsDataType == 'HydrogenColumnDensity':
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.12, axes_class=plt.Axes)
    cb = plt.colorbar(im, cax=cax, format='%.0e')
    cb.set_label('Hydrogen Column Density', rotation=270, labelpad=20, fontsize=14)
    cb.ax.tick_params(labelsize=12)
elif regionOfInterest.fitsDataType == 'VisualExtinction':
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.45, axes_class=plt.Axes)
    cb = plt.colorbar(im, cax=cax)
    cb.set_label('$A_V$', rotation=270, labelpad=25, fontsize=14)
    cb.ax.tick_params(labelsize=12, width=1.2, length=5)
    cb.ax.yaxis.set_major_locator(AutoLocator())
# ---- Style the colour bar.

# ---- Style the legend (scale_factor 0.3 means multiply by 0.3)
marker1 = plt.scatter([], [], s=10*0.3, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker2 = plt.scatter([], [], s=100*0.3, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker3 = plt.scatter([], [], s=500*0.3, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker4 = plt.scatter([], [], s=1000*0.3, facecolor=(1, 1, 1, 0.7), edgecolor='black')
marker5 = plt.scatter([], [], s=100*0.3, facecolor=(1, 0, 0, 0.7), edgecolor='black')
marker6 = plt.scatter([], [], s=100*0.3, facecolor=(0, 0, 1, 0.7), edgecolor='black')
marker7 = plt.scatter([], [], s=100*0.3, facecolor=(0, 1, 0, 0.7), edgecolor='black')
legend_markers = [marker1, marker2, marker4, marker5, marker6, marker7]

labels = [
    str(10)+r'$\mu$G',
    str(100)+r'$\mu$G',
    str(1000) + "+"+r'$\mu$G',
    'Away from us',
    'Towards us',
    'Off points'
    ]

legend = ax.legend(handles=legend_markers, labels=labels, scatterpoints=1, ncol=2,
                   loc='lower left', fontsize=pc.BLOSMAP_LEGEND_FONTSIZE, framealpha=0.85, edgecolor='black')

frame = legend.get_frame()
frame.set_facecolor('white')
# ---- Style the legend.

# ---- Style the textbox
offPointsText = "RM$_{{\\rm Off}}$: {:+.1f} rad/m$^2$ \n$A_V$ Off: {:+.2f} mag".format(fiducialRM, fiducialExtinction)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.85, edgecolor='black')
ax.text(0.02, 0.98, offPointsText, transform=ax.transAxes, fontsize=pc.BLOSMAP_LEGEND_FONTSIZE, verticalalignment='top', bbox=props)
# ---- Style the textbox

# ---- Display or save the figure
# plt.show()
plt.savefig(BLOSPointsPlotFile, bbox_inches='tight', dpi=300, facecolor='white')
plt.close()
# ---- Display or save the figure.
message = 'Saving BLOS figure to ' + BLOSPointsPlotFile
logging.info(message)
print(message)
# -------- CREATE A FIGURE - BLOS POINT MAP. --------
