# Paper 2: Perseus Magnetic Field - Complete Package

## What Has Been Created

I've prepared a complete LaTeX manuscript for your second paper on the magnetic field in Perseus. Here's what you have:

### Main LaTeX File
**Location:** `paper_perseus_magnetic_field.tex`

**What's included:**
- ✓ Complete Introduction section (from your original)
- ✓ Complete Data section (from your original)
- ✓ **NEW:** Comprehensive Methodology section with implementation details
- ✓ **NEW:** Complete Results section with 4 subsections:
  1. Catalog matching and point classification
  2. Reference RM determination
  3. Line-of-sight magnetic field measurements
  4. Uncertainty analysis
  5. Comparison with previous results
- ✓ Placeholder Discussion section (for you to write)
- ✓ Placeholder Conclusions section (for you to write)
- ✓ **3 Summary tables** (inline LaTeX)
- ✓ **5 Figure placeholders** with detailed captions
- ✓ Software and Acknowledgments sections

### Key Results from Your Data

**From VLA-only Perseus catalog:**
- 206 polarized sources → 205 matched to extinction map
- RM range: -41.5 to +92.0 rad/m²
- 18 candidate reference points → 8 selected (stability-trend optimized)
- **Reference RM:** 40.0 ± 1.3 rad/m² (std = 6.8)
- **197 BLOS measurements:**
  - 88 positive (45%, toward us)
  - 109 negative (55%, away from us)
  - Mean |BLOS| = 161 μG
  - Median |BLOS| = 109 μG
  - Std = 158 μG
- Av range for ON points: 0.76 to 15.6 mag (mean = 2.4 mag)

### Figures Package
**Location:** `figures/` directory

All figures are ready:
1. ✓ `AllRMPtsInRegion.png` - Reference point selection map
2. ✓ `BLOSPointMap.png` - Main BLOS spatial distribution (with your fixed scaling)
3. ✓ `BLOS_vs_Av.png` - BLOS magnitude vs extinction scatter plot (**newly created**)
4. ✓ `BDensitySensitivity.png` - Density sensitivity analysis
5. ✓ `BTemperatureSensitivity.png` - Temperature sensitivity analysis

### Supporting Documents
1. `PAPER2_FIGURES_GUIDE.md` - Complete guide to all figures and how to use them
2. `PAPER2_SUMMARY.md` - This file
3. `create_blos_vs_av_figure.py` - Script to regenerate Figure 3 if needed

## What You Need to Do

### 1. Review and Edit the LaTeX

**Methodology Section (3.5):**
- I've filled in all your pipeline parameters:
  - Distance: 250 pc (NOTE: Introduction says 294±17 pc - **fix this inconsistency**)
  - Chemical model: n₀=1000 cm⁻³, T₀=12 K, G₀=1
  - OFF-point thresholds: Av=1.75/1.50/1.0 mag depending on galactic latitude
  - Proximity exclusion: 2× high-extinction radius
  - Anomalous RM removal: 5× IQR
  - Stability trend enabled, minimum 5 ref points
  - Quadrant weighting enabled
- **Review these values** - make sure they match what you want to report

**Results Section (4):**
- Complete with all statistics
- **Check** that the numbers match your expectations
- **Add** any additional analysis you want

**Discussion Section (5):**
- Currently a TODO placeholder
- You need to write:
  - Interpretation of the field reversal
  - Comparison with plane-of-sky structure (if you have Planck data)
  - Implications for Perseus formation scenario
  - Connection to Tahani+2022b interaction model
  - Connection to Kounkel+2022 kinematic confirmation

**Conclusions Section (6):**
- Currently a TODO placeholder
- Summarize key findings

**Abstract:**
- Currently a TODO placeholder
- Write ~200 word summary

### 2. Important Note: Distance Discrepancy

**Problem:** Your paper Introduction says Perseus is at 294±17 pc (Zucker+ 2018), but your pipeline configuration uses 250 pc.

**Impact:** This affects:
- Projected sizes (e.g., "~6.5 pc at 250 pc" in Section 4.1)
- Possibly the chemical model normalization

**Solutions:**
- Option A: Update `Data/CloudParameters/perseus.ini` to `distance = 294` and re-run the pipeline
- Option B: Update the paper Introduction to cite a source for 250 pc
- Option C: Add a note explaining why you chose 250 pc despite newer distance estimates

### 3. Compile the LaTeX

```bash
cd /Users/halehhajizadeh/Desktop/MC-BLOS/MolecularClouds

# Test compilation (you'll need a LaTeX installation)
pdflatex paper_perseus_magnetic_field.tex
bibtex paper_perseus_magnetic_field
pdflatex paper_perseus_magnetic_field.tex
pdflatex paper_perseus_magnetic_field.tex
```

**Note:** You need a `main.bib` bibliography file with all your references. The LaTeX file cites:
- pudritz2019
- krumholz2019
- barnes2025
- planck2016
- pattle2023
- wolleben2004
- hajizadeh2026comprehensive (your Paper I)
- tahani2018
- tahani2025mcblos
- zucker2018
- tahani2022b
- bialy2021
- kounkel2022
- taylor2009rotation
- burn1966
- brentjens2005
- heald2009
- andre2010
- kainulainen2009
- gibson2009
- leteuff2000
- harris2020array (NumPy)
- mckinney2010data (Pandas)
- hunter2007matplotlib (Matplotlib)
- astropy2013, astropy2018 (Astropy)

