"""
Plot configuration loader.

Reads configPlotting.ini and exposes all plotting parameters as module-level variables.
This allows easy customization of all plot aesthetics without touching code.
"""

import configparser
import os
import matplotlib.pyplot as plt

# Find the config file relative to the LocalLibraries directory
_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configPlotting.ini')
_config = configparser.ConfigParser()
_config.read(_config_path)

# Helper functions to read config values with type conversion
def _get_str(section, key, fallback=None):
    return _config.get(section, key, fallback=fallback)

def _get_int(section, key, fallback=None):
    return _config.getint(section, key, fallback=fallback)

def _get_float(section, key, fallback=None):
    return _config.getfloat(section, key, fallback=fallback)

def _get_bool(section, key, fallback=None):
    return _config.getboolean(section, key, fallback=fallback)

# ============================================================================
# GLOBAL MATPLOTLIB SETTINGS
# ============================================================================
# Apply global matplotlib rcParams from config
FONT_FAMILY = _get_str('Global', 'font_family', 'serif')
FONT_SIZE = _get_int('Global', 'font_size', 14)
USE_LATEX = _get_bool('Global', 'use_latex', False)

plt.rcParams.update({
    "font.family": FONT_FAMILY,
    "font.size": FONT_SIZE,
    "axes.labelsize": FONT_SIZE,
    "axes.titlesize": FONT_SIZE,
    "legend.fontsize": FONT_SIZE - 2,
    "xtick.labelsize": FONT_SIZE - 2,
    "ytick.labelsize": FONT_SIZE - 2,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "text.usetex": USE_LATEX,
})

# ============================================================================
# FIGURE
# ============================================================================
FIGURE_WIDTH = _get_int('Figure', 'width', 7)
FIGURE_HEIGHT = _get_int('Figure', 'height', 7)
FIGURE_DPI = _get_int('Figure', 'dpi', 120)

# ============================================================================
# HEATMAP
# ============================================================================
HEATMAP_CMAP = _get_str('Heatmap', 'colormap', 'BrBG')
HEATMAP_INTERPOLATION = _get_str('Heatmap', 'interpolation', 'nearest')

# ============================================================================
# AXES
# ============================================================================
# RA
RA_LABEL = _get_str('Axes', 'ra_label', 'RA (degree)')
RA_LABEL_FONTSIZE = _get_int('Axes', 'ra_label_fontsize', 16)
RA_TICK_FONTSIZE = _get_int('Axes', 'ra_tick_fontsize', 14)
RA_NUM_TICKS = _get_int('Axes', 'ra_num_ticks', 12)
RA_MINOR_FREQUENCY = _get_int('Axes', 'ra_minor_frequency', 5)
RA_GRID_COLOR = _get_str('Axes', 'ra_grid_color', 'white')
RA_GRID_ALPHA = _get_float('Axes', 'ra_grid_alpha', 0.5)
RA_GRID_LINESTYLE = _get_str('Axes', 'ra_grid_linestyle', 'solid')

# Dec
DEC_LABEL = _get_str('Axes', 'dec_label', 'Dec (degree)')
DEC_LABEL_FONTSIZE = _get_int('Axes', 'dec_label_fontsize', 16)
DEC_TICK_FONTSIZE = _get_int('Axes', 'dec_tick_fontsize', 14)
DEC_NUM_TICKS = _get_int('Axes', 'dec_num_ticks', 8)
DEC_GRID_COLOR = _get_str('Axes', 'dec_grid_color', 'white')
DEC_GRID_ALPHA = _get_float('Axes', 'dec_grid_alpha', 0.5)
DEC_GRID_LINESTYLE = _get_str('Axes', 'dec_grid_linestyle', 'solid')

# Galactic overlay
GAL_LON_LABEL = _get_str('Axes', 'gal_lon_label', 'Longitude')
GAL_LAT_LABEL = _get_str('Axes', 'gal_lat_label', 'Latitude')
GAL_LABEL_FONTSIZE = _get_int('Axes', 'gal_label_fontsize', 14)
GAL_TICK_FONTSIZE = _get_int('Axes', 'gal_tick_fontsize', 12)
GAL_TICK_COLOR = _get_str('Axes', 'gal_tick_color', 'grey')
GAL_NUM_LON_TICKS = _get_int('Axes', 'gal_num_lon_ticks', 12)
GAL_NUM_LAT_TICKS = _get_int('Axes', 'gal_num_lat_ticks', 8)
GAL_GRID_COLOR = _get_str('Axes', 'gal_grid_color', 'grey')
GAL_GRID_ALPHA = _get_float('Axes', 'gal_grid_alpha', 0.5)
GAL_GRID_LINESTYLE = _get_str('Axes', 'gal_grid_linestyle', 'dashed')

# ============================================================================
# COLORBAR
# ============================================================================
# Visual extinction
AV_LABEL = _get_str('Colorbar', 'av_label', '$A_V$')
AV_LABEL_FONTSIZE = _get_int('Colorbar', 'av_label_fontsize', 14)
AV_LABELPAD = _get_int('Colorbar', 'av_labelpad', 20)
AV_TICK_FONTSIZE = _get_int('Colorbar', 'av_tick_fontsize', 12)
AV_TICK_WIDTH = _get_float('Colorbar', 'av_tick_width', 1.2)
AV_TICK_LENGTH = _get_int('Colorbar', 'av_tick_length', 5)
AV_FRACTION = _get_float('Colorbar', 'av_fraction', 0.035)
AV_PAD = _get_float('Colorbar', 'av_pad', 0.12)
AV_SHRINK = _get_float('Colorbar', 'av_shrink', 1.0)

