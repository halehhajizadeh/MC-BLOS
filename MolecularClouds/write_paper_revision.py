"""Regenerate paper tables only; never overwrite the authored manuscript."""
from pathlib import Path
import json
import re
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
from LocalLibraries import config
OUT=Path(config.CloudOutputDir)
TABLES=OUT/'PaperTables'
FINAL=OUT/'FinalData'
s=json.loads((TABLES/'analysis_summary.json').read_text())
b=pd.read_csv(FINAL/'catalog_with_flags.csv')
f=pd.read_csv(FINAL/'FinalBLOSResults.csv',sep='\t')
m=pd.read_csv(TABLES/'faraday_matches.csv')
z=pd.read_csv(TABLES/'zeeman_comparison.csv')

def table(name, columns, caption, header, rows, notes, long=False):
    notes = notes.replace('same 197 ON positions', f"same {s['n']} ON positions")
    notes = notes.replace('eight OFF points', f"{s['reference_count']} OFF points")
    notes = notes.replace('eight-point scalar reference', f"{s['reference_count']}-point scalar reference")
    notes = notes.replace('ID 205 has interpolated extinction.', 'Interpolated extinction is identified in the machine-readable catalog.')
    notes = notes.replace('Source 55, nearest both L1448 pointings, has F2=1.', 'Nearest source IDs and flags are listed in the machine-readable comparison.')
    notes = notes.replace('archived extinction-weighted line fit', 'current extinction-weighted line fit')
    if s.get('on_point_multiplier') == 3:
        notes = notes.replace('The $m=3$ row changes sample membership only;', 'The All and $m=3$ rows coincide for this run;')
    if name in {'faraday_difference_budget.tex', 'foreground_comparison.tex'}:
        long = True
    if not long:
        lines=[r'\begin{table*}[!t]',r'\centering',r'\caption{'+caption+'}',
               r'\scriptsize',r'\begin{tabular}{'+columns+'}',r'\toprule',
               header+r' \\',r'\midrule']
        lines+=[' & '.join(row)+r' \\' for row in rows]
        lines += [r'\bottomrule',r'\end{tabular}',r'\par\smallskip',
                  r'\begin{minipage}{0.97\textwidth}\scriptsize '+notes+r'\end{minipage}',
                  r'\end{table*}']
        (TABLES/name).write_text('\n'.join(lines)+'\n')
        return
    lines=([r'\startlongtable'] if long else [])+[r'\begin{deluxetable*}{'+columns+'}',
        r'\tabletypesize{\scriptsize}',r'\tablewidth{0pt}',r'\tablecaption{'+caption+'}',
        r'\tablehead{'+header+'}',r'\startdata']
    lines += [' & '.join(row)+r' \\' for row in rows]
    lines += [r'\enddata',r'\tablecomments{'+notes+'}',r'\end{deluxetable*}']
    (TABLES/name).write_text('\n'.join(lines)+'\n')

def number(x):
    if np.isnan(x):
        raise ValueError('Undefined field or excursion in paper table')
    return r'$\infty$' if not np.isfinite(x) else f'{x:.1f}'

assert set(b['ID#'])==set(f['ID#'])
np.testing.assert_allclose(b['Magnetic_Field(uG)'], f.set_index('ID#').loc[b['ID#'],'Magnetic_Field(uG)'])
np.testing.assert_allclose(m['VLA_Magnetic_Field(uG)'], b.set_index('ID#').loc[m.VLA_ID,'Magnetic_Field(uG)'])
cat=b.merge(f[['ID#','TotalUpperBUncertainty','TotalLowerBUncertainty']],on='ID#',validate='one_to_one')
cat.to_csv(FINAL/'BLOS_catalog_for_paper.csv',index=False)
cat.to_csv(TABLES/'BLOS_catalog_for_paper.csv',index=False)
rows=[]
for _,r in cat.iterrows():
    rows.append([str(int(r['ID#'])),f'{r["Ra(deg)"]:.4f}',f'{r["Dec(deg)"]:.4f}',f'{r.Extinction:.2f}',
        f'{r.RM_Raw_Value:.2f}',f'{r.RM_Raw_Err:.3f}',number(r['Magnetic_Field(uG)']),
        number(r.TotalUpperBUncertainty),number(r.TotalLowerBUncertainty),
        '--' if r.F1<0 else str(int(r.F1)), '--' if r.F2<0 else str(int(r.F2))])
