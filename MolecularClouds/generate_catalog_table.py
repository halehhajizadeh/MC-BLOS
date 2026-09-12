#!/usr/bin/env python3
"""
Generate the BLOS catalog table for the paper appendix.
"""

import pandas as pd
import numpy as np
import os

# Paths
from LocalLibraries import config
base_dir = config.CloudOutputDir
final_data_dir = os.path.join(base_dir, 'FinalData')
paper_tables_dir = os.environ.get(
    'MCBLOS_PAPER_TABLES_DIR',
    os.path.join(os.path.dirname(__file__), 'PaperTables'),
)
os.makedirs(paper_tables_dir, exist_ok=True)

# Load data
blos_data = pd.read_csv(os.path.join(final_data_dir, 'BLOSPoints.csv'), sep='\t')
final_results = pd.read_csv(os.path.join(final_data_dir, 'FinalBLOSResults.csv'), sep='\t')

# Merge the data
blos_data['TotalUpperBUncertainty'] = final_results['TotalUpperBUncertainty']
blos_data['TotalLowerBUncertainty'] = final_results['TotalLowerBUncertainty']

# Generate LaTeX table (first 20 rows as sample, full table in machine-readable format)
print("="*80)
print("SAMPLE BLOS CATALOG TABLE (first 20 rows)")
print("="*80)

latex_header = r"""
\begin{longtable}{ccccccccc}
\caption{Line-of-sight magnetic field measurements\label{tab:blos-catalog}} \\
\toprule
ID & RA & Dec & $A_V$ & RM$_{\rm obs}$ & $\delta$RM & $B_\parallel$ & $\sigma_{B,+}$ & $\sigma_{B,-}$ \\
 & (deg) & (deg) & (mag) & (rad~m$^{-2}$) & (rad~m$^{-2}$) & ($\mu$G) & ($\mu$G) & ($\mu$G) \\
\midrule
\endfirsthead
\multicolumn{9}{c}{\tablename\ \thetable{} -- continued} \\
\toprule
ID & RA & Dec & $A_V$ & RM$_{\rm obs}$ & $\delta$RM & $B_\parallel$ & $\sigma_{B,+}$ & $\sigma_{B,-}$ \\
 & (deg) & (deg) & (mag) & (rad~m$^{-2}$) & (rad~m$^{-2}$) & ($\mu$G) & ($\mu$G) & ($\mu$G) \\
\midrule
\endhead
\midrule
\multicolumn{9}{r}{Continued on next page} \\
\endfoot
\bottomrule
\endlastfoot
"""

print(latex_header)

# Print first 20 rows
for idx, row in blos_data.head(20).iterrows():
    source_id = row['ID#']
    ra = row['Ra(deg)']
    dec = row['Dec(deg)']
    av = row['Extinction']
    rm_obs = row['RM_Raw_Value']
    rm_err = row['RM_Raw_Err']
    b_par = row['Magnetic_Field(uG)']
    b_upper = row['TotalUpperBUncertainty']
    b_lower = row['TotalLowerBUncertainty']

    print(f"{source_id} & {ra:.4f} & {dec:.4f} & {av:.2f} & {rm_obs:.1f} & {rm_err:.1f} & {b_par:.0f} & {b_upper:.0f} & {b_lower:.0f} \\\\")

print(r"\multicolumn{9}{c}{$\vdots$} \\")
print(r"\end{longtable}")

print("\n" + "="*80)
print("Full catalog saved to CSV for machine-readable format")
print("="*80)

# Save full catalog as CSV
catalog_output = blos_data[['ID#', 'Ra(deg)', 'Dec(deg)', 'Extinction',
                            'RM_Raw_Value', 'RM_Raw_Err', 'Magnetic_Field(uG)',
                            'TotalUpperBUncertainty', 'TotalLowerBUncertainty']].copy()
catalog_output.columns = ['ID', 'RA_deg', 'Dec_deg', 'Av_mag', 'RM_obs_rad_m2',
                          'RM_err_rad_m2', 'B_parallel_uG', 'B_upper_err_uG', 'B_lower_err_uG']

catalog_output.to_csv(os.path.join(paper_tables_dir, 'BLOS_catalog_for_paper.csv'), index=False)
print(f"\nSaved: {os.path.join(paper_tables_dir, 'BLOS_catalog_for_paper.csv')}")

# Also create a short-format LaTeX table for the paper body (sample)
short_table = r"""
\begin{deluxetable*}{ccccccccc}
\tablecaption{Sample of $B_\parallel$ measurements (full table available online)\label{tab:blos-sample}}
\tablewidth{0pt}
\tablehead{
\colhead{ID} & \colhead{RA} & \colhead{Dec} & \colhead{$A_V$} & \colhead{RM$_{\rm obs}$} & \colhead{$\delta$RM} & \colhead{$B_\parallel$} & \colhead{$\sigma_{B,+}$} & \colhead{$\sigma_{B,-}$} \\
\colhead{} & \colhead{(deg)} & \colhead{(deg)} & \colhead{(mag)} & \colhead{(rad~m$^{-2}$)} & \colhead{(rad~m$^{-2}$)} & \colhead{($\mu$G)} & \colhead{($\mu$G)} & \colhead{($\mu$G)}
}
\startdata
"""

for idx, row in blos_data.head(10).iterrows():
    source_id = row['ID#']
    ra = row['Ra(deg)']
    dec = row['Dec(deg)']
    av = row['Extinction']
    rm_obs = row['RM_Raw_Value']
    rm_err = row['RM_Raw_Err']
    b_par = row['Magnetic_Field(uG)']
    b_upper = row['TotalUpperBUncertainty']
    b_lower = row['TotalLowerBUncertainty']

    short_table += f"{source_id} & {ra:.4f} & {dec:.4f} & {av:.2f} & {rm_obs:.1f} & {rm_err:.1f} & {b_par:.0f} & {b_upper:.0f} & {b_lower:.0f} \\\\\n"

short_table += """\\enddata
\\tablecomments{{Column descriptions: (1) Source ID from Paper~I; (2--3) J2000 coordinates; (4) Visual extinction from \\textit{{Herschel}}; (5--6) Observed RM and uncertainty from Paper~I; (7) Line-of-sight magnetic field; (8--9) Asymmetric uncertainties on $B_\\parallel$. The complete table with all {} sources is available in machine-readable format.}}
\\end{{deluxetable*}}
""".format(len(blos_data))

with open(os.path.join(paper_tables_dir, 'blos_sample_table.tex'), 'w') as f:
    f.write(short_table)
print(f"Saved: {os.path.join(paper_tables_dir, 'blos_sample_table.tex')}")

print("\n" + "="*80)
print("CATALOG STATISTICS")
print("="*80)
print(f"Total sources: {len(blos_data)}")
print(f"RA range: {blos_data['Ra(deg)'].min():.3f} to {blos_data['Ra(deg)'].max():.3f} deg")
print(f"Dec range: {blos_data['Dec(deg)'].min():.3f} to {blos_data['Dec(deg)'].max():.3f} deg")
print(f"Extinction range: {blos_data['Extinction'].min():.2f} to {blos_data['Extinction'].max():.2f} mag")
print(f"RM range: {blos_data['RM_Raw_Value'].min():.1f} to {blos_data['RM_Raw_Value'].max():.1f} rad/m²")
print(f"B_parallel range: {blos_data['Magnetic_Field(uG)'].min():.0f} to {blos_data['Magnetic_Field(uG)'].max():.0f} µG")