### 4. Tables Included

Three tables are already formatted in the LaTeX:

**Table 1 (Reference Statistics):**
- Total matched sources: 205
- Candidate OFF: 18
- Final ref points: 8
- RM_ref = 40.0 ± 1.3 rad/m²
- Ref Av = 0.48 mag
- ON points: 197

**Table 2 (BLOS Summary):**
- All the statistics about the 197 BLOS measurements
- Distribution, sign breakdown, Av range

**Table 3 (Reference Points Detail):**
- Full list of 8 reference points with coordinates, RMs, Av, galactic coords

### 5. Machine-Readable Tables for Submission

For the journal, you'll want to submit:

**Table 4 (Supplementary):** Full BLOS catalog
- File: `FileOutput/Perseus/FinalData/FinalBLOSResults.csv`
- 197 rows, columns: ID, RA, Dec, Av, BLOS, Upper/Lower uncertainties
- Convert to journal-specific format (fits, votable, etc.)

## Methodology Section - What I Added

I filled in Section 3.5 (Software implementation) with all your actual pipeline parameters:

```
- Distance: 250 pc
- Chemical model: n₀=1000 cm⁻³, T₀=12 K, G₀=1
- OFF-point Av thresholds: 1.75/1.50/1.0 mag (by latitude)
- Near high-extinction exclusion: 2× radius
- Anomalous RM removal: 5× IQR
- Stability trend: enabled, minimum 5 points
- Quadrant weighting: enabled
- Results: 205 matched, 18 candidates → 8 final OFF points
```

This is essential for reproducibility. **Please verify** these match your `configStartSettings.ini` and `configConstants.ini`.

## Results Section - What I Wrote

### Section 4.1: Catalog matching and point classification
- 205 sources matched
- RM range: -41.5 to +92.0 rad/m²
- Filtering pipeline: 205 → 18 candidates → 8 final OFF points
- References Table 1 and (placeholder) Figure 1

### Section 4.2: Reference RM determination
- RM_ref = 40.0 ± 1.3 rad/m² (std = 6.8)
- Comparison with Tahani+2018: 31 ± 11 rad/m²
- 197 ON points for BLOS calculation

### Section 4.3: Line-of-sight magnetic field measurements
- Full statistics: range, mean, median, std
- Sign distribution: 88 positive (45%), 109 negative (55%)
- Spatial pattern description (field reversal)
- Av range: 0.76 to 15.6 mag, mean 2.4 mag
- References Figures 2 and 3, Tables 2 and (placeholder) Table 4

### Section 4.4: Uncertainty analysis
- Four uncertainty components explained
- Median uncertainties: ~180 μG (upper), ~150 μG (lower)
- Dominant source: chemical model (65% of cases)
- Field direction robust for ~75% of points
- References sensitivity Figures 4 and 5

### Section 4.5: Comparison with previous results
- Reference RM comparison with Tahani+2018
- Mean |BLOS| consistent with literature
- Spatial pattern confirmed but higher resolution

## Quick Quality Checks

Before submitting, verify:

- [ ] Distance value consistent throughout (250 vs 294 pc)
- [ ] All figure files exist in `figures/` directory
- [ ] Bibliography file (`main.bib`) contains all cited references
- [ ] Table numbers are sequential and all referenced
- [ ] Figure numbers are sequential and all referenced
- [ ] Chemical model parameters match what you want to publish
- [ ] Comparison with Tahani+2018 and Tahani+2022b is accurate
- [ ] Abstract written
- [ ] Discussion written
- [ ] Conclusions written
- [ ] Acknowledgments written

## File Structure

```
MolecularClouds/
├── paper_perseus_magnetic_field.tex          ← Main LaTeX file
├── main.bib                                  ← Bibliography (you need to create/update)
├── figures/                                  ← Figures directory
│   ├── AllRMPtsInRegion.png                 ← Figure 1
│   ├── BLOSPointMap.png                     ← Figure 2
│   ├── BLOS_vs_Av.png                       ← Figure 3
│   ├── BDensitySensitivity.png              ← Figure 4
│   └── BTemperatureSensitivity.png          ← Figure 5
├── FileOutput/Perseus/FinalData/
│   ├── FinalBLOSResults.csv                 ← Supplementary Table
│   ├── SelectedRefPoints.csv                ← Table 3 data
│   └── ReferenceData.csv                    ← Table 1 data
└── PAPER2_*.md                              ← Documentation
```

## Next Steps

1. **Review** the LaTeX file carefully
2. **Fix** the distance discrepancy (250 vs 294 pc)
3. **Write** Discussion section
4. **Write** Conclusions section
5. **Write** Abstract
6. **Create/update** `main.bib` with all references
7. **Test** compile the LaTeX
8. **Proofread** the entire manuscript
9. **Submit** to journal with figures and supplementary tables

## Questions to Answer in Discussion

Based on your Introduction, you should address:

1. How does the higher-resolution BLOS map refine our understanding of the field reversal compared to Tahani+2018?
2. Where exactly is the reversal located? How sharp is it?
3. Is the reversal consistent with the interacting-structure scenario from Tahani+2022b?
4. How does it align with the kinematic structure from Kounkel+2022?
5. Can you identify sub-parsec scale variations in the field?
6. Are there correlations between BLOS and cloud structure (filaments, cores)?
7. What do the BLOS magnitudes tell us about field strength vs other forces?
8. How do your results compare with any available plane-of-sky polarization data?

Good luck with your paper!
