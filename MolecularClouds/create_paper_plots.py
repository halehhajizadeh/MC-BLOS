#!/usr/bin/env python3
"""
Create additional publication-quality plots for the Perseus B_LOS paper.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import os

# Set publication-quality plot parameters
rcParams['font.family'] = 'serif'
rcParams['font.size'] = 12
rcParams['axes.labelsize'] = 14
rcParams['axes.titlesize'] = 14
rcParams['xtick.labelsize'] = 12
rcParams['ytick.labelsize'] = 12
rcParams['legend.fontsize'] = 11
rcParams['figure.dpi'] = 150
rcParams['savefig.dpi'] = 300
rcParams['text.usetex'] = False

# Paths
from LocalLibraries import config
base_dir = config.CloudOutputDir
final_data_dir = os.path.join(base_dir, 'FinalData')
plots_dir = os.path.join(base_dir, 'Plots')
paper_tables_dir = os.environ.get(
    'MCBLOS_PAPER_TABLES_DIR',
    os.path.join(base_dir, 'PaperTables'),
)
os.makedirs(paper_tables_dir, exist_ok=True)

# Load data - use BLOSPoints.csv for full data including RM columns
blos_data = pd.read_csv(os.path.join(final_data_dir, 'BLOSPoints.csv'), sep='\t')
final_results = pd.read_csv(os.path.join(final_data_dir, 'FinalBLOSResults.csv'), sep='\t')
ref_data = pd.read_csv(os.path.join(final_data_dir, 'ReferenceData.csv'), sep='\t')
selected_ref = pd.read_csv(os.path.join(final_data_dir, 'SelectedRefPoints.csv'), sep='\t')
zeeman_file = os.path.join(paper_tables_dir, 'zeeman_comparison.csv')
zeeman_data = pd.read_csv(zeeman_file)

# Extract values
B_parallel = blos_data['Magnetic_Field(uG)'].values
extinction = blos_data['Extinction'].values
ra = blos_data['Ra(deg)'].values
dec = blos_data['Dec(deg)'].values
rm_raw = blos_data['RM_Raw_Value'].values
rm_scaled = blos_data['Scaled_RM'].values
upper_err = final_results['TotalUpperBUncertainty'].values
lower_err = final_results['TotalLowerBUncertainty'].values

# Reference values
rm_ref = ref_data['Reference RM'].values[0]
rm_ref_sem = ref_data['Reference RM Std'].values[0]
rm_ref_std = selected_ref['Rotation_Measure(rad/m2)'].std(ddof=1)
n_ref = len(selected_ref)
n_matched = len(pd.read_csv(config.MatchedRMExtinctionFile, sep=config.dataSeparator))
av_ref = ref_data['Reference Extinction'].values[0]

print("="*60)
print("SUMMARY STATISTICS FOR PAPER")
print("="*60)
print(f"\nReference RM: {rm_ref:.1f} ± {rm_ref_sem:.1f} rad/m² (std: {rm_ref_std:.1f})")
print(f"Reference Extinction: {av_ref:.2f} mag")
print(f"Number of ON points: {len(B_parallel)}")
print(f"\nB_parallel statistics:")
print(f"  Range: {B_parallel.min():.1f} to {B_parallel.max():.1f} µG")
print(f"  Mean |B_parallel|: {np.abs(B_parallel).mean():.1f} µG")
print(f"  Median |B_parallel|: {np.median(np.abs(B_parallel)):.1f} µG")
print(f"  Std: {np.std(B_parallel):.1f} µG")
print(f"\nField direction:")
positive = np.sum(B_parallel > 0)
negative = np.sum(B_parallel < 0)
print(f"  Positive (toward): {positive} ({100*positive/len(B_parallel):.1f}%)")
print(f"  Negative (away): {negative} ({100*negative/len(B_parallel):.1f}%)")
print(f"\nExtinction range: {extinction.min():.2f} to {extinction.max():.2f} mag")
print(f"Mean extinction: {extinction.mean():.2f} mag")

# ==============================================================================
# PLOT 1: Histogram of B_parallel values
# ==============================================================================
from matplotlib.ticker import MaxNLocator, MultipleLocator
with plt.rc_context({'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
                     'mathtext.fontset': 'stix'}):
    fig, ax = plt.subplots(figsize=(8, 5))
    # Fixed-width bins with zero on a bin edge; retain the entire field range.
    bin_width = 50.0
    extent = bin_width * np.ceil(np.max(np.abs(B_parallel)) / bin_width)
    bins = np.arange(-extent, extent + bin_width, bin_width)
    counts, _ = np.histogram(B_parallel, bins=bins)
    assert counts.sum() == len(B_parallel)
    ax.hist(B_parallel[B_parallel < 0], bins=bins, color='#c65b52',
            edgecolor='white', linewidth=0.65,
            label=rf'Away ($B_\parallel<0$): {negative}')
    ax.hist(B_parallel[B_parallel >= 0], bins=bins, color='#397bb5',
            edgecolor='white', linewidth=0.65,
            label=rf'Toward ($B_\parallel>0$): {positive}')
    ax.axvline(0, color='0.25', linestyle='--', linewidth=1.1)
    ax.set_xlabel(r'$B_\parallel$ ($\mu$G)')
    ax.set_ylabel('Number of sources')
    ax.set_xlim(-extent, extent)
    ax.set_ylim(0, counts.max() * 1.28)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.xaxis.set_major_locator(MultipleLocator(250))
    ax.set_axisbelow(True)
    ax.grid(axis='y', color='0.92', linewidth=0.7)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(direction='out')
    ax.legend(loc='upper right', frameon=False)
    ax.text(0.025, 0.96, f'{len(B_parallel)} ON sources\n'
            + r'Bin width: 50 $\mu$G', transform=ax.transAxes,
            va='top', fontsize=11, color='0.25')

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'BLOS_histogram.png'), bbox_inches='tight')
plt.savefig(os.path.join(plots_dir, 'BLOS_histogram.pdf'), bbox_inches='tight')
plt.close()
print("\nSaved: BLOS_histogram.png/pdf")

# ==============================================================================
# PLOT 2: B_parallel vs Extinction with error bars
# ==============================================================================
fig, ax = plt.subplots(figsize=(10, 7))

# Color by sign
pos_mask = B_parallel > 0
neg_mask = B_parallel < 0

# Plot with asymmetric error bars
ax.errorbar(extinction[pos_mask], B_parallel[pos_mask],
            yerr=[lower_err[pos_mask], upper_err[pos_mask]],
            fmt='o', color='royalblue', markersize=6, alpha=0.6,
            ecolor='lightblue', elinewidth=1, capsize=0,
            label=r'$B_\parallel > 0$ (toward observer)')

ax.errorbar(extinction[neg_mask], B_parallel[neg_mask],
            yerr=[lower_err[neg_mask], upper_err[neg_mask]],
            fmt='o', color='firebrick', markersize=6, alpha=0.6,
            ecolor='lightcoral', elinewidth=1, capsize=0,
            label=r'$B_\parallel < 0$ (away from observer)')

ax.axhline(0, color='black', linestyle='--', linewidth=1.5, alpha=0.7)
ax.axvline(av_ref, color='green', linestyle=':', linewidth=2, alpha=0.7,
           label=f'$A_V$ ref = {av_ref:.2f} mag')

ax.set_xlabel(r'Visual Extinction $A_V$ (mag)')
ax.set_ylabel(r'$B_\parallel$ (µG)')
ax.set_title('Line-of-Sight Magnetic Field vs. Extinction')
ax.legend(loc='upper right')
ax.set_xlim(0, 16)
ax.set_ylim(-1000, 1000)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'BLOS_vs_Av.png'), bbox_inches='tight')
plt.savefig(os.path.join(plots_dir, 'BLOS_vs_Av.pdf'), bbox_inches='tight')
plt.close()
print("Saved: BLOS_vs_Av.png/pdf")

# ==============================================================================
# PLOT 3: RM_observed vs RM_cloud (after subtraction)
# ==============================================================================
fig, ax = plt.subplots(figsize=(10, 7))

rm_cloud = rm_raw - rm_ref  # Cloud contribution

# Color by sign
pos_rm = rm_cloud > 0
neg_rm = rm_cloud < 0

ax.scatter(rm_raw[pos_rm], rm_cloud[pos_rm], c='royalblue', s=40, alpha=0.6,
           label=r'$\mathrm{RM_{cloud}} > 0$', edgecolors='navy', linewidths=0.5)
ax.scatter(rm_raw[neg_rm], rm_cloud[neg_rm], c='firebrick', s=40, alpha=0.6,
           label=r'$\mathrm{RM_{cloud}} < 0$', edgecolors='darkred', linewidths=0.5)

# Add 1:1 line shifted by RM_ref
x_line = np.linspace(-50, 100, 100)
ax.plot(x_line, x_line - rm_ref, 'k--', linewidth=1.5, alpha=0.5,
        label=f'$RM_{{cloud}} = RM_{{obs}} - {rm_ref:.1f}$')

ax.axhline(0, color='gray', linestyle=':', linewidth=1, alpha=0.7)
ax.axvline(rm_ref, color='green', linestyle=':', linewidth=2, alpha=0.7,
           label=f'$RM_{{ref}}$ = {rm_ref:.1f} rad/m²')

ax.set_xlabel(r'$\mathrm{RM_{observed}}$ (rad m$^{-2}$)')
ax.set_ylabel(r'$\mathrm{RM_{cloud}}$ (rad m$^{-2}$)')
ax.set_title('Observed RM vs. Cloud RM Contribution')
ax.legend(loc='upper left')
ax.set_xlim(-50, 100)
ax.set_ylim(-80, 70)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'RM_observed_vs_cloud.png'), bbox_inches='tight')
plt.savefig(os.path.join(plots_dir, 'RM_observed_vs_cloud.pdf'), bbox_inches='tight')
plt.close()
print("Saved: RM_observed_vs_cloud.png/pdf")

# ==============================================================================
# PLOT 4: |B_parallel| vs Extinction (log scale)
# ==============================================================================
fig, ax = plt.subplots(figsize=(10, 7))

abs_B = np.abs(B_parallel)

# Color by sign
ax.scatter(extinction[pos_mask], abs_B[pos_mask], c='royalblue', s=50, alpha=0.6,
           label=r'$B_\parallel > 0$ (toward)', edgecolors='navy', linewidths=0.5)
ax.scatter(extinction[neg_mask], abs_B[neg_mask], c='firebrick', s=50, alpha=0.6,
           label=r'$B_\parallel < 0$ (away)', edgecolors='darkred', linewidths=0.5)

ax.set_xlabel(r'Visual Extinction $A_V$ (mag)')
ax.set_ylabel(r'$|B_\parallel|$ (µG)')
ax.set_title('Magnetic Field Strength vs. Extinction')
ax.set_yscale('log')
ax.set_xlim(0, 16)
ax.set_ylim(1, 5000)
ax.legend(loc='upper right')

# Add horizontal lines for reference
ax.axhline(np.median(abs_B), color='green', linestyle='--', linewidth=1.5,
           label=f'Median = {np.median(abs_B):.0f} µG')

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'BLOS_abs_vs_Av_log.png'), bbox_inches='tight')
plt.savefig(os.path.join(plots_dir, 'BLOS_abs_vs_Av_log.pdf'), bbox_inches='tight')
plt.close()
print("Saved: BLOS_abs_vs_Av_log.png/pdf")

# ==============================================================================
# PLOT 5: Spatial distribution with field direction
# ==============================================================================
fig, ax = plt.subplots(figsize=(12, 8))

# Size proportional to |B_parallel|, capped for visualization
size_scale = np.clip(np.abs(B_parallel) / 10, 10, 200)

# Plot positive (toward) and negative (away) separately
scatter_pos = ax.scatter(ra[pos_mask], dec[pos_mask],
                         s=size_scale[pos_mask], c='royalblue',
                         alpha=0.6, edgecolors='navy', linewidths=0.5,
                         label=r'$B_\parallel > 0$ (toward)')
scatter_neg = ax.scatter(ra[neg_mask], dec[neg_mask],
                         s=size_scale[neg_mask], c='firebrick',
                         alpha=0.6, edgecolors='darkred', linewidths=0.5,
                         label=r'$B_\parallel < 0$ (away)')

# Plot reference points
ref_ra = selected_ref['Ra(deg)'].values
ref_dec = selected_ref['Dec(deg)'].values
ax.scatter(ref_ra, ref_dec, s=100, c='green', marker='s',
           edgecolors='darkgreen', linewidths=1.5, zorder=5,
           label='Reference points')

# Published OH Zeeman pointings in Perseus.
ax.scatter(zeeman_data['Ra(deg)'], zeeman_data['Dec(deg)'],
           s=np.clip(np.abs(zeeman_data['B'].values) * 3, 60, 180),
           c='blue', marker='*', edgecolors='white', linewidths=0.7,
           zorder=8, label='OH Zeeman pointings')
for _, row in zeeman_data.iterrows():
    ax.annotate(row['Region'], (row['Ra(deg)'], row['Dec(deg)']),
                xytext=(5, 5), textcoords='offset points', fontsize=9,
                color='navy', zorder=9)

ax.set_xlabel('Right Ascension (deg)')
ax.set_ylabel('Declination (deg)')
ax.set_title(r'Spatial Distribution of $B_\parallel$ in Perseus')
ax.invert_xaxis()  # RA increases to the left
ax.legend(loc='lower left')

# Add size legend
for size_val in [50, 200, 500]:
    ax.scatter([], [], s=size_val/10, c='gray', alpha=0.5,
               label=f'{size_val} µG')

ax.legend(loc='lower left', ncol=2)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'BLOS_spatial_distribution.png'), bbox_inches='tight')
plt.savefig(os.path.join(plots_dir, 'BLOS_spatial_distribution.pdf'), bbox_inches='tight')
plt.close()
print("Saved: BLOS_spatial_distribution.png/pdf")

# ==============================================================================
# Generate LaTeX table for reference points
# ==============================================================================
print("\n" + "="*60)
print("REFERENCE POINTS TABLE (LaTeX format)")
print("="*60)

ref_table_latex = r"""
\begin{deluxetable*}{cccccc}
\tablecaption{Selected reference (OFF) points\label{tab:reference-points}}
\tablewidth{0pt}
\tablehead{
\colhead{ID} & \colhead{RA} & \colhead{Dec} & \colhead{RM} & \colhead{$\delta$RM} & \colhead{$A_V$} \\
\colhead{} & \colhead{(deg)} & \colhead{(deg)} & \colhead{(rad~m$^{-2}$)} & \colhead{(rad~m$^{-2}$)} & \colhead{(mag)}
}
\startdata
"""

for idx, row in selected_ref.iterrows():
    ra_val = row['Ra(deg)']
    dec_val = row['Dec(deg)']
    rm_val = row['Rotation_Measure(rad/m2)']
    rm_err = row['RM_Err(rad/m2)']
    av_val = row['Extinction_Value']
    source_id = row['ID#']

    ref_table_latex += f"{source_id} & {ra_val:.3f} & {dec_val:.3f} & {rm_val:.1f} & {rm_err:.1f} & {av_val:.2f} \\\\\n"

ref_table_latex += r"""\enddata
\tablecomments{The """ + str(n_ref) + r""" reference points selected with stability analysis and spatial separation. The reference RM is """ + f"{rm_ref:.1f}" + r""" $\pm$ """ + f"{rm_ref_sem:.1f}" + r"""~rad~m$^{-2}$ (standard deviation """ + f"{rm_ref_std:.1f}" + r"""~rad~m$^{-2}$).}
\end{deluxetable*}
"""

print(ref_table_latex)

# Save table to file
with open(os.path.join(paper_tables_dir, 'reference_points_table.tex'), 'w') as f:
    f.write(ref_table_latex)
print(f"\nSaved: reference_points_table.tex")

# ==============================================================================
# Generate summary statistics table
# ==============================================================================
print("\n" + "="*60)
print("SUMMARY STATISTICS TABLE (LaTeX format)")
print("="*60)

stats_table = r"""
\begin{table}[htbp]
\centering
\caption{Line-of-sight magnetic field summary statistics}
\label{tab:blos-summary}
\begin{tabular}{lc}
\toprule
Parameter & Value \\
\midrule
Total RM sources matched & """ + f"{n_matched}" + r""" \\
Reference (OFF) points & """ + f"{n_ref}" + r""" \\
ON points (cloud sight lines) & """ + f"{len(B_parallel)}" + r""" \\
\midrule
Reference RM (rad~m$^{-2}$) & $""" + f"{rm_ref:.1f}" + r""" \pm """ + f"{rm_ref_sem:.1f}" + r"""$ \\
Reference RM std.\ dev.\ (rad~m$^{-2}$) & """ + f"{rm_ref_std:.1f}" + r""" \\
Reference $A_V$ (mag) & """ + f"{av_ref:.2f}" + r""" \\
\midrule
$B_\parallel$ range ($\mu$G) & """ + f"{B_parallel.min():.0f}" + r""" to """ + f"{B_parallel.max():.0f}" + r""" \\
Mean $|B_\parallel|$ ($\mu$G) & """ + f"{np.mean(np.abs(B_parallel)):.0f}" + r""" \\
Median $|B_\parallel|$ ($\mu$G) & """ + f"{np.median(np.abs(B_parallel)):.0f}" + r""" \\
Std.\ dev.\ ($\mu$G) & """ + f"{np.std(B_parallel):.0f}" + r""" \\
\midrule
Positive $B_\parallel$ (toward) & """ + f"{positive} ({100*positive/len(B_parallel):.0f}" + r"""\%) \\
Negative $B_\parallel$ (away) & """ + f"{negative} ({100*negative/len(B_parallel):.0f}" + r"""\%) \\
\midrule
ON-point $A_V$ range (mag) & """ + f"{extinction.min():.2f}" + r""" to """ + f"{extinction.max():.2f}" + r""" \\
Mean ON-point $A_V$ (mag) & """ + f"{extinction.mean():.2f}" + r""" \\
\bottomrule
\end{tabular}
\end{table}
"""

print(stats_table)

with open(os.path.join(paper_tables_dir, 'summary_statistics_table.tex'), 'w') as f:
    f.write(stats_table)
print(f"\nSaved: summary_statistics_table.tex")

print("\n" + "="*60)
print("ALL PLOTS AND TABLES GENERATED SUCCESSFULLY")
print("="*60)
