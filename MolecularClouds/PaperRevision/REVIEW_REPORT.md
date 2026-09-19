# Paper revision review

The numerical and literature comparisons are complete for the available inputs.
The revised manuscript includes a populated abstract, updated methods/results,
an active discussion and conclusions, comparison tables, seven figures, and a
corrected full catalog. It is an author-review draft, not a claim that the
physical electron model or the foreground has been independently validated.

## Main findings

| Quantity | Revised result |
|---|---:|
| Published input sources / ON estimates | 205 / 197 |
| Reference RM and SEM | 31.5523 ± 6.0739 rad m⁻² |
| Median / mean absolute field | 116.07 / 178.07 μG |
| Signed field range | −993.02 to +858.33 μG |
| Nominal positive / negative fields | 123 / 74 |
| Conditional RM direction score >2 / <−2 | 78 / 27 |
| F1=F2=0 ON sources | 128; 76 positive, 52 negative |
| Median absolute field in quality sample | 109.11 μG |
| Unbounded extinction sensitivity | 13 sight lines |
| Close positional literature matches | 13; 11 nominal sign agreements |
| Separation-eligible reference subsets | 1,287 |
| Persistent directions among 189 common ON sources | 78 positive, 40 negative |
| Scalar-to-plane foreground sign changes | 74 |

The main conclusion is more limited than the old draft's proposed confirmation:
there is a regional direction contrast under scalar foreground subtraction,
and it survives conservative source-quality filtering. It is not yet a
foreground-independent demonstration of a cloud-scale reversal or a unique
three-dimensional magnetic morphology.

## Corrections made

1. **Catalog membership.** The configured input contains 206 rows. Its saved
   205 matches included local source 121, absent from published Paper I, while
   omitting the published source J032941.7+313346 on an invalid extinction
   pixel. Adopted published membership, retained common source IDs, and restored
   the missing source as ID 205 with explicitly marked local interpolation.
   All 205 revised positions match published counterparts within 0.1 arcsec.
   The archived-membership alternative remains separate; its median is unchanged.
2. **Electron-column boundaries.** Fixed descending interpolation coordinates
   and integration of paths shorter than the first grid layer. Identical-input
   median field change is 0.25%; maximum is 58.7%. No signs change because of
   these numerical corrections. The archived implementation reproduces the
   archived fields to relative tolerance 1e-10 before modification.
3. **Uncertainties.** Aligned sensitivity tables by source ID. The paper uses
   unclipped, unrounded quadrature excursions and explicitly represents 13
   unbounded extinction-related excursions. Direction significance is assessed
   separately from those excursions. The m=3 uncertainty table is regenerated.
4. **Interpolation setting.** Fixed the configuration reader's mismatch with
   the generated negative-extinction interpolation option, retaining the old
   option name as a fallback. Original input/output configuration paths were
   not redirected or overwritten.
5. **Barnard 1 position.** Replaced the erroneous RA near 51.32° with the original
   Zeeman pointing transformed to RA 53.32429°. Nearest VLA separation is
   9.54 arcmin; no same-beam Arecibo comparison is available. The nearest L1448
   sight line is also outside both Arecibo beams and has a complexity flag.
6. **Literature baseline.** Replaced the unsupported “approximately ten to 197”
   comparison with the actual 24-source 2018 table and 13 close matches. Three
   matched observed RMs differ by more than their combined 3σ measurement error;
   the two nominal sign disagreements are inconclusive in the new RM diagnostic.
7. **Spatial evidence.** Added an extinction-derived axis comparison and shared
   reference Monte Carlo propagation. The northern positive fraction is 74%,
   versus 52% south; the quality-cut fractions are 80% and 45%. The strict ON
   extinction cut weakens this contrast, although it preserves a global imbalance.
8. **Foreground sensitivity.** Added an eight-reference plane and leave-one-out
   prediction. Plane/constant RMS residuals are 10.3/18.4 rad m⁻², but only 44
   ON positions lie inside the reference convex hull. The plane is not promoted
   to the adopted foreground; its 74 sign changes constrain the strength of the
   interpretation.
9. **Manuscript and presentation.** Added six missing literature entries,
   reconciled active text with the new tables, restored the OFF-selection figure,
   fixed text running outside two-column margins around tables, and separated
   sensitivity intervals from confidence intervals. Original disabled draft
   discussion is preserved in `original/paper2_haleh.tex`.

## Verification completed

- Six focused numerical regression tests cover partial layers, increasing
  interpolation, out-of-grid values, sensitivity row permutation/missing IDs,
  and preservation of unbounded excursions.
- Reproduced original nominal fields before correction; rechecked that the
  stability recommendation remains eight references.
- Verified unique catalog matches and matching RM rounding, 24 parsed literature
  rows, original NVSS associations, unique accepted VLA associations, and actual
  separation eligibility of the 13-candidate reference pool.
- Recomputed every table and figure from the reconciled sample with a fixed
  simulation seed. Density and temperature tables retain the same source IDs.
- Compiled the manuscript with AASTeX 7.0.1 and BibTeX; inspected rendered
  scientific figures and manuscript pages for placement, margins, and labels.
- Final checks confirm all seven figures are present, all cited bibliography
  keys resolve, and there are no undefined references, overfull boxes, or
  stuck-float warnings. The supplied class emits its harmless internal
  `aastex701` versus `aastex7` naming warning.

## Remaining author verification before submission

**Confirm the exact extinction product and its effective angular resolution.**
The file `2015_02_CalTauPer_toBernsteinCooper.fits` records a 2015 extraction
from an older image and 1.5-arcmin pixel spacing. Its header does not identify
the full processing chain or the smoothing beam. The inherited attribution to
2MASS/NICEST is not, by itself, verification of this exact reprocessed file.
Do not substitute pixel spacing for effective resolution. The manuscript
states the limitation; the underlying product or provider should settle it.

The inherited single-pixel Galactic Faraday-map number was removed because its
sampling record could not be recovered. The manuscript retains the qualitative
distinction between total Galactic rotation and the OFF-cloud reference. This
change does not affect the field calculations.

Review the adopted treatment of the restored published source's invalid pixel,
the removal of finite-error clipping, and the updated AI-assistance disclosure
with the coauthors. These choices are explicit in the draft and reproducible;
the alternative archived-membership results are preserved.

If the paper is intended to claim a robust cloud-only reversal or a particular
formation history, it needs additional foreground constraints beyond this
eight-reference dataset. The revised paper instead makes the narrower claim
supported by the completed analyses. No extra observation or unperformed
analysis is represented as completed.
