# Perseus paper revision — 18 September 2026

This directory contains the reanalysis used by the revised `../paper2_haleh.tex`.
It does not overwrite `FileOutput_ImprovedPlots` or its archived scientific tables.
The original manuscript, bibliography, and numerical implementation are in
`original/`. The revised paper uses the **published Paper I membership**, not
the 206-entry configured legacy RM input.

## Read first

- `REVIEW_REPORT.md`: findings, changes, and remaining author verification.
- `build/paper2_haleh.pdf`: compiled revised manuscript.
- `tables/analysis_summary.json`: numerical results used in the manuscript.
- `corrected/catalog_with_flags.csv`: nominal fields, electron columns,
  published source identifiers, F1/F2, interpolation flag, and sign diagnostic.
- `corrected/FinalBLOSResults.tsv`: asymmetric, **unclipped** sensitivity
  excursions; infinity means unbounded extinction-related sensitivity.
- `corrected/MatchedRMExtinction.tsv`: reconciled 205-source input, with
  interpolated extinction marked by `Extinction_Observed=False`.
- `tables/faraday_matches.csv`: 13 close positional associations and both
  surveys' RMs, fields, and uncertainty information.
- `tables/zeeman_comparison.csv`: original pointings, beams, nearest VLA
  sight lines, separations, and quality flags.
- `tables/paper1_crossmatch.csv`: one-to-one match of all 205 adopted sources.
- `tables/input_sha256.json`: input and numerical-code checksums.

The local IDs are preserved for 204 common sources. Local ID 121 is removed;
ID 205 identifies the restored published source VCPMC J032941.7+313346.
The 197 revised ON sources therefore do not have consecutive local IDs.

## Reproduce

From `MolecularClouds`, using the existing project environment:

```sh
MPLCONFIGDIR=/private/tmp/mcblos-mpl XDG_CACHE_HOME=/private/tmp/mcblos-cache ../.venv/bin/python -m unittest test_paper_numerics
MPLCONFIGDIR=/private/tmp/mcblos-mpl XDG_CACHE_HOME=/private/tmp/mcblos-cache ../.venv/bin/python revise_paper_analysis.py
../.venv/bin/python write_paper_revision.py
TEXINPUTS=.:PaperRevision/build: pdflatex -interaction=nonstopmode -halt-on-error -output-directory=PaperRevision/build paper2_haleh.tex
BIBINPUTS=.: BSTINPUTS=PaperRevision/build: bibtex PaperRevision/build/paper2_haleh
TEXINPUTS=.:PaperRevision/build: pdflatex -interaction=nonstopmode -halt-on-error -output-directory=PaperRevision/build paper2_haleh.tex
TEXINPUTS=.:PaperRevision/build: pdflatex -interaction=nonstopmode -halt-on-error -output-directory=PaperRevision/build paper2_haleh.tex
```

The analysis script reads the original inputs and writes this directory only.
It uses deterministic simulation seed 20260917. Downloaded papers and their
text extraction are cached under `sources/`; no network is needed to rerun.
The manuscript generator reconstructs the revision from the preserved starting
draft and generated tables. **After manual edits to the revised manuscript,
do not rerun that generator without merging those edits.** Compiling the
manuscript directly is safe.

`Run.py` is the general legacy workflow, not the reproduction command for this
paper. Its configuration still points to the original data/output paths.
Stage 07 now aligns sensitivity rows by ID and preserves infinite excursions,
but otherwise retains its historical finite-error clipping and rounding.
The paper explicitly uses the separate, unclipped `LocalLibraries/Uncertainty.py`
prescription through `revise_paper_analysis.py`.

## Scientific choices

- Hold the eight adopted OFF references fixed while correcting the numerical
  integration; recheck that the original stability calculation still recommends
  eight. The extinction-based reference candidate pool is unchanged.
- Use increasing interpolation coordinates and integrate a partial first layer
  only to the requested depth. Preserve the existing full-layer quadrature.
- Use the valid pixels in the 5×5 window to linearly interpolate the one restored
  source's invalid central pixel. This source is F1=1 and is excluded by the
  conservative source-quality cut. Preserve the archived-membership calculation
  in `corrected/archived_input_corrected.tsv`.
- Join every density/temperature sensitivity by source ID, including the m=3
  sample. Retain ±50% density and ±20% temperature sensitivity.
- Keep the linear-sum RM uncertainty term for strength excursions. Combine
  independent contributions in quadrature, without clipping a large excursion
  to just below zero. These are sensitivity estimates, not Gaussian intervals.
- For the separate direction diagnostic, combine ON RM measurement error and
  reference SEM in quadrature, explicitly conditional on the scalar foreground.
- Use one shared reference draw per Monte Carlo realization. The resulting
  quantiles are propagated-error ranges, not spatial-null p-values.
- Compute reference persistence only for sources that remain ON in every
  combination, including every combination's extinction threshold.
- Use the previously archived extinction-only axis, not an axis optimized to
  maximize the observed sign contrast. The plane foreground test is diagnostic;
  most ON positions lie outside the reference convex hull.

## Primary sources and provenance

- Paper I published table: https://content.cld.iop.org/journals/0067-0049/283/2/54/revision1/apjsae472et2_mrt.txt
  (`sources/paper1_published_table2.txt`). The local pre-publication table was
  also inspected; published data are authoritative for adopted membership.
- Tahani et al. 2018, Table 6: https://arxiv.org/pdf/1802.07831
  (`sources/tahani2018.pdf`, `sources/tahani2018.txt`). Parsed 24 rows;
  recovered original NVSS positions from the local Taylor catalog, requiring
  agreement in RM to tabulated rounding precision. VLA matching radius 10 arcsec;
  all 13 accepted separations are below 2.2 arcsec. Unmatched literature rows
  remain available in `faraday_matches_all.csv`; their nearest neighbours are
  **not** counted as repeat sight lines.
- Tahani et al. 2022: https://arxiv.org/html/2201.04718v2
  (`sources/tahani2022.pdf`). Morphological interpretation and sign-selected
  weighted means are contextual, not independent strength validation.
- Goodman et al. 1989, Figure 1: https://articles.adsabs.harvard.edu/pdf/1989ApJ...338L..61G
  (`sources/goodman1989.pdf`). Original pointing FK4 B1950 03h30m12s,
  +30d57m26s, transformed with Astropy to ICRS 53.324291°, +31.124988°.
  The observing FWHM is 2.9 arcmin. Zeeman signs are reversed to positive-toward.
- Troland & Crutcher 2008, Tables 1 and 2: https://arxiv.org/pdf/0802.2253
  (`sources/troland2008.pdf`). L1448 positions are explicitly J2000, beam about
  3 arcmin FWHM; original signed Zeeman strengths are −26.0±3.7 and −20.6±3.4 μG.
- Coudé et al. 2019: https://arxiv.org/abs/1904.07221
- Choi et al. 2024: https://arxiv.org/abs/2411.01960
- Cortés et al. 2025: https://arxiv.org/abs/2509.21701
- AASTeX 7.0.1 compilation resources: https://journals.aas.org/wp-content/uploads/2025/05/aastex701.zip

The original Crutcher 1993 PDF is scanned and its text extraction is incomplete.
Its contextual B1 value is supported by Tahani 2018's discussion; no independent
beam-matched test is claimed for that larger-beam measurement.
