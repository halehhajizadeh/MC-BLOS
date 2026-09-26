"""Summarize all saved pipeline runs without modifying their science products."""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
DRAWS=10000
SEED=0

def median_weighted(x,w):
    order=np.argsort(x);x=x[order];w=w[order]
    c=np.cumsum(w);half=w.sum()/2
    i=int(np.searchsorted(c,half))
    return float((x[i]+x[i+1])/2 if i+1<len(x) and np.isclose(c[i],half,rtol=1e-14,atol=0) else x[i])

def weighted_bootstrap(x,w):
    order=np.argsort(x);x=x[order];w=w[order]
    counts=np.random.default_rng(SEED).multinomial(len(x),np.full(len(x),1/len(x)),DRAWS)
    mass=counts*w;total=mass.sum(axis=1);c=np.cumsum(mass,axis=1)
    ix=(c>=total[:,None]/2).argmax(axis=1)
    med=x[ix].copy()
    for k in np.flatnonzero(np.isclose(c[np.arange(DRAWS),ix],total/2,rtol=1e-14,atol=0)):
        after=np.flatnonzero(mass[k,ix[k]+1:]>0)
        if len(after):med[k]=(x[ix[k]]+x[ix[k]+1+after[0]])/2
    return float((mass@x/total).std()),float(med.std())

def add_statistics(row,prefix,x):
    """Add ordinary mean/median values and bootstrap error bars."""
    x=np.asarray(x,dtype=float)
    prefix=f'{prefix}_' if prefix else ''
    if len(x)==0:
        row[f'{prefix}n']=0
        for name in ('mean','median'):
            row[f'{prefix}{name}_B_uG']=None
            row[f'{prefix}{name}_bootstrap_sd_uG']=None
        return
    sample=np.random.default_rng(SEED).choice(x,(DRAWS,len(x)),replace=True)
    row[f'{prefix}n']=int(len(x))
    row[f'{prefix}mean_B_uG']=float(x.mean())
    row[f'{prefix}mean_bootstrap_sd_uG']=float(sample.mean(axis=1).std())
    row[f'{prefix}median_B_uG']=float(np.median(x))
    row[f'{prefix}median_bootstrap_sd_uG']=float(np.median(sample,axis=1).std())

def add_weighted_statistics(row,prefix,x,weights):
    """Add inverse-variance weighted statistics and bootstrap error bars."""
    prefix=f'{prefix}_' if prefix else ''
    x=np.asarray(x,dtype=float);weights=np.asarray(weights,dtype=float)
    if len(x)==0:
        for name in ('mean','median'):
            row[f'{prefix}weighted_{name}_B_uG']=None
            row[f'{prefix}weighted_{name}_bootstrap_sd_uG']=None
        return
    row[f'{prefix}weighted_mean_B_uG']=float(np.average(x,weights=weights))
    row[f'{prefix}weighted_median_B_uG']=median_weighted(x,weights)
    mean_sd,median_sd=weighted_bootstrap(x,weights)
    row[f'{prefix}weighted_mean_bootstrap_sd_uG']=mean_sd
    row[f'{prefix}weighted_median_bootstrap_sd_uG']=median_sd

