#!/usr/bin/env python3
"""
Generate the COMPLETE BLOS catalog table for the paper (all 197 sources).
"""

import pandas as pd
import numpy as np
import os

# Paths
from LocalLibraries import config
base_dir = config.CloudOutputDir
final_data_dir = os.path.join(base_dir, 'FinalData')

# Load data
blos_data = pd.read_csv(os.path.join(final_data_dir, 'BLOSPoints.csv'), sep='\t')
final_results = pd.read_csv(os.path.join(final_data_dir, 'FinalBLOSResults.csv'), sep='\t')

# Merge the data
blos_data['TotalUpperBUncertainty'] = final_results['TotalUpperBUncertainty']
blos_data['TotalLowerBUncertainty'] = final_results['TotalLowerBUncertainty']

# Generate FULL LaTeX longtable for all 197 sources
print("Generating full BLOS catalog table (197 sources)...")

latex_table = r"""\begin{longtable}{ccccccccc}
\caption{Complete catalog of line-of-sight magnetic field measurements toward the Perseus Molecular Cloud. Columns: (1) Source ID from Paper~I; (2--3) J2000 equatorial coordinates; (4) Visual extinction from \textit{Herschel}; (5--6) Observed rotation measure and uncertainty from Paper~I; (7) Derived line-of-sight magnetic field; (8--9) Upper and lower uncertainties on $B_\parallel$, which include contributions from RM measurement error, reference RM uncertainty, extinction uncertainty, and chemical model sensitivity.\label{tab:blos-catalog}} \\
\toprule
ID & RA & Dec & $A_V$ & RM$_{\rm obs}$ & $\delta$RM & $B_\parallel$ & $\sigma_{B,+}$ & $\sigma_{B,-}$ \\
 & (deg) & (deg) & (mag) & (rad~m$^{-2}$) & (rad~m$^{-2}$) & ($\mu$G) & ($\mu$G) & ($\mu$G) \\
\midrule
\endfirsthead
\multicolumn{9}{c}{\tablename\ \thetable{} -- continued from previous page} \\
\toprule
ID & RA & Dec & $A_V$ & RM$_{\rm obs}$ & $\delta$RM & $B_\parallel$ & $\sigma_{B,+}$ & $\sigma_{B,-}$ \\
 & (deg) & (deg) & (mag) & (rad~m$^{-2}$) & (rad~m$^{-2}$) & ($\mu$G) & ($\mu$G) & ($\mu$G) \\
\midrule
\endhead
\midrule
\multicolumn{9}{r}{\textit{Continued on next page}} \\
\endfoot
\bottomrule
\endlastfoot
"""

# Add ALL rows
for idx, row in blos_data.iterrows():
    source_id = int(row['ID#'])
    ra = row['Ra(deg)']
    dec = row['Dec(deg)']
    av = row['Extinction']
    rm_obs = row['RM_Raw_Value']
    rm_err = row['RM_Raw_Err']
    b_par = row['Magnetic_Field(uG)']
    b_upper = row['TotalUpperBUncertainty']
    b_lower = row['TotalLowerBUncertainty']

    latex_table += f"{source_id} & {ra:.4f} & {dec:.4f} & {av:.2f} & {rm_obs:.1f} & {rm_err:.1f} & {b_par:.0f} & {b_upper:.0f} & {b_lower:.0f} \\\\\n"

latex_table += r"\end{longtable}"

# Save the full table
output_file = os.path.join(final_data_dir, 'blos_full_catalog_table.tex')
with open(output_file, 'w') as f:
    f.write(latex_table)

print(f"Saved complete catalog table to: {output_file}")
print(f"Total rows: {len(blos_data)}")
