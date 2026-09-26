"""Descriptive sight-line bootstrap intervals for the 197/134 comparison."""
from pathlib import Path
import numpy as np
import pandas as pd
from LocalLibraries import config

root=Path(__file__).resolve().parent
base=Path(config.CloudOutputDir)
out=base/'All_Figures_and_Tables'
rng=np.random.default_rng(20260924)
draws=20000
rows=[]
for sample,path in [('Previous main (197)',root/'FileOutput_ImprovedPlots/Perseus'),
                    ('Multiplier 3 (134)',base)]:
    d=pd.read_csv(path/'FinalData/FinalBLOSResults.csv',sep='\t')
    x=np.abs(d['Magnetic_Field(uG)'].to_numpy(float))
    assert np.isfinite(x).all()
    sigma=(d.TotalUpperBUncertainty.to_numpy(float)+d.TotalLowerBUncertainty.to_numpy(float))/2
    valid=np.isfinite(sigma)&(sigma>0)
    for weighted in [False,True]:
        values=x[valid] if weighted else x
        weights=1/sigma[valid]**2 if weighted else np.ones(len(values))
        order=np.argsort(values)
        values,weights=values[order],weights[order]
        counts=rng.multinomial(len(values),np.full(len(values),1/len(values)),size=draws)
        mass=counts*weights
        total=mass.sum(axis=1)
        mean=mass@values/total
        cumulative=np.cumsum(mass,axis=1)
        index=(cumulative>=total[:,None]/2).argmax(axis=1)
        median=values[index].copy()
        # At an exact half-weight tie use the next occupied value.
        tie=np.isclose(cumulative[np.arange(draws),index],total/2,rtol=1e-14,atol=0)
        for k in np.flatnonzero(tie):
            following=np.flatnonzero(mass[k,index[k]+1:]>0)
            if len(following):
                median[k]=(values[index[k]]+values[index[k]+1+following[0]])/2
        point_mean=float(np.average(values,weights=weights))
        cum=np.cumsum(weights)
        j=int(np.searchsorted(cum,weights.sum()/2))
        point_median=float(values[j])
        if j+1<len(values) and np.isclose(cum[j],weights.sum()/2,rtol=1e-14,atol=0):
            point_median=float((values[j]+values[j+1])/2)
        if not weighted:
            np.testing.assert_allclose(point_median,np.median(values))
        for statistic,point,distribution in [('Mean',point_mean,mean),('Median',point_median,median)]:
            low,high=np.quantile(distribution,[.025,.975])
            rows.append(dict(sample=sample,statistic=('Error-weighted ' if weighted else '')+statistic.lower(),
                n=len(values),estimate_uG=point,lower_95_uG=float(low),upper_95_uG=float(high),
                lower_bar_uG=float(point-low),upper_bar_uG=float(high-point)))
table=pd.DataFrame(rows)
table.to_csv(out/'Comparison_197_vs_134_bootstrap.csv',index=False)
lines=['# Summary statistics with descriptive 95% bootstrap intervals','',
       '| Statistic of absolute BLOS (µG) | Previous main: 197 | New: 134 |',
       '|---|---:|---:|']
for stat in ['mean','median','Error-weighted mean','Error-weighted median']:
    pair=table[table.statistic==stat]
    cells=[f"{r.estimate_uG:.2f} [{r.lower_95_uG:.2f}, {r.upper_95_uG:.2f}]" for r in pair.itertuples()]
    lines.append('| '+stat.capitalize()+' | '+' | '.join(cells)+' |')
lines+=['', 'Brackets give the 2.5th and 97.5th percentiles of 20,000 sight-line bootstrap resamples (seed 20260924).',
        'Each draw resamples entire source entries with their fixed nominal fields and errors.',
        'Unweighted statistics use all 197/134 sources; weighted statistics use 184/132 sources with finite positive errors.',
        'Weights are the inverse square of the average upper/lower error. These intervals are descriptive sampling intervals,',
        'not full propagated measurement-error bars. They do not include shared reference/model systematics or spatial',
        'correlations. The two samples overlap, so these intervals are not a test of their difference.',
        'No error bars are assigned to catalog counts or extrema by this procedure.']
(out/'Comparison_197_vs_134_errorbars.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
