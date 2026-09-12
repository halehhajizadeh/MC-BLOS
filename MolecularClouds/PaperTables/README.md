# Paper tables

These are the paper-facing Perseus tables generated from the current
`FileOutput_ImprovedPlots/Perseus` results.

- `reference_points_table.tex`: selected OFF/reference points
- `blos_sample_table.tex`: short sample table
- `blos_full_catalog_table.tex`: complete 197-source catalog
- `summary_statistics_table.tex`: summary statistics
- `BLOS_catalog_for_paper.csv`: machine-readable complete catalog

Regenerate the catalog files from `MolecularClouds` with:

```text
python generate_catalog_table.py
python generate_full_catalog_table.py
```
