# Manuscript review

Reviewed all sections of `paper2_haleh.tex` against the saved multiplier-1
Perseus tables, the reference filters, field calculation, uncertainty code,
and the multiplier-3 nominal fields. This is a manuscript revision, not a
new validation of the chemical model or of Paper I observations.

## Added material

- An audit of all 18 initial low-extinction candidates: four proximity
  rejections (18, 27, 132, 170), one separation exclusion (197, near 198),
  eight selected references and five eligible but unused candidates.
- A labeled RM-versus-extinction figure showing the candidate categories.
- An appendix with coordinates, RM, RM error, extinction and selection status.
- A concise ON-cut comparison: 197 versus 134 sources for multipliers 1 and 3;
  the nominal fields of all 134 common sources are numerically identical.
- Explicit treatment of the common reference-error covariance, distinguishing
  a descriptive binomial benchmark from a test of spatial reversal.

## Verified corrections

- Mean nearest-neighbour spacing of the 197 ON positions: 5.298 arcmin,
  0.453 pc at 294 pc or 0.385 pc at 250 pc, not 1.4 pc. This is a sampling
  summary, not a resolution or a bound on reversal width.
- The saved pipeline uses 250 pc for the proximity filter. The manuscript
  now separates that setting from the 294 pc literature distance.
- Reference extinction is 0.552902 mag, not 0.53 mag.
- A conditional sign check using measurement error and reference SEM in
  quadrature gives 77 positive and 27 negative points beyond two sigma.
  These are not counts based on the asymmetric pipeline error bars.
- Low-extinction Spearman probability is 2.917e-10, not below 1e-10.
- Bootstrap standard deviations are 13.23 and 10.26 microgauss for the
  mean and median absolute fields, respectively; the original rounded values
  are supported, but exclude correlated/model systematics.
- Proximity uses a square extending 20 pixels in each coordinate, not a
  circular radius. Extinction-error boxes use the positional-error prescription,
  not the Jeans-length proximity prescription.
- The code first adds RM measurement error and reference SEM linearly, then
  combines the resulting field error with the other contributions. Its error
  clipping means the catalog errors are not ordinary Gaussian intervals.
- The 3003-combination movie uses the 14 pre-separation candidates, a broader
  pool than the 13 candidates eligible under the adopted separation rule.
- The stability summary has been regenerated from 191 common finite trends;
  the caption now distinguishes that illustration from the selection algorithm.
- The map caption now correctly describes circular OFF markers.

## Remaining scientific checks before submission

1. **Chemical integration:** `LocalLibraries/CalculateB.py` passes
   `[Av[val], Av[val-1]]` to `np.interp`. For the increasing chemical grid
   these endpoints are descending. This requires numerical correction and a
   controlled comparison before treating absolute field strengths as final.
   I have not silently changed the model or regenerated its science results.
2. **Multiplier-3 errors:** the nominal table has 134 rows but the sensitivity
   tables have 197, and stage 07 combines values by position. Its existing
   uncertainty bars are therefore not reliable. The added manuscript check
   uses only verified nominal values. Multiplier-1 IDs match the inspected
   temperature/density sensitivity tables.
3. **Extinction-map provenance:** the published Paper I identifies its displayed
   map as 2MASS/NICEST. The unsupported Herschel attribution has been removed
   from Paper II. Confirm the exact local FITS product's provenance and effective
   resolution before submission; its 1.5-arcmin pixel spacing is not its resolution.
4. **Paper I:** checked against the author's published ApJS 283:54 PDF.
   Corrected 206 to 205, the 2019-only coverage, retained frequency windows,
   polarization beam, regional NVSS comparison, and published bibliography entry.
   The catalog now describes its numeric IDs as local matched-catalog identifiers,
   not the VCPMC identifiers used in Paper I. A full cross-match retaining F1/F2
   is still required for a source-quality sensitivity test. No flag cut or numerical
   rerun has been performed in this editorial revision.
5. **Literature and bibliography:** 48 missing cited entries were recovered
   from the author's supplied Overleaf project, without overwriting existing
   entries. Recovery is not independent bibliographic verification. The 2018
   abstract explicitly describes the Perseus reversal evidence as tentative;
   the manuscript wording was softened accordingly. The 2022 paper supports
   a concave geometry consistent with SCI, not unique proof of that scenario.
6. **Spatial claims:** the global sign ratio is not a clustering test. A
   spatially varying foreground and a quantitative reversal model remain
   necessary for stronger geometric conclusions. The combination experiment
   does not validate all possible foreground models.

Primary literature consulted:

- https://arxiv.org/abs/1802.07831
- https://arxiv.org/abs/2201.04718
- https://www.frontiersin.org/journals/astronomy-and-space-sciences/articles/10.3389/fspas.2022.940027/full

## Reproduction

From `MolecularClouds`, run `../.venv/bin/python review_paper_results.py`.
It writes the audit CSV/LaTeX and `manuscript_checks.json` under
`FileOutput_ImprovedPlots/Perseus/PaperTables`, and the new PDF/PNG under
the corresponding `Plots` directory. It reads saved results and does not
alter pipeline configuration or calculations.
