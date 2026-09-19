"""Source-aligned, unclipped sensitivity uncertainties for paper reanalysis.

These combine a conservative (linear-sum) RM term with model excursions;
they are not Gaussian confidence intervals. Zero cloud extinction permits
an unbounded field magnitude, represented by infinity, never a finite cap.
"""
import numpy as np


def align_fields(base, sensitivity):
    if base['ID#'].duplicated().any() or sensitivity['ID#'].duplicated().any():
        raise ValueError('Duplicate source identifiers')
    indexed = sensitivity.set_index('ID#')
    missing = set(base['ID#']) - set(indexed.index)
    if missing:
        raise ValueError(f'Missing sensitivity sources: {sorted(missing)}')
    return indexed.loc[base['ID#'], 'Magnetic_Field(uG)'].to_numpy(float)


def combine_uncertainties(base, density_plus, density_minus, temp_plus, temp_minus):
    b = base['Magnetic_Field(uG)'].to_numpy(float)
    rm = base['TotalRMScaledErrWithStDev'].to_numpy(float) / (
        .812 * base['Electron_Column_pc_cm3'].to_numpy(float))
    upper, lower = rm**2, rm**2
    pairs = [(base.BField_of_Min_Extinction.to_numpy(float),
              base.BField_of_Max_Extinction.to_numpy(float)),
             (align_fields(base, density_plus), align_fields(base, density_minus)),
             (align_fields(base, temp_plus), align_fields(base, temp_minus))]
    for a, c in pairs:
        if np.isnan(a).any() or np.isnan(c).any():
            raise ValueError('Undefined model values in uncertainty calculation')
        upper = upper + (np.maximum.reduce([b, a, c]) - b)**2
        lower = lower + (b - np.minimum.reduce([b, a, c]))**2
    result = base[['ID#', 'Ra(deg)', 'Dec(deg)', 'Extinction', 'Magnetic_Field(uG)']].copy()
    result['TotalUpperBUncertainty'] = np.sqrt(upper)
    result['TotalLowerBUncertainty'] = np.sqrt(lower)
    result['UnboundedExtinctionSensitivity'] = ~(np.isfinite(upper) & np.isfinite(lower))
    return result
