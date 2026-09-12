#!/usr/bin/env python3
"""
Generate the complete BLOS catalog table for the paper.
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

# Generate FULL LaTeX longtable for all 197 sources
print("Generating full BLOS catalog table...")

latex_table = r"""\startlongtable
\begin{deluxetable*}{rrrrrrrrr}
\tabletypesize{\scriptsize}
\tablewidth{0pt}
\tablecaption{Complete catalog of line-of-sight magnetic field measurements toward Perseus.\label{tab:blos-catalog}}
\tablehead{
\colhead{ID} & \colhead{RA} & \colhead{Dec} & \colhead{$A_V$} &
\colhead{RM$_{\rm obs}$} & \colhead{$\delta$RM} & \colhead{$B_\parallel$} &
\colhead{$\sigma_{B,+}$} & \colhead{$\sigma_{B,-}$} \\
\colhead{} & \colhead{(deg)} & \colhead{(deg)} & \colhead{(mag)} &
\colhead{(rad m$^{-2}$)} & \colhead{(rad m$^{-2}$)} &
\colhead{($\mu$G)} & \colhead{($\mu$G)} & \colhead{($\mu$G)}
}
\startdata
"""

# Add ALL rows
for row_number, (_, row) in enumerate(blos_data.iterrows()):
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

latex_table += r"""\enddata
\tablecomments{Coordinates are J2000. Extinction is from \textit{Herschel}.
RM and its uncertainty are observed values. The final two columns give the
upper and lower field uncertainties, including RM measurement, reference RM,
extinction, and chemical model contributions.}
\end{deluxetable*}
"""

# Save the full table
output_file = os.path.join(paper_tables_dir, 'blos_full_catalog_table.tex')
with open(output_file, 'w') as f:
    f.write(latex_table)

print(f"Saved complete catalog table to: {output_file}")
print(f"Total rows: {len(blos_data)}")