table('blos_full_catalog_table.tex','rrrrrrrrrrr',
 r'Line-of-sight field estimates for the published Paper I sample.\label{tab:blos-catalog}',
 r'\colhead{ID} & \colhead{RA (deg)} & \colhead{Dec (deg)} & \colhead{$A_V$} & \colhead{RM} & \colhead{$\delta$RM} & \colhead{$B_\parallel$} & \colhead{$\Delta B_+$} & \colhead{$\Delta B_-$} & \colhead{F1} & \colhead{F2}',rows,
 r'Coordinates are J2000/ICRS. Units: extinction in mag, RM in rad m$^{-2}$, fields in $\mu$G. F1/F2 are Paper I quality flags. Infinity denotes unbounded sensitivity, not a nominal infinite field. ID 205 has interpolated extinction. See Appendix~\ref{app:catalog} and Section~\ref{sec:catalog-provenance} for definitions and membership.',long=True)
table('blos_sample_table.tex','rrrrrrrrrrr',
 r'Sample of the field catalog.\label{tab:blos-sample}',
 r'\colhead{ID} & \colhead{RA (deg)} & \colhead{Dec (deg)} & \colhead{$A_V$} & \colhead{RM} & \colhead{$\delta$RM} & \colhead{$B_\parallel$} & \colhead{$\Delta B_+$} & \colhead{$\Delta B_-$} & \colhead{F1} & \colhead{F2}',rows[:10],
 r'The full machine-readable table provides source identifiers and flags. Units and uncertainty conventions follow the complete catalog.')
rows=[]
for _,r in m.iterrows():
    rows.append([str(int(r.Literature_ID)),str(int(r.VLA_ID)),f'{r.separation_arcsec:.2f}',
      f'{r.RM:.1f}',f'{r.VLA_RM_Raw_Value:.2f}',f'{r.B:.0f}',f'{r["VLA_Magnetic_Field(uG)"]:.1f}',
      f'{r.RM_residual_sigma:.2f}',f'{int(r.VLA_F1)}/{int(r.VLA_F2)}'])
table('faraday_comparison.tex','rrrrrrrrr',r'Positional matches to the Perseus measurements of \citet{tahani2018}.\label{tab:faraday-comparison}',
 r'\colhead{2018 ID} & \colhead{Local ID} & \colhead{Sep. ($^{\prime\prime}$)} & \colhead{RM$_{09}$} & \colhead{RM$_{\rm VLA}$} & \colhead{$B_{18}$} & \colhead{$B_{\rm VLA}$} & \colhead{$z_{\rm RM}$} & \colhead{F1/F2}',rows,
 r'RM is in rad m$^{-2}$ and field in $\mu$G. Original Table 6 positions were associated with the Taylor catalog within $30\arcsec$, verifying agreement of the tabulated RMs to their rounding precision; those full-precision coordinates were matched to VLA positions within $10\arcsec$. All accepted separations are below $2.2\arcsec$. $z_{\rm RM}$ uses the quadrature sum of the two catalog measurement errors, excluding cross-survey systematics. Full asymmetric field excursions and source identifiers are provided in the machine-readable table. These are positional associations; source structure can differ between surveys.')
rows=[]
for _,r in z.iterrows():
    rows.append([r.Region,f'{r["Ra(deg)"]:.5f}',f'{r["Dec(deg)"]:.5f}',f'{r.B:.1f} $\\pm$ {r.Error:.1f}',
        f'{r.FWHM_arcmin:.1f}',str(int(r.nearest_ID)),f'{r.separation_arcmin:.2f}',f'{r.VLA_B:.1f}'])
table('zeeman_comparison.tex','lrrrrrrr',r'Local comparison with Arecibo OH Zeeman measurements.\label{tab:zeeman-comparison}',
 r'\colhead{Region} & \colhead{RA (deg)} & \colhead{Dec (deg)} & \colhead{$B_Z$ ($\mu$G)} & \colhead{FWHM ($\prime$)} & \colhead{Local ID} & \colhead{Sep. ($\prime$)} & \colhead{$B_{\rm VLA}$ ($\mu$G)}',rows,
 r'Positive fields point toward the observer. B1 uses the original B1950 pointing in Figure 1 of \citet{goodman1989measurement}, transformed to ICRS. L1448 coordinates and strengths are from Tables 1 and 2 of \citet{troland2008magnetic}. FWHM is the beam diameter. None of the nearest VLA sight lines lies within the half-power radius. Source 55, nearest both L1448 pointings, has F2=1. These are regional comparisons, not measurements through identical gas.')
rows=[]
for r in s['regions']:
    rows.append([r['sample'].replace('F1=0,F2=0','F1=F2=0'),r['side'],str(r['n']),str(r['positive']),str(r['negative']),str(r['positive_2sigma']),str(r['negative_2sigma'])])
