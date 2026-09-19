"""Reproducible paper checks; writes only PaperRevision, preserving archived runs.

Run from MolecularClouds: ../.venv/bin/python revise_paper_analysis.py
The adopted eight references are held fixed to isolate numerical corrections.
"""
from pathlib import Path
from itertools import combinations
import hashlib
import json
import re
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.wcs import WCS
from astropy import units as u
from scipy.spatial import Delaunay
from scipy.interpolate import griddata
from LocalLibraries.CalculateB import CalculateB
from LocalLibraries.Uncertainty import combine_uncertainties
from LocalLibraries import config

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'FileOutput_ImprovedPlots/Perseus'
OUT = ROOT / 'PaperRevision'
CHEM = ROOT / 'Data/ChemicalAbundance/n1.0e3_T12.0_G1'
for sub in ['tables', 'plots', 'corrected', 'build']:
    (OUT / sub).mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family': 'serif', 'mathtext.fontset': 'stix', 'font.size': 10})
warnings.filterwarnings('ignore', category=FutureWarning)

def read(name):
    return pd.read_csv(BASE / name, sep='\t')

def coords(df):
    return SkyCoord(df['Ra(deg)'].to_numpy()*u.deg, df['Dec(deg)'].to_numpy()*u.deg)

def savefig(fig, name):
    for ext in ['pdf', 'png']:
        fig.savefig(OUT / 'plots' / f'{name}.{ext}', dpi=180, bbox_inches='tight')
    plt.close(fig)

matched = read('FinalData/MatchedRMExtinction.csv')
old = read('FinalData/BLOSPoints.csv')
refs = read('FinalData/SelectedRefPoints.csv')
ref_rm = refs['Rotation_Measure(rad/m2)'].mean()
ref_av = refs.Extinction_Value.mean()
ref_sem = refs['Rotation_Measure(rad/m2)'].std(ddof=1) / np.sqrt(len(refs))
ref_avgerr = refs['RM_Err(rad/m2)'].mean()
on = matched.set_index('ID#').loc[old['ID#']].reset_index()

def calculate(points=None, t='0', n='0', rm=ref_rm, av=ref_av, sem=ref_sem):
    if points is None:
        points=on
    return CalculateB(str(CHEM / f'Av_T{t}_n{n}.out'), points,
                      rm, ref_avgerr, sem, av)

# Verify the archived numerical implementation reproduces the archived fields.
import types
legacy = types.ModuleType('LocalLibraries.legacy_calculate')
legacy.__package__ = 'LocalLibraries'
exec((OUT / 'original/CalculateB.py').read_text(), legacy.__dict__)
replica = legacy.CalculateB(str(CHEM/'Av_T0_n0.out'), on,
                           ref_rm, ref_avgerr, ref_sem, ref_av)
np.testing.assert_allclose(replica['Magnetic_Field(uG)'], old['Magnetic_Field(uG)'], rtol=1e-10)

archived_b=calculate()
archived_b.to_csv(OUT/'corrected/archived_input_corrected.tsv',sep='\t',index=False)
# Source quality: author's complete Paper I machine-readable catalog.
rows = []
for line in (OUT/'sources/paper1_published_table2.txt').read_text().splitlines():
    if line.startswith('VCPMC '):
        z = line.split()
        rows.append([' '.join(z[:2])] + list(map(float,z[2:9])) + list(map(int,z[9:11])))
p1 = pd.DataFrame(rows, columns=['Source','Ra(deg)','Dec(deg)','RM','RM_error',
                                'fracpol','flux','noise','F1','F2'])
assert len(p1)==205

