#!/usr/bin/env python3
"""
Create an interactive HTML version of the RM map where hovering shows source IDs
Uses proper celestial coordinates (RA/Dec in degrees)
"""
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
import LocalLibraries.config as config
from LocalLibraries.RegionOfInterest import Region

# Load the region
cloudName = config.cloud
regionOfInterest = Region(cloudName)

# Load matched data
matched_data = pd.read_csv(config.MatchedRMExtinctionFile, sep=config.dataSeparator)

# Load extinction data and WCS
hdu = regionOfInterest.hdu
extinction_data = hdu.data
wcs = regionOfInterest.wcs

# Get the Perseus cloud bounds from regionOfInterest
xmin = int(regionOfInterest.xmin) if not np.isnan(regionOfInterest.xmin) else 0
xmax = int(regionOfInterest.xmax) if not np.isnan(regionOfInterest.xmax) else extinction_data.shape[1]
ymin = int(regionOfInterest.ymin) if not np.isnan(regionOfInterest.ymin) else 0
ymax = int(regionOfInterest.ymax) if not np.isnan(regionOfInterest.ymax) else extinction_data.shape[0]

# Crop extinction data to Perseus region
extinction_cropped = extinction_data[ymin:ymax, xmin:xmax]

# Create RA/Dec coordinate arrays for the cropped region only
ny_crop, nx_crop = extinction_cropped.shape
x_grid, y_grid = np.meshgrid(np.arange(xmin, xmax), np.arange(ymin, ymax))
ra_grid, dec_grid = wcs.all_pix2world(x_grid, y_grid, 0)

# Create figure with proper coordinate system
fig = go.Figure()

# Add cropped extinction map with RA/Dec coordinates
fig.add_trace(go.Heatmap(
    x=ra_grid[0, :],  # RA along x-axis
    y=dec_grid[:, 0],  # Dec along y-axis
    z=extinction_cropped,  # Use cropped data
    colorscale='Hot',  # Matches matplotlib 'hot'
    zmin=0,  # Fixed minimum value
    zmax=15,  # Fixed maximum value
    colorbar=dict(
        title=dict(
            text='A<sub>V</sub>',
            side='right',
            font=dict(family='serif', size=14)
        ),
        len=0.75,  # Match matplotlib colorbar length
        thickness=15,  # Thinner to match matplotlib
        x=1.01,
        y=0.5,
        yanchor='middle',
        tickfont=dict(family='serif', size=12),
        tickmode='auto',
        nticks=8
    ),
    hoverinfo='skip',
    name='Extinction Map'
))

# Add scatter points with RA/Dec coordinates directly
fig.add_trace(go.Scatter(
    x=matched_data['Ra(deg)'],
    y=matched_data['Dec(deg)'],
    mode='markers',
    marker=dict(
        size=8,
        color='lime',
        line=dict(color='black', width=1)
    ),
    text=[f"<b>ID: {int(id)}</b><br>RA: {ra:.4f}°<br>Dec: {dec:.4f}°<br>A<sub>V</sub>: {av:.2f} mag<br>RM: {rm:.1f} rad/m²"
          for id, ra, dec, av, rm in zip(
              matched_data['ID#'],
              matched_data['Ra(deg)'],
              matched_data['Dec(deg)'],
              matched_data['Extinction_Value'],
              matched_data['Rotation_Measure(rad/m2)']
          )],
    hovertemplate='%{text}<extra></extra>',
    name='RM Sources'
))

# Calculate proper aspect ratio for the Perseus region
ra_range = ra_grid[0, :].max() - ra_grid[0, :].min()
dec_range = dec_grid[:, 0].max() - dec_grid[:, 0].min()

# Match the PNG/PDF figure size: 8x8 inches at 300 DPI = 2400x2400 pixels
# But scale down for web viewing
fig_size = 960  # Square figure like PNG/PDF

# Update layout with proper celestial coordinates focused on Perseus
fig.update_layout(
    title=dict(
        text='',  # No title (clean like PDF)
        font=dict(family='serif', size=20, color='black')
    ),
    xaxis=dict(
        title=dict(text='RA (degree)', font=dict(family='serif', size=16)),
        showgrid=True,
        gridcolor='rgba(255,255,255,0.5)',
        gridwidth=1,
        autorange='reversed',  # RA increases to the left
        range=[ra_grid[0, -1], ra_grid[0, 0]],  # Exact bounds from data (reversed for RA)
        tickfont=dict(family='serif', size=14),
        showline=True,
        linewidth=2,
        linecolor='black',
        mirror=True,
        constrain='domain'
    ),
    yaxis=dict(
        title=dict(text='Dec (degree)', font=dict(family='serif', size=16)),
        showgrid=True,
        gridcolor='rgba(255,255,255,0.5)',
        gridwidth=1,
        range=[dec_grid[0, 0], dec_grid[-1, 0]],  # Exact bounds from data
        tickfont=dict(family='serif', size=14),
        showline=True,
        linewidth=2,
        linecolor='black',
        mirror=True,
        scaleanchor='x',
        constrain='domain'
    ),
    width=fig_size,
    height=fig_size,
    hovermode='closest',
    plot_bgcolor='black',
    paper_bgcolor='white',
    font=dict(family='serif', size=14),
    margin=dict(l=80, r=140, t=50, b=80)
)

# Save interactive HTML
output_file = 'figures/AllRMPtsInRegion_interactive.html'
fig.write_html(output_file)
print(f"✅ Created interactive map: {output_file}")
print(f"   Region: RA {ra_grid[0, :].min():.2f}° to {ra_grid[0, :].max():.2f}°, Dec {dec_grid[:, 0].min():.2f}° to {dec_grid[:, 0].max():.2f}°")
print(f"   Styling: Hot colormap (vmin=0, vmax=15), serif fonts, {fig_size}×{fig_size}px (square like PDF)")
print(f"   Open in browser to hover over points and see IDs.")
