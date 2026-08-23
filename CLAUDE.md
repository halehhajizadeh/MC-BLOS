# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MC-BLOS is an automated implementation of the Faraday rotation-based technique (Tahani et al. 2018) for measuring the line-of-sight magnetic field (BLOS) in molecular clouds. It takes an RM catalog, an extinction/column density FITS map, and chemical evolution code outputs to produce BLOS maps with uncertainties.

## Environment Setup

All scripts run from the `MolecularClouds/` directory. Dependencies are managed with `uv`:

```bash
cd MolecularClouds
uv venv
uv pip install -r requirements.txt
```

Scripts require `LocalLibraries` on the Python path:

```bash
export PYTHONPATH="${PYTHONPATH}:LocalLibraries"
```

## Running the Pipeline

Scripts must be run from `MolecularClouds/` (config files are read relative to cwd).

**Run the full pipeline for the configured cloud:**
```bash
python Run.py
```

**Run an individual step:**
```bash
python 03cMapReferencePoints.py
```

**Run for a specific cloud (overrides `configStartSettings.ini`):**
```bash
python RunCloud.py Perseus
```

**Run with a custom config for multiple clouds:**
```bash
python RunParamClouds.py myConfig.ini Perseus Orion
```

**Convert a custom RM catalog to Taylor format:**
```bash
python convert_custom_catalog.py /path/to/true_detections_full.csv Data/RMCatalog/output.dat
```

## Pipeline Steps

The numbered scripts must be run in order:

| Script | Purpose |
|--------|---------|
| `01MakeDir.py` | Creates the output directory structure under `FileOutput/<CloudName>/` |
| `02aRMMatching.py` | Spatially matches RM catalog sources to the extinction FITS map |
| `02bRMMapping.py` | Plots the RM map overlay |
| `03aFilterReferencePoints.py` | Filters candidate OFF (reference/background) points by extinction thresholds, proximity to cloud, and anomalous RM |
| `03bConsiderReferencePoints.py` | Optional stability trend analysis to find the optimal number of reference points |
| `03cMapReferencePoints.py` | Selects and maps the final reference points (quadrant-balanced by default) |
| `04CalculateBLOS.py` | Calculates BLOS values using scaled RM and electron column density |
| `05a/05bDensitySensitivity` | Varies initial density `n0` and recalculates BLOS for sensitivity analysis |
| `06a/06bTempSensitivity` | Varies initial temperature `T0` and recalculates BLOS for sensitivity analysis |
| `07UncertaintyAnalysis.py` | Combines density and temperature sensitivity into final uncertainty estimates |

## Configuration

Three INI files control all behaviour (read by `LocalLibraries/config.py` at import time):

- **`configStartSettings.ini`** — Runtime judgement parameters: active cloud name, extinction interpolation, OFF-point filtering thresholds, quadrant weighting, plotting options
- **`configDirectoryAndNames.ini`** — All directory paths and output file names; `root` must be an absolute path to the `MolecularClouds/` directory
- **`configConstants.ini`** — Physical constants (extinction-to-column-density conversion, pc-to-cm)

`LocalLibraries/config.py` imports these at module load time and exposes every setting as a module-level variable used throughout all scripts.

## Adding a New Cloud

1. Copy `cloudTemplate.ini` to `Data/CloudParameters/<cloudname>.ini` (lowercase filename)
2. Fill in: `distance` (pc), `cloudJeansLength`, `fitsFileName`, `fitsDataType` (`HydrogenColumnDensity` or `VisualExtinction`), pixel bounds `xmin/xmax/ymin/ymax`, and chemical abundance parameters `n0`, `T0`, `G0`
3. Place the extinction/column density FITS file in `Data/`
4. Place the RM catalog in `Data/RMCatalog/` and update `configDirectoryAndNames.ini → rm catalogue`
5. Place chemical abundance files in `Data/ChemicalAbundance/n{n0}_T{T0}_G{G0}/` matching the template `Av_T{}_n{}.out`
6. Set `cloud = <CloudName>` in `configStartSettings.ini`

## Key Architecture

**`LocalLibraries/config.py`** is the single source of truth for all configuration. It reads all three INI files at import and exposes paths, thresholds, and constants as module globals. Every other module does `from . import config` to access these — changing the INI and re-running a script picks up the new values without touching library code.

**`LocalLibraries/RegionOfInterest.py`** — `Region(regionName)` loads the cloud's `.ini`, opens the FITS file, converts pixel bounds to RA/Dec, and resolves the path to the chemical abundance file. Scripts instantiate one `Region` object and pass it around.

**`LocalLibraries/RMCatalog.py`** — `RMCatalog(filename, ra/dec bounds)` reads a Taylor-format catalog and filters to the region of interest. The Taylor format is whitespace-delimited with named columns (see class docstring for full column spec).

**`LocalLibraries/CalculateB.py`** — `CalculateB(...)` is the core computation: it loads the chemical abundance file, interpolates electron column density from the cloud extinction layers, and applies the Faraday rotation formula `B = RM_scaled / (0.812 × Ne × pc_to_cm × 2)`.

**`LocalLibraries/RefJudgeLib.py`** — Geometric and statistical helpers for classifying reference points: quadrant division via Ridge regression on the extinction map, near-cloud exclusion via box search, IQR-based anomaly removal.

**`LocalLibraries/OptimalRefPoints.py`** — Stability trend algorithm: calculates BLOS as a function of number of reference points added one-by-one, then finds the count at which BLOS values stabilise. Used by `03bConsiderReferencePoints.py` when `find optimal reference points = True`.

**RM catalog format**: The pipeline natively reads the Taylor et al. (2009) format (whitespace-delimited, specific column order). Use `convert_custom_catalog.py` to convert CSV catalogs with `RA/DEC/RM/E_RM` columns into this format.

## Output Structure

All outputs are written under `FileOutput/<CloudName>/`:
- `FinalData/` — `BLOSPoints.csv`, `FinalBLOSResults.csv`, matched/filtered point tables
- `IntermediateData/` — Rejected point tables, stability trend data, quadrant division data
- `Plots/` — All PNG figures
- `Logs/` — Per-script log files (`01.txt` through `07.txt`)
- `DensitySensitivity/` and `TemperatureSensitivity/` — Sensitivity sweep outputs