orig_ix,orig_sep,_=coords(matched).match_to_catalog_sky(coords(p1))
orig_valid=orig_sep.arcsec<.1
assert orig_valid.sum()==204
unmatched_published=p1.iloc[[j for j in range(len(p1)) if j not in orig_ix[orig_valid]]]
unmatched_published.to_csv(OUT/'tables/unmatched_published.csv',index=False)
matched.loc[~orig_valid].to_csv(OUT/'tables/unmatched_archived.csv',index=False)
# Explicit published-catalog alternative: sample the omitted published source
# with the same WCS nearest pixel and 5x5 extinction sensitivity window.
new=unmatched_published.iloc[0]
map_hdu=fits.open(ROOT/'Data/2015_02_CalTauPer_toBernsteinCooper.fits')[0]
map_wcs=WCS(map_hdu.header)
ny,nx=map_wcs.world_to_array_index_values(new['Ra(deg)'],new['Dec(deg)'])
patch=map_hdu.data[int(ny)-2:int(ny)+3,int(nx)-2:int(nx)+3]
assert patch.shape==(5,5)
good=np.isfinite(patch)&(patch>=0)
gy,gx=np.indices(patch.shape)
interpolated_av=float(griddata(np.column_stack((gx[good],gy[good])),patch[good],[[2,2]],method='linear')[0])
newrow=on.iloc[0].copy()
newrow['Extinction_Observed']=False
for col,value in {'ID#':205,'Ra(deg)':new['Ra(deg)'],'Dec(deg)':new['Dec(deg)'],
 'Rotation_Measure(rad/m2)':new.RM,'RM_Err(rad/m2)':new.RM_error,
 'Extinction_Index_x':nx,'Extinction_Index_y':ny,'Extinction_Value':interpolated_av,
 'Min_Extinction_Value':patch[good].min(),'Max_Extinction_Value':patch[good].max()}.items():
    newrow[col]=value
newpoints=pd.DataFrame([newrow])

# Recompute coordinate metadata rather than inheriting another source's values.
for prefix,xx,yy in [('center',int(nx),int(ny)),
 ('min',int(nx)-2+int(gx[good][np.argmin(patch[good])]),int(ny)-2+int(gy[good][np.argmin(patch[good])])),
 ('max',int(nx)-2+int(gx[good][np.argmax(patch[good])]),int(ny)-2+int(gy[good][np.argmax(patch[good])]))]:
    ra,dec=map_wcs.wcs_pix2world(xx,yy,0)
    cols={'center':('RA_inExtincFile(degree)','Dec_inExtincFile(degree)'),
          'min':('Min_Extinction_Ra','Min_Extinction_Dec'),
          'max':('Max_Extinction_RA','Max_Extinction_dec')}[prefix]
    newrow[cols[0]]=float(ra);newrow[cols[1]]=float(dec)
assert interpolated_av>1
matched=pd.concat([matched[matched['ID#']!=121],pd.DataFrame([newrow])],ignore_index=True)
on=matched[~matched['ID#'].isin(refs['ID#'])].copy().reset_index(drop=True)
assert len(on)==197 and (on.Extinction_Value>=ref_av).all()
matched.to_csv(OUT/'corrected/MatchedRMExtinction.tsv',sep='\t',index=False)
old=legacy.CalculateB(str(CHEM/'Av_T0_n0.out'),on,ref_rm,ref_avgerr,ref_sem,ref_av)
b = calculate()
models = {}
for key, t, n in [('density_plus','0','+50'),('density_minus','0','-50'),
                  ('temp_plus','+20','0'),('temp_minus','-20','0')]:
    models[key] = calculate(t=t, n=n)
    models[key].to_csv(OUT / 'corrected' / f'{key}.tsv', sep='\t', index=False)
final = combine_uncertainties(b, **models)
b.to_csv(OUT/'corrected/BLOSPoints.tsv', sep='\t', index=False)
final.to_csv(OUT/'corrected/FinalBLOSResults.tsv', sep='\t', index=False)

ix, sep, _ = coords(matched).match_to_catalog_sky(coords(p1))
valid=sep.arcsec<0.1
assert valid.sum()==205 and len(set(ix[valid]))==205
quality = matched[['ID#','Ra(deg)','Dec(deg)']].copy()
for col in ['Source','F1','F2']:
    quality[col]=p1.iloc[ix][col].to_numpy()