def summarize(bfile,efile,label):
    b=pd.read_csv(bfile,sep='\t');e=pd.read_csv(efile,sep='\t')
    assert not b['ID#'].duplicated().any() and not e['ID#'].duplicated().any()
    assert set(b['ID#'])==set(e['ID#']),label
    e=e.set_index('ID#').loc[b['ID#']]
    values=b['Magnetic_Field(uG)'].to_numpy(float)
    np.testing.assert_allclose(values,e['Magnetic_Field(uG)'],rtol=1e-10,atol=1e-10)
    finite=np.isfinite(values)
    assert finite.any(),label
    v=values[finite]
    upper=e.TotalUpperBUncertainty.to_numpy(float)
    lower=e.TotalLowerBUncertainty.to_numpy(float)
    sigma=(upper+lower)/2
    valid=finite&np.isfinite(upper)&np.isfinite(lower)&(upper>=0)&(lower>=0)&(sigma>0)
    row=dict(dataset=label,n_total=len(values),n_finite_fields=len(v),
             positive=int((v>0).sum()),negative=int((v<0).sum()),zero=int((v==0).sum()),
             min_B_uG=float(v.min()),max_B_uG=float(v.max()),std_signed_B_uG=float(v.std(ddof=1)) if len(v)>1 else None,
             n_weighted=int(valid.sum()),n_excluded_weighted=int((~valid).sum()),
             n_nonfinite_errors=int((~np.isfinite(upper)|~np.isfinite(lower)).sum()),
             field_source=str(bfile.relative_to(ROOT)),uncertainty_source=str(efile.relative_to(ROOT)),
             field_sha256=hashlib.sha256(bfile.read_bytes()).hexdigest(),
             uncertainty_sha256=hashlib.sha256(efile.read_bytes()).hexdigest())
    for kind,x in [('signed',v),('abs',abs(v))]:
        # Keep the established overall column names for compatibility.
        if kind=='signed':
            add_statistics(row,'',x)
            if valid.any():
                add_weighted_statistics(row,'',values[valid],1/sigma[valid]**2)
        else:
            sample=np.random.default_rng(SEED).choice(x,(DRAWS,len(x)),replace=True)
            row['mean_abs_B_uG']=float(x.mean())
            row['mean_abs_bootstrap_sd_uG']=float(sample.mean(axis=1).std())
            row['median_abs_B_uG']=float(np.median(x))
            row['median_abs_bootstrap_sd_uG']=float(np.median(sample,axis=1).std())
            if valid.any():
                x=abs(values[valid]);w=1/sigma[valid]**2
                row['weighted_mean_abs_B_uG']=float(np.average(x,weights=w))
                row['weighted_median_abs_B_uG']=median_weighted(x,w)
                a,c=weighted_bootstrap(x,w)
                row['weighted_mean_abs_bootstrap_sd_uG']=a
                row['weighted_median_abs_bootstrap_sd_uG']=c
                row['effective_weighted_n']=float(w.sum()**2/np.sum(w**2))
    # Separate signed positive and negative populations, including their
    # error-weighted versions and bootstrap error bars.
    for side,mask in [('positive',values>0),('negative',values<0)]:
        add_statistics(row,side,values[mask])
        weighted_mask=mask&valid
        if weighted_mask.any():
            add_weighted_statistics(row,side,values[weighted_mask],1/sigma[weighted_mask]**2)
        else:
            add_weighted_statistics(row,side,np.array([]),np.array([]))
    return row

NOTES='''All fields are in microgauss. Ordinary statistics use finite nominal fields.
Errors following ± are one bootstrap standard deviation from 10,000 source
resamples, with seed 0; these are sampling errors, not full measurement errors.
Weighted means/medians use w = 1/sigma_B² and sigma_B = (upper + lower)/2.
Nonfinite, negative, or zero weighting errors are excluded and counted.
Both signed fields and magnitudes are in the CSV/JSON; the main display uses |B|.
The positive_* and negative_* columns give separate signed-population statistics,
including ordinary and inverse-variance weighted means/medians and bootstrap
error bars. Their *_n columns report the population sizes.
The standard deviation describes signed B, with ddof=1. Source IDs align errors.
Saved uncertainty prescriptions differ between historical and paper-reanalysis
runs; these statistics preserve each prescription, including any old clipping.
Shared reference/model systematics and spatial correlations are not modeled.
Effective weighted N measures weight concentration, not physical independence.
Subset rows overlap their parent catalogs; no independent comparison is implied.
Reference-RM weighting is distinct from weighting the final BLOS measurements.
'''

def display(rows):
    lines=['| Dataset | ON | + / − | Mean |B| (µG) | Median |B| (µG) | Error-weighted mean (µG) | Error-weighted median (µG) | Weighted N |',
           '|---|---:|---:|---:|---:|---:|---:|---:|']
    lines[0]=lines[0].replace('Mean |B|','Mean absolute B').replace('Median |B|','Median absolute B')
    for r in rows:
        def val(prefix):
            if prefix+'_abs_B_uG' not in r:return 'Unavailable'
            return f"{r[prefix+'_abs_B_uG']:.2f} ± {r[prefix+'_abs_bootstrap_sd_uG']:.2f}"
        lines.append(f"| {r['dataset']} | {r['n_total']} | {r['positive']} / {r['negative']} | "+
                     ' | '.join(val(k) for k in ['mean','median','weighted_mean','weighted_median'])+f" | {r['n_weighted']} |")
    lines+=['','| Dataset | Group | N | Mean B (µG) | Median B (µG) | Weighted mean B (µG) | Weighted median B (µG) |',
            '|---|---|---:|---:|---:|---:|---:|']
    for r in rows:
        for group in ['positive','negative']:
            def group_val(name):
                value=r.get(f'{group}_{name}_B_uG')
                error=r.get(f'{group}_{name}_bootstrap_sd_uG')
                return 'Unavailable' if value is None else f'{value:.2f} ± {error:.2f}'
            def weighted_val(name):
                value=r.get(f'{group}_weighted_{name}_B_uG')
                error=r.get(f'{group}_weighted_{name}_bootstrap_sd_uG')
                return 'Unavailable' if value is None else f'{value:.2f} ± {error:.2f}'
            lines.append(f"| {r['dataset']} | {group} | {r[f'{group}_n']} | {group_val('mean')} | {group_val('median')} | {weighted_val('mean')} | {weighted_val('median')} |")
    lines+=['','| Dataset | Minimum B (µG) | Maximum B (µG) | Signed-B standard deviation (µG) | Excluded from weighting |',
            '|---|---:|---:|---:|---:|']
    for r in rows:
        sd=r['std_signed_B_uG']
        sdtext=f'{sd:.2f}' if sd is not None else 'Unavailable'
        lines.append(f"| {r['dataset']} | {r['min_B_uG']:.2f} | {r['max_B_uG']:.2f} | {sdtext} | {r['n_excluded_weighted']} |")
    return '\n'.join(lines)+'\n'

