"""Add inverse-RM-variance reference results without changing the main run."""
from pathlib import Path
import json
import shutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from LocalLibraries import config
from LocalLibraries.RegionOfInterest import Region
from LocalLibraries.CalculateB import CalculateB
from LocalLibraries.Uncertainty import combine_uncertainties

base=Path(config.CloudOutputDir)
out=base/'ErrorWeighted'
out.mkdir(exist_ok=True)
refs=pd.read_csv(config.ChosenRefPointFile,sep='\t')
old=pd.read_csv(base/'FinalData/BLOSPoints.csv',sep='\t')
matched=pd.read_csv(config.MatchedRMExtinctionFile,sep='\t').set_index('ID#')
points=matched.loc[old['ID#']].reset_index()
errors=refs['RM_Err(rad/m2)'].to_numpy(float)
assert np.isfinite(errors).all() and (errors>0).all()
w=1/errors**2
alpha=w/w.sum()
rm=refs['Rotation_Measure(rad/m2)'].to_numpy(float)
mean=float(alpha@rm)
formal=float(1/np.sqrt(w.sum()))
chi2=float(np.sum(w*(rm-mean)**2)/(len(rm)-1))
scaled=formal*np.sqrt(max(1,chi2))
av=float(refs.Extinction_Value.mean())
region=Region(config.cloud)
chem=Path(region.AvFilePath).parent

def calc(error,t='0',n='0'):
    return CalculateB(str(chem/f'Av_T{t}_n{n}.out'),points,mean,
                      float(alpha@errors),error,av)

b=calc(formal)
models=[calc(formal,t,n) for t,n in [('0','+50'),('0','-50'),('+20','0'),('-20','0')]]
f=combine_uncertainties(b,*models)
bs=calc(scaled)
fs=combine_uncertainties(bs,*models)
assert b['ID#'].tolist()==old['ID#'].tolist()
expected=(old.RM_Raw_Value-mean)/(.812*old.Electron_Column_pc_cm3)
np.testing.assert_allclose(b['Magnetic_Field(uG)'],expected,rtol=1e-12)
np.testing.assert_allclose(b.Electron_Column_pc_cm3,old.Electron_Column_pc_cm3)
np.testing.assert_allclose(b['Magnetic_Field(uG)'],bs['Magnetic_Field(uG)'])
np.testing.assert_allclose(alpha.sum(),1)
refs['InverseVarianceWeight']=w
refs['NormalizedWeight']=alpha
refs.to_csv(out/'ErrorWeighted_reference_weights.csv',index=False)
b.to_csv(out/'ErrorWeighted_BLOSPoints.tsv',sep='\t',index=False)
f.to_csv(out/'ErrorWeighted_FinalBLOSResults_formal.tsv',sep='\t',index=False)
fs.to_csv(out/'ErrorWeighted_FinalBLOSResults_scatter_scaled.tsv',sep='\t',index=False)
catalog=pd.read_csv(base/'FinalData/BLOS_catalog_for_paper.csv')
assert catalog['ID#'].tolist()==b['ID#'].tolist()
comparison=catalog[['ID#','Source','Ra(deg)','Dec(deg)','Extinction']].copy()
comparison['B_unweighted_uG']=old['Magnetic_Field(uG)'].to_numpy()
comparison['B_error_weighted_uG']=b['Magnetic_Field(uG)'].to_numpy()
comparison['Sign_changed']=np.sign(comparison.B_unweighted_uG)!=np.sign(comparison.B_error_weighted_uG)
for label,table in [('formal',f),('scatter_scaled',fs)]:
    for side in ['Upper','Lower']:
        comparison[f'{label}_{side.lower()}_error_uG']=table[f'Total{side}BUncertainty'].to_numpy()
comparison.to_csv(out/'ErrorWeighted_catalog_comparison.csv',index=False)
summary=dict(method='Inverse RM measurement variance; same OFF and ON membership; unweighted reference extinction retained',
    distance_pc=region.distance,on_multiplier=config.onPtsExtMultipleThreshold,
    reference_count=len(refs),on_count=len(b),reference_extinction=av,
    unweighted_reference_rm=float(rm.mean()),weighted_reference_rm=mean,
    formal_reference_error=formal,reference_reduced_chi_square=chi2,
    scatter_scaled_reference_error=float(scaled),effective_reference_count=float(1/np.sum(alpha**2)),
    positive=int((b.Scaled_RM>0).sum()),negative=int((b.Scaled_RM<0).sum()),
    changed_signs=int(comparison.Sign_changed.sum()),median_abs_B=float(b['Magnetic_Field(uG)'].abs().median()),
    mean_abs_B=float(b['Magnetic_Field(uG)'].abs().mean()))
(out/'ErrorWeighted_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
notes='''Inverse-variance weighted reference comparison

Weights are 1 / RM_error^2 for the same eight selected OFF points.
RM_weighted = sum(weight * RM) / sum(weight).
Formal reference error = 1 / sqrt(sum(weight)). This assumes a common
reference RM and independent measurement errors; it excludes sky variation.
The second error estimate multiplies the formal error by
sqrt(max(1, reduced_chi_square)), as an explicitly labeled scatter diagnostic.
It is not a validated spatial-foreground model or complete systematic error.

The reference extinction and ON membership remain those of the main run:
RM measurement errors are not extinction errors. Distance and multiplier are
unchanged. Both weighted error variants give the same nominal B values.
Final field uncertainties retain the paper prescription: linear-sum ON RM
and reference error, then quadrature with extinction, density (+/-50%) and
temperature (+/-20%) excursions. They are not Gaussian confidence intervals.
The unweighted primary outputs are preserved.
'''
(out/'ErrorWeighted_README.txt').write_text(notes)
plt.rcParams.update({'font.family':'serif','font.size':11})
fig,ax=plt.subplots(figsize=(6,5))
ax.scatter(comparison.B_unweighted_uG,comparison.B_error_weighted_uG,
           c=np.where(comparison.Sign_changed,'darkorange','steelblue'),s=18)
lo=min(comparison.B_unweighted_uG.min(),comparison.B_error_weighted_uG.min())
hi=max(comparison.B_unweighted_uG.max(),comparison.B_error_weighted_uG.max())
ax.plot([lo,hi],[lo,hi],'--',color='0.5')
ax.axhline(0,color='0.8',lw=.7);ax.axvline(0,color='0.8',lw=.7)
ax.set(xlabel=r'Unweighted-reference $B_\parallel$ ($\mu$G)',
       ylabel=r'Error-weighted-reference $B_\parallel$ ($\mu$G)',
       title=f'Same {len(b)} ON sources; orange: sign changes')
fig.tight_layout()
for ext in ['png','pdf']:
    fig.savefig(out/f'ErrorWeighted_BLOS_comparison.{ext}',dpi=220)
plt.close(fig)
for path in out.iterdir():
    if path.is_file():
        shutil.copy2(path,base/'All_Figures_and_Tables'/path.name)
        if path.suffix in {'.png','.pdf'}:
            shutil.copy2(path,base/'Plots'/path.name)
print(json.dumps(summary,indent=2))
