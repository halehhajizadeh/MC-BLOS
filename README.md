# MC-BLOS (v1.0)

Recent surveys and telescopes have extensively observed the plane-of-sky component of magnetic fields in molecular clouds, but observations of their line-of-sight magnetic fields remain limited. To address this gap, we developed MC-BLOS (v1.0), an automated software implementation of the Faraday rotation-based technique introduced by Tahani et al. (2018).

Key Features:
- Input: Faraday rotation of point sources (extra-galactic sources or pulsars), extinction or column density maps, chemical evolution code results, and a configurable text/CSV file for cloud-specific parameters.
- Predefined initial parameters (density, temperature, surrounding boundary) for each cloud, with user modification options.
- Automated execution of the technique, outputting line-of-sight magnetic field maps and tables with uncertainties.
- Significant reduction in analysis time compared to manual methods.

The software has been validated against previously-published cloud data, producing results consistent within uncertainty ranges. MC-BLOS is poised to facilitate the analysis of forthcoming Faraday rotation observations associated with molecular clouds.

### Spatially separated OFF points

In `MolecularClouds/configStartSettings.ini`, `minimum reference separation arcmin`
under `[Judgement - Optimal Reference Points]` sets the minimum angular distance
between selected OFF points. This workspace uses 1.2 arcminutes; zero disables the
filter, and older configurations without this setting retain their previous behavior.

Stage 03a prefers candidates with lower extinction, breaking ties by lower RM
uncertainty and then ID. It excludes candidates closer than this distance to an
already retained candidate before the stability analysis and quadrant selection.
Excluded OFF candidates are recorded in `IntermediateData/OverlapRej.csv` and
`Rejected.csv`; input observations are preserved. Manual OFF selections must also
satisfy the separation rule. Distances are measured on the sky, independently of
the displayed marker sizes. Changing this setting requires rerunning stages 03–07.