quality.loc[~valid,'Source']='UNMATCHED_LOCAL'
quality.loc[~valid,['F1','F2']]=-1
quality['match_arcsec']=sep.arcsec
quality['RM_difference_from_PaperI']=matched['Rotation_Measure(rad/m2)'].to_numpy()-p1.iloc[ix].RM.to_numpy()
assert quality.loc[valid,'RM_difference_from_PaperI'].abs().max()<.011
quality.loc[~valid,'RM_difference_from_PaperI']=np.nan
quality.to_csv(OUT/'tables/paper1_crossmatch.csv',index=False)
b=b.merge(quality[['ID#','Source','F1','F2']],on='ID#',validate='one_to_one')
b['Extinction_Interpolated'] = b['ID#']==205
clean=(b.F1==0)&(b.F2==0)
clean_refs=refs.merge(quality[['ID#','F1','F2']],on='ID#')
clean_refs=clean_refs[(clean_refs.F1==0)&(clean_refs.F2==0)]

# Original Table 6 is parsed from its archived PDF text, not manually rounded anew.
txt=(OUT/'sources/tahani2018.txt').read_text()
section=txt.split('Table 6. Perseus BLOS values.')[1].split('Table 7.')[0]
rows=[]
for line in section.splitlines():
    z=line.split()
    if len(z)==9 and z[0].isdigit():
        rows.append(list(map(float,z)))
lit=pd.DataFrame(rows,columns=['Literature_ID','Ra(deg)','Dec(deg)','Av','RM',
                               'Cloud_RM','B','Upper','Lower'])
assert len(lit)==24
lit['Literature_ID']=lit.Literature_ID.astype(int)
lit.to_csv(OUT/'tables/tahani2018_perseus.csv',index=False)
nvss=pd.read_csv(ROOT/'Data/RMCatalog/catalog.dat',sep=r'\s+')
nvss['Ra(deg)']=15*(nvss.raHours+nvss.raMins/60+nvss.raSecs/3600)
nvss['Dec(deg)']=np.sign(nvss.decDegs)*(abs(nvss.decDegs)+nvss.decArcmins/60+nvss.decArcsecs/3600)
ni,ns,_=coords(lit).match_to_catalog_sky(coords(nvss))
assert ns.arcsec.max()<30
assert np.max(abs(nvss.iloc[ni].rotationMeasures.to_numpy()-lit.RM.to_numpy()))<.11
exact=nvss.iloc[ni].reset_index(drop=True)
vi,vs,_=coords(exact).match_to_catalog_sky(coords(b))
comparison=lit.copy()
comparison['NVSS_RA']=exact['Ra(deg)']; comparison['NVSS_Dec']=exact['Dec(deg)']
comparison['NVSS_RM_error']=exact.RMErrs
comparison['VLA_ID']=b.iloc[vi]['ID#'].to_numpy()
comparison['VLA_Source']=b.iloc[vi].Source.to_numpy()
comparison['separation_arcsec']=vs.arcsec
comparison['position_match']=vs.arcsec<10
for col in ['Magnetic_Field(uG)','RM_Raw_Value','RM_Raw_Err','Scaled_RM','Extinction','Electron_Column_pc_cm3','F1','F2']:
    comparison['VLA_'+col]=b.iloc[vi][col].to_numpy()
f=final.set_index('ID#').loc[comparison.VLA_ID]
comparison['VLA_Upper']=f.TotalUpperBUncertainty.to_numpy()
comparison['VLA_Lower']=f.TotalLowerBUncertainty.to_numpy()
comparison['RM_residual_sigma']=(comparison.VLA_RM_Raw_Value-comparison.RM)/np.hypot(comparison.VLA_RM_Raw_Err,comparison.NVSS_RM_error)
comparison['Literature_Ne_from_rounded_B']=comparison.Cloud_RM/(.812*comparison.B)
comparison.to_csv(OUT/'tables/faraday_matches_all.csv',index=False)
matches=comparison[comparison.position_match].copy()
assert not matches.VLA_ID.duplicated().any()
matches.to_csv(OUT/'tables/faraday_matches.csv',index=False)

