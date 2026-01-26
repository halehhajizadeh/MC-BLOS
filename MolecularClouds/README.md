# MC-BLOS Analysis for Perseus

This repository contains my analysis of the Perseus molecular cloud using the MC-BLOS software.

## Attribution

This work is based on the **MC-BLOS** software developed by **Mehrnoosh Tahani**.

- Original repository: https://github.com/MehrnooshTahani/MC-BLOS
- License: MIT License (see LICENSE file)

## Installation

Using uv (recommended):
```bash
uv venv
uv pip install -r requirements.txt
```

Or using pip:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your RM catalog in `Data/RMCatalog/`
2. Configure `configStartSettings.ini` and `configDirectoryAndNames.ini`
3. Run the analysis scripts in order:
```bash
export PYTHONPATH="${PYTHONPATH}:LocalLibraries"
python 01MakeDir.py
python 02aRMMatching.py
python 02bRMMapping.py
python 03aFilterReferencePoints.py
python 03bConsiderReferencePoints.py
python 03cMapReferencePoints.py
python 04CalculateBLOS.py
python 05aDensitySensitivity.py
python 05bDensitySensitivityPlot.py
python 06aTempSensitivity.py
python 06bTempSensitivityPlot.py
python 07UncertaintyAnalysis.py
```

## Modifications

- Added `convert_custom_catalog.py` for converting custom RM catalogs to Taylor format
- Bug fix in `03bConsiderReferencePoints.py` for optional stability trend analysis
- Configuration files for Perseus cloud analysis
