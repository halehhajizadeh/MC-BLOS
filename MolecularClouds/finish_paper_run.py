"""Finish a configured pipeline run and collect all paper products together.

Run after stages 01--03 and revise_paper_analysis.py have succeeded.
"""
from pathlib import Path
import os
import subprocess
import sys
import shutil
import json
import hashlib
from itertools import combinations
import pandas as pd
import numpy as np
from LocalLibraries import config
from LocalLibraries.MatchedRMExtinctionFunctions import calcFiducialVals

ROOT = Path(__file__).resolve().parent
BASE = Path(config.CloudOutputDir)
os.environ['MPLBACKEND'] = 'Agg'
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/mcblos-mpl')

def run(script, *args):
    print('Running', script, *args, flush=True)
    with (BASE / 'Logs' / (Path(script).stem + ('_' + '_'.join(args) if args else '') + '.log')).open('w') as log:
        subprocess.run([sys.executable, script, *args], cwd=ROOT,
                       stdout=log, stderr=subprocess.STDOUT, check=True)

def preserve(names, tag):
    for name in names:
        for ext in ['png', 'pdf']:
            path = BASE / 'Plots' / f'{name}.{ext}'
            if path.exists():
                shutil.copy2(path, path.with_name(f'{name}_{tag}.{ext}'))

preserve(['BLOSPointMap', 'BLOS_histogram', 'stability_option2_summary'], 'diagnostic')
for script in ['04CalculateBLOS.py', '05aDensitySensitivity.py', '05bDensitySensitivityPlot.py',
               '06aTempSensitivity.py', '06bTempSensitivityPlot.py', '07UncertaintyAnalysis.py']:
    run(script)
shutil.copy2(BASE/'FinalData/FinalBLOSResults.csv', BASE/'FinalData/FinalBLOSResults_stage07.tsv')
preserve(['BLOSPointMap'], 'pipeline')
# Restore the full paper uncertainty prescription and source-aligned sensitivities.
run('revise_paper_analysis.py')
run('create_paper_plots_pdf.py')
preserve(['BLOS_histogram','BLOS_vs_Av','RM_observed_vs_cloud',
          'BLOS_abs_vs_Av_log','BLOS_spatial_distribution'], 'alternative')
for script in ['create_paper_plots.py','create_stability_plots.py',
               '04b_BLOS_OverlapHighlight.py','plot_perseus_tahani.py',
               'review_paper_results.py','write_paper_revision.py']:
    run(script)
run('04CalculateBLOS.py','--zeeman-only')
run('04CalculateBLOS.py','--zeeman-only','--sign-secure')
run('04CalculateBLOS.py','--zeeman-only','--uncertainty-100')

# Generate the complete combination metadata for the existing two sensitivity
# figures without rendering thousands of animation frames.
candidates = pd.read_csv(config.FilteredRefPointsFile, sep=config.dataSeparator)
matched = pd.read_csv(config.MatchedRMExtinctionFile, sep=config.dataSeparator)
refs = pd.read_csv(config.ChosenRefPointFile, sep=config.dataSeparator)
rows = []
for frame, indices in enumerate(combinations(range(len(candidates)), len(refs)), 1):
    ref = candidates.iloc[list(indices)]
    rm, err, sem, av = calcFiducialVals(ref)
    limit = config.onPtsExtMultipleThreshold * av
    keep = ~matched['ID#'].isin(ref['ID#']) & (matched.Extinction_Value >= limit)
    rows.append(dict(frame=frame, reference_ids=','.join(map(str,ref['ID#'])),
        reference_rm=rm, reference_rm_avg_err=err, reference_rm_sem=sem,
        reference_extinction=av, on_point_extinction_limit=limit, n_blos_points=int(keep.sum())))
combdir = Path(config.FileOutputDir) / 'Perseus_test'
combdir.mkdir(exist_ok=True)
pd.DataFrame(rows).to_csv(combdir/'reference_combinations.csv', index=False)
run('08aAnalyzeReferenceMovie.py')