# Zeeman positions: Troland & Crutcher 2008 Table 1 (J2000); B1 approximate
# position from Tahani 2018 section 4.2.2. Beam sizes are FWHM diameters.
b1=SkyCoord('03h30m12s','30d57m26s',frame='fk4',equinox='B1950').icrs
zee=pd.DataFrame([
 ['B1',b1.ra.deg,b1.dec.deg,27.,4.,2.9,'Goodman1989 Figure 1 pointing; FK4 B1950 to ICRS'],
 ['L1448-CO',15*(3+25/60+30.5/3600),30+45/60+43/3600,26.,3.7,3.,'Troland2008 Tables 1 and 2'],
 ['L1448-COe',15*(3+25/60+44.6/3600),30+45/60+42/3600,20.6,3.4,3.,'Troland2008 Tables 1 and 2']],
 columns=['Region','Ra(deg)','Dec(deg)','B','Error','FWHM_arcmin','Provenance'])
zi,zs,_=coords(zee).match_to_catalog_sky(coords(b))
zee['nearest_ID']=b.iloc[zi]['ID#'].to_numpy(); zee['separation_arcmin']=zs.arcmin
zee['VLA_B']=b.iloc[zi]['Magnetic_Field(uG)'].to_numpy()
zee['VLA_F1']=b.iloc[zi].F1.to_numpy(); zee['VLA_F2']=b.iloc[zi].F2.to_numpy()
zee['inside_halfpower_radius']=zs.arcmin<=zee.FWHM_arcmin/2
zee.to_csv(OUT/'tables/zeeman_comparison.csv',index=False)

# Broad pool recreates the original 14 candidates, including the close pair.
cand=read('FinalData/AllPotentialRefPoints.csv')
near=set(read('IntermediateData/NearHighExtRej.csv')['ID#'])
pool=cand[~cand['ID#'].isin(near)].copy().reset_index(drop=True)
assert len(pool)==14
eligible=pool[pool['ID#']!=197].reset_index(drop=True)
_,minimum_separation,_=coords(eligible).match_to_catalog_sky(coords(eligible),nthneighbor=2)
assert minimum_separation.arcmin.min()>=1.2
ensemble={}
for name,p in [('broad',pool),('eligible',eligible)]:
    sets=list(combinations(range(len(p)),8))
    means=np.array([p.iloc[list(c)]['Rotation_Measure(rad/m2)'].mean() for c in sets])
    avs=np.array([p.iloc[list(c)].Extinction_Value.mean() for c in sets])
    common=b[(~b['ID#'].isin(p['ID#'])) & (b.Extinction>=avs.max())].copy()
    common['persistent_sign']=np.where(common.RM_Raw_Value>means.max(),1,
                               np.where(common.RM_Raw_Value<means.min(),-1,0))
    common.to_csv(OUT/f'tables/{name}_sign_persistence.csv',index=False)
    ensemble[name]={'combinations':len(means),'rm_min':means.min(),'rm_max':means.max(),
                    'maximum_reference_av':avs.max(),
                    'common':len(common),'positive':int((common.persistent_sign==1).sum()),
                    'negative':int((common.persistent_sign==-1).sum()),
                    'sensitive':int((common.persistent_sign==0).sum())}

# Axis is from the archived extinction-only fit, independent of RM signs.
axis=read('IntermediateData/QuadrantDivisionData.csv').iloc[0]
slope=axis['Slope of Line Through Cloud']; intercept=axis['Vertical Offset of Line Through Cloud']
pos=on.set_index('ID#').loc[b['ID#']]
offset=pos.Extinction_Index_y.to_numpy()-slope*pos.Extinction_Index_x.to_numpy()-intercept
b['axis_side']=np.where(offset>=0,'north','south')
b['RM_sign_score']=b.Scaled_RM/np.hypot(b.RM_Raw_Err,ref_sem)
b.to_csv(OUT/'corrected/catalog_with_flags.csv',index=False)
regions=[]
for sample,mask in [('all',np.ones(len(b),bool)),('F1=0,F2=0',clean),('m=3',b.Extinction>=3*ref_av)]:
    for side in ['north','south']:
        d=b[mask & (b.axis_side==side)]
        regions.append(dict(sample=sample,side=side,n=len(d),positive=int((d.Scaled_RM>0).sum()),
             negative=int((d.Scaled_RM<0).sum()),positive_2sigma=int((d.RM_sign_score>2).sum()),
             negative_2sigma=int((d.RM_sign_score<-2).sum()),median_abs_B=d['Magnetic_Field(uG)'].abs().median()))
