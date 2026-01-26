#!/usr/bin/env python3
"""
convert_custom_catalog.py

Converts the VLA-Perseus RM catalog (true_detections_full.csv) to Taylor format
for use with the MC-BLOS pipeline.

Input CSV columns:
    Source_ID, RA, E_RA, DEC, E_DEC, RM, E_RM, RMS, Threshold,
    ampPeakPIfit, dAmpPeakPIfit, fracPol, S_reffreq, Dataset

Output Taylor format columns:
    raHours, raMins, raSecs, raErrSecs,
    decDegs, decArcmins, decArcsecs, decErrArcsecs,
    longitudeDegs, latitudeDegs,
    nvssStokesIs, stokesIErrs,
    AvePeakPIs, PIErrs,
    polarizationPercents, mErrPercents,
    rotationMeasures, RMErrs

Usage:
    python3 convert_custom_catalog.py <input_file> [output_file]

Example:
    python3 convert_custom_catalog.py /path/to/true_detections_full.csv perseus_rm_catalog.dat
"""

import sys
import os
import numpy as np
import pandas as pd
from itertools import zip_longest

from astropy.coordinates import Angle, SkyCoord
import astropy.units as u


def convert_custom_to_taylor_format(input_file_path: str, output_file_path: str) -> None:
    """
    Converts a VLA-Perseus catalog (true_detections_full.csv) to Taylor format.

    Column mapping:
        RA (deg)           -> raHours, raMins, raSecs (converted to HMS)
        E_RA (deg)         -> raErrSecs (converted to arcseconds)
        DEC (deg)          -> decDegs, decArcmins, decArcsecs (converted to DMS)
        E_DEC (deg)        -> decErrArcsecs (converted to arcseconds)
        (calculated)       -> longitudeDegs, latitudeDegs (Galactic coordinates)
        S_reffreq          -> nvssStokesIs (Stokes I at reference frequency)
        (not available)    -> stokesIErrs (set to NaN)
        ampPeakPIfit       -> AvePeakPIs (peak polarized intensity)
        dAmpPeakPIfit      -> PIErrs (error on peak polarized intensity)
        fracPol            -> polarizationPercents (fractional polarization, already in %)
        (not available)    -> mErrPercents (set to NaN)
        RM                 -> rotationMeasures (rotation measure in rad/m^2)
        E_RM               -> RMErrs (error on rotation measure)

    Parameters
    ----------
    input_file_path : str
        Path to the input CSV file (true_detections_full.csv format)
    output_file_path : str
        Path for the output Taylor-format file
    """
    print(f"Reading VLA-Perseus catalog from: {input_file_path}")
    data = pd.read_csv(input_file_path)

    print(f"Found {len(data)} sources in catalog")

    # -------------------------------------------------------------------------
    # RA: Convert from degrees to hours, minutes, seconds
    # Input: RA (degrees)
    # Output: raHours, raMins, raSecs
    # -------------------------------------------------------------------------
    ra_deg = data['RA']
    ra_angle = Angle(ra_deg, unit='deg')
    ra_hms = ra_angle.hms
    ra_hours = ra_hms.h
    ra_mins = ra_hms.m
    ra_secs = ra_hms.s

    # -------------------------------------------------------------------------
    # DEC: Convert from degrees to degrees, arcminutes, arcseconds
    # Input: DEC (degrees)
    # Output: decDegs, decArcmins, decArcsecs
    # -------------------------------------------------------------------------
    dec_deg = data['DEC']
    dec_angle = Angle(dec_deg, unit='deg')
    dec_dms = dec_angle.dms
    dec_degs = dec_dms.d
    dec_arcmins = np.abs(dec_dms.m)
    dec_arcsecs = np.abs(dec_dms.s)

    # -------------------------------------------------------------------------
    # Position errors: Convert from degrees to arcseconds
    # Input: E_RA, E_DEC (degrees)
    # Output: raErrSecs, decErrArcsecs (arcseconds)
    # -------------------------------------------------------------------------
    ra_err_deg = data['E_RA']
    dec_err_deg = data['E_DEC']
    ra_err_arcsecs = Angle(ra_err_deg, unit='deg').to(u.arcsec).value
    dec_err_arcsecs = Angle(dec_err_deg, unit='deg').to(u.arcsec).value

    # -------------------------------------------------------------------------
    # Galactic coordinates: Calculate from RA/DEC
    # Input: RA, DEC (degrees)
    # Output: longitudeDegs, latitudeDegs (Galactic l, b in degrees)
    # -------------------------------------------------------------------------
    print("Calculating Galactic coordinates...")
    coords = SkyCoord(ra=ra_deg.values * u.deg, dec=dec_deg.values * u.deg, frame='icrs')
    galactic = coords.galactic
    longitude_degs = galactic.l.deg
    latitude_degs = galactic.b.deg

    # -------------------------------------------------------------------------
    # Stokes I (total intensity)
    # Input: S_reffreq (Stokes I at reference frequency)
    # Output: nvssStokesIs
    # Note: stokesIErrs not available in input catalog, set to NaN
    # -------------------------------------------------------------------------
    nvss_stokes_is = data['S_reffreq']
    stokes_i_errs = np.full(len(data), np.nan)

    # -------------------------------------------------------------------------
    # Polarized intensity
    # Input: ampPeakPIfit (peak polarized intensity from RM synthesis)
    #        dAmpPeakPIfit (error on peak polarized intensity, if available)
    # Output: AvePeakPIs, PIErrs
    # -------------------------------------------------------------------------
    ave_peak_pis = data['ampPeakPIfit']
    if 'dAmpPeakPIfit' in data.columns:
        pi_errs = data['dAmpPeakPIfit']
    else:
        print("Note: dAmpPeakPIfit column not found, setting PIErrs to NaN")
        pi_errs = np.full(len(data), np.nan)

    # -------------------------------------------------------------------------
    # Fractional polarization
    # Input: fracPol (fractional polarization, already in percentage)
    # Output: polarizationPercents
    # Note: mErrPercents not available in input catalog, set to NaN
    # -------------------------------------------------------------------------
    polarization_percents = data['fracPol']
    m_err_percents = np.full(len(data), np.nan)

    # -------------------------------------------------------------------------
    # Rotation measure
    # Input: RM (rotation measure in rad/m^2)
    #        E_RM (error on rotation measure)
    # Output: rotationMeasures, RMErrs
    # -------------------------------------------------------------------------
    rotation_measures = data['RM']
    rm_errs = data['E_RM']

    # -------------------------------------------------------------------------
    # Build Taylor format output
    # -------------------------------------------------------------------------
    taylor_columns = [
        'raHours', 'raMins', 'raSecs', 'raErrSecs',
        'decDegs', 'decArcmins', 'decArcsecs', 'decErrArcsecs',
        'longitudeDegs', 'latitudeDegs',
        'nvssStokesIs', 'stokesIErrs',
        'AvePeakPIs', 'PIErrs',
        'polarizationPercents', 'mErrPercents',
        'rotationMeasures', 'RMErrs'
    ]

    taylor_data = list(zip_longest(
        ra_hours, ra_mins, ra_secs, ra_err_arcsecs,
        dec_degs, dec_arcmins, dec_arcsecs, dec_err_arcsecs,
        longitude_degs, latitude_degs,
        nvss_stokes_is, stokes_i_errs,
        ave_peak_pis, pi_errs,
        polarization_percents, m_err_percents,
        rotation_measures, rm_errs,
        fillvalue=''
    ))

    taylor_df = pd.DataFrame(taylor_data, columns=taylor_columns)

    # Ensure output directory exists
    out_dir = os.path.dirname(os.path.abspath(output_file_path))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    print(f"Saving Taylor-format catalog to: {output_file_path}")
    taylor_df.to_csv(output_file_path, sep='\t', na_rep='nan', index=False)

    print("\nConversion complete!")
    print(f"Total sources converted: {len(taylor_df)}")
    print("\nFirst few entries:")
    print(taylor_df.head())


def main():
    if len(sys.argv) < 2:
        print("\nUsage: python3 convert_custom_catalog.py <input_file> [output_file]\n")
        sys.exit(1)

    input_file = sys.argv[1]

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # Default output name
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'Data', 'RMCatalog',
            f'{base_name}_taylor.dat'
        )

    convert_custom_to_taylor_format(input_file, output_file)


if __name__ == "__main__":
    main()
