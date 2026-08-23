# Perseus Pipeline Run Summary - Combined Catalog

**Date:** 2026-08-13

## Catalog Combination

### Input Catalogs:
1. **perseus_vla_rm.dat** - VLA-Perseus observations (206 sources)
2. **catalog.dat** - Taylor et al. 2009 catalog filtered to Perseus region (74 sources)

### Combination Results:
- **Duplicates removed:** 17 sources (within 10 arcsec matching radius)
- **Unique sources added:** 57 additional sources from main catalog
- **Total combined catalog:** 263 sources

**New catalog file:** `Data/RMCatalog/perseus_combined.dat`

## Pipeline Execution Results

### Matched RM Points:
- **260 rotation measure points** matched to visual extinction values
- Output: `FileOutput/Perseus/FinalData/MatchedRMExtinction.csv`

### Reference Points Selected:
- **9 reference points** selected for BLOS calibration
- Output: `FileOutput/Perseus/FinalData/SelectedRefPoints.csv`

### BLOS Calculations:
- **251 on-cloud BLOS measurements** calculated
- Output: `FileOutput/Perseus/FinalData/BLOSPoints.csv`
- Final results with uncertainties: `FileOutput/Perseus/FinalData/FinalBLOSResults.csv`

### Sensitivity Analysis:
- Density sensitivity analysis completed
- Temperature sensitivity analysis completed
- Uncertainty bounds calculated for all BLOS measurements

## Comparison to Previous Run

### Previous Run (perseus_vla_rm.dat only):
- Sources matched: ~206
- Reference points: unknown (check logs)

### Current Run (perseus_combined.dat):
- Sources matched: 260 (+54 from combination)
- Reference points: 9
- BLOS measurements: 251

## Output Files Generated

All outputs saved to: `FileOutput/Perseus/`

### Final Data:
- `BLOSPoints.csv` - Magnetic field measurements
- `FinalBLOSResults.csv` - BLOS with uncertainty bounds
- `MatchedRMExtinction.csv` - RM-extinction matched data
- `SelectedRefPoints.csv` - Reference points used
- `ReferenceData.csv` - Reference statistics

### Plots:
- `AllRMPtsInRegion.png` - All RM sources overlay
- `BLOSPointMap.png` - BLOS spatial distribution
- `QuadrantDivisionPlot.png` - Reference point quadrant balance
- Filter plots (near/far high extinction, anomalous RM)
- `BDensitySensitivity.png` - Density parameter sensitivity
- `BTemperatureSensitivity.png` - Temperature parameter sensitivity

### Sensitivity Data:
- `DensitySensitivity/` - BLOS variations with density
- `TemperatureSensitivity/` - BLOS variations with temperature

## Configuration Used

- **Cloud:** Perseus
- **RM Catalog:** perseus_combined.dat
- **Extinction Map:** 2015_02_CalTauPer_toBernsteinCooper.fits
- **Distance:** 250 pc
- **Chemical Parameters:** n0=1000, T0=12, G0=1
- **Reference Point Selection:** Quadrant-balanced with stability trend analysis