pd.DataFrame(regions).to_csv(OUT/'tables/region_statistics.csv',index=False)
rng=np.random.default_rng(20260917)
rm_draw=rng.normal(b.RM_Raw_Value.to_numpy(),b.RM_Raw_Err.to_numpy(),(20000,len(b)))
rm_draw-=rng.normal(ref_rm,ref_sem,(20000,1))
simulation={}
for sample,mask in [('all',np.ones(len(b),bool)),('clean',clean)]:
    north=np.asarray(mask & (b.axis_side=='north')); south=np.asarray(mask & (b.axis_side=='south'))
    delta=(rm_draw[:,north]>0).mean(axis=1)-(rm_draw[:,south]>0).mean(axis=1)
    simulation[sample]={'positive_fraction_north_minus_south_quantiles':np.quantile(delta,[.025,.5,.975]).tolist(),
      'description':'Conditional Gaussian RM propagation with one shared reference draw; not a spatial-null p-value.'}

# A fitted foreground plane is a sensitivity diagnostic, not a validated model.
xy=np.column_stack(((b['Ra(deg)']-52)*np.cos(np.deg2rad(31)),b['Dec(deg)']-31))
rx=np.column_stack(((refs['Ra(deg)']-52)*np.cos(np.deg2rad(31)),refs['Dec(deg)']-31))
design=np.column_stack((np.ones(len(refs)),rx)); target=refs['Rotation_Measure(rad/m2)'].to_numpy()
coef=np.linalg.lstsq(design,target,rcond=None)[0]
prediction=np.column_stack((np.ones(len(b)),xy))@coef
loo_plane=[];loo_constant=[]
for i in range(len(refs)):
    take=np.arange(len(refs))!=i
    loo_plane.append(design[i]@np.linalg.lstsq(design[take],target[take],rcond=None)[0]-target[i])
    loo_constant.append(target[take].mean()-target[i])
pd.DataFrame({'ID#':b['ID#'],'plane_reference_RM':prediction,
 'plane_cloud_RM':b.RM_Raw_Value-prediction,'adopted_cloud_RM':b.Scaled_RM}).to_csv(OUT/'tables/foreground_plane_sensitivity.csv',index=False)

# Corrected m=3 uncertainty propagation uses source IDs throughout.
keep=b.Extinction>=3*ref_av
m3base=b[keep]
m3final=combine_uncertainties(m3base,**models)
m3final.to_csv(OUT/'corrected/multiplier3_results.tsv',sep='\t',index=False)

delta=100*(b['Magnetic_Field(uG)'].to_numpy()/old['Magnetic_Field(uG)'].to_numpy()-1)
audit=pd.DataFrame({'ID#':b['ID#'],'old_B':old['Magnetic_Field(uG)'],
                   'corrected_B':b['Magnetic_Field(uG)'],'change_percent':delta})