bundle = BASE / 'All_Figures_and_Tables'
bundle.mkdir(exist_ok=True)
sources = []
for folder in [BASE/'Plots', BASE/'PaperTables', BASE/'FinalData', BASE/'Logs',
               BASE/'IntermediateData', BASE/'DensitySensitivity', BASE/'TemperatureSensitivity',
               combdir/'statistics', combdir,
               BASE.parent/'Perseus_SignSecure/Plots', BASE.parent/'Perseus_Uncertainty100/Plots',
               BASE.parent/'Perseus_SignSecure/FinalData', BASE.parent/'Perseus_Uncertainty100/FinalData']:
    for path in sorted(folder.glob('*')):
        if path.is_file() and path.suffix in {'.png','.pdf','.csv','.tsv','.tex','.json','.npz','.txt','.log'}:
            dest = bundle/path.name
            if dest.exists() and dest.read_bytes()!=path.read_bytes():
                dest=bundle/('__'.join(path.relative_to(BASE.parent).parts))
            shutil.copy2(path,dest)
            sources.append(dict(file=dest.name, source=str(path.relative_to(BASE.parent)),
                                sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
pd.DataFrame(sources).to_csv(bundle/'file_manifest.csv',index=False)
for path in [ROOT/'configStartSettings.ini',ROOT/'configDirectoryAndNames.ini',
             ROOT/'configConstants.ini',ROOT/'Data/CloudParameters/perseus.ini']:
    shutil.copy2(path,bundle/path.name)
b = pd.read_csv(BASE/'FinalData/BLOSPoints.csv',sep='\t')
f = pd.read_csv(BASE/'FinalData/FinalBLOSResults.csv',sep='\t')
assert b['ID#'].tolist()==f['ID#'].tolist()
assert (b.Extinction>=config.onPtsExtMultipleThreshold*refs.Extinction_Value.mean()).all()
assert np.isfinite(b['Magnetic_Field(uG)']).all()
old=ROOT/'FileOutput_ImprovedPlots/Perseus'
for folder, suffixes in [('Plots',{'.png','.pdf'}),('PaperTables',{'.csv','.tex','.json'})]:
    missing=[p.name for p in (old/folder).iterdir() if p.suffix in suffixes and not (bundle/p.name).exists()]
    assert not missing, (folder,missing)
summary=json.loads((BASE/'PaperTables/analysis_summary.json').read_text())
readme=f'''Paper run: Perseus, distance 294 pc, ON multiplier {config.onPtsExtMultipleThreshold:g}.

All figures and tables are together in this directory. PDF and PNG versions
are supplied; CSV/TSV files contain data and TEX files contain paper tables.
The manifest maps each file to its source and SHA-256 checksum.

ON sample: {len(b)}; references: {len(refs)}.
ON threshold: {config.onPtsExtMultipleThreshold*refs.Extinction_Value.mean():.9f} mag.
Reference RM: {summary['reference_rm']:.9f} rad/m^2.
Reference SEM: {summary['reference_sem']:.9f} rad/m^2.
Positive/negative fields: {summary['positive']}/{summary['negative']}.

The primary catalog uses the published Paper I cross-match and the existing
paper uncertainty prescription (combine_uncertainties). The original stage-07
uncertainties are separately labeled FinalBLOSResults_stage07.tsv.
Alternative plot styles and filtered samples have explicit filename suffixes.
Sensitivity tables include all density and temperature perturbations.
The reference-combination figures use all {len(rows)} combinations of the
filtered pool before the separation exclusion; the eligible-pool diagnostics
are reported separately. Animation frames were not requested or generated.
The All and m=3 diagnostic rows coincide because this run already adopts m=3.
Source IDs are assigned by matching and can differ from older runs; use Source
and sky coordinates for cross-run associations. No manuscript text was changed.
'''
(bundle/'README.txt').write_text(readme)
print(readme,flush=True)
print('BUNDLE:',bundle,flush=True)
