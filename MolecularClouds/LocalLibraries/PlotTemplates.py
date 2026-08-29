'''
Contains common plots or plot elements utilized in various scripts
'''
import logging

import matplotlib.pyplot as plt
import adjustText
import math

import numpy as np
from astropy.wcs import WCS
from matplotlib import pyplot as plt

import ConversionLibrary as cl
import config

def extinctionPlot(regionOfInterest):
    '''
    Plots the extinction plot of a given region.
    :param regionOfInterest: RegionOfInterest object which gives data on where and what part of the HDU is to be plotted. RegionOfInterest Object.
    :return: fig, ax - the figure and axis of the plot. Matplotlib objects.
    '''
    hdu = regionOfInterest.hdu
    fig, ax, im = heatPlot(hdu)
    ax = equatorialCoords(ax)
    ax = overlayCoords(ax)
    cb = colourbar(regionOfInterest, im)
    ax = setBoundsIfValid(ax, regionOfInterest.xmin, regionOfInterest.xmax, regionOfInterest.ymin, regionOfInterest.ymax)

    return fig, ax

def heatPlot(hdu):
    '''
    Creates a heat plot for the given HDU.

    :param hdu: The HDU image file.
    :return: fig, ax, im: The figure, axis, and image of the plot. Matplotlib objects.
    '''
    wcs = WCS(hdu.header)

    fig = plt.figure(figsize=(10, 10), dpi=300, facecolor='w', edgecolor='k')
    ax = fig.add_subplot(111, projection=wcs)
    # Fixed vmin/vmax for consistent colormap across plots
    vmin = 0
    vmax = 15
    im = ax.imshow(hdu.data, origin='lower', cmap='BrBG', interpolation='nearest',
                   vmin=vmin, vmax=vmax)

    return fig, ax, im

def equatorialCoords(ax):
    '''
    Overlays the given axes with equatorial coordinates.
    :param ax: The axis of the plot. Matplotlib axis object.
    :return: Nothing, it applies it to the axis.
    '''
    # ---- Style the main axes and their grid
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

    # Set tick label sizes and positions
    ra.set_ticklabel(size=14)
    dec.set_ticklabel(size=14)

    # Force Dec labels and ticks to appear ONLY on left side
    dec.set_ticks_position('l')
    dec.set_ticklabel_position('l')
    dec.set_axislabel_position('l')

    ra.grid(color='white', alpha=0.5, linestyle='solid')
    dec.grid(color='white', alpha=0.5, linestyle='solid')
    # ---- Style the main axes and their grid.
    return ax

def overlayCoords(ax):
    '''
    Overlays galactic coordinates onto the axis.
    :param ax: The axis of the plot. Matplotlib axis object.
    :return: Nothing, it applies it to the axis.
    '''
    # ---- Style the overlay and its grid
    overlay = ax.get_coords_overlay('galactic')

    overlay[0].set_axislabel('Longitude', fontsize=14, color='grey')
    overlay[1].set_axislabel('Latitude', fontsize=14, minpad=-1)

    # Manually position the Latitude label - positioned in gap between plot and colorbar
    ax.text(1.02, 0.60, 'Latitude', fontsize=14, color='grey',
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
    return ax


def colourbar(regionOfInterest, im):
    '''
    Sets the colour bar on the image for our region of interest.
    :param regionOfInterest: Used to obtain data on the fits data type. RegionOfInterest object.
    :param im: The matplotlib image object to make a colour bar for.
    :return: cb - the pointer to the colourbar object.
    '''
    from matplotlib.ticker import AutoLocator
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    cb = None
    # Get the axes from the image
    ax = im.axes

    # ---- Style the colour bar
    if regionOfInterest.fitsDataType == 'HydrogenColumnDensity':
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.48, axes_class=plt.Axes)
        cb = plt.colorbar(im, cax=cax, format='%.0e')
        cb.set_label('Hydrogen Column Density', rotation=270, labelpad=25, fontsize=14)
        cb.ax.tick_params(labelsize=12, width=1.2, length=5)
    elif regionOfInterest.fitsDataType == 'VisualExtinction':
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.48, axes_class=plt.Axes)
        cb = plt.colorbar(im, cax=cax)
        cb.set_label('$A_V$', rotation=270, labelpad=25, fontsize=14)
        cb.ax.tick_params(labelsize=12, width=1.2, length=5)
        # Use automatic locator for proper tick values
        cb.ax.yaxis.set_major_locator(AutoLocator())
    # ---- Style the colour bar.
    return cb