# Hydrogen column density
H_LABEL = _get_str('Colorbar', 'h_label', 'Hydrogen Column Density')
H_LABEL_FONTSIZE = _get_int('Colorbar', 'h_label_fontsize', 14)
H_LABELPAD = _get_int('Colorbar', 'h_labelpad', 20)
H_TICK_FONTSIZE = _get_int('Colorbar', 'h_tick_fontsize', 12)
H_FRACTION = _get_float('Colorbar', 'h_fraction', 0.035)
H_PAD = _get_float('Colorbar', 'h_pad', 0.12)
H_SHRINK = _get_float('Colorbar', 'h_shrink', 0.8)

# ============================================================================
# RM MAP
# ============================================================================
RMMAP_TITLE_FONTSIZE = _get_int('RMMap', 'title_fontsize', 12)
RMMAP_TITLE_PAD = _get_int('RMMap', 'title_pad', 50)
RMMAP_MARKER_SHAPE = _get_str('RMMap', 'marker_shape', 'o')
RMMAP_MARKER_EDGE_WIDTH = _get_float('RMMap', 'marker_edge_width', 0.5)
RMMAP_MARKER_EDGE_COLOR = _get_str('RMMap', 'marker_edge_color', 'black')
RMMAP_LEGEND_ALPHA = _get_float('RMMap', 'legend_alpha', 0.4)
RMMAP_LEGEND_FACECOLOR = _get_str('RMMap', 'legend_facecolor', 'white')
RMMAP_LEGEND_MARKER_EDGE_COLOR = _get_str('RMMap', 'legend_marker_edge_color', 'black')
RMMAP_LEGEND_MARKER_FACECOLOR = _get_str('RMMap', 'legend_marker_facecolor_white', 'white')
RMMAP_LEGEND_MARKER_ALPHA = _get_float('RMMap', 'legend_marker_alpha', 0.7)
RMMAP_LEGEND_SIZE_10 = _get_int('RMMap', 'legend_size_10', 10)
RMMAP_LEGEND_SIZE_50 = _get_int('RMMap', 'legend_size_50', 50)
RMMAP_LEGEND_SIZE_100 = _get_int('RMMap', 'legend_size_100', 100)
RMMAP_LEGEND_SIZE_200 = _get_int('RMMap', 'legend_size_200', 200)
RMMAP_NEGATIVE_COLOR = _get_str('RMMap', 'rm_negative_color', 'red')
RMMAP_POSITIVE_COLOR = _get_str('RMMap', 'rm_positive_color', 'blue')

# ============================================================================
# REFERENCE POINTS
# ============================================================================
REFPT_MARKER_SHAPE = _get_str('RefPoints', 'marker_shape', 'o')
REFPT_MARKER_FACECOLOR = _get_str('RefPoints', 'marker_facecolor', 'green')
REFPT_MARKER_EDGE_WIDTH = _get_float('RefPoints', 'marker_edge_width', 0.5)
REFPT_MARKER_EDGE_COLOR = _get_str('RefPoints', 'marker_edge_color', 'black')
REFPT_MARKER_SIZE = _get_int('RefPoints', 'marker_size', 50)
REFPT_LABEL_FONTSIZE = _get_int('RefPoints', 'label_fontsize', 9)
REFPT_LABEL_COLOR = _get_str('RefPoints', 'label_color', 'white')
REFPT_ADJUST_TEXT = _get_bool('RefPoints', 'adjust_text', True)
REFPT_TITLE_FONTSIZE = _get_int('RefPoints', 'title_fontsize', 12)
REFPT_TITLE_PAD = _get_int('RefPoints', 'title_pad', 50)
REFPT_CONTOUR_COLOR = _get_str('RefPoints', 'contour_color', 'black')
REFPT_CONTOUR_LINEWIDTH = _get_float('RefPoints', 'contour_linewidth', 0.5)
REFPT_CONTOUR_ALPHA = _get_float('RefPoints', 'contour_alpha', 0.25)
REFPT_CONTOUR_CMAP = _get_str('RefPoints', 'contour_cmap', 'Greys')

# ============================================================================
# BLOS MAP
# ============================================================================
BLOSMAP_MARKER_SHAPE = _get_str('BLOSMap', 'marker_shape', 'o')
BLOSMAP_MARKER_EDGE_WIDTH = _get_float('BLOSMap', 'marker_edge_width', 0.5)
BLOSMAP_MARKER_EDGE_COLOR = _get_str('BLOSMap', 'marker_edge_color', 'black')
BLOSMAP_CMAP = _get_str('BLOSMap', 'blos_colormap', 'RdBu')
BLOSMAP_REVERSE_CMAP = _get_bool('BLOSMap', 'blos_reverse_cmap', True)
BLOSMAP_TITLE_FONTSIZE = _get_int('BLOSMap', 'title_fontsize', 12)
BLOSMAP_TITLE_PAD = _get_int('BLOSMap', 'title_pad', 50)
BLOSMAP_LEGEND_FONTSIZE = _get_int('BLOSMap', 'legend_fontsize', 13)
BLOSMAP_LEGEND_ALPHA = _get_float('BLOSMap', 'legend_alpha', 0.4)
BLOSMAP_LEGEND_FACECOLOR = _get_str('BLOSMap', 'legend_facecolor', 'white')

# ============================================================================
# PUBLICATION
# ============================================================================
PUB_SHOW_TITLE = _get_bool('Publication', 'show_title', False)
PUB_SHOW_LABELS = _get_bool('Publication', 'show_labels', False)
