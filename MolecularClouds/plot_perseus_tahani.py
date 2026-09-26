"""Map saved improved-plots Perseus fields and Tahani (2018) Table 6 at fixed sizes.
Run from MolecularClouds; literature table is produced by revise_paper_analysis.py.
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import AutoLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import pandas as pd
from LocalLibraries.RegionOfInterest import Region


def main():
    root = Path(__file__).resolve().parent
    from LocalLibraries import config
    output = Path(config.CloudOutputDir)
    data = pd.read_csv(output / 'FinalData/BLOSPoints.csv', sep='\t')
    lit = pd.read_csv(output / 'PaperTables/tahani2018_perseus.csv')
    region = Region('Perseus')
    plt.rcParams.update({'font.family': 'serif', 'font.size': 12})
    fig = plt.figure(figsize=(10, 10))
    fig.subplots_adjust(left=0.10, right=0.88, bottom=0.10, top=0.92)
    ax = fig.add_subplot(111, projection=region.wcs)
    im = ax.imshow(region.hdu.data, origin='lower', cmap='BrBG', interpolation='nearest', vmin=0, vmax=15)
    transform = ax.get_transform('world')
    # Show both Faraday catalogs.
    ax.scatter(data['Ra(deg)'], data['Dec(deg)'], transform=transform, s=38,
               c=np.where(data['Magnetic_Field(uG)'] > 0, 'blue', 'red'),
               edgecolors='white', linewidths=0.35, alpha=0.85, zorder=3)
    ax.scatter(lit['Ra(deg)'], lit['Dec(deg)'], transform=transform, s=110,
               marker='s', facecolors='none', edgecolors=np.where(lit.B > 0, 'blue', 'red'),
               linewidths=1.7, zorder=4)
    ax.set_xlim(region.xmin, region.xmax)
    ax.set_ylim(region.ymin, region.ymax)
    ra, dec = ax.coords
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
    overlay = ax.get_coords_overlay('galactic')
    overlay[0].set_axislabel('Longitude', fontsize=14, color='grey')
    overlay[1].set_axislabel('', fontsize=14, minpad=-1)
    ax.text(1.02, 0.60, 'Latitude', fontsize=14, color='grey', rotation=270,
            transform=ax.transAxes, verticalalignment='center', horizontalalignment='left')
    overlay[0].set_ticks(color='grey', number=12)
    overlay[1].set_ticks(color='grey', number=8)
    overlay[0].set_ticklabel(size=12, color='grey')
    overlay[1].set_ticklabel(size=12, color='grey')
    overlay.grid(color='grey', linestyle='dashed', alpha=0.5)
    handles = [
        Line2D([], [], marker='o', linestyle='none', color='0.25', markersize=6,
               label='This work'),
        Line2D([], [], marker='s', linestyle='none', markerfacecolor='none', color='0.25',
               markersize=9, label='Tahani et al. (2018) RM points'),
        Line2D([], [], marker='o', linestyle='none', color='blue', label='Positive: toward observer'),
        Line2D([], [], marker='o', linestyle='none', color='red', label='Negative: away from observer')]
    ax.legend(handles=handles, loc='lower left', fontsize=10, framealpha=0.4)
    # Match the original improved-plots BLOS colorbar geometry.
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad=0.48, axes_class=plt.Axes)
    cb = plt.colorbar(im, cax=cax)
    cb.set_label(r'$A_V$', rotation=270, labelpad=25, fontsize=14)
    cb.ax.tick_params(labelsize=12, width=1.2, length=5)
    cb.ax.yaxis.set_major_locator(AutoLocator())
    for ext in ('png', 'pdf'):
        path = output / 'Plots' / f'BLOSPointMap_ConstantSize_Tahani2018.{ext}'
        fig.savefig(path, dpi=300, bbox_inches='tight')
        print(path)
    plt.close(fig)
    region.hdulist.close()


if __name__ == '__main__':
    main()
