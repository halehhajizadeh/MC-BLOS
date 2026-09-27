"""Run the 294 pc Perseus pipeline with data-centered quadrant weighting.

Two independent runs are produced for ON-point extinction multipliers 1 and 3.
The quadrant intersection is shifted to the median location of the filtered
reference candidates, while the cloud-map ridge supplies the quadrant direction.
"""
from pathlib import Path
from configparser import ConfigParser
import json
import os
import shutil
import subprocess
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'Data'
ENV = dict(os.environ, MPLBACKEND='Agg', MPLCONFIGDIR='/private/tmp/mcblos-mpl')


def configure(runroot, cfg, multiplier):
    start = ConfigParser()
    start.read(cfg / 'configStartSettings.ini')
    start['Judgement - Cloud Quadrant Sampling']['use minimum quadrant sampling'] = 'True'
    start['Judgement - Cloud Quadrant Sampling']['minimum points per quadrant'] = '1'
    start['Judgement - Cloud Quadrant Sampling']['weighting scheme'] = 'Quadrant'
    start['Judgement - Cloud Quadrant Sampling']['quadrant center'] = 'filtered_reference_median'
    start['Judgement - Optimal Reference Points']['minimum reference separation arcmin'] = '0'
    start['Judgement - On Point Extinction Multiple of Off Point Average Multiplier'][
        'on point extinction multiple of off point average multiplier'] = str(multiplier)
    with (cfg / 'configStartSettings.ini').open('w') as handle:
        start.write(handle)

    names = ConfigParser()
    names.read(cfg / 'configDirectoryAndNames.ini')
    names['Output Directories']['file output'] = runroot.name
    # Keep shared data in the repository, but read the run-specific cloud
    # parameter file so the distance is isolated to this experiment.
    names['Input Directories']['input data'] = str(DATA)
    names['Input Directories']['cloud parameter data'] = str(cfg)
    with (cfg / 'configDirectoryAndNames.ini').open('w') as handle:
        names.write(handle)

    cloud = ConfigParser()
    cloud.read(cfg / 'perseus.ini')
    cloud['Cloud Info']['distance'] = '294'
    with (cfg / 'perseus.ini').open('w') as handle:
        cloud.write(handle)


def run_one(multiplier):
    runroot = ROOT / f'FileOutput_QuadrantShift_v3_M{multiplier}_D294'
    runroot.mkdir(exist_ok=False)
    cfg = runroot / 'RunConfig'
    cfg.mkdir()
    for name in ['configStartSettings.ini', 'configDirectoryAndNames.ini', 'configConstants.ini']:
        shutil.copy2(ROOT / name, cfg / name)
    shutil.copy2(ROOT / 'Data/CloudParameters/perseus.ini', cfg / 'perseus.ini')
    configure(runroot, cfg, multiplier)

    logs = runroot / 'ExecutionLogs'
    logs.mkdir()

    def run(script, *args):
        print(f"M{multiplier}: {script} {' '.join(args)}", flush=True)
        with (logs / f'{Path(script).stem}.log').open('w') as handle:
            subprocess.run([sys.executable, str(ROOT / script), *args], cwd=cfg,
                           env=ENV, stdout=handle, stderr=subprocess.STDOUT,
                           check=True)

    for script in ['01MakeDir.py', '02aRMMatching.py', '02bRMMapping.py',
                   '03aFilterReferencePoints.py', '03bConsiderReferencePoints.py',
                   '03cMapReferencePoints.py']:
        run(script)
    run('04CalculateBLOS.py', '--no-zeeman')
    for script in ['05aDensitySensitivity.py', '05bDensitySensitivityPlot.py',
                   '06aTempSensitivity.py', '06bTempSensitivityPlot.py',
                   '07UncertaintyAnalysis.py']:
        run(script)

    base = runroot / 'Perseus'
    selected = pd.read_csv(base / 'FinalData/SelectedRefPoints.csv', sep='\t')
    quadrants = pd.read_csv(base / 'IntermediateData/QuadrantDivisionData.csv', sep='\t').iloc[0]
    summary = {
        'distance_pc': 294,
        'on_point_multiplier': multiplier,
        'quadrant_center': 'filtered_reference_median',
        'quadrant_weighting': 'Quadrant',
        'minimum_points_per_quadrant': 1,
        'selected_reference_count': len(selected),
        'quadrant_center_x': float(quadrants['Cloud Center X']),
        'quadrant_center_y': float(quadrants['Cloud Center Y']),
    }
    (runroot / 'quadrant_run_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    for multiplier in (1, 3):
        run_one(multiplier)
