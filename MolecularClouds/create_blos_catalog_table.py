#!/usr/bin/env python3
"""
Generate LaTeX longtable for the full BLOS catalog
"""
import pandas as pd

# Read the BLOS results
df = pd.read_csv('FileOutput/Perseus/FinalData/FinalBLOSResults.csv', sep='\t')

# Create LaTeX longtable
latex_lines = []
latex_lines.append(r"\begin{longtable}{ccccccc}")
latex_lines.append(r"\caption{Complete catalog of line-of-sight magnetic field measurements\label{tab:blos-catalog}} \\")
latex_lines.append(r"\hline")
latex_lines.append(r"ID & RA & Dec & $A_V$ & $B_\parallel$ & $\delta B_\parallel^+$ & $\delta B_\parallel^-$ \\")
latex_lines.append(r" & (deg) & (deg) & (mag) & ($\mu$G) & ($\mu$G) & ($\mu$G) \\")
latex_lines.append(r"\hline")
latex_lines.append(r"\endfirsthead")
latex_lines.append(r"")
latex_lines.append(r"\multicolumn{7}{c}{\tablename\ \thetable\ -- Continued from previous page} \\")
latex_lines.append(r"\hline")
latex_lines.append(r"ID & RA & Dec & $A_V$ & $B_\parallel$ & $\delta B_\parallel^+$ & $\delta B_\parallel^-$ \\")
latex_lines.append(r" & (deg) & (deg) & (mag) & ($\mu$G) & ($\mu$G) & ($\mu$G) \\")
latex_lines.append(r"\hline")
latex_lines.append(r"\endhead")
latex_lines.append(r"")
latex_lines.append(r"\hline")
latex_lines.append(r"\multicolumn{7}{r}{Continued on next page} \\")
latex_lines.append(r"\endfoot")
latex_lines.append(r"")
latex_lines.append(r"\hline")
latex_lines.append(r"\endlastfoot")
latex_lines.append(r"")

# Add data rows
for idx, row in df.iterrows():
    line = f"{int(row['ID#'])} & {row['Ra(deg)']:.4f} & {row['Dec(deg)']:.4f} & {row['Extinction']:.2f} & {row['Magnetic_Field(uG)']:.1f} & {int(row['TotalUpperBUncertainty'])} & {int(row['TotalLowerBUncertainty'])} \\\\"
    latex_lines.append(line)

latex_lines.append(r"\end{longtable}")

# Write to file
with open('blos_catalog_table.tex', 'w') as f:
    f.write('\n'.join(latex_lines))

print(f"Created LaTeX table with {len(df)} rows")
print("Output file: blos_catalog_table.tex")
print("\nTable statistics:")
print(f"  Mean |B_parallel|: {df['Magnetic_Field(uG)'].abs().mean():.1f} μG")
print(f"  Median |B_parallel|: {df['Magnetic_Field(uG)'].abs().median():.1f} μG")
print(f"  Range: {df['Magnetic_Field(uG)'].min():.1f} to {df['Magnetic_Field(uG)'].max():.1f} μG")
