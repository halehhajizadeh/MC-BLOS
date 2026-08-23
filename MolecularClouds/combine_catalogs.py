#!/usr/bin/env python3
"""
combine_catalogs.py

Combines the VLA-Perseus catalog with the main Taylor catalog,
removing duplicates based on position matching.

Usage:
    python3 combine_catalogs.py
"""

import pandas as pd
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u


def read_taylor_catalog(filepath):
    """Read a Taylor-format catalog."""
    print(f"Reading {filepath}...")
    df = pd.read_csv(filepath, sep='\t')
    print(f"  Found {len(df)} sources")
    return df


def coords_from_taylor(df):
    """Convert Taylor format RA/Dec to SkyCoord objects."""
    # Convert HMS to decimal degrees
    ra_deg = (df['raHours'] + df['raMins']/60.0 + df['raSecs']/3600.0) * 15.0

    # Convert DMS to decimal degrees
    dec_deg = np.abs(df['decDegs']) + df['decArcmins']/60.0 + df['decArcsecs']/3600.0
    # Handle negative declinations
    dec_deg = np.where(df['decDegs'] < 0, -dec_deg, dec_deg)

    coords = SkyCoord(ra=ra_deg*u.deg, dec=dec_deg*u.deg, frame='icrs')
    return coords


def filter_to_region(df, ra_min, ra_max, dec_min, dec_max):
    """Filter catalog to a specific RA/Dec region."""
    coords = coords_from_taylor(df)

    # Handle RA wraparound if necessary
    ra_deg = coords.ra.deg
    if ra_max < ra_min:
        # Wraparound case
        mask = ((ra_deg >= ra_min) | (ra_deg <= ra_max)) & \
               (coords.dec.deg >= dec_min) & (coords.dec.deg <= dec_max)
    else:
        mask = (ra_deg >= ra_min) & (ra_deg <= ra_max) & \
               (coords.dec.deg >= dec_min) & (coords.dec.deg <= dec_max)

    filtered = df[mask].copy()
    print(f"  Filtered to {len(filtered)} sources in region")
    return filtered


def remove_duplicates(df1, df2, match_radius_arcsec=10.0):
    """
    Remove sources from df2 that are already in df1.

    Parameters:
    - df1: Primary catalog (kept as-is)
    - df2: Secondary catalog (duplicates removed)
    - match_radius_arcsec: Matching radius in arcseconds

    Returns:
    - Combined catalog with duplicates removed
    """
    print(f"\nChecking for duplicates (matching radius: {match_radius_arcsec} arcsec)...")

    coords1 = coords_from_taylor(df1)
    coords2 = coords_from_taylor(df2)

    # Find matches
    idx, sep2d, _ = coords2.match_to_catalog_sky(coords1)
    matches = sep2d.arcsec < match_radius_arcsec

    n_duplicates = matches.sum()
    print(f"  Found {n_duplicates} duplicate sources")

    # Keep only non-matching sources from df2
    df2_unique = df2[~matches].copy()
    print(f"  Keeping {len(df2_unique)} unique sources from secondary catalog")

    # Combine
    combined = pd.concat([df1, df2_unique], ignore_index=True)
    print(f"  Combined catalog: {len(combined)} total sources")

    return combined


def main():
    # File paths
    perseus_catalog = 'Data/RMCatalog/perseus_vla_rm.dat'
    main_catalog = 'Data/RMCatalog/catalog.dat'
    output_catalog = 'Data/RMCatalog/perseus_combined.dat'

    # Read both catalogs
    print("="*60)
    print("COMBINING RM CATALOGS FOR PERSEUS")
    print("="*60)

    perseus_df = read_taylor_catalog(perseus_catalog)
    main_df = read_taylor_catalog(main_catalog)

    # Get Perseus region bounds from the VLA catalog
    perseus_coords = coords_from_taylor(perseus_df)
    ra_min = perseus_coords.ra.deg.min() - 2.0  # Add 2 degree margin
    ra_max = perseus_coords.ra.deg.max() + 2.0
    dec_min = perseus_coords.dec.deg.min() - 2.0
    dec_max = perseus_coords.dec.deg.max() + 2.0

    print(f"\nPerseus region bounds:")
    print(f"  RA:  {ra_min:.2f} to {ra_max:.2f} deg")
    print(f"  Dec: {dec_min:.2f} to {dec_max:.2f} deg")

    # Filter main catalog to Perseus region
    print(f"\nFiltering main catalog to Perseus region...")
    main_perseus = filter_to_region(main_df, ra_min, ra_max, dec_min, dec_max)

    # Combine catalogs, removing duplicates
    combined_df = remove_duplicates(perseus_df, main_perseus, match_radius_arcsec=10.0)

    # Save combined catalog
    print(f"\nSaving combined catalog to: {output_catalog}")
    combined_df.to_csv(output_catalog, sep='\t', na_rep='nan', index=False)

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"VLA-Perseus sources:     {len(perseus_df)}")
    print(f"Main catalog (Perseus):  {len(main_perseus)}")
    print(f"Combined (unique):       {len(combined_df)}")
    print(f"Total new sources added: {len(combined_df) - len(perseus_df)}")
    print("="*60)


if __name__ == "__main__":
    main()
