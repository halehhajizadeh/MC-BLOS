"""Reproduce nominal movie fields and summarize reference-choice sensitivity.

Run from MolecularClouds. Outputs stay within Perseus_test/statistics.
Uses the existing electron-column helpers, including their interpolation
convention, to reproduce the movie rather than changing the physical model.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from LocalLibraries import config
from LocalLibraries.RegionOfInterest import Region
from LocalLibraries.CalculateB import CalculateB, findLayerOfInterest, electronColumnDensity


def main():
    base = Path(config.FileOutputDir) / 'Perseus_test'
    out = base / 'statistics'
    out.mkdir(exist_ok=True)
    meta = pd.read_csv(base / 'reference_combinations.csv')
    matched = pd.read_csv(config.MatchedRMExtinctionFile, sep=config.dataSeparator)
    candidates = pd.read_csv(config.FilteredRefPointsFile, sep=config.dataSeparator)
    region = Region(config.cloud)
    abundance = pd.read_csv(region.AvFilePath, sep=r'\s+', skiprows=1)
    av, xe = abundance['Av'].to_numpy(), abundance['e-'].to_numpy()
    ids = matched['ID#'].to_numpy()
    observed = matched['Rotation_Measure(rad/m2)'].to_numpy()
    extinction = matched['Extinction_Value'].to_numpy()
    fields = np.full((len(meta), len(matched)), np.nan)
    checks = {0, int(meta.reference_rm.idxmin()), int(meta.reference_rm.idxmax()), len(meta)-1}
    for k, row in meta.iterrows():
        selected = [int(x) for x in row.reference_ids.split(',')]
        ref = candidates[candidates['ID#'].isin(selected)]
        np.testing.assert_allclose(ref['Rotation_Measure(rad/m2)'].mean(), row.reference_rm)
        np.testing.assert_allclose(ref.Extinction_Value.mean(), row.reference_extinction)
        keep = ~np.isin(ids, selected) & (extinction >= row.on_point_extinction_limit)
        scaled = extinction - row.reference_extinction
        _, layers = findLayerOfInterest(av, xe, scaled)
        ne = np.asarray(electronColumnDensity(av, xe, layers, scaled))
        b = (observed - row.reference_rm) / (0.812 * ne * config.pcTocm * 2)
        if config.negScaledExtOption == 'Delete':
            keep &= scaled >= 0
        elif config.negScaledExtOption == 'Zero':
            b[scaled < 0] = 0
        assert keep.sum() == row.n_blos_points, (k, keep.sum(), row.n_blos_points)
        fields[k, keep] = b[keep]
        if k in checks:
            full = CalculateB(region.AvFilePath, matched.loc[keep], row.reference_rm,
                              row.reference_rm_avg_err, row.reference_rm_sem,
                              row.reference_extinction, config.negScaledExtOption)
            np.testing.assert_allclose(full['Magnetic_Field(uG)'], fields[k, keep], rtol=1e-12)
        if k % 500 == 0:
            print('Calculated', k+1, '/', len(meta), flush=True)
    common = np.isfinite(fields).all(axis=0)
    b = fields[:, common]
    meta['positive_common'] = (b > 0).sum(axis=1)
    meta['negative_common'] = (b < 0).sum(axis=1)
    meta['median_abs_b_common'] = np.median(abs(b), axis=1)
    meta.to_csv(out / 'combination_statistics.csv', index=False)
    np.savez_compressed(out / 'nominal_fields.npz', fields=fields, ids=ids,
                        frames=meta.frame.to_numpy(), common=common)
    source = matched.loc[common, ['ID#', 'Ra(deg)', 'Dec(deg)', 'Extinction_Value']].copy()
    source['positive_fraction'] = (b > 0).mean(axis=0)
    source['B_min'] = b.min(axis=0)
    source['B_median'] = np.median(b, axis=0)
    source['B_max'] = b.max(axis=0)
    source['B_p16'], source['B_p84'] = np.percentile(b, [16, 84], axis=0)
    source.to_csv(out / 'common_sightline_statistics.csv', index=False)
    print('COMMON', common.sum(), 'always positive', (b.min(axis=0)>0).sum(),
          'always negative', (b.max(axis=0)<0).sum(),
          'switch', ((b.min(axis=0)<0)&(b.max(axis=0)>0)).sum())
    print(meta[['reference_rm','positive_common','negative_common','median_abs_b_common']].describe())
    print('EXTREMES', meta.loc[[meta.reference_rm.idxmin(),meta.reference_rm.idxmax()],
          ['frame','reference_rm','positive_common','negative_common','median_abs_b_common']].to_string(index=False))
    plt.rcParams.update({'font.family':'serif','font.size':10,'pdf.fonttype':42})
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), constrained_layout=True)
    axes[0].hist(meta.reference_rm, bins=30, color='slateblue', edgecolor='white')
    axes[0].set(xlabel=r'Reference RM (rad m$^{-2}$)', ylabel='Number of combinations', title='(a) Reference selection')
    axes[1].scatter(meta.reference_rm, meta.positive_common/common.sum(), s=3, color='royalblue')
    axes[1].set(xlabel=r'Reference RM (rad m$^{-2}$)', ylabel='Positive-field fraction', title=f'(b) Same {common.sum()} sight lines', ylim=(0,1))
    axes[2].scatter(meta.reference_extinction, meta.median_abs_b_common, s=4,
                    c=meta.reference_rm, cmap='viridis')
    axes[2].set(xlabel=r'Reference $A_V$ (mag)', ylabel=r'Median $|B_\parallel|$ ($\mu$G)', title='(c) Field magnitude')
    fig.colorbar(axes[2].collections[0], ax=axes[2], label=r'Reference RM (rad m$^{-2}$)')
    fig.savefig(out/'reference_sensitivity_summary.pdf')
    fig.savefig(out/'reference_sensitivity_summary.png', dpi=220)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7,6), constrained_layout=True)
    sc=ax.scatter(source['Ra(deg)'], source['Dec(deg)'], c=source.positive_fraction,
                  cmap='coolwarm_r', vmin=0, vmax=1, s=38, edgecolors='black', linewidths=.3)
    ax.invert_xaxis()
    ax.set(xlabel='RA (degree)', ylabel='Dec (degree)')
    ax.set_aspect(1/np.cos(np.deg2rad(source['Dec(deg)'].mean())))
    fig.colorbar(sc, ax=ax, label='Fraction of combinations with positive field')
    fig.savefig(out/'reference_sign_stability.pdf')
    fig.savefig(out/'reference_sign_stability.png', dpi=220)
    plt.close(fig)


if __name__ == '__main__':
    main()
