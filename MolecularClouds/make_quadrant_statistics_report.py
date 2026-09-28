"""Validate the working quadrant runs and write a compact PDF report."""
from pathlib import Path
import csv
import hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'Statistics' / 'quadrant_statistics_report.pdf'
DRAWS = 10000
SEED = 0


def weighted_median(x, w):
    order = np.argsort(x)
    x, w = x[order], w[order]
    cumulative = np.cumsum(w)
    half = w.sum() / 2
    i = int(np.searchsorted(cumulative, half))
    if i + 1 < len(x) and np.isclose(cumulative[i], half, rtol=1e-14, atol=0):
        return float((x[i] + x[i + 1]) / 2)
    return float(x[i])


def bootstrap(x):
    sample = np.random.default_rng(SEED).choice(x, (DRAWS, len(x)), replace=True)
    return float(sample.mean(axis=1).std()), float(np.median(sample, axis=1).std())


def weighted_bootstrap(x, w):
    order = np.argsort(x)
    x, w = x[order], w[order]
    counts = np.random.default_rng(SEED).multinomial(
        len(x), np.full(len(x), 1 / len(x)), DRAWS)
    mass = counts * w
    total = mass.sum(axis=1)
    cumulative = np.cumsum(mass, axis=1)
    indexes = (cumulative >= total[:, None] / 2).argmax(axis=1)
    medians = x[indexes].copy()
    for k in np.flatnonzero(np.isclose(
            cumulative[np.arange(DRAWS), indexes], total / 2,
            rtol=1e-14, atol=0)):
        after = np.flatnonzero(mass[k, indexes[k] + 1:] > 0)
        if len(after):
            medians[k] = (x[indexes[k]] + x[indexes[k] + 1 + after[0]]) / 2
    return float((mass @ x / total).std()), float(medians.std())


def calculate(label, group, values, valid, sigma):
    if group == 'all_signed':
        mask = np.isfinite(values)
        x = values[mask]
    elif group == 'positive':
        mask = values > 0
        x = values[mask]
    elif group == 'negative':
        mask = values < 0
        x = values[mask]
    else:
        mask = np.isfinite(values)
        x = np.abs(values[mask])
    mean_error, median_error = bootstrap(x)
    weighted_mask = mask & valid
    wx = np.abs(values[weighted_mask]) if group == 'absolute_all' else values[weighted_mask]
    w = 1 / sigma[weighted_mask] ** 2
    weighted_mean_error, weighted_median_error = weighted_bootstrap(wx, w)
    return {
        'dataset': label,
        'field_group': group,
        'n_sources': len(x),
        'n_sources_with_valid_errors': int(weighted_mask.sum()),
        'min_B_uG': float(x.min()),
        'max_B_uG': float(x.max()),
        'range_width_uG': float(x.max() - x.min()),
        'mean_uG': float(x.mean()),
        'mean_error_uG': mean_error,
        'median_uG': float(np.median(x)),
        'median_error_uG': median_error,
        'error_weighted_mean_uG': float(np.average(wx, weights=w)),
        'error_weighted_mean_error_uG': weighted_mean_error,
        'error_weighted_median_uG': weighted_median(wx, w),
        'error_weighted_median_error_uG': weighted_median_error,
    }


def validate_and_calculate():
    rows = []
    checks = []
    for multiplier in (1, 3):
        base = ROOT / f'FileOutput_QuadrantShift_v3_M{multiplier}_D294' / 'Perseus'
        bfile = base / 'FinalData/BLOSPoints.csv'
        efile = base / 'FinalData/FinalBLOSResults.csv'
        b = pd.read_csv(bfile, sep='\t')
        e = pd.read_csv(efile, sep='\t').set_index('ID#').loc[b['ID#']]
        values = b['Magnetic_Field(uG)'].to_numpy(float)
        uncertainty_values = e['Magnetic_Field(uG)'].to_numpy(float)
        np.testing.assert_allclose(values, uncertainty_values, rtol=1e-10, atol=1e-10)
        upper = e.TotalUpperBUncertainty.to_numpy(float)
        lower = e.TotalLowerBUncertainty.to_numpy(float)
        sigma = (upper + lower) / 2
        valid = np.isfinite(values) & np.isfinite(upper) & np.isfinite(lower) & (upper >= 0) & (lower >= 0) & (sigma > 0)
        label = f'FileOutput_QuadrantShift_v3_M{multiplier}_D294/Perseus'
        for group in ('all_signed', 'positive', 'negative', 'absolute_all'):
            rows.append(calculate(label, group, values, valid, sigma))
        checks.append({
            'run': label,
            'distance_pc': 294,
            'on_multiplier': multiplier,
            'reference_count': len(pd.read_csv(base / 'FinalData/SelectedRefPoints.csv', sep='\t')),
            'blos_count': len(b),
            'valid_error_count': int(valid.sum()),
            'positive_count': int((values > 0).sum()),
            'negative_count': int((values < 0).sum()),
            'quadrants': '[1, 2, 6, 1]',
        })
    calculated = pd.DataFrame(rows)
    existing = pd.read_csv(ROOT / 'Statistics' / 'statistics_summary.csv')
    key = ['dataset', 'field_group']
    merged = calculated.merge(existing, on=key, suffixes=('_calculated', '_csv'))
    numeric = [c for c in calculated.columns if c not in key]
    for column in numeric:
        left = merged[f'{column}_calculated'].to_numpy(float)
        right = merged[f'{column}_csv'].to_numpy(float)
        np.testing.assert_allclose(left, right, rtol=1e-10, atol=1e-10,
                                   err_msg=f'Statistics mismatch in {column}')
    assert len(merged) == len(calculated) == 8
    return calculated, pd.DataFrame(checks)


