"""Diagnostics with explicit reference and sampling assumptions for the paper."""
import numpy as np


def field_difference_steps(rm_old, cloud_old, b_old, rm_new, reference_new, ne_new):
    """Replace observed RM, reference RM, then Ne; return signed additive changes.

    The old Ne is reconstructed from rounded published quantities. Attribution
    is order-dependent, but the sum must equal the complete field difference.
    """
    ne_old = np.asarray(cloud_old) / (.812 * np.asarray(b_old))
    ref_old = np.asarray(rm_old) - np.asarray(cloud_old)
    step_rm = (np.asarray(rm_new) - ref_old) / (.812 * ne_old)
    step_ref = (np.asarray(rm_new) - reference_new) / (.812 * ne_old)
    step_ne = (np.asarray(rm_new) - reference_new) / (.812 * np.asarray(ne_new))
    return ne_old, step_rm - b_old, step_ref - step_rm, step_ne - step_ref


def proximity_groups(separation_arcmin, threshold=1.2):
    """Connected components of an angular proximity graph, not source identities."""
    n = len(separation_arcmin)
    parent = np.arange(n)
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i, j in zip(*np.where(np.triu(separation_arcmin < threshold, 1))):
        parent[root(j)] = root(i)
    return np.unique([root(i) for i in range(n)], return_inverse=True)[1]


def mean_contrast(values, north):
    values, north = np.asarray(values), np.asarray(north, dtype=bool)
    if not north.any() or north.all():
        raise ValueError('Both regions need observations')
    return float(values[north].mean() - values[~north].mean())


