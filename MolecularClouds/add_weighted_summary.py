"""Descriptive inverse-field-variance means and weighted medians."""
from pathlib import Path
import json
import shutil
import numpy as np
import pandas as pd
from LocalLibraries import config

base=Path(config.CloudOutputDir)
cases=[('Original reference',base/'FinalData/FinalBLOSResults.csv'),
       ('Error-weighted reference: formal error',base/'ErrorWeighted/ErrorWeighted_FinalBLOSResults_formal.tsv'),
       ('Error-weighted reference: scatter-scaled error',base/'ErrorWeighted/ErrorWeighted_FinalBLOSResults_scatter_scaled.tsv')]

def weighted_median(values,weights):
    order=np.argsort(values)
    x,w=values[order],weights[order]
    cumulative=np.cumsum(w)
    half=w.sum()/2
    i=int(np.searchsorted(cumulative,half))
    if i+1<len(x) and np.isclose(cumulative[i],half,rtol=1e-14,atol=0):
        return float((x[i]+x[i+1])/2)
    return float(x[i])

assert weighted_median(np.array([1.,3.]),np.ones(2))==2
assert weighted_median(np.array([1.,3.,9.]),np.array([1.,5.,1.]))==3
rows=[]
for name,path in cases:
    d=pd.read_csv(path,sep='\t')
    b=d['Magnetic_Field(uG)'].to_numpy(float)
    sigma=(d.TotalUpperBUncertainty.to_numpy(float)+d.TotalLowerBUncertainty.to_numpy(float))/2
    use=np.isfinite(b)&np.isfinite(sigma)&(sigma>0)
    x=b[use];w=1/sigma[use]**2
    alpha=w/w.sum()
    row=dict(result=name,n_total=len(b),n_weighted=int(use.sum()),n_excluded=int((~use).sum()),
             effective_n=float(1/np.sum(alpha**2)))
    for label,values in [('signed_B',x),('abs_B',abs(x))]:
        row[f'error_weighted_mean_{label}_uG']=float(alpha@values)
        row[f'error_weighted_median_{label}_uG']=weighted_median(values,w)
        row[f'unweighted_mean_same_subset_{label}_uG']=float(values.mean())
        row[f'unweighted_median_same_subset_{label}_uG']=float(np.median(values))
    rows.append(row)
result=pd.DataFrame(rows)
out=base/'ErrorWeighted'
result.to_csv(out/'ErrorWeighted_mean_median.csv',index=False)
(out/'ErrorWeighted_mean_median.json').write_text(json.dumps(rows,indent=2)+'\n')
notes='''Descriptive error-weighted mean and median of source fields

This is a second weighting operation, distinct from weighting the OFF RMs.
For each source sigma_B = (upper_error + lower_error)/2 and weight = 1/sigma_B^2.
Weighted mean = sum(weight * B)/sum(weight). Weighted median is the value
where cumulative weight reaches half (average adjacent values at an exact tie).
Both signed B and absolute B are summarized, in microgauss.
Sources with nonfinite or nonpositive sigma_B are excluded; counts are given.
Unweighted statistics on the identical finite-error subset are also provided.
The two error-weighted-reference rows use formal and scatter-scaled reference
errors respectively. Their nominal fields agree but their weighting differs.

These are descriptive statistics. The supplied asymmetric errors include model
excursions and are not Gaussian standard deviations. Shared reference and
chemical-model errors correlate the sources; these weights do not model that
covariance. No independent-source standard error or median confidence interval
is assigned. Small-error sources can dominate; effective_n measures weight
concentration, not the number of physically independent observations.
'''
(out/'ErrorWeighted_mean_median_README.txt').write_text(notes)
for path in out.glob('ErrorWeighted_mean_median*'):
    shutil.copy2(path,base/'All_Figures_and_Tables'/path.name)
    shutil.copy2(path,base/'PaperTables'/path.name)
print(result.to_string(index=False))