audit.to_csv(OUT/'tables/numerical_correction.csv',index=False)
report={'n':len(b),'reference_rm':ref_rm,'reference_sem':ref_sem,'reference_av':ref_av,
 'median_abs_B':b['Magnetic_Field(uG)'].abs().median(),'mean_abs_B':b['Magnetic_Field(uG)'].abs().mean(),
 'min_B':b['Magnetic_Field(uG)'].min(),'max_B':b['Magnetic_Field(uG)'].max(),
 'std_B':b['Magnetic_Field(uG)'].std(ddof=1),'median_change_percent':np.median(delta),
 'max_abs_change_percent':max(abs(delta)),'unbounded_extinction':int(final.UnboundedExtinctionSensitivity.sum()),
 'sign_changes_from_correction':int((np.sign(b['Magnetic_Field(uG)'])!=np.sign(old['Magnetic_Field(uG)'])).sum()),
 'positive':int((b.Scaled_RM>0).sum()),'negative':int((b.Scaled_RM<0).sum()),
 'positive_2sigma':int((b.RM_sign_score>2).sum()),'negative_2sigma':int((b.RM_sign_score<-2).sum()),
 'clean_n':int(clean.sum()),'clean_positive':int((b.loc[clean,'Scaled_RM']>0).sum()),
 'clean_negative':int((b.loc[clean,'Scaled_RM']<0).sum()),
 'clean_median_abs_B':b.loc[clean,'Magnetic_Field(uG)'].abs().median(),
 'clean_reference_n':len(clean_refs),'clean_reference_ids':clean_refs['ID#'].tolist(),
 'literature_total':len(lit),'faraday_position_matches':len(matches),
 'faraday_same_nominal_sign':int((np.sign(matches.B)==np.sign(matches['VLA_Magnetic_Field(uG)'])).sum()),
 'rm_match_median_residual':float(np.median(matches.VLA_RM_Raw_Value-matches.RM)),
 'rm_match_large_residual_n':int((abs(matches.RM_residual_sigma)>3).sum()),
 'ensemble':ensemble,'regions':regions,'simulation':simulation,
 'foreground_plane':{'coefficients':coef.tolist(),'loo_rmse_plane':float(np.sqrt(np.mean(np.array(loo_plane)**2))),
  'loo_rmse_constant':float(np.sqrt(np.mean(np.array(loo_constant)**2))),
  'sign_changes':int((np.sign(b.RM_Raw_Value-prediction)!=np.sign(b.Scaled_RM)).sum())}}
if len(clean_refs)>=2:
    cr=clean_refs['Rotation_Measure(rad/m2)'].mean()
    report['clean_reference_rm']=cr
    report['clean_reference_sign_changes']=int((np.sign(b.RM_Raw_Value-cr)!=np.sign(b.Scaled_RM)).sum())
    cq=calculate(rm=cr,av=clean_refs.Extinction_Value.mean(),
                 sem=clean_refs['Rotation_Measure(rad/m2)'].std(ddof=1)/np.sqrt(len(clean_refs)))
    cq.to_csv(OUT/'corrected/clean_reference_BLOS.tsv',sep='\t',index=False)
report['foreground_plane']['sources_inside_reference_hull']=int((Delaunay(rx).find_simplex(xy)>=0).sum())
report['foreground_plane']['reference_prediction_range']=[float(prediction.min()),float(prediction.max())]

newb=b[b['ID#']==205]
newb.to_csv(OUT/'tables/missing_published_source_recalculated.csv',index=False)
report['catalog_discrepancy']={'local_unmatched_id':121,'published_missing_source':new.Source,
 'published_source_raw_extinction':float(map_hdu.data[ny,nx]),
 'adopted_treatment':'Published membership; local linear interpolation of invalid central extinction.',
 'published_source_extinction':float(newb.Extinction.iloc[0]),
 'published_source_B':float(newb['Magnetic_Field(uG)'].iloc[0]),
 'archived_n':len(archived_b),'archived_positive':int((archived_b.Scaled_RM>0).sum()),
 'archived_negative':int((archived_b.Scaled_RM<0).sum()),
 'archived_median_abs_B':float(archived_b['Magnetic_Field(uG)'].abs().median()),
 'archived_mean_abs_B':float(archived_b['Magnetic_Field(uG)'].abs().mean())}

# Recheck the stability recommendation on the original filtered pool, keeping
# source-selection constraints distinct from the numerical correction.
from LocalLibraries import OptimalRefPoints as optimal
from types import SimpleNamespace
trend=optimal.findTrendData(read('IntermediateData/FilteredPotRefPoints.csv'),matched,
                           SimpleNamespace(AvFilePath=str(CHEM/'Av_T0_n0.out')))