def write_diagnostics(b, refs, matches, report, tables, final, plots):
    """Write checks alongside the usual tables/plots; update the summary in place."""
    import pandas as pd
    import matplotlib.pyplot as plt
    from astropy.coordinates import SkyCoord
    from astropy import units as u
    from scipy.spatial import Delaunay
    coords = SkyCoord(b['Ra(deg)'].to_numpy()*u.deg, b['Dec(deg)'].to_numpy()*u.deg)
    angular = coords[:, None].separation(coords[None, :]).arcmin
    clean = (b.F1==0) & (b.F2==0)
    rng = np.random.default_rng(20260922)
    rows, group_rows = [], []
    for name, mask in [('All', np.ones(len(b), bool)), ('Clean', clean),
                       ('m=3', b.Extinction >= 3*report['reference_av'])]:
        d = b.loc[mask].reset_index(drop=True)
        positions = np.flatnonzero(mask)
        groups = proximity_groups(angular[np.ix_(positions, positions)])
        d['proximity_group'] = groups
        d[['ID#','Source','proximity_group']].assign(sample=name).to_csv(
            tables/f'proximity_groups_{name.replace("=", "")}.csv', index=False)
        # Equal group weights reduce the influence of angularly concentrated entries.
        # Groups that straddle the axis are omitted from this sensitivity statistic.
        group = d.groupby('proximity_group').agg(
            rm=('RM_Raw_Value','mean'), side=('axis_side','first'),
            sides=('axis_side','nunique'), n=('ID#','size'))
        usable = group[group.sides==1]
        group_rows.append(dict(sample=name, groups=len(group), multi_entry_groups=int((group.n>1).sum()),
                               cross_axis_groups=int((group.sides>1).sum()), largest_group=int(group.n.max())))
        for method, values, sides in [('Sight lines', d.RM_Raw_Value.to_numpy(), d.axis_side.to_numpy()),
                                     ('Proximity groups', usable.rm.to_numpy(), usable.side.to_numpy())]:
            north = sides=='north'
            a, c = values[north], values[~north]
            # Stratified bootstrap: descriptive sample uncertainty, not a spatial-null test.
            bootstrap = rng.choice(a,(10000,len(a)),replace=True).mean(axis=1) - rng.choice(c,(10000,len(c)),replace=True).mean(axis=1)
            q = np.quantile(bootstrap,[.025,.975])
            rows.append(dict(sample=name, weighting=method, n_north=len(a), n_south=len(c),
                             mean_north=a.mean(), mean_south=c.mean(), delta=mean_contrast(values,north),
                             bootstrap_low=q[0], bootstrap_high=q[1]))
    contrasts = pd.DataFrame(rows)
    contrasts.to_csv(tables/'observed_rm_contrast.csv', index=False)
    report['observed_rm_contrast'] = rows
    report['proximity_groups'] = group_rows
    fig, ax = plt.subplots(figsize=(7,4))
    for i, r in contrasts.iterrows():
        ax.errorbar(r.delta, i, xerr=[[r.delta-r.bootstrap_low],[r.bootstrap_high-r.delta]],
                    fmt='o', color='tab:blue' if r.weighting=='Sight lines' else '0.35', capsize=3)
    ax.set_yticks(np.arange(len(contrasts)))
    ax.set_yticklabels([f'{r["sample"]}: {r["weighting"]}' for r in rows])
    ax.axvline(0, ls='--', color='0.6')
    ax.set_xlabel(r'$\langle {\rm RM}\rangle_N-\langle {\rm RM}\rangle_S$ (rad m$^{-2}$)')
    ax.invert_yaxis()
    fig.tight_layout()
    for ext in ['png','pdf']: fig.savefig(plots/f'observed_rm_contrast.{ext}', dpi=200, bbox_inches='tight')
    plt.close(fig)

    # Ordered input-replacement experiment using published rounded quantities.
    m = matches.copy()
    ne, drm, dref, dne = field_difference_steps(m.RM, m.Cloud_RM, m.B,
        m.VLA_RM_Raw_Value, report['reference_rm'], m.VLA_Electron_Column_pc_cm3)
    m['Ne_literature_reconstructed'] = ne
    m['Ne_ratio_new_old'] = m.VLA_Electron_Column_pc_cm3/ne
    m['delta_B_observed_RM'] = drm
    m['delta_B_reference_RM'] = dref
    m['delta_B_electron_column'] = dne
    m['delta_B_total'] = m['VLA_Magnetic_Field(uG)']-m.B
    np.testing.assert_allclose(drm+dref+dne, m.delta_B_total, atol=1e-10)
    m.to_csv(tables/'faraday_difference_budget.csv', index=False)
    report['ne_ratio_matched'] = dict(min=float(m.Ne_ratio_new_old.min()),
        median=float(m.Ne_ratio_new_old.median()), max=float(m.Ne_ratio_new_old.max()))

    # Leave-one-reference-out changes; recompute the extinction membership rule.
    loo=[]
    for _, r in refs.iterrows():
        ref = refs[refs['ID#']!=r['ID#']]
        rm = ref['Rotation_Measure(rad/m2)'].mean()
        av = ref.Extinction_Value.mean()
        use = b.Extinction>=report.get('on_point_multiplier', 1)*av
        residual = b.RM_Raw_Value-rm
        north = b.axis_side=='north'
        loo.append(dict(omitted_id=int(r['ID#']), reference_rm=rm, reference_av=av,
            n_on=int(use.sum()), changed_signs_common=int(((np.sign(residual)!=np.sign(b.Scaled_RM)) & use).sum()),
            positive_fraction_difference=float((residual[use & north]>0).mean()-(residual[use & ~north]>0).mean())))
    pd.DataFrame(loo).to_csv(tables/'leave_one_reference_out.csv', index=False)
    report['leave_one_reference_out'] = loo

    # Contrast and sign changes for the diagnostic plane, split by interpolation support.
    xy = np.column_stack(((b['Ra(deg)']-52)*np.cos(np.deg2rad(31)),b['Dec(deg)']-31))
    rx = np.column_stack(((refs['Ra(deg)']-52)*np.cos(np.deg2rad(31)),refs['Dec(deg)']-31))
    inside = Delaunay(rx).find_simplex(xy)>=0
    plane = np.column_stack((np.ones(len(b)),xy)) @ np.array(report['foreground_plane']['coefficients'])
    models = {'Constant': np.full(len(b),report['reference_rm']), 'Plane':plane,
              'Clean references':np.full(len(b),report['clean_reference_rm'])}
    foreground=[]
    for model,pred in models.items():
        residual = b.RM_Raw_Value-pred
        for subset, mask in [('All',np.ones(len(b),bool)),('Inside hull',inside),('Outside hull',~inside),('Clean',clean)]:
            north = (b.axis_side=='north') & mask
            south = (b.axis_side=='south') & mask
            foreground.append(dict(model=model, subset=subset, n=int(np.sum(mask)),
                n_north=int(north.sum()), n_south=int(south.sum()),
                changed_signs=int(((np.sign(residual)!=np.sign(b.Scaled_RM)) & mask).sum()),
                delta_mean_cloud_rm=float(residual[north].mean()-residual[south].mean()),
                delta_positive_fraction=float((residual[north]>0).mean()-(residual[south]>0).mean())))
    pd.DataFrame(foreground).to_csv(tables/'foreground_comparison.csv', index=False)
    report['foreground_comparison'] = foreground
    reliability = b[['ID#','Source','Ra(deg)','Dec(deg)','RM_sign_score']].copy()
    reliability['inside_reference_hull'] = inside
    reliability['same_sign_constant_plane'] = np.sign(b.Scaled_RM)==np.sign(b.RM_Raw_Value-plane)
    reliability.to_csv(final/'direction_diagnostics.csv', index=False)

    # Magnitude diagnostic: nominal values, quality flags and unbounded excursions.
    f = pd.read_csv(final/'FinalBLOSResults.csv',sep='\t').set_index('ID#').loc[b['ID#']]
    unbounded = f.UnboundedExtinctionSensitivity.to_numpy(bool)
    extreme = b.assign(UnboundedExtinctionSensitivity=unbounded).sort_values(
        'Magnetic_Field(uG)', key=lambda v:v.abs(), ascending=False).head(10)
    extreme.to_csv(tables/'largest_field_estimates.csv',index=False)
    report['largest_fields'] = extreme[['ID#','Magnetic_Field(uG)','Scaled_RM','Scaled_Extinction',
                                      'Electron_Column_pc_cm3','F1','F2','UnboundedExtinctionSensitivity']].to_dict('records')
    fig, ax = plt.subplots(figsize=(6.5,4.5))
    colors=np.where(b.Scaled_RM>0,'#2166ac','#b2182b')
    for mask, marker in [(clean,'o'),(~clean,'x')]:
        ax.scatter(b.loc[mask,'Scaled_Extinction'],b.loc[mask,'Magnetic_Field(uG)'].abs(),c=colors[mask],marker=marker,s=23)
    ax.scatter(b.loc[unbounded,'Scaled_Extinction'],b.loc[unbounded,'Magnetic_Field(uG)'].abs(),
               facecolors='none',edgecolors='black',s=70,label='Unbounded extinction excursion')
    for _,r in extreme.head(3).iterrows():
        ax.annotate(str(int(r['ID#'])),(r.Scaled_Extinction,abs(r['Magnetic_Field(uG)'])),xytext=(4,5),textcoords='offset points',fontsize=8)
    ax.set(xscale='log',yscale='log',xlabel=r'Cloud $A_V$ (mag)',ylabel=r'Nominal $|B_\parallel|$ ($\mu$G)')
    ax.legend(fontsize=8)
    fig.tight_layout()
    for ext in ['png','pdf']: fig.savefig(plots/f'field_strength_sensitivity.{ext}',dpi=200,bbox_inches='tight')
    plt.close(fig)