table('spatial_comparison.tex','llrrrrr',r'Field directions on either side of the extinction-derived axis.\label{tab:spatial-comparison}',
 r'\colhead{Sample} & \colhead{Side} & \colhead{$N$} & \colhead{$B>0$} & \colhead{$B<0$} & \colhead{$S>2$} & \colhead{$S<-2$}',rows,
 r'The axis is the archived extinction-weighted line fit, independent of RM signs. North and south label the positive and negative pixel-$y$ offsets from this line. $S$ is defined in Equation~\ref{eq:sign-score}. All rows retain the same eight-point scalar reference. The $m=3$ row changes sample membership only; the quality cut excludes nonzero flags.')


# Ordered replacement budget; the order is stated explicitly in the manuscript.
d=pd.read_csv(TABLES/'faraday_difference_budget.csv')
rows=[]
for _,r in d.iterrows():
    rows.append([str(int(r.Literature_ID)),f'{r.Ne_ratio_new_old:.3f}',
                 f'{r.delta_B_observed_RM:.1f}',f'{r.delta_B_reference_RM:.1f}',
                 f'{r.delta_B_electron_column:.1f}',f'{r.delta_B_total:.1f}'])
table('faraday_difference_budget.tex','rrrrrr',
 r'Ordered decomposition of matched field differences.\label{tab:difference-budget}',
 r'\colhead{2018 ID} & \colhead{$N_{e,\rm VLA}/N_{e,18}$} & \colhead{$\Delta B_{\rm RM}$} & \colhead{$\Delta B_{\rm ref}$} & \colhead{$\Delta B_{N_e}$} & \colhead{$\Delta B_{\rm total}$}',rows,
 r'Changes are in $\mu$G. Starting from the published field, replace the observed RM, then the reference RM, then the electron column. The three signed contributions sum to the total change; their allocation depends on this order. The earlier electron column is reconstructed from rounded published cloud RMs and fields, not a rerun of the earlier chemical model.')
rows=[]
for r in s['observed_rm_contrast']:
    rows.append([r['sample'],r['weighting'],str(r['n_north']),str(r['n_south']),
                 f"{r['delta']:.2f}",f"[{r['bootstrap_low']:.2f}, {r['bootstrap_high']:.2f}]"])
table('observed_rm_contrast.tex','llrrrr',
 r'Regional observed-RM contrast.\label{tab:rm-contrast}',
 r'\colhead{Sample} & \colhead{Weighting} & \colhead{$N_N$} & \colhead{$N_S$} & \colhead{$\Delta\langle\mathrm{RM}\rangle$} & \colhead{Bootstrap range}',rows,
 r'RM is in rad m$^{-2}$. Ranges are the 2.5th--97.5th percentiles of 10,000 resamples within each region, not spatial-null probabilities. Proximity groups are connected components with links shorter than $1.2\arcmin$; each group receives equal weight and groups crossing the axis are omitted. This is a geometric sensitivity test, not an identification of independent physical sources.')
rows=[]
for r in s['foreground_comparison']:
    rows.append([r['model'],r['subset'],str(r['n']),str(r['changed_signs']),
                 f"{r['delta_mean_cloud_rm']:.2f}",f"{r['delta_positive_fraction']:.3f}"])
table('foreground_comparison.tex','llrrrr',
 r'Sensitivity to the non-cloud RM model.\label{tab:foreground}',
 r'\colhead{Model} & \colhead{Subset} & \colhead{$N$} & \colhead{Sign changes} & \colhead{$\Delta\langle\mathrm{RM}_{\rm cloud}\rangle$} & \colhead{$\Delta f_+$}',rows,
 r'Changes are relative to the adopted scalar reference, on the same 197 ON positions before alternative extinction cuts. RM differences are in rad m$^{-2}$. The plane is an unweighted fit to eight OFF points; it is a sensitivity diagnostic. Inside/outside refers to their convex hull. Clean means F1=F2=0. These model comparisons do not give probabilities that any foreground model is correct.')
# A minimal summary table for readers and downstream checks.
rows=[[label,value] for label,value in [
 ('ON estimates',str(s['n'])),('Positive / negative',f"{s['positive']} / {s['negative']}"),
 (r'Median $|B_\parallel|$ ($\mu$G)',f"{s['median_abs_B']:.2f}"),
 (r'Mean $|B_\parallel|$ ($\mu$G)',f"{s['mean_abs_B']:.2f}"),
 ('Unbounded extinction excursions',str(s['unbounded_extinction']))]]
table('summary_statistics_table.tex','lr',r'Nominal field summary.\label{tab:summary}',r'Quantity & Value',rows,
 r'Summary statistics describe nominal model-dependent estimates; no total systematic confidence interval is implied.')
print('Updated paper tables and machine-readable catalog in the standard output folders.')

(FINAL/'summary_statistics_table.tex').write_text((TABLES/'summary_statistics_table.tex').read_text())