choices=optimal.stabilityCheckAlg(trend)
report['corrected_stability_reference_count']=optimal.mode([v for v in choices if 5<=v<=len(matched)])
trend.to_csv(OUT/'tables/corrected_reference_trends.csv',index=False)
finite_trend=trend.replace([np.inf,-np.inf],np.nan).dropna()
fig,ax=plt.subplots(figsize=(6,4)); tx=np.arange(1,trend.shape[1]+1)
q=np.percentile(finite_trend,[10,25,50,75,90],axis=0)
ax.fill_between(tx,q[0],q[4],color='tab:blue',alpha=.12)
ax.fill_between(tx,q[1],q[3],color='tab:blue',alpha=.25)
ax.plot(tx,q[2],color='tab:blue');ax.axvline(8,ls='--',color='black')
ax.set(xlabel='Number of reference points',ylabel=r'Median $B_\parallel$ ($\mu$G)')
savefig(fig,'stability_option2_summary')

fig,ax=plt.subplots(figsize=(6,4))
ax.scatter(old.Extinction,delta,s=15,color='0.25'); ax.axhline(0,color='0.6',lw=.8)
ax.set(xlabel=r'Observed $A_V$ (mag)',ylabel=r'Change in $B_\parallel$ (%)')
savefig(fig,'numerical_correction')
fig,axs=plt.subplots(1,2,figsize=(10,4))
for _,r in matches.iterrows():
    color='tab:orange' if r.VLA_F1!=0 or r.VLA_F2!=0 else 'tab:blue'
    axs[0].errorbar(r.RM,r.VLA_RM_Raw_Value,xerr=r.NVSS_RM_error,yerr=r.VLA_RM_Raw_Err,fmt='o',color=color)
    if np.isfinite(r.VLA_Upper) and np.isfinite(r.VLA_Lower):
        axs[1].errorbar(r.B,r['VLA_Magnetic_Field(uG)'],xerr=[[r.Lower],[r.Upper]],
                       yerr=[[r.VLA_Lower],[r.VLA_Upper]],fmt='o',color=color,alpha=.8)
    else:
        axs[1].errorbar(r.B,r['VLA_Magnetic_Field(uG)'],xerr=[[r.Lower],[r.Upper]],
                       yerr=[[r.VLA_Lower],[0]],fmt='^',color=color)
        axs[1].annotate('',xy=(r.B,r['VLA_Magnetic_Field(uG)']+350),
                         xytext=(r.B,r['VLA_Magnetic_Field(uG)']),
                         arrowprops={'arrowstyle':'->','color':color})
    for ax,x,y in [(axs[0],r.RM,r.VLA_RM_Raw_Value),(axs[1],r.B,r['VLA_Magnetic_Field(uG)'])]:
        if r.Literature_ID in [2,4,9,10,14,19]:
            offset=(5,10) if r.Literature_ID!=19 else (10,-15)
            ax.annotate(str(int(r.Literature_ID)),(x,y),xytext=offset,textcoords='offset points',fontsize=8)
for ax in axs:
    low=min(ax.get_xlim()[0],ax.get_ylim()[0]);high=max(ax.get_xlim()[1],ax.get_ylim()[1])
    ax.plot([low,high],[low,high],'--',color='0.5',zorder=0); ax.set_xlim(low,high);ax.set_ylim(low,high)
axs[0].set(xlabel=r'NVSS RM (rad m$^{-2}$)',ylabel=r'VLA RM (rad m$^{-2}$)')
axs[1].set(xlabel=r'Published $B_\parallel$ ($\mu$G)',ylabel=r'Corrected $B_\parallel$ ($\mu$G)')
fig.tight_layout();savefig(fig,'faraday_comparison')

hdu=fits.open(ROOT/'Data/2015_02_CalTauPer_toBernsteinCooper.fits')[0];wcs=WCS(hdu.header)
def mapaxes():
    fig=plt.figure(figsize=(8,6)); ax=fig.add_subplot(111,projection=wcs)
    ax.imshow(hdu.data,origin='lower',cmap='Greys',vmin=0,vmax=6)
    px,py=wcs.world_to_pixel(coords(b));ax.set_xlim(px.min()-20,px.max()+20);ax.set_ylim(py.min()-20,py.max()+20)
    ax.set_xlabel('Right ascension (J2000)');ax.set_ylabel('Declination (J2000)')
    return fig,ax
