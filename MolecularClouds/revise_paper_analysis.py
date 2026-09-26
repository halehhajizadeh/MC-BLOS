"""Reproduce the Perseus paper in the standard FileOutput_ImprovedPlots location.

Run from MolecularClouds: ../.venv/bin/python revise_paper_analysis.py
Uses the current pipeline references and configured ON extinction multiplier.
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
from scipy.spatial import Delaunay, ConvexHull
from scipy.interpolate import griddata
from LocalLibraries.CalculateB import CalculateB
from LocalLibraries.Uncertainty import combine_uncertainties
from LocalLibraries import config
from LocalLibraries.PaperDiagnostics import write_diagnostics

ROOT = Path(__file__).resolve().parent
BASE = Path(config.CloudOutputDir)
TABLES = BASE / 'PaperTables'
FINAL = BASE / 'FinalData'
PLOTS = BASE / 'Plots'
SOURCES = ROOT / 'Data'
CHEM = ROOT / 'Data/ChemicalAbundance/n1.0e3_T12.0_G1'
for directory in [TABLES, FINAL, PLOTS]:
    directory.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family': 'serif', 'mathtext.fontset': 'stix', 'font.size': 10})
warnings.filterwarnings('ignore', category=FutureWarning)

def read(name):
    return pd.read_csv(BASE / name, sep='\t')

def coords(df):
    return SkyCoord(df['Ra(deg)'].to_numpy()*u.deg, df['Dec(deg)'].to_numpy()*u.deg)

def savefig(fig, name):
    for ext in ['pdf', 'png']:
        fig.savefig(PLOTS / f'{name}.{ext}', dpi=180, bbox_inches='tight')
    plt.close(fig)

matched = read('FinalData/MatchedRMExtinction.csv')
refs = read('FinalData/SelectedRefPoints.csv')
ref_rm = refs['Rotation_Measure(rad/m2)'].mean()
ref_av = refs.Extinction_Value.mean()
ref_sem = refs['Rotation_Measure(rad/m2)'].std(ddof=1) / np.sqrt(len(refs))
ref_avgerr = refs['RM_Err(rad/m2)'].mean()
on = matched[~matched['ID#'].isin(refs['ID#'])].copy().reset_index(drop=True)

def calculate(points=None, t='0', n='0', rm=ref_rm, av=ref_av, sem=ref_sem):
    if points is None:
        points=on
    return CalculateB(str(CHEM / f'Av_T{t}_n{n}.out'), points,
                      rm, ref_avgerr, sem, av)

# Source quality: author's complete Paper I machine-readable catalog.
rows = []
for line in (SOURCES/'RMCatalog/paper1_published_table2.txt').read_text().splitlines():
    if line.startswith('VCPMC '):
        z = line.split()
        rows.append([' '.join(z[:2])] + list(map(float,z[2:9])) + list(map(int,z[9:11])))
p1 = pd.DataFrame(rows, columns=['Source','Ra(deg)','Dec(deg)','RM','RM_error',
                                'fracpol','flux','noise','F1','F2'])
assert len(p1)==205

orig_ix,orig_sep,_=coords(matched).match_to_catalog_sky(coords(p1))
orig_valid=orig_sep.arcsec<.1
assert orig_valid.sum() in (204, 205)
missing = p1.iloc[[j for j in range(len(p1)) if j not in orig_ix[orig_valid]]]
map_hdu = fits.open(ROOT/'Data/2015_02_CalTauPer_toBernsteinCooper.fits')[0]
map_wcs = WCS(map_hdu.header)
if len(missing):
    assert len(missing)==1 and matched.loc[~orig_valid, 'ID#'].tolist()==[121]
    new = missing.iloc[0]
    ny, nx = map_wcs.world_to_array_index_values(new['Ra(deg)'], new['Dec(deg)'])
    ny, nx = int(ny), int(nx)
    patch = map_hdu.data[ny-2:ny+3,nx-2:nx+3]
    good = np.isfinite(patch) & (patch>=0)
    gy,gx = np.indices(patch.shape)
    interpolated_av = float(griddata(np.column_stack((gx[good],gy[good])),patch[good],[[2,2]],method='linear')[0])
    assert np.isfinite(interpolated_av) and interpolated_av>1
    newrow = matched.iloc[0].copy()
    for col,value in {'ID#':205,'Ra(deg)':new['Ra(deg)'],'Dec(deg)':new['Dec(deg)'],
       'Rotation_Measure(rad/m2)':new.RM,'RM_Err(rad/m2)':new.RM_error,
       'Extinction_Index_x':nx,'Extinction_Index_y':ny,'Extinction_Value':interpolated_av,
       'Min_Extinction_Value':patch[good].min(),'Max_Extinction_Value':patch[good].max(),
       'Extinction_Observed':False,'Error_Range(pix)':2}.items():
        newrow[col]=value
    for prefix,xx,yy in [('center',nx,ny),
       ('min',nx-2+int(gx[good][np.argmin(patch[good])]),ny-2+int(gy[good][np.argmin(patch[good])])),
       ('max',nx-2+int(gx[good][np.argmax(patch[good])]),ny-2+int(gy[good][np.argmax(patch[good])]))]:
        ra,dec=map_wcs.wcs_pix2world(xx,yy,0)
        cols={'center':('RA_inExtincFile(degree)','Dec_inExtincFile(degree)'),
              'min':('Min_Extinction_Ra','Min_Extinction_Dec'),
              'max':('Max_Extinction_RA','Max_Extinction_dec')}[prefix]
        newrow[cols[0]]=float(ra);newrow[cols[1]]=float(dec)
    matched=pd.concat([matched[orig_valid],pd.DataFrame([newrow])],ignore_index=True)
else:
    # Exclude local catalog entries absent from the published Paper I sample.
    matched=matched.loc[orig_valid].copy().reset_index(drop=True)
assert set(refs['ID#']).issubset(set(matched['ID#']))
on=matched[~matched['ID#'].isin(refs['ID#']) & (matched.Extinction_Value>=config.onPtsExtMultipleThreshold*ref_av)].copy().reset_index(drop=True)
assert len(on)>0
b = calculate()
models = {}
for key, t, n in [('density_plus','0','+50'),('density_minus','0','-50'),
                  ('temp_plus','+20','0'),('temp_minus','-20','0')]:
    models[key] = calculate(t=t, n=n)
    models[key].to_csv(FINAL / f'{key}.tsv', sep='\t', index=False)
# Refresh the usual sensitivity-stage products on the same published membership.
for name, perturbations in [('DensitySensitivity', ['0','+1','-1','+2.5','-2.5','+5','-5','+10','-10','+20','-20','+30','-30','+40','-40','+50','-50']),
                            ('TemperatureSensitivity', ['0','+5','-5','+10','-10','+20','-20'])]:
    for perturbation in perturbations:
        t,n=('0',perturbation) if name=='DensitySensitivity' else (perturbation,'0')
        calculate(t=t,n=n).to_csv(BASE/name/f'B_Av_T{t}_n{n}.csv',sep='\t',index=False)
final = combine_uncertainties(b, **models)
b.to_csv(FINAL/'BLOSPoints.csv', sep='\t', index=False)
final.to_csv(FINAL/'FinalBLOSResults.csv', sep='\t', index=False)
matched.to_csv(FINAL/'MatchedRMExtinction.csv',sep='\t',index=False)

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
quality.to_csv(TABLES/'paper1_crossmatch.csv',index=False)
b=b.merge(quality[['ID#','Source','F1','F2']],on='ID#',validate='one_to_one')
b['Extinction_Interpolated'] = b['ID#'].map(matched.set_index('ID#')['Extinction_Observed']).eq(False)
clean=(b.F1==0)&(b.F2==0)
clean_refs=refs.merge(quality[['ID#','F1','F2']],on='ID#')
clean_refs=clean_refs[(clean_refs.F1==0)&(clean_refs.F2==0)]

# Original Table 6 is parsed from its archived PDF text, not manually rounded anew.
txt=(SOURCES/'tahani2018.txt').read_text()
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
lit.to_csv(TABLES/'tahani2018_perseus.csv',index=False)
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
comparison.to_csv(TABLES/'faraday_matches_all.csv',index=False)
matches=comparison[comparison.position_match].copy()
assert not matches.VLA_ID.duplicated().any()
matches.to_csv(TABLES/'faraday_matches.csv',index=False)

# Original Goodman 1989 Figure 1 pointing (B1950); Troland 2008 Table 1 (J2000).
# Beam sizes are FWHM diameters.
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
zee.to_csv(TABLES/'zeeman_comparison.csv',index=False)

# Broad pool recreates the original 14 candidates, including the close pair.
cand=read('FinalData/AllPotentialRefPoints.csv')
near=set(read('IntermediateData/NearHighExtRej.csv')['ID#'])
pool=cand[~cand['ID#'].isin(near)].copy().reset_index(drop=True)
from LocalLibraries.RefJudgeLib import separateReferencePoints
eligible, _ = separateReferencePoints(pool, config.minRefSeparationArcmin)
eligible = eligible.reset_index(drop=True)
_,minimum_separation,_=coords(eligible).match_to_catalog_sky(coords(eligible),nthneighbor=2)
assert minimum_separation.arcmin.min()>=config.minRefSeparationArcmin
ensemble={}
for name,p in [('broad',pool),('eligible',eligible)]:
    sets=list(combinations(range(len(p)),len(refs)))
    means=np.array([p.iloc[list(c)]['Rotation_Measure(rad/m2)'].mean() for c in sets])
    avs=np.array([p.iloc[list(c)].Extinction_Value.mean() for c in sets])
    common=b[(~b['ID#'].isin(p['ID#'])) & (b.Extinction>=config.onPtsExtMultipleThreshold*avs.max())].copy()
    common['persistent_sign']=np.where(common.RM_Raw_Value>means.max(),1,
                               np.where(common.RM_Raw_Value<means.min(),-1,0))
    common.to_csv(TABLES/f'{name}_sign_persistence.csv',index=False)
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
b.to_csv(FINAL/'catalog_with_flags.csv',index=False)
regions=[]
for sample,mask in [('all',np.ones(len(b),bool)),('F1=0,F2=0',clean),('m=3',b.Extinction>=3*ref_av)]:
    for side in ['north','south']:
        d=b[mask & (b.axis_side==side)]
        regions.append(dict(sample=sample,side=side,n=len(d),positive=int((d.Scaled_RM>0).sum()),
             negative=int((d.Scaled_RM<0).sum()),positive_2sigma=int((d.RM_sign_score>2).sum()),
             negative_2sigma=int((d.RM_sign_score<-2).sum()),median_abs_B=d['Magnetic_Field(uG)'].abs().median()))
pd.DataFrame(regions).to_csv(TABLES/'region_statistics.csv',index=False)
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
 'plane_cloud_RM':b.RM_Raw_Value-prediction,'adopted_cloud_RM':b.Scaled_RM}).to_csv(TABLES/'foreground_plane_sensitivity.csv',index=False)

# Corrected m=3 uncertainty propagation uses source IDs throughout.
keep=b.Extinction>=3*ref_av
m3base=b[keep]
m3final=combine_uncertainties(m3base,**models)
m3final.to_csv(FINAL/'multiplier3_results.tsv',sep='\t',index=False)

report={'n':len(b),'reference_count':len(refs),'on_point_multiplier':config.onPtsExtMultipleThreshold,'reference_rm':ref_rm,'reference_sem':ref_sem,'reference_av':ref_av,
 'median_abs_B':b['Magnetic_Field(uG)'].abs().median(),'mean_abs_B':b['Magnetic_Field(uG)'].abs().mean(),
 'min_B':b['Magnetic_Field(uG)'].min(),'max_B':b['Magnetic_Field(uG)'].max(),
 'std_B':b['Magnetic_Field(uG)'].std(ddof=1),
 'unbounded_extinction':int(final.UnboundedExtinctionSensitivity.sum()),
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
    cq.to_csv(FINAL/'clean_reference_BLOS.tsv',sep='\t',index=False)
report['foreground_plane']['sources_inside_reference_hull']=int((Delaunay(rx).find_simplex(xy)>=0).sum())
report['foreground_plane']['reference_prediction_range']=[float(prediction.min()),float(prediction.max())]

# Recheck the stability recommendation on the original filtered pool, keeping
# source-selection constraints distinct from the numerical correction.
from LocalLibraries import OptimalRefPoints as optimal
from types import SimpleNamespace
trend=optimal.findTrendData(pool,matched,
                           SimpleNamespace(AvFilePath=str(CHEM/'Av_T0_n0.out')))
choices=optimal.stabilityCheckAlg(trend)
report['corrected_stability_reference_count']=optimal.mode([v for v in choices if 5<=v<=len(matched)])
eligible_trend=optimal.findTrendData(eligible,matched,
                           SimpleNamespace(AvFilePath=str(CHEM/'Av_T0_n0.out')))
eligible_choices=optimal.stabilityCheckAlg(eligible_trend)
alternate_n=int(optimal.mode([v for v in eligible_choices if 5<=v<=len(eligible)]))
alternate_refs=eligible.iloc[:alternate_n]
ar=alternate_refs['Rotation_Measure(rad/m2)'].mean()
aa=alternate_refs.Extinction_Value.mean()
alternate_on=matched[(~matched['ID#'].isin(alternate_refs['ID#'])) & (matched.Extinction_Value>=config.onPtsExtMultipleThreshold*aa)]
alternate_b=calculate(points=alternate_on,rm=ar,av=aa,sem=alternate_refs['Rotation_Measure(rad/m2)'].sem())
alternate_b.to_csv(FINAL/'separation_first_BLOS.csv',sep='\t',index=False)
shared=b.merge(alternate_b[['ID#','Scaled_RM']],on='ID#',suffixes=('_adopted','_alternate'))
report['separation_first_selection']={'count':alternate_n,'reference_rm':float(ar),
 'reference_av':float(aa),'n_on':len(alternate_b),'common_on':len(shared),
 'changed_signs_common':int((np.sign(shared.Scaled_RM_adopted)!=np.sign(shared.Scaled_RM_alternate)).sum())}
trend.to_csv(TABLES/'corrected_reference_trends.csv',index=False)
finite_trend=trend.replace([np.inf,-np.inf],np.nan).dropna()
fig,ax=plt.subplots(figsize=(6,4)); tx=np.arange(1,trend.shape[1]+1)
q=np.percentile(finite_trend,[10,25,50,75,90],axis=0)
ax.fill_between(tx,q[0],q[4],color='tab:blue',alpha=.12)
ax.fill_between(tx,q[1],q[3],color='tab:blue',alpha=.25)
ax.plot(tx,q[2],color='tab:blue');ax.axvline(len(refs),ls='--',color='black')
ax.set_xticks(tx)
ax.set(xlabel='Number of reference points',ylabel=r'Median $B_\parallel$ ($\mu$G)')
savefig(fig,'stability_option2_summary')

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
    im=ax.imshow(hdu.data,origin='lower',cmap='Greys',vmin=0,vmax=6)
    fig.colorbar(im,ax=ax,pad=.03,label=r'$A_V$ (mag)',extend='max',shrink=.85)
    px,py=wcs.world_to_pixel(coords(b));ax.set_xlim(px.min()-20,px.max()+20);ax.set_ylim(py.min()-20,py.max()+20)
    ax.set_xlabel('Right ascension (J2000)');ax.set_ylabel('Declination (J2000)')
    return fig,ax
fig,ax=mapaxes()
persistent=pd.read_csv(TABLES/'eligible_sign_persistence.csv')
for sign,color,label in [(1,'blue','Persistent toward'),(-1,'red','Persistent away'),(0,'0.6','Reference-sensitive')]:
    d=persistent[persistent.persistent_sign==sign]
    ax.scatter(d['Ra(deg)'],d['Dec(deg)'],transform=ax.get_transform('world'),s=22,color=color,label=f'{label} ({len(d)})')
xline=np.linspace(750,1100,100);ax.plot(xline,slope*xline+intercept,'--',color='darkgreen',label='Extinction-derived axis')
ax.scatter(refs['Ra(deg)'],refs['Dec(deg)'],transform=ax.get_transform('world'),s=40,color='green',marker='s',label='OFF references')
ax.legend(fontsize=8,loc='upper right');savefig(fig,'spatial_robustness')
fig,ax=mapaxes()
for mask,marker,label in [(clean,'o','F1=F2=0'),(~clean,'x','Nonzero quality flag')]:
    ax.scatter(b.loc[mask,'Ra(deg)'],b.loc[mask,'Dec(deg)'],transform=ax.get_transform('world'),
     s=np.clip(abs(b.loc[mask,'Magnetic_Field(uG)'])*.35,12,200),
     color=np.where(b.loc[mask,'Scaled_RM']>0,'#2166ac','#b2182b'),marker=marker,alpha=.75,label=label)
ax.scatter(refs['Ra(deg)'],refs['Dec(deg)'],transform=ax.get_transform('world'),s=40,color='green',marker='s',label='OFF references')
ax.plot(xline,slope*xline+intercept,'--',color='darkgreen',label='Extinction-derived axis')
ax.legend(fontsize=8)
savefig(fig,'BLOSPointMap')
fig,ax=mapaxes()
same=np.sign(b.RM_Raw_Value-prediction)==np.sign(b.Scaled_RM)
ax.scatter(b['Ra(deg)'],b['Dec(deg)'],transform=ax.get_transform('world'),
           s=25,c=np.where(same,'0.6','#e66101'))
hull=ConvexHull(rx);vertices=np.r_[hull.vertices,hull.vertices[0]]
ax.plot(refs.iloc[vertices]['Ra(deg)'],refs.iloc[vertices]['Dec(deg)'],transform=ax.get_transform('world'),color='green',label='OFF convex hull')
ax.scatter(refs['Ra(deg)'],refs['Dec(deg)'],transform=ax.get_transform('world'),s=40,color='green',marker='s')
ax.set_title('Orange: sign changes under plane foreground',fontsize=11)
ax.legend(fontsize=8)
savefig(fig,'foreground_sensitivity')
fig,axs=plt.subplots(1,3,figsize=(12,4))
for ax,(_,r) in zip(axs,zee.iterrows()):
    center=SkyCoord(r['Ra(deg)']*u.deg,r['Dec(deg)']*u.deg)
    dx,dy=center.spherical_offsets_to(coords(b));x=dx.arcmin;y=dy.arcmin
    for use,marker in [(clean,'o'),(~clean,'x')]:
        ax.scatter(x[use],y[use],c=np.where(b.loc[use,'Scaled_RM']>0,'blue','red'),s=20,marker=marker)
    ax.add_patch(plt.Circle((0,0),r.FWHM_arcmin/2,fill=False,color='black'))
    ax.plot(0,0,'k*',ms=10)
    ax.text(.04,.97,rf'OH: $+{r.B:g}\pm{r.Error:g}\,\mu$G'+f'\nNearest: {r.separation_arcmin:.2f} arcmin',transform=ax.transAxes,va='top',fontsize=9)
    nearest=int(np.argmin(center.separation(coords(b)).arcmin))
    ax.plot([0,x[nearest]],[0,y[nearest]],'--',color='0.5',lw=.8)
    ax.annotate(f'ID {int(b.iloc[nearest]["ID#"])}',(x[nearest],y[nearest]),xytext=(4,6),textcoords='offset points',fontsize=9)
    ax.set(xlim=(25,-25),ylim=(-25,25),title=r.Region,xlabel='East offset (arcmin)',ylabel='North offset (arcmin)')
    ax.set_aspect('equal')
fig.tight_layout();savefig(fig,'zeeman_local_maps')
fig,ax=plt.subplots(figsize=(6,4))
bins=np.linspace(-1050,1050,31)
for mask,color in [(b.Scaled_RM>0,'blue'),(b.Scaled_RM<0,'red')]:
    ax.hist(b.loc[mask,'Magnetic_Field(uG)'],bins=bins,color=color,alpha=.6)
ax.axvline(b['Magnetic_Field(uG)'].median(),color='green',ls='--',label='Median signed field')
ax.legend(fontsize=9)
ax.set(xlabel=r'$B_\parallel$ ($\mu$G)',ylabel='Sight lines');savefig(fig,'BLOS_histogram')

write_diagnostics(b,refs,matches,report,TABLES,FINAL,PLOTS)
(TABLES/'analysis_summary.json').write_text(json.dumps(report,indent=2,default=lambda v:v.item())+'\n')
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
          for p in [ROOT/'LocalLibraries/CalculateB.py',ROOT/'LocalLibraries/Uncertainty.py',
                    ROOT/'LocalLibraries/config.py',ROOT/'LocalLibraries/PaperDiagnostics.py',
                    ROOT/'configStartSettings.ini',ROOT/'configDirectoryAndNames.ini',
                    ROOT/'Data/CloudParameters/perseus.ini',
                    ROOT/'revise_paper_analysis.py',SOURCES/'RMCatalog/paper1_published_table2.txt',
                    BASE/'FinalData/MatchedRMExtinction.csv',BASE/'FinalData/SelectedRefPoints.csv',
                    BASE/'FinalData/AllPotentialRefPoints.csv',
                    BASE/'IntermediateData/QuadrantDivisionData.csv',
                    CHEM/'Av_T0_n0.out']}
for path in [*CHEM.glob('Av_T*_n*.out'), ROOT/'Data/2015_02_CalTauPer_toBernsteinCooper.fits',
             ROOT/'Data/RMCatalog/catalog.dat',SOURCES/'tahani2018.pdf',
             SOURCES/'tahani2018.txt']:
    manifest[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
(TABLES/'input_sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(report,indent=2,default=lambda v:v.item()))