def setBoundsIfValid(ax, xmin, xmax, ymin, ymax):
    '''
    Sets the axis bounds if the given bounds are valid bounds.
    :param ax: The axis of the plot. Matplotlib axis object.
    :param xmin: The desired x minimum bound. int.
    :param xmax: The desired x maximum bound. int.
    :param ymin: The desired y minimum bound. int.
    :param ymax: The desired y maximum bound. int.
    :return: Nothing, it applies it to the axis.
    '''
    if not math.isnan(xmax) and not math.isnan(xmin):
        ax.set_xlim(xmin, xmax)
    if not math.isnan(ymax) and not math.isnan(ymin):
        ax.set_ylim(ymin, ymax)
    return ax

def labelPoints(ax, labels, xCoords, yCoords, size = 9, color = 'w', textFix = True):
    '''
    Labels points on a given graph given by the axis.

    :param ax: The axis of the plot. Matplotlib axis object.
    :param labels: A set of labels for the points. List.
    :param xCoords: A set of x coordinates denoting where the points are. List.
    :param yCoords: A set of y coordinates denoting where the points are. List.
    :param size: The size of the text. Integer.
    :param color: The colour of the text. String.
    :return: text: A list of matlotlib text objects pointing to each of the labels. List.
    '''
    # ---- Annotate the chosen reference points
    text = []
    for i, label in enumerate(labels):
        # Each point is labelled in order of increasing extinction value
        # To label with ID number use: txt = ax.text(x_AllRef[i], y_AllRef[i], str(number), size=9, color='w')
        # txt = ax.text(x_AllRef[i], y_AllRef[i], str(i + 1), size=9, color='w')
        txt = ax.text(xCoords[i], yCoords[i], label, size=size, color=color)
        text.append(txt)
    if textFix:
        adjustText.adjust_text(text)
    return text
    # ---- Annotate the chosen reference points


def plotRefPoints(refPoints, regionOfInterest, title, fontsize=12, pad=50, marker='o', facecolor='green', linewidth=.5, edgecolors='black', s=50, textFix=True):
    '''
    Given a list of reference points and the data of the region in question,
    generates a basic plot of the region with the locations of the reference points.
    :param refPoints: A pandas datatable containing the reference point information.
    :param regionOfInterest: RegionOfInterest class corresponding to a given region of interest.
    :param title: Title of the plot.
    :return: fig, ax - the figure and plot axes of the plot.
    '''
    # -------- PREPARE TO PLOT REFERENCE POINTS --------
    labels = list(refPoints['ID#'])
    Ra = list(refPoints['Ra(deg)'])
    Dec = list(refPoints['Dec(deg)'])

    # ---- Convert Ra and Dec of reference points into pixel values of the fits file
    x, y = cl.RADec2xy(Ra, Dec, regionOfInterest.wcs)
    # ---- Convert Ra and Dec of reference points into pixel values of the fits file.
    # -------- PREPARE TO PLOT REFERENCE POINTS. --------

    # -------- CREATE A FIGURE - ALL REF POINTS MAP --------
    fig, ax = extinctionPlot(regionOfInterest)
    plt.title(title, fontsize=fontsize, pad=pad)
    ax.scatter(x, y, marker=marker, facecolor=facecolor, linewidth=linewidth, edgecolors=edgecolors, s=s)
    # ---- Annotate the chosen reference points
    labelPoints(ax, labels, x, y, textFix=textFix)
    # ---- Annotate the chosen reference points
    # -------- CREATE A FIGURE - ALL REF POINTS MAP. --------
    return fig, ax


def plotRefPointScript(title, saveFigurePath, refPoints, regionOfInterest, contourThreshold = math.nan, textFix=True):
    '''
    Wrapper function for commonly duplicated code in creating a reference point plot.
    :param titleFragment: Part of the title. String.
    :param saveFragment: Part of the save file name. String.
    :param cloudName: Part of the title. String.
    :param refPoints: Input reference point data to be mapped on the image.
    :param hdu: HDU image file of the region.
    :param regionOfInterest: Region information in a RegionOfInterest class.
    :return: Nothing.
    '''
    # -------- PREPARE TO PLOT REFERENCE POINTS --------

    fig, ax = plotRefPoints(refPoints, regionOfInterest, title, textFix=textFix)
    if np.isfinite(contourThreshold):
        mask = regionOfInterest.hdu.data > contourThreshold
        ax.contour(mask, levels=1, colors='black', linewidths=0.5)
        ax.contourf(mask, levels=1, alpha = 0.25, cmap = 'Greys')
    # ---- Display or save the figure
    plt.savefig(saveFigurePath, bbox_inches='tight')
    plt.close()
    # ---- Display or save the figure.

    # ---- Log info
    message = 'Saving the map: {} to {}'.format(title, saveFigurePath)
    logging.info(config.logSectionDivider)
    logging.info(message)
    print(message)
    # ---- Log info
    # -------- CREATE A FIGURE - REF POINTS MAP. --------