fig,ax=mapaxes()
persistent=pd.read_csv(OUT/'tables/eligible_sign_persistence.csv')
for sign,color,label in [(1,'blue','Persistent toward'),(-1,'red','Persistent away'),(0,'0.6','Reference-sensitive')]:
    d=persistent[persistent.persistent_sign==sign]
    ax.scatter(d['Ra(deg)'],d['Dec(deg)'],transform=ax.get_transform('world'),s=22,color=color,label=f'{label} ({len(d)})')
ax.scatter(lit['Ra(deg)'],lit['Dec(deg)'],transform=ax.get_transform('world'),s=55,
           facecolors='none',edgecolors=np.where(lit.B>0,'blue','red'),marker='s',label='Tahani et al. 2018')
xline=np.linspace(750,1100,100);ax.plot(xline,slope*xline+intercept,'--',color='darkgreen',label='Extinction-derived axis')
ax.legend(fontsize=8,loc='upper right');savefig(fig,'spatial_robustness')
fig,ax=mapaxes()
ax.scatter(b['Ra(deg)'],b['Dec(deg)'],transform=ax.get_transform('world'),
 s=np.clip(abs(b['Magnetic_Field(uG)'])*.35,12,200),color=np.where(b.Scaled_RM>0,'blue','red'),alpha=.65)
ax.scatter(refs['Ra(deg)'],refs['Dec(deg)'],transform=ax.get_transform('world'),s=35,color='green')
savefig(fig,'BLOSPointMap')
fig,axs=plt.subplots(1,3,figsize=(12,4))
for ax,(_,r) in zip(axs,zee.iterrows()):
    center=SkyCoord(r['Ra(deg)']*u.deg,r['Dec(deg)']*u.deg)
    dx,dy=center.spherical_offsets_to(coords(b));x=dx.arcmin;y=dy.arcmin
    ax.scatter(x,y,c=np.where(b.Scaled_RM>0,'blue','red'),s=20)
    ax.add_patch(plt.Circle((0,0),r.FWHM_arcmin/2,fill=False,color='black'))
    ax.plot(0,0,'k*',ms=10)
    for j in np.where(np.hypot(x,y)<25)[0]:ax.annotate(str(int(b.iloc[j]['ID#'])),(x[j],y[j]),fontsize=7)
    ax.set(xlim=(25,-25),ylim=(-25,25),title=r.Region,xlabel='East offset (arcmin)',ylabel='North offset (arcmin)')
    ax.set_aspect('equal')
fig.tight_layout();savefig(fig,'zeeman_local_maps')
fig,ax=plt.subplots(figsize=(6,4))
bins=np.linspace(-1050,1050,31)
for mask,color in [(b.Scaled_RM>0,'blue'),(b.Scaled_RM<0,'red')]:
    ax.hist(b.loc[mask,'Magnetic_Field(uG)'],bins=bins,color=color,alpha=.6)
ax.axvline(b['Magnetic_Field(uG)'].median(),color='green',ls='--')
ax.set(xlabel=r'$B_\parallel$ ($\mu$G)',ylabel='Sight lines');savefig(fig,'BLOS_histogram')

(OUT/'tables/analysis_summary.json').write_text(json.dumps(report,indent=2,default=lambda v:v.item())+'\n')
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
          for p in [ROOT/'LocalLibraries/CalculateB.py',ROOT/'LocalLibraries/Uncertainty.py',
                    ROOT/'LocalLibraries/config.py',
                    ROOT/'revise_paper_analysis.py',OUT/'sources/paper1_published_table2.txt',
                    BASE/'FinalData/BLOSPoints.csv',BASE/'FinalData/SelectedRefPoints.csv',
                    CHEM/'Av_T0_n0.out']}
for path in [*CHEM.glob('Av_T*_n*.out'), ROOT/'Data/2015_02_CalTauPer_toBernsteinCooper.fits',
             ROOT/'Data/RMCatalog/catalog.dat',OUT/'sources/tahani2018.pdf',
             OUT/'sources/goodman1989.pdf',OUT/'sources/troland2008.pdf']:
    manifest[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
(OUT/'tables/input_sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(report,indent=2,default=lambda v:v.item()))
