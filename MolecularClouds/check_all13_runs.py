"""Verify the two adopted 13-reference runs and write their comparison."""
from pathlib import Path
import json
import hashlib
import shutil
import numpy as np
import pandas as pd

root=Path(__file__).resolve().parent
bases=[root/f'FileOutput_All13_M{m}_D294/Perseus' for m in [1,3]]
read=lambda p,name:pd.read_csv(p/'FinalData'/name,sep='\t')
b1,b3=[read(p,'BLOSPoints.csv').set_index('ID#') for p in bases]
r1,r3=[read(p,'SelectedRefPoints.csv').set_index('ID#') for p in bases]
assert len(r1)==len(r3)==13
pd.testing.assert_frame_equal(r1,r3)
assert set(b3.index).issubset(b1.index)
np.testing.assert_allclose(b1.loc[b3.index,'Magnetic_Field(uG)'],b3['Magnetic_Field(uG)'],rtol=1e-12)
assert np.array_equal(np.sign(b1.loc[b3.index,'Magnetic_Field(uG)']),np.sign(b3['Magnetic_Field(uG)']))
for p in bases:
    f=read(p,'FinalBLOSResults.csv')
    assert not f[['TotalUpperBUncertainty','TotalLowerBUncertainty']].isna().any().any()
comparison=pd.read_csv(root/'All13_M1_vs_M3_comparison.csv').set_index('multiplier')
lines=['# All 13 historical OFF references: multiplier 1 versus 3','',
       'Distance 294 pc. Identical 13 OFF positions and unweighted reference averaging in both runs.','',
       '| Quantity | Multiplier 1 | Multiplier 3 |','|---|---:|---:|']
for label,key in [('ON sources','n_on'),('Reference RM (rad/m²)','reference_rm'),
                  ('Reference RM SEM (rad/m²)','reference_sem'),('ON extinction threshold (mag)','on_threshold'),
                  ('Positive fields','positive'),('Negative fields','negative'),
                  ('Standard deviation of signed B (µG)','std_signed_B'),
                  ('Unbounded extinction uncertainties','unbounded'),('Sources with finite weighting errors','n_weighted')]:
    lines.append('| '+label+' | '+' | '.join(f'{comparison.loc[m,key]:.3f}' if key in ['reference_rm','reference_sem','on_threshold','std_signed_B'] else str(int(comparison.loc[m,key])) for m in [1,3])+' |')
for label,key,error in [('Mean absolute B (µG)','mean_abs_B','mean_bootstrap_sd'),
                        ('Median absolute B (µG)','median_abs_B','median_bootstrap_sd'),
                        ('Error-weighted mean absolute B (µG)','weighted_mean_abs_B','weighted_mean_bootstrap_sd'),
                        ('Error-weighted median absolute B (µG)','weighted_median_abs_B','weighted_median_bootstrap_sd')]:
    lines.append('| '+label+' | '+' | '.join(f'{comparison.loc[m,key]:.2f} ± {comparison.loc[m,error]:.2f}' for m in [1,3])+' |')
lines+=['', 'Errors on means and medians are one bootstrap standard deviation from 10,000 resamples.',
        'These are descriptive sampling errors, excluding shared reference/model systematics and spatial covariance.',
        'Error weights use the inverse square of the average upper/lower uncertainty; unbounded values are excluded.',
        f'All {len(b3)} multiplier-3 sources are a subset of multiplier 1. Their nominal fields and signs agree.',
        'The historical 13-point set was explicitly retained; the automatic 294-pc filter would allow 15 separated points.']
text='\n'.join(lines)+'\n'
for p in bases:
    bundle=p/'All_Figures_and_Tables'
    manifest=p/'PaperTables/input_sha256.json'
    hashes=json.loads(manifest.read_text())
    for name in ['configStartSettings.ini','configDirectoryAndNames.ini','configConstants.ini']:
        hashes.pop(name,None)
        cfg=p.parent/'RunConfig'/name
        hashes[str(cfg.relative_to(root))]=hashlib.sha256(cfg.read_bytes()).hexdigest()
    helper=root/'LocalLibraries/MatchedRMExtinctionFunctions.py'
    hashes[str(helper.relative_to(root))]=hashlib.sha256(helper.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(hashes,indent=2)+'\n')
    for folder in ['Plots','PaperTables','FinalData','IntermediateData','DensitySensitivity','TemperatureSensitivity','Logs']:
        for path in (p/folder).iterdir():
            if path.is_file():
                prefixed=bundle/(folder+'__'+path.name)
                dest=prefixed if prefixed.exists() else bundle/path.name
                shutil.copy2(path,dest)
    (bundle/'All13_M1_vs_M3_comparison.md').write_text(text)
    report=dict(reference_count=13,identical_references=True,multiplier3_subset=True,
                common_nominal_fields_equal=True,uncertainty_tables_without_nans=True,
                pdf_figures=len(list((p/'Plots').glob('*.pdf'))),
                latex_tables=len(list((p/'PaperTables').glob('*.tex'))))
    (bundle/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    hashes={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in bundle.iterdir() if q.is_file() and q.name!='bundle_sha256.json'}
    (bundle/'bundle_sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
print(text)
