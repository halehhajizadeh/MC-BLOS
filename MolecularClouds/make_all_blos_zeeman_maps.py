"""Create consistent BLOS spatial maps with the three literature Zeeman points."""
from pathlib import Path
import json
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import AutoLocator

from LocalLibraries import config
from LocalLibraries.RegionOfInterest import Region
from LocalLibraries import PlotUtils as putil

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'Statistics' / 'BLOS_maps_all_results'
ZEEMAN = ROOT / 'FileOutput_ImprovedPlots/Perseus/PaperTables/zeeman_comparison.csv'


def safe_name(label):
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', label).strip('_')


def load_references(bfile):
    direct = bfile.parent / 'SelectedRefPoints.csv'
    if direct.exists():
        return pd.read_csv(direct, sep='\t')
    fallback = bfile.parent.parent / 'FinalData/SelectedRefPoints.csv'
    return pd.read_csv(fallback, sep='\t') if fallback.exists() else pd.DataFrame()


def plot_directory(bfile, label):
    if bfile.parent.name == 'FinalData':
        return bfile.parent.parent / 'Plots' / 'ZeemanMaps' / safe_name(label)
    return bfile.parent / 'Plots' / 'ZeemanMaps' / safe_name(label)


def make_map(label, bfile, zeeman, region):
    data = pd.read_csv(bfile, sep='\t')
    refs = load_references(bfile)
    ref_data_file = bfile.parent / 'ReferenceData.csv'
    if not ref_data_file.exists():
        ref_data_file = bfile.parent.parent / 'FinalData/ReferenceData.csv'
    ref_data = pd.read_csv(ref_data_file, sep='\t') if ref_data_file.exists() else pd.DataFrame()
    values = data['Magnetic_Field(uG)'].to_numpy(float)
    ra = data['Ra(deg)'].to_numpy(float)
    dec = data['Dec(deg)'].to_numpy(float)
    pos = values > 0
    neg = values < 0

    fig = plt.figure(figsize=(10, 10), dpi=220, facecolor='w')
    ax = fig.add_subplot(111, projection=region.wcs)
    im = ax.imshow(region.hdu.data, origin='lower', cmap='BrBG', interpolation='nearest', vmin=0, vmax=15)
    x, y = region.wcs.wcs_world2pix(ra, dec, 0)
    colors, sizes = putil.p2RGB(values, size_cap=1000, scale_factor=0.5, alpha=0.7)
    ax.scatter(x[pos], y[pos], s=np.asarray(sizes)[pos], facecolor='blue', alpha=0.7,
               marker='o', linewidth=0.8, edgecolors='black', label='Towards us')
    ax.scatter(x[neg], y[neg], s=np.asarray(sizes)[neg], facecolor='red', alpha=0.7,
               marker='o', linewidth=0.8, edgecolors='black', label='Away from us')

    if not refs.empty:
        rx, ry = region.wcs.wcs_world2pix(refs['Ra(deg)'].to_numpy(), refs['Dec(deg)'].to_numpy(), 0)
        ax.scatter(rx, ry, s=100, c='limegreen', marker='o', edgecolors='darkgreen', linewidth=1.5,
                   zorder=5, label='Off points')

    zx, zy = region.wcs.wcs_world2pix(zeeman['Ra(deg)'].to_numpy(), zeeman['Dec(deg)'].to_numpy(), 0)
    # Zeeman pointings are comparison measurements, so use one fixed symbol
    # size rather than scaling them with their measured field strengths.
    ax.scatter(zx, zy, s=150, facecolor='deepskyblue', marker='*', edgecolors='white',
               linewidth=0.7, zorder=20, label='OH Zeeman measurements')
    label_offsets = {'B1': (8, 10), 'L1448-CO': (-58, 12), 'L1448-COe': (10, -22)}
    for _, row in zeeman.iterrows():
        px, py = region.wcs.wcs_world2pix(row['Ra(deg)'], row['Dec(deg)'], 0)
        ax.annotate(row['Region'], (px, py), xytext=label_offsets.get(row['Region'], (8, 8)),
                    textcoords='offset points', fontsize=9, color='navy', zorder=21,
                    bbox=dict(boxstyle='round,pad=0.15', facecolor='white', alpha=0.7, edgecolor='none'))

    ax.set_xlim(region.xmin, region.xmax); ax.set_ylim(region.ymin, region.ymax)
    ra_axis, dec_axis = ax.coords[0], ax.coords[1]
    ra_axis.set_major_formatter('d'); dec_axis.set_major_formatter('d')
    ra_axis.set_axislabel('RA (degree)', fontsize=16); dec_axis.set_axislabel('Dec (degree)', fontsize=16)
    ra_axis.set_ticks(number=12); dec_axis.set_ticks(number=8)
    ra_axis.display_minor_ticks(True); dec_axis.display_minor_ticks(True); ra_axis.set_minor_frequency(5)
    ra_axis.set_ticklabel(size=14); dec_axis.set_ticklabel(size=14)
    dec_axis.set_ticks_position('l'); dec_axis.set_ticklabel_position('l'); dec_axis.set_axislabel_position('l')
    ra_axis.grid(color='white', alpha=0.5); dec_axis.grid(color='white', alpha=0.5)
    overlay = ax.get_coords_overlay('galactic')
    overlay[0].set_axislabel('Longitude', fontsize=14, color='grey')
    overlay[1].set_axislabel(''); overlay[0].set_ticks(color='grey', number=12); overlay[1].set_ticks(color='grey', number=8)
    overlay[0].set_ticklabel(size=12, color='grey'); overlay[1].set_ticklabel(size=12, color='grey')
    overlay.grid(color='grey', linestyle='dashed', alpha=0.5)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad=0.48, axes_class=plt.Axes)
    cb = plt.colorbar(im, cax=cax); cb.set_label('$A_V$', rotation=270, labelpad=25, fontsize=14)
    cb.ax.yaxis.set_major_locator(AutoLocator())
    handles, labels = ax.get_legend_handles_labels()
    for amount in (10, 100, 1000):
        handles.append(ax.scatter([], [], s=amount * 0.5, facecolor='white', edgecolor='black', alpha=0.7))
        labels.append(f'{amount} µG')
    ax.legend(handles, labels, loc='lower left', ncol=2, fontsize=9, framealpha=0.75)
    if not ref_data.empty:
        rm = ref_data['Reference RM'].iloc[0]
        av = ref_data['Reference Extinction'].iloc[0]
        ax.text(0.02, 0.98, f'$\\mathrm{{RM}}_{{\\mathrm{{Off}}}}$: {rm:+.1f} rad/m$^2$\n'
                f'$A_V$ Off: {av:+.2f} mag', transform=ax.transAxes, fontsize=12,
                va='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.set_title('')
    fig.tight_layout()
    return fig


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    zeeman = pd.read_csv(ZEEMAN)
    region = Region(config.cloud)
    saved = json.loads((ROOT / 'Statistics/statistics_summary.json').read_text())
    combined = OUT / 'all_blos_zeeman_maps.pdf'
    with PdfPages(combined) as pdf:
        for entry in saved:
            label = entry['dataset']
            bfile = ROOT / entry['field_source']
            fig = make_map(label, bfile, zeeman, region)
            stem = safe_name(label)
            own_dir = plot_directory(bfile, label)
            own_dir.mkdir(parents=True, exist_ok=True)
            fig.savefig(own_dir / 'BLOSPointMap_Zeeman.png', bbox_inches='tight')
            fig.savefig(own_dir / 'BLOSPointMap_Zeeman.pdf', bbox_inches='tight')
            # Keep a uniquely named copy in the combined output directory for
            # convenient browsing without changing the result directories.
            fig.savefig(OUT / f'{stem}.png', bbox_inches='tight')
            fig.savefig(OUT / f'{stem}.pdf', bbox_inches='tight')
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            print(label, flush=True)
    print(combined)
