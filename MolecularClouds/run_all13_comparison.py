"""Run m=1 and m=3 with the historical 13 separated OFF positions, at 294 pc.

Each subprocess reads its own configuration snapshot; global settings are untouched.
"""
from pathlib import Path
from configparser import ConfigParser
import os
import sys
import subprocess
import shutil
import json
import hashlib
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
from LocalLibraries.RefJudgeLib import separateReferencePoints

ROOT=Path(__file__).resolve().parent
historical=ROOT/'FileOutput_ImprovedPlots/Perseus/IntermediateData/FilteredPotRefPoints.csv'
requested,_=separateReferencePoints(pd.read_csv(historical,sep='\t'),1.2)
assert len(requested)==13
env=dict(os.environ,MPLBACKEND='Agg',MPLCONFIGDIR='/private/tmp/mcblos-mpl')
summary=[]

for multiplier in [1,3]:
    runroot=ROOT/f'FileOutput_All13_M{multiplier}_D294'
    runroot.mkdir(exist_ok=False)
    cfg=runroot/'RunConfig'
    cfg.mkdir()
    for name in ['configStartSettings.ini','configDirectoryAndNames.ini','configConstants.ini']:
        shutil.copy2(ROOT/name,cfg/name)
    shutil.copy2(ROOT/'Data/CloudParameters/perseus.ini',cfg/'perseus.ini')
    c=ConfigParser();c.read(cfg/'configStartSettings.ini')
    c['Judgement - On Point Extinction Multiple of Off Point Average Multiplier']['on point extinction multiple of off point average multiplier']=str(multiplier)
    c['Judgement - Optimal Reference Points']['find optimal reference points']='False'
    c['Judgement - Cloud Quadrant Sampling']['weighting scheme']='None'
    c['Judgement - User Judgement']['use manual user selection of reference points']='False'
    with (cfg/'configStartSettings.ini').open('w') as f:c.write(f)
    c=ConfigParser();c.read(cfg/'configDirectoryAndNames.ini')
    c['Output Directories']['file output']=runroot.name
    with (cfg/'configDirectoryAndNames.ini').open('w') as f:c.write(f)
    base=runroot/'Perseus'
    def run(script,*args):
        print(f'm={multiplier}: {script} '+ ' '.join(args),flush=True)
        logdir=runroot/'ExecutionLogs';logdir.mkdir(exist_ok=True)
        with (logdir/(Path(script).stem+'_'+'_'.join(args)+'.log')).open('w') as f:
            subprocess.run([sys.executable,str(ROOT/script),*args],cwd=cfg,env=env,
                           stdout=f,stderr=subprocess.STDOUT,check=True)
    for script in ['01MakeDir.py','02aRMMatching.py','02bRMMapping.py','03aFilterReferencePoints.py']:
        run(script)
    matched=pd.read_csv(base/'FinalData/MatchedRMExtinction.csv',sep='\t')
    sky=lambda d:SkyCoord(d['Ra(deg)'],d['Dec(deg)'],unit='deg')
    indices,sep,_=sky(requested).match_to_catalog_sky(sky(matched))
    assert sep.arcsec.max()<.1 and len(set(indices))==13
    fixed=matched.iloc[indices].sort_values('Extinction_Value').reset_index(drop=True)
    candidatefile=base/'IntermediateData/FilteredPotRefPoints.csv'
    current=pd.read_csv(candidatefile,sep='\t')
    assert set(fixed['ID#']).issubset(set(current['ID#']))
    shutil.copy2(candidatefile,candidatefile.with_name('AutomaticFilteredPotRefPoints.csv'))
    fixed.to_csv(candidatefile,sep='\t',index=False)
    audit=requested[['ID#','Ra(deg)','Dec(deg)']].copy()
    audit['current_ID']=matched.iloc[indices]['ID#'].to_numpy()
    audit['match_arcsec']=sep.arcsec
    audit.to_csv(runroot/'Requested13_reference_crossmatch.csv',index=False)
    for script in ['03bConsiderReferencePoints.py','03cMapReferencePoints.py']:
        run(script)
    selected=pd.read_csv(base/'FinalData/SelectedRefPoints.csv',sep='\t')
    assert len(selected)==13 and set(selected['ID#'])==set(fixed['ID#'])
    run('04CalculateBLOS.py','--no-zeeman')
    for script in ['05aDensitySensitivity.py','05bDensitySensitivityPlot.py',
                   '06aTempSensitivity.py','06bTempSensitivityPlot.py','07UncertaintyAnalysis.py']:
        run(script)
    shutil.copy2(base/'FinalData/FinalBLOSResults.csv',base/'FinalData/FinalBLOSResults_stage07.tsv')
    run('revise_paper_analysis.py')
    for script in ['create_paper_plots.py','create_stability_plots.py',
                   'plot_perseus_tahani.py','review_paper_results.py','write_paper_revision.py']:
        run(script)
    # Plot saved final fields, so the paper catalog is not recalculated here.
    run('04CalculateBLOS.py','--zeeman-only','--no-zeeman')
    for ext in ['png','pdf']:
        shutil.copy2(base/f'Plots/BLOSPointMap.{ext}',base/f'Plots/BLOSPointMap_NoZeeman.{ext}')
    # Replace global-config provenance with the actual run configuration hashes.
    manifest=base/'PaperTables/input_sha256.json'
    hashes=json.loads(manifest.read_text())
    for name in ['configStartSettings.ini','configDirectoryAndNames.ini','configConstants.ini']:
        hashes.pop(name,None)
        hashes[str((cfg/name).relative_to(ROOT))]=hashlib.sha256((cfg/name).read_bytes()).hexdigest()
    hashes[str(historical.relative_to(ROOT))]=hashlib.sha256(historical.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(hashes,indent=2)+'\n')
    b=pd.read_csv(base/'FinalData/BLOSPoints.csv',sep='\t')
    f=pd.read_csv(base/'FinalData/FinalBLOSResults.csv',sep='\t')
    r=pd.read_csv(base/'FinalData/ReferenceData.csv',sep='\t').iloc[0]
    assert b['ID#'].tolist()==f['ID#'].tolist()
    assert not set(b['ID#'])&set(selected['ID#'])
    assert (b.Extinction>=multiplier*r['Reference Extinction']).all()
    assert np.isfinite(b['Magnetic_Field(uG)']).all()
    for folder in ['DensitySensitivity','TemperatureSensitivity']:
        for path in (base/folder).glob('*.csv'):
            assert pd.read_csv(path,sep='\t')['ID#'].tolist()==b['ID#'].tolist(),path
    values=abs(b['Magnetic_Field(uG)'].to_numpy())
    boot=np.random.default_rng(0).choice(values,(10000,len(values)),replace=True)
    sigma=(f.TotalUpperBUncertainty.to_numpy()+f.TotalLowerBUncertainty.to_numpy())/2
    valid=np.isfinite(sigma)&(sigma>0)
    x=values[valid];w=1/sigma[valid]**2
    order=np.argsort(x);x=x[order];w=w[order]
    counts=np.random.default_rng(0).multinomial(len(x),np.full(len(x),1/len(x)),10000)
    mass=counts*w;tot=mass.sum(axis=1)
    wm=mass@x/tot
    wd=x[(np.cumsum(mass,axis=1)>=tot[:,None]/2).argmax(axis=1)]
    row=dict(multiplier=multiplier,reference_count=13,n_on=len(b),
        reference_rm=r['Reference RM'],reference_sem=r['Reference RM Std'],reference_av=r['Reference Extinction'],
        on_threshold=multiplier*r['Reference Extinction'],
        positive=int((b.Scaled_RM>0).sum()),negative=int((b.Scaled_RM<0).sum()),
        min_B=b['Magnetic_Field(uG)'].min(),max_B=b['Magnetic_Field(uG)'].max(),
        mean_abs_B=values.mean(),mean_bootstrap_sd=boot.mean(axis=1).std(),
        median_abs_B=np.median(values),median_bootstrap_sd=np.median(boot,axis=1).std(),
        std_signed_B=b['Magnetic_Field(uG)'].std(ddof=1),n_weighted=int(valid.sum()),
        weighted_mean_abs_B=np.average(x,weights=w),weighted_mean_bootstrap_sd=wm.std(),
        weighted_median_abs_B=x[np.searchsorted(np.cumsum(w),w.sum()/2)],weighted_median_bootstrap_sd=wd.std(),
        unbounded=int(f.UnboundedExtinctionSensitivity.sum()))
    summary.append(row)
    (base/'PaperTables/all13_summary.json').write_text(json.dumps(row,indent=2)+'\n')
    bundle=base/'All_Figures_and_Tables';bundle.mkdir()
    for folder in ['Plots','PaperTables','FinalData','IntermediateData','DensitySensitivity','TemperatureSensitivity','Logs']:
        for path in (base/folder).iterdir():
            if path.is_file():
                dest=bundle/path.name
                if dest.exists() and dest.read_bytes()!=path.read_bytes():dest=bundle/(folder+'__'+path.name)
                shutil.copy2(path,dest)
    shutil.copy2(runroot/'Requested13_reference_crossmatch.csv',bundle)
    notes=f'''All 13 historical separated OFF positions; ON multiplier {multiplier}; distance 294 pc.
The requested reference set is crossmatched from {historical.relative_to(ROOT)}.
At 294 pc the automatic pool has 15 separated candidates; this run intentionally
uses the specified historical 13, with automatic count optimization disabled.
AutomaticFilteredPotRefPoints.csv retains the full current filtered list.
Reference RM and extinction are unweighted averages of the 13 references.
Main paper fields use the published Paper I membership and the paper uncertainty
prescription; stage07 uncertainties are retained separately for provenance.
Bootstrap errors are one standard deviation of 10,000 source resamples.
Error-weighted statistics use 1 / (average upper/lower error)^2, excluding
unbounded errors; sampling errors omit shared and spatial covariance.
Paper broad/eligible ensemble diagnostics explore the current larger pool;
their alternate-reference products are explicitly labeled, not the adopted run.
Configuration snapshots are in ../RunConfig relative to the Perseus directory.
'''
    (bundle/'README.txt').write_text(notes)
    print(json.dumps(row,indent=2),flush=True)

comparison=pd.DataFrame(summary)
comparison.to_csv(ROOT/'All13_M1_vs_M3_comparison.csv',index=False)
for multiplier in [1,3]:
    dest=ROOT/f'FileOutput_All13_M{multiplier}_D294/Perseus/All_Figures_and_Tables'
    comparison.to_csv(dest/'All13_M1_vs_M3_comparison.csv',index=False)
print(comparison.to_string(index=False),flush=True)
