#!/usr/bin/env python3
"""
Generate two versions of the stability trend plot:
1. Representative subset (~25 sources)
2. Summary statistics (median + shaded percentile region)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pathlib import Path
from LocalLibraries import config
from LocalLibraries.RegionOfInterest import Region
from LocalLibraries.OptimalRefPoints import findTrendData
from LocalLibraries.RefJudgeLib import separateReferencePoints

# Set publication quality font settings
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'STIXGeneral', 'serif']
plt.rcParams['mathtext.fontset'] = 'stix'

# Load the trend data
trend_data_path = config.StabilityTrendDataTablePath
matched = pd.read_csv(config.MatchedRMExtinctionFile, sep=config.dataSeparator)
candidates = pd.read_csv(config.FilteredRefPointsFile, sep=config.dataSeparator)
separated, _ = separateReferencePoints(candidates, config.minRefSeparationArcmin)
separated = separated.reset_index(drop=True)
selected = pd.read_csv(config.ChosenRefPointFile, sep=config.dataSeparator)
if set(separated.head(len(selected))['ID#']) != set(selected['ID#']):
    raise ValueError('Paper stability plot requires the selected references to lead the separated candidate sequence.')
trend_data = findTrendData(separated, matched, Region(config.cloud))
total_trends = len(trend_data)
# Use the same finite sight lines at every N so gaps or changing samples do not
# distort the summary bands or truncate the last columns of the figure.
trend_data = trend_data.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
if trend_data.empty:
    raise ValueError('No sight lines have finite fields across the reference-count sequence.')
print(f'Paper stability summary: {len(trend_data)} sight lines valid at every N '
      f'({total_trends - len(trend_data)} incomplete trends excluded).')
trend_data.to_csv(Path(config.CloudIntermediateDataDir) / 'PaperStabilityTrend.csv', sep=config.dataSeparator)

# Get the optimal number of reference points (N=8)
optimal_n = len(pd.read_csv(config.ChosenRefPointFile, sep=config.dataSeparator))
plots_dir = Path(config.CloudPlotsDir)

x = [int(col) for col in trend_data.columns]

# ============== OPTION 1: Representative Subset ==============
print("Creating Option 1: Representative subset plot...")

fig1, ax1 = plt.subplots(figsize=(8, 5), dpi=300, facecolor='w', edgecolor='k')

# Get final BLOS values and select representative subset
final_values = trend_data.iloc[:, -1].values

# Select ~25 sources spanning the range of final BLOS values
n_subset = 25
sorted_indices = np.argsort(final_values)
step = max(1, len(sorted_indices) // n_subset)
selected_indices = sorted_indices[::step][:n_subset]

# Plot selected sources
for idx in selected_indices:
    y_vals = trend_data.iloc[idx].values
    final_val = y_vals[-1]

    if final_val > 0:
        color = 'blue'
    elif final_val < 0:
        color = 'red'
    else:
        color = 'gray'

    ax1.plot(x, y_vals, '-', color=color, alpha=0.6, linewidth=1.2)

# Add vertical line at optimal N
ax1.axvline(x=optimal_n, color='black', linestyle='--', linewidth=1.5)

# Add horizontal line at y=0
ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)

# Labels and formatting
ax1.set_xlabel('Number of reference points', fontsize=16)
ax1.set_ylabel(r'$B_\parallel$ ($\mu$G)', fontsize=16)
ax1.tick_params(axis='both', which='major', labelsize=14)
ax1.set_xticks(x)

# Legend
legend_elements = [
    Line2D([0], [0], color='blue', alpha=0.7, linewidth=1.5, label=r'Positive $B_\parallel$'),
    Line2D([0], [0], color='red', alpha=0.7, linewidth=1.5, label=r'Negative $B_\parallel$'),
    Line2D([0], [0], color='black', linestyle='--', linewidth=1.5, label=f'Selected N = {optimal_n}')
]
ax1.legend(handles=legend_elements, loc='upper right', fontsize=11)

plt.tight_layout()
plt.savefig(plots_dir / 'stability_option1_subset.pdf', format='pdf', bbox_inches='tight')
plt.savefig(plots_dir / 'stability_option1_subset.png', bbox_inches='tight')
plt.close()

print(f"  Saved: stability_option1_subset.pdf (showing {n_subset} representative sources)")

# ============== OPTION 2: Summary Statistics ==============
print("Creating Option 2: Summary statistics plot...")

fig2, ax2 = plt.subplots(figsize=(8, 5), dpi=300, facecolor='w', edgecolor='k')

# Calculate statistics for each number of reference points
median_vals = []
p25_vals = []
p75_vals = []
p10_vals = []
p90_vals = []

for col in trend_data.columns:
    vals = trend_data[col].values
    median_vals.append(np.median(vals))
    p25_vals.append(np.percentile(vals, 25))
    p75_vals.append(np.percentile(vals, 75))
    p10_vals.append(np.percentile(vals, 10))
    p90_vals.append(np.percentile(vals, 90))

# Plot shaded regions
ax2.fill_between(x, p10_vals, p90_vals, alpha=0.2, color='steelblue', label='10th-90th percentile')
ax2.fill_between(x, p25_vals, p75_vals, alpha=0.4, color='steelblue', label='25th-75th percentile')

# Plot median line
ax2.plot(x, median_vals, '-', color='darkblue', linewidth=2.5, label='Median')

# Add vertical line at optimal N
ax2.axvline(x=optimal_n, color='black', linestyle='--', linewidth=1.5, label=f'Selected N = {optimal_n}')

# Add horizontal line at y=0
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)

# Labels and formatting
ax2.set_xlabel('Number of reference points', fontsize=16)
ax2.set_ylabel(r'$B_\parallel$ ($\mu$G)', fontsize=16)
ax2.tick_params(axis='both', which='major', labelsize=14)
ax2.set_xticks(x)

# Legend
ax2.legend(loc='upper right', fontsize=11)

plt.tight_layout()
plt.savefig(plots_dir / 'stability_option2_summary.pdf', format='pdf', bbox_inches='tight')
plt.savefig(plots_dir / 'stability_option2_summary.png', bbox_inches='tight')
plt.savefig(plots_dir / 'BLOS_stability_trend.pdf', format='pdf', bbox_inches='tight')
plt.savefig(plots_dir / 'BLOS_stability_trend.png', bbox_inches='tight')
plt.close()

print(f"  Saved: stability_option2_summary.pdf (median + percentile bands)")

print("\nDone! Compare the two PDFs:")
print("  - stability_option1_subset.pdf: 25 representative sources")
print("  - stability_option2_summary.pdf: median with shaded percentile regions")