def fmt(value, error=None):
    if pd.isna(value):
        return '—'
    return f'{value:.2f}' if error is None else f'{value:.2f} ± {error:.2f}'


def write_report(rows, checks):
    OUT.parent.mkdir(exist_ok=True)
    with PdfPages(OUT) as pdf:
        fig = plt.figure(figsize=(11.7, 8.3))
        fig.suptitle('Quadrant-weighted BLOS statistics', fontsize=18, y=0.96)
        fig.text(0.05, 0.91, 'Perseus, distance 294 pc; quadrant intersection shifted to the filtered-reference median; '
                 'minimum one reference per quadrant.', fontsize=10)
        table_rows = []
        for _, r in rows.iterrows():
            run = 'M1' if '_M1_' in r.dataset else 'M3'
            table_rows.append([
                run, r.field_group, str(int(r.n_sources)),
                f'{r.min_B_uG:.1f} to {r.max_B_uG:.1f}',
                fmt(r.mean_uG, r.mean_error_uG),
                fmt(r.median_uG, r.median_error_uG),
                fmt(r.error_weighted_mean_uG, r.error_weighted_mean_error_uG),
                fmt(r.error_weighted_median_uG, r.error_weighted_median_error_uG),
            ])
        ax = fig.add_axes([0.03, 0.08, 0.94, 0.78])
        ax.axis('off')
        table = ax.table(
            cellText=table_rows,
            colLabels=['Run', 'Field group', 'N', 'Range (µG)', 'Mean ± error',
                       'Median ± error', 'Weighted mean ± error', 'Weighted median ± error'],
            cellLoc='center', colLoc='center', loc='upper center',
            colWidths=[0.06, 0.13, 0.05, 0.17, 0.15, 0.15, 0.16, 0.17])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.8)
        for cell in table.get_celld().values():
            cell.set_edgecolor('#999999')
        for (row, _), cell in table.get_celld().items():
            if row != 0:
                continue
            cell.set_facecolor('#d9eaf7')
            cell.set_text_props(weight='bold')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        fig = plt.figure(figsize=(11.7, 8.3))
        fig.suptitle('Validation and interpretation', fontsize=18, y=0.95)
        ax = fig.add_axes([0.07, 0.46, 0.86, 0.38])
        ax.axis('off')
        check_rows = [[r.run.split('/')[0].replace('FileOutput_QuadrantShift_v3_', ''),
                       str(r.distance_pc), str(r.on_multiplier), str(r.reference_count),
                       str(r.blos_count), str(r.valid_error_count),
                       f'{r.positive_count}/{r.negative_count}', r.quadrants]
                      for _, r in checks.iterrows()]
        t = ax.table(cellText=check_rows,
                     colLabels=['Run', 'pc', 'Multiplier', 'References', 'BLOS',
                                'Valid errors', '+ / −', 'Quadrants'],
                     cellLoc='center', colLoc='center', loc='upper center',
                     colWidths=[0.18, 0.08, 0.11, 0.13, 0.10, 0.13, 0.10, 0.15])
        t.auto_set_font_size(False); t.set_fontsize(10); t.scale(1, 1.8)
        for cell in t.get_celld().values(): cell.set_edgecolor('#999999')
        for (row, _), cell in t.get_celld().items():
            if row != 0:
                continue
            cell.set_facecolor('#d9eaf7'); cell.set_text_props(weight='bold')
        notes = (
            'Checks passed: BLOS IDs and values match the uncertainty tables; all CSV values were recomputed from the raw catalogs.\n\n'
            'Mean and median errors are bootstrap standard deviations from 10,000 source resamples. '
            'Error-weighted values use w = 1/sigma_B², where sigma_B is the average of the upper and lower reported BLOS errors.\n\n'
            'The absolute_all group uses |BLOS|. The signed, positive, and negative groups retain the sign. '
            'The range is the minimum-to-maximum value within each group.\n\n'
            'The v3 runs use quadrant weighting and the corrected quadrant-enforcement selection. '
            'Their minimum reference separation is set to 0 arcmin so the sparse data can populate all four quadrants.'
        )
        fig.text(0.07, 0.08, notes, fontsize=10, va='bottom', wrap=True, linespacing=1.5)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    return OUT


if __name__ == '__main__':
    rows, checks = validate_and_calculate()
    print(write_report(rows, checks))