def save(folder,rows):
    folder.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(folder/'statistics_summary.csv',index=False)
    (folder/'statistics_summary.json').write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n')
    (folder/'statistics_summary.md').write_text('# Saved-result statistics\n\n'+display(rows)+'\n'+NOTES)
    (folder/'README.txt').write_text(NOTES)

if __name__=='__main__':
    assert median_weighted(np.array([1.,3.]),np.array([1.,1.]))==2
    assert median_weighted(np.array([9.,3.,1.]),np.array([1.,5.,1.]))==3
    allrows=[];inventory=[]
    for bfile in sorted(ROOT.glob('FileOutput*/*/FinalData/BLOSPoints.csv')):
        base=bfile.parent.parent;label=str(base.relative_to(ROOT))
        efile=bfile.with_name('FinalBLOSResults.csv')
        if not efile.exists():
            inventory.append(dict(directory=label,status='No final uncertainty table'));continue
        print('Summarizing',label,flush=True)
        rows=[summarize(bfile,efile,label)]
        # Keep the archived stage-07 prescription explicitly separate.
        stage=bfile.with_name('FinalBLOSResults_stage07.tsv')
        if stage.exists():rows.append(summarize(stage,stage,label+' [archived stage07 catalog]'))
        refpath=bfile.with_name('ReferenceData.csv')
        if refpath.exists():
            ref=pd.read_csv(refpath,sep='\t').iloc[0]
            for row in rows:
                row['reference_count']=int(ref['Number of Reference Points'])
                row['reference_rm']=float(ref['Reference RM'])
                row['reference_error_saved']=float(ref['Reference RM Std'])
                row['reference_av']=float(ref['Reference Extinction'])
        save(base/'Statistics',rows)
        bundle=base/'All_Figures_and_Tables'
        if bundle.exists():
            for name in ['statistics_summary.csv','statistics_summary.json','statistics_summary.md']:
                shutil.copy2(base/'Statistics'/name,bundle/name)
        allrows.extend(rows);inventory.append(dict(directory=label,status='Completed',variants=len(rows)))
    for efile in sorted(ROOT.glob('FileOutput*/*/ErrorWeighted/ErrorWeighted_FinalBLOSResults_*.tsv')):
        folder=efile.parent
        label=str(folder.relative_to(ROOT))+' ['+efile.stem.removeprefix('ErrorWeighted_FinalBLOSResults_')+']'
        row=summarize(folder/'ErrorWeighted_BLOSPoints.tsv',efile,label)
        allrows.append(row)
    for folder in sorted(ROOT.glob('FileOutput*/*/ErrorWeighted')):
        rows=[r for r in allrows if r['dataset'].startswith(str(folder.relative_to(ROOT))+' [')]
        if rows:save(folder/'Statistics',rows)
    # Reference-combination experiments are ensembles, not single ON catalogs.
    for source in sorted(ROOT.glob('FileOutput*/*/statistics/combination_statistics.csv')):
        d=pd.read_csv(source)
        dest=source.parent/'ensemble_statistics_summary.csv'
        d.select_dtypes(include=[np.number]).describe().T.to_csv(dest)
        inventory.append(dict(directory=str(source.parent.relative_to(ROOT)),status='Ensemble numerical summary',variants=len(d)))
    save(ROOT/'Statistics',allrows)
    pd.DataFrame(inventory).to_csv(ROOT/'Statistics/directory_inventory.csv',index=False)
    for top in sorted(ROOT.glob('FileOutput*')):
        rows=[r for r in allrows if r['dataset'].startswith(top.name+'/')]
        if rows:save(top/'Statistics',rows)
    print(display(allrows))
    print('Datasets/variants:',len(allrows),'Main result directories:',len(list(ROOT.glob('FileOutput*/*/FinalData/BLOSPoints.csv'))))
