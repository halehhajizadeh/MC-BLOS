"""Verify the flat paper bundle and include detailed stage logs."""
from pathlib import Path
import hashlib
import json
import shutil
import pandas as pd
import numpy as np
from LocalLibraries import config
from LocalLibraries.RegionOfInterest import Region

base=Path(config.CloudOutputDir)
bundle=base/'All_Figures_and_Tables'
manifest=pd.read_csv(bundle/'file_manifest.csv').to_dict('records')
for path in (base/'Logs').iterdir():
    if path.is_file():
        dest=bundle/path.name
        shutil.copy2(path,dest)
        manifest=[r for r in manifest if r['file']!=dest.name]
        manifest.append(dict(file=dest.name,source=str(path.relative_to(base.parent)),
                             sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
pd.DataFrame(manifest).to_csv(bundle/'file_manifest.csv',index=False)
for row in manifest:
    assert hashlib.sha256((bundle/row['file']).read_bytes()).hexdigest()==row['sha256'],row['file']
readme=(bundle/'README.txt').read_text().replace('current eligible pool;',
    'filtered pool before the separation exclusion (eligible-pool results are separate);')
(bundle/'README.txt').write_text(readme)
b=pd.read_csv(bundle/'BLOSPoints.csv',sep='\t')
f=pd.read_csv(bundle/'FinalBLOSResults.csv',sep='\t')
cat=pd.read_csv(bundle/'BLOS_catalog_for_paper.csv')
refs=pd.read_csv(bundle/'SelectedRefPoints.csv',sep='\t')
assert b['ID#'].tolist()==f['ID#'].tolist()==cat['ID#'].tolist()
np.testing.assert_allclose(b['Magnetic_Field(uG)'],cat['Magnetic_Field(uG)'])
assert np.isfinite(b['Magnetic_Field(uG)']).all()
assert not f[['TotalUpperBUncertainty','TotalLowerBUncertainty']].isna().any().any()
assert (b.Extinction>=config.onPtsExtMultipleThreshold*refs.Extinction_Value.mean()).all()
assert len(set(b['ID#']) & set(refs['ID#']))==0
for path in list((base/'DensitySensitivity').glob('*.csv'))+list((base/'TemperatureSensitivity').glob('*.csv')):
    assert pd.read_csv(path,sep='\t')['ID#'].tolist()==b['ID#'].tolist(),path
region=Region(config.cloud)
report=dict(distance_pc=region.distance,on_point_multiplier=config.onPtsExtMultipleThreshold,
    on_sources=len(b),reference_sources=len(refs),
    figure_files=sum(p.suffix in {'.pdf','.png'} for p in bundle.iterdir()),
    latex_tables=sum(p.suffix=='.tex' for p in bundle.iterdir()),
    data_tables=sum(p.suffix in {'.csv','.tsv'} for p in bundle.iterdir()),
    unbounded_extinction_sources=int(f.UnboundedExtinctionSensitivity.sum()),
    source_alignment_passed=True,sensitivity_alignment_passed=True,manifest_hashes_passed=True)
(bundle/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
