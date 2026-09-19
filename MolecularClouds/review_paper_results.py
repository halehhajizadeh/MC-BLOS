"""Reproduce manuscript checks and the OFF-candidate audit from saved results.

Run from MolecularClouds; does not rerun or alter the scientific pipeline.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
from scipy.stats import spearmanr, binomtest

# Match the serif typography and label sizes of the other paper figures.
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'STIXGeneral', 'serif'],
    'mathtext.fontset': 'stix',
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 11,
})

base = Path('FileOutput_ImprovedPlots/Perseus')
tables, plots = base / 'PaperTables', base / 'Plots'
def read(name):
    return pd.read_csv(base / name, sep='\t')

candidates = read('FinalData/AllPotentialRefPoints.csv')
selected = set(read('FinalData/SelectedRefPoints.csv')['ID#'])
near = set(read('IntermediateData/NearHighExtRej.csv')['ID#'])
overlap = set(read('IntermediateData/OverlapRej.csv')['ID#'])
audit = candidates[['ID#', 'Ra(deg)', 'Dec(deg)', 'Rotation_Measure(rad/m2)',
                    'RM_Err(rad/m2)', 'Extinction_Value']].copy()
audit['Status'] = ['Selected OFF' if i in selected else 'Near high extinction' if i in near
                   else 'Separation exclusion' if i in overlap else 'Eligible, not selected'
                   for i in audit['ID#']]
audit.to_csv(tables / 'off_candidate_audit.csv', index=False)
tex = [r'\begin{deluxetable*}{rrrrrrl}', r'\tabletypesize{\scriptsize}',
       r'\tablewidth{0pt}',
       r'\tablecaption{All low-extinction OFF candidates and their selection status.\label{tab:off-audit}}',
       r'\tablehead{\colhead{ID} & \colhead{RA (deg)} & \colhead{Dec (deg)} & \colhead{RM (rad m$^{-2}$)} & \colhead{$\delta$RM (rad m$^{-2}$)} & \colhead{$A_V$ (mag)} & \colhead{Status}}', r'\startdata']
for row in audit.itertuples(index=False, name=None):
    i, ra, dec, rm, err, av, status = row
    tex.append(f'{int(i)} & {ra:.4f} & {dec:.4f} & {rm:.1f} & {err:.1f} & {av:.3f} & {status} ' + r'\\')
tex += [r'\enddata', r'\tablecomments{Coordinates are J2000. IDs are the identifiers in the matched MC-BLOS catalog. Near-high-extinction rejection tests a square extending 20 pixels in each coordinate around a candidate. ID 197 is excluded from OFF selection because it lies within 1.2 arcmin of the preferred candidate 198. Rejection from the OFF sample does not remove an observation from the ON sample. No candidates are rejected by the anomalous-RM filter; the far-cloud filter is disabled.}', r'\end{deluxetable*}']
(tables / 'off_candidate_audit.tex').write_text('\n'.join(tex) + '\n')

fig, ax = plt.subplots(figsize=(8, 4.8), constrained_layout=True)
styles = [('Selected OFF', '#218c45'), ('Eligible, not selected', '#2878b5'),
          ('Near high extinction', '#d45a36'), ('Separation exclusion', '#9553a5')]
for label, color in styles:
    d = audit[audit.Status == label]
    ax.errorbar(d.Extinction_Value, d['Rotation_Measure(rad/m2)'],
                yerr=d['RM_Err(rad/m2)'], fmt='o', color=color, capsize=2,
                label=f'{label} ({len(d)})', ms=6)
    for _, r in d.iterrows():
        offset = {186: (-20, 5), 198: (8, 5), 197: (8, -12),
                  27: (4, -12), 70: (4, -12)}.get(int(r['ID#']), (4, 5))
        ax.annotate(str(int(r['ID#'])), (r.Extinction_Value, r['Rotation_Measure(rad/m2)']),
                    xytext=offset, textcoords='offset points', fontsize=10)
ref = read('FinalData/ReferenceData.csv').iloc[0]
ax.axhline(ref['Reference RM'], color='0.35', ls='--', lw=1)
ax.set(xlabel=r'Visual extinction $A_V$ (mag)', ylabel=r'Observed RM (rad m$^{-2}$)',
       xlim=(.2, 1.07), ylim=(0, 82))
ax.legend(ncol=2, loc='upper left', frameon=False)
for ext in ['pdf', 'png']:
    fig.savefig(plots / f'off_candidate_selection.{ext}', dpi=300)
plt.close(fig)

b = read('FinalData/BLOSPoints.csv')
coords = SkyCoord(b['Ra(deg)'], b['Dec(deg)'], unit='deg')
_, sep, _ = coords.match_to_catalog_sky(coords, nthneighbor=2)
sigma = np.hypot(b.RM_Raw_Err, ref['Reference RM Std'])
sig = abs(b.Scaled_RM) > 2 * sigma
rng = np.random.default_rng(0)
boot = rng.choice(abs(b['Magnetic_Field(uG)']), (10000, len(b)), replace=True)
report = dict(mean_nn_arcmin=float(sep.arcmin.mean()), mean_nn_pc_250=float(sep.radian.mean()*250),
              mean_nn_pc_294=float(sep.radian.mean()*294),
              sign_2sigma_positive=int((sig & (b.Scaled_RM>0)).sum()),
              sign_2sigma_negative=int((sig & (b.Scaled_RM<0)).sum()),
              mean_bootstrap_sd=float(boot.mean(axis=1).std()),
              median_bootstrap_sd=float(np.median(boot, axis=1).std()),
              binomial_p=float(binomtest(int((b.Scaled_RM>0).sum()),len(b)).pvalue))
for name, mask in [('all', np.ones(len(b), dtype=bool)), ('av_le_3', b.Extinction<=3)]:
    rho, p = spearmanr(b.Extinction[mask], abs(b['Magnetic_Field(uG)'][mask]))
    report[name] = dict(n=int(mask.sum()), rho=float(rho), p=float(p))
for sub in ['DensitySensitivity/B_Av_T0_n+50.csv','TemperatureSensitivity/B_Av_T+20_n0.csv']:
    assert b['ID#'].tolist() == read(sub)['ID#'].tolist(), sub
m3 = pd.read_csv(Path('FileOutput_ImprovedPlots_Multiplier3/Perseus/FinalData/BLOSPoints.csv'), sep='\t')
common = b.set_index('ID#').loc[m3['ID#']]
assert np.allclose(common['Magnetic_Field(uG)'], m3['Magnetic_Field(uG)'])
report['multiplier3'] = dict(n=len(m3), positive=int((m3.Scaled_RM>0).sum()),
    negative=int((m3.Scaled_RM<0).sum()), threshold=float(3*ref['Reference Extinction']),
    common_nominal_fields_unchanged=True)
(tables / 'manuscript_checks.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
