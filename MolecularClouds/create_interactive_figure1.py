#!/usr/bin/env python3
"""
Create interactive HTML version of Figure 1 for ApJ online publication.
This creates a Plotly figure with hover tooltips showing source IDs.
"""
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS

from LocalLibraries.RegionOfInterest import Region
import LocalLibraries.config as config

print("Creating interactive figure for ApJ online edition...")

# Load the region
cloudName = config.cloud
regionOfInterest = Region(cloudName)

# Load the data
matched_data = pd.read_csv(config.MatchedRMExtinctionFile, sep=config.dataSeparator)
ref_points = pd.read_csv('FileOutput/Perseus/FinalData/SelectedRefPoints.csv', sep='\t')
blos_data = pd.read_csv('FileOutput/Perseus/FinalData/FinalBLOSResults.csv', sep='\t')

# Merge data
on_points = matched_data[~matched_data['ID#'].isin(ref_points['ID#'])]
on_with_blos = on_points.merge(blos_data[['ID#', 'Magnetic_Field(uG)', 'Extinction']],
                                 on='ID#', how='left')

# Get extinction map data
ext_data = regionOfInterest.hdu.data
wcs = WCS(regionOfInterest.hdu.header)

# Create world coordinates for the extinction map
ny, nx = ext_data.shape
x_idx, y_idx = np.meshgrid(np.arange(nx), np.arange(ny))
ra_grid, dec_grid = wcs.all_pix2world(x_idx, y_idx, 0)

# Create Plotly figure
fig = go.Figure()

# Add extinction map as heatmap
fig.add_trace(go.Heatmap(
    x=ra_grid[0,:],  # RA along x-axis
    y=dec_grid[:,0],  # Dec along y-axis
    z=ext_data,
    colorscale='BrBG',
    colorbar=dict(title='A<sub>V</sub> (mag)', x=1.02),
    hovertemplate='RA: %{x:.3f}°<br>Dec: %{y:.3f}°<br>A<sub>V</sub>: %{z:.2f}<extra></extra>',
    name='Extinction'
))

# Separate ON points by sign
positive_mask = on_with_blos['Magnetic_Field(uG)'] > 0
negative_mask = on_with_blos['Magnetic_Field(uG)'] < 0

# Add positive B_parallel points (blue)
if positive_mask.sum() > 0:
    pos_data = on_with_blos[positive_mask]
    fig.add_trace(go.Scatter(
        x=pos_data['Ra(deg)'],
        y=pos_data['Dec(deg)'],
        mode='markers',
        marker=dict(size=8, color='#0066CC', line=dict(width=0.5, color='black')),
        name='Positive B∥',
        hovertemplate=(
            '<b>ID: %{customdata[0]}</b><br>' +
            'RA: %{x:.4f}°<br>' +
            'Dec: %{y:.4f}°<br>' +
            'B∥: %{customdata[1]:.1f} μG<br>' +
            'A<sub>V</sub>: %{customdata[2]:.2f} mag' +
            '<extra></extra>'
        ),
        customdata=np.column_stack((
            pos_data['ID#'].values,
            pos_data['Magnetic_Field(uG)'].values,
            pos_data['Extinction'].values
        ))
    ))

# Add negative B_parallel points (red)
if negative_mask.sum() > 0:
    neg_data = on_with_blos[negative_mask]
    fig.add_trace(go.Scatter(
        x=neg_data['Ra(deg)'],
        y=neg_data['Dec(deg)'],
        mode='markers',
        marker=dict(size=8, color='#CC0000', line=dict(width=0.5, color='black')),
        name='Negative B∥',
        hovertemplate=(
            '<b>ID: %{customdata[0]}</b><br>' +
            'RA: %{x:.4f}°<br>' +
            'Dec: %{y:.4f}°<br>' +
            'B∥: %{customdata[1]:.1f} μG<br>' +
            'A<sub>V</sub>: %{customdata[2]:.2f} mag' +
            '<extra></extra>'
        ),
        customdata=np.column_stack((
            neg_data['ID#'].values,
            neg_data['Magnetic_Field(uG)'].values,
            neg_data['Extinction'].values
        ))
    ))

# Add reference points (green)
fig.add_trace(go.Scatter(
    x=ref_points['Ra(deg)'],
    y=ref_points['Dec(deg)'],
    mode='markers',
    marker=dict(size=12, color='#00CC00', line=dict(width=1, color='black')),
    name='Reference (OFF) points',
    hovertemplate=(
        '<b>REF ID: %{customdata[0]}</b><br>' +
        'RA: %{x:.4f}°<br>' +
        'Dec: %{y:.4f}°<br>' +
        'RM: %{customdata[1]:.1f} rad m<sup>-2</sup><br>' +
        'A<sub>V</sub>: %{customdata[2]:.2f} mag' +
        '<extra></extra>'
    ),
    customdata=np.column_stack((
        ref_points['ID#'].values,
        ref_points['RM'].values,
        ref_points['Av'].values
    ))
))

# Update layout
fig.update_layout(
    xaxis_title='RA (degrees)',
    yaxis_title='Dec (degrees)',
    font=dict(family='Times New Roman, serif', size=14),
    width=1000,
    height=800,
    hovermode='closest',
    plot_bgcolor='white',
    paper_bgcolor='white',
    legend=dict(
        x=1.02,
        y=1,
        bgcolor='rgba(255,255,255,0.9)',
        bordercolor='black',
        borderwidth=1
    )
)

# Reverse x-axis (RA increases to the left in astronomy)
fig.update_xaxes(autorange='reversed', showgrid=True, gridcolor='lightgray')
fig.update_yaxes(showgrid=True, gridcolor='lightgray')

# Save as interactive HTML
output_html = 'figures/AllRMPtsInRegion_interactive.html'
fig.write_html(output_html)
print(f"Saved interactive HTML figure to: {output_html}")

# Also save a standalone version that can be embedded
output_html_standalone = 'figures/AllRMPtsInRegion_interactive_standalone.html'
fig.write_html(output_html_standalone, include_plotlyjs='cdn')
print(f"Saved standalone HTML to: {output_html_standalone}")

print("\nInteractive figure created!")
print("When you hover over points, you'll see:")
print("  - Source ID number")
print("  - RA, Dec coordinates")
print("  - B_parallel value (for ON points)")
print("  - RM value (for reference points)")
print("  - Extinction value")
print("\nFor ApJ submission:")
print("  1. Include the static PNG/PDF in the main paper")
print("  2. Submit the interactive HTML as supplementary material")
print("  3. ApJ will host it as a 'Figure Set' with interactive viewing online")
