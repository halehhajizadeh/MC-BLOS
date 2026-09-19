"""Generate revised tables and manuscript from the preserved pre-revision draft."""
from pathlib import Path
import json
import re
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'PaperRevision'
s=json.loads((OUT/'tables/analysis_summary.json').read_text())
b=pd.read_csv(OUT/'corrected/catalog_with_flags.csv')
f=pd.read_csv(OUT/'corrected/FinalBLOSResults.tsv',sep='\t')
m=pd.read_csv(OUT/'tables/faraday_matches.csv')
z=pd.read_csv(OUT/'tables/zeeman_comparison.csv')

def table(name, columns, caption, header, rows, notes, long=False):
    if not long:
        lines=[r'\begin{table*}[!t]',r'\centering',r'\caption{'+caption+'}',
               r'\scriptsize',r'\begin{tabular}{'+columns+'}',r'\toprule',
               header+r' \\',r'\midrule']
        lines+=[' & '.join(row)+r' \\' for row in rows]
        lines += [r'\bottomrule',r'\end{tabular}',r'\par\smallskip',
                  r'\begin{minipage}{0.97\textwidth}\scriptsize '+notes+r'\end{minipage}',
                  r'\end{table*}']
        (OUT/'tables'/name).write_text('\n'.join(lines)+'\n')
        return
    lines=([r'\startlongtable'] if long else [])+[r'\begin{deluxetable*}{'+columns+'}',
        r'\tabletypesize{\scriptsize}',r'\tablewidth{0pt}',r'\tablecaption{'+caption+'}',
        r'\tablehead{'+header+'}',r'\startdata']
    lines += [' & '.join(row)+r' \\' for row in rows]
    lines += [r'\enddata',r'\tablecomments{'+notes+'}',r'\end{deluxetable*}']
    (OUT/'tables'/name).write_text('\n'.join(lines)+'\n')

def number(x):
    return r'$\infty$' if not np.isfinite(x) else f'{x:.0f}'

cat=b.merge(f[['ID#','TotalUpperBUncertainty','TotalLowerBUncertainty']],on='ID#',validate='one_to_one')
cat.to_csv(OUT/'corrected/paper_catalog.csv',index=False)
rows=[]
for _,r in cat.iterrows():
    rows.append([str(int(r['ID#'])),f'{r["Ra(deg)"]:.4f}',f'{r["Dec(deg)"]:.4f}',f'{r.Extinction:.2f}',
        f'{r.RM_Raw_Value:.2f}',f'{r.RM_Raw_Err:.2f}',number(r['Magnetic_Field(uG)']),
        number(r.TotalUpperBUncertainty),number(r.TotalLowerBUncertainty),
        '--' if r.F1<0 else str(int(r.F1)), '--' if r.F2<0 else str(int(r.F2))])
table('corrected_full_catalog.tex','rrrrrrrrrrr',
 r'Corrected catalog matched to the published Paper I sample.\label{tab:blos-catalog}',
 r'\colhead{ID} & \colhead{RA (deg)} & \colhead{Dec (deg)} & \colhead{$A_V$} & \colhead{RM} & \colhead{$\delta$RM} & \colhead{$B_\parallel$} & \colhead{$\Delta B_+$} & \colhead{$\Delta B_-$} & \colhead{F1} & \colhead{F2}',rows,
 r'Coordinates are J2000/ICRS to the precision shown. Extinction is in mag, RM and its error in rad m$^{-2}$, and fields in $\mu$G. IDs refer to the local matched catalog. The machine-readable cross-match supplies Paper I identifiers. F1 and F2 are Paper I flags. Local ID 121 was removed because it has no published counterpart; ID 205 identifies the restored published source with interpolated extinction. An infinite excursion means that the extinction sensitivity window reaches zero cloud extinction. The excursions are not Gaussian confidence intervals. See Section~\ref{sec:catalog-provenance} for the input correction.',long=True)
rows=[]
for _,r in m.iterrows():
    rows.append([str(int(r.Literature_ID)),str(int(r.VLA_ID)),f'{r.separation_arcsec:.2f}',
      f'{r.RM:.1f}',f'{r.VLA_RM_Raw_Value:.2f}',f'{r.B:.0f}',f'{r["VLA_Magnetic_Field(uG)"]:.1f}',
      f'{r.RM_residual_sigma:.2f}',f'{int(r.VLA_F1)}/{int(r.VLA_F2)}'])
table('faraday_comparison.tex','rrrrrrrrr',r'Positional matches to the Perseus measurements of \citet{tahani2018}.\label{tab:faraday-comparison}',
 r'\colhead{2018 ID} & \colhead{Local ID} & \colhead{Sep. ($^{\prime\prime}$)} & \colhead{RM$_{09}$} & \colhead{RM$_{\rm VLA}$} & \colhead{$B_{18}$} & \colhead{$B_{\rm VLA}$} & \colhead{$z_{\rm RM}$} & \colhead{F1/F2}',rows,
 r'RM is in rad m$^{-2}$ and field in $\mu$G. Original Table 6 positions were associated with the Taylor catalog within $30\arcsec$, verifying agreement of the tabulated RMs to their rounding precision; those full-precision coordinates were matched to VLA positions within $10\arcsec$. All accepted separations are below $2.2\arcsec$. $z_{\rm RM}$ uses the quadrature sum of the two catalog measurement errors, excluding cross-survey systematics. Full asymmetric field excursions and source identifiers are provided in the machine-readable table. These are positional associations; source structure can differ between surveys.')
rows=[]
for _,r in z.iterrows():
    rows.append([r.Region,f'{r["Ra(deg)"]:.5f}',f'{r["Dec(deg)"]:.5f}',f'{r.B:.1f} $\\pm$ {r.Error:.1f}',
        f'{r.FWHM_arcmin:.1f}',str(int(r.nearest_ID)),f'{r.separation_arcmin:.2f}',f'{r.VLA_B:.1f}'])
table('zeeman_comparison.tex','lrrrrrrr',r'Local comparison with Arecibo OH Zeeman measurements.\label{tab:zeeman-comparison}',
 r'\colhead{Region} & \colhead{RA (deg)} & \colhead{Dec (deg)} & \colhead{$B_Z$ ($\mu$G)} & \colhead{FWHM ($\prime$)} & \colhead{Local ID} & \colhead{Sep. ($\prime$)} & \colhead{$B_{\rm VLA}$ ($\mu$G)}',rows,
 r'Positive fields point toward the observer. B1 uses the original B1950 pointing in Figure 1 of \citet{goodman1989measurement}, transformed to ICRS. L1448 coordinates and strengths are from Tables 1 and 2 of \citet{troland2008magnetic}. FWHM is the beam diameter. None of the nearest VLA sight lines lies within the half-power radius. Source 55, nearest both L1448 pointings, has F2=1. These are regional comparisons, not measurements through identical gas.')
rows=[]
for r in s['regions']:
    rows.append([r['sample'].replace('F1=0,F2=0','F1=F2=0'),r['side'],str(r['n']),str(r['positive']),str(r['negative']),str(r['positive_2sigma']),str(r['negative_2sigma'])])
table('spatial_comparison.tex','llrrrrr',r'Field directions on either side of the extinction-derived axis.\label{tab:spatial-comparison}',
 r'\colhead{Sample} & \colhead{Side} & \colhead{$N$} & \colhead{$B>0$} & \colhead{$B<0$} & \colhead{$S>2$} & \colhead{$S<-2$}',rows,
 r'The axis is the archived extinction-weighted line fit, independent of RM signs. North and south label the positive and negative pixel-$y$ offsets from this line. $S$ is defined in Equation~\ref{eq:sign-score}. All rows retain the same eight-point scalar reference. The $m=3$ row changes sample membership only; the quality cut excludes nonzero flags.')

p=(OUT/'original/paper2_haleh.tex').read_text()
# Old disabled draft sections are preserved in original/, not mixed into this revision.
p='\n'.join(line for line in p.splitlines() if not line.lstrip().startswith('%'))+'\n'
p=p.replace(r'\usepackage{amsmath}',r'''\usepackage{amsmath}
\graphicspath{{PaperRevision/plots/}{FileOutput_ImprovedPlots/Perseus/Plots/}}
\shorttitle{Magnetic Field in Perseus}
\shortauthors{Hajizadeh et al.}''')
p=p.replace('B_\\parallel,dl','B_\\parallel\\,dl').replace(r'\mathrm{rad,m^{-2}}',r'\mathrm{rad\,m^{-2}}')
p=p.replace('However, these estimates were available at only approximately ten positions through the cloud.',
 'Their full Perseus catalog contains 24 field estimates over a wider area, of which 11 retain their sign within their reported uncertainty excursions.')
p=p.replace('The main advance of this work is the increase from approximately ten positions with cloud field estimates in the earlier analysis to 197 positions within our survey footprint.',
 'The main advance of this work is the denser sampling provided by 197 field estimates within the VLA survey area. We identify 13 positional matches to the 24 published Perseus estimates; the total counts cover different areas and are not a footprint-matched density ratio.')
p=p.replace('They motivate improved\nspatial sampling $B_\\parallel$ across the cloud.',
 'They motivate improved\nspatial sampling of $B_\\parallel$ across the cloud.')
p=p.replace('This catalog substantially increases the number of sampled positions and provides the observational basis for the present study.',
 'This survey provides the observational basis for the present study; the archived analysis input has a one-source discrepancy with the published catalog, documented below.')
p=p.replace('reports 205 polarized sources, all of which were used here, with a source density',
 'reports 205 polarized sources, with a source density')
where=r'\subsection{Extinction Map}'
p=p.replace(where,r'''\subsection{Input Catalog Provenance}
\label{sec:catalog-provenance}
We retain the archived 205-source input for traceability in this revision.
A positional cross-match to the published Paper I machine-readable table
recovers 204 sources within $0.1\arcsec$, with RM differences consistent with
rounding. Local source 121, at $(52.52029^\circ,31.19632^\circ)$ with
RM $18.96$~rad~m$^{-2}$, has no published counterpart. Conversely,
VCPMC J032941.7+313346, with RM $50.70$~rad~m$^{-2}$, is absent from the
archived input. The latter falls on an invalid extinction pixel ($A_V=-1$).
Its field cannot be obtained from that pixel without a missing-data prescription.
As an explicit sensitivity scenario, linear interpolation from valid pixels
in the surrounding $5\times5$ window gives $A_V=6.12$~mag and
$B_\parallel=+78.9~\mu$G. Replacing source 121 by this source preserves the
197-point sample and median absolute field, while changing the nominal sign
counts from 122/75 to 123/74. This scenario is supplied separately; the
identity and intended treatment of these two sources must be reconciled
before the catalog is finalized. The quality-selected analysis excludes
source 121 because its published flags are unavailable.

'''+where)
p=p.replace('The visual-extinction\n  ($A_V$) map used here has a pixel spacing of $1.5$~arcmin, distinct\n  from its effective angular resolution.',
 'The visual-extinction\n  ($A_V$) map used here has a pixel spacing of $1.5$~arcmin. The local FITS\n  header does not establish the effective beam or fully document this\n  reprocessed product; the pixel spacing is not treated as its resolution.')
p=p.replace('We used \\texttt{MC-BLOS} v1.0', 'We used \\texttt{MC-BLOS} v1.0 with the numerical corrections described below')
p=p.replace('used for Perseus. Full descriptions', 'used for Perseus. Full descriptions')
p=p.replace('We ran the\n  software with its default configuration except where noted, having first',
 'We retained the\n  archived selection configuration except where noted, having first')
p=p.replace('  \\subsection{Input Parameters}',r'''  \subsection{Numerical Verification}
  We reproduced the archived nominal fields with the archived implementation
  before correcting two boundary operations in the electron-column calculation.
  Extinction coordinates supplied to linear interpolation are now increasing;
  a path shorter than the first model layer integrates only to the requested
  depth, assuming constant abundance between the surface and that first point.
  The existing full-layer quadrature is retained. Holding the selected OFF
  sample fixed, the median fractional change in field strength is 0.25\%,
  with a largest absolute change of 58.7\% for a shallow sight line.
  No nominal field signs change. Repeating the original stability calculation
  with the corrected fields still recommends eight references.
  The corrected calculations and the archived comparison are retained
  separately. All sensitivity calculations are joined to the nominal catalog
  by source identifier rather than row position.

  \subsection{Input Parameters}''')
p=p.replace('  The software additionally applies a clipping prescription intended to\n  prevent the non-RM contributions alone from implying a field reversal.\n  These asymmetric uncertainties are model-dependent estimates, not\n  formal Gaussian confidence intervals.',
 '  For the revised catalog we retain these excursions without the original\n  sign-related clipping or integer rounding. If the extinction window reaches\n  zero cloud extinction, the electron column can approach zero and the\n  magnitude excursion is reported as unbounded; this occurs for 13 sight lines.\n  These asymmetric uncertainties are model-dependent sensitivity estimates,\n  not formal Gaussian confidence intervals or tests of field direction.')
p=p.replace('All 205 polarized sources from Paper~I are matched to the extinction\n  map.',
 'All 205 sources in the archived input are matched to the extinction\n  map; the published-catalog discrepancy is described in Section~\\ref{sec:catalog-provenance}.')
p=p.replace('  $B_\\parallel$ is recomputed for each OFF point.', '  $B_\\parallel$ is recomputed for the remaining ON points.')
p=p.replace(r'\input{off_candidate_audit.tex}',r'''\input{FileOutput_ImprovedPlots/Perseus/PaperTables/off_candidate_audit.tex}
\begin{figure*}
\centering
\includegraphics[width=0.72\textwidth]{off_candidate_selection.pdf}
\caption{Initial low-extinction reference candidates and their selection status. Error bars show the input RM errors. Labels are local source identifiers. The dashed line is the adopted reference RM.}
\label{fig:off-selection}
\end{figure*}''')
p=p.replace('All six\nthey remain', 'All six\nremain')
p=p.replace('Their extinctions span', 'The full ON sample has extinctions spanning')
p=p.replace('$-991$ to $+858$', '$-993$ to $+858$')
p=p.replace('$176 \\pm 13$', '$178$').replace('$116 \\pm 10$', '$116$').replace('$245$', '$252$')
p=p.replace(r'\subsubsection{Exhaustive Eight-Point Reference Combinations}',r'''\subsection{Spatial Distribution and Direction Uncertainty}
\label{sec:signs}
For a positive electron column, field direction depends only on cloud RM.
We therefore use a separate conditional diagnostic,
\begin{equation}
S_i=\frac{{\rm RM}_i-{\rm RM}_{\rm ref}}
{\sqrt{\delta{\rm RM}_i^2+\sigma_{\rm ref}^2}},
\label{eq:sign-score}
\end{equation}
where $\sigma_{\rm ref}=6.07$~rad~m$^{-2}$ is the reference mean's standard
error. This diagnostic assumes independent ON measurement errors and a
Gaussian approximation to the reference-mean error; it is distinct from
the conservative linear-sum RM term used for field-strength excursions.
We find 77 sight lines with $S>2$ and 27 with $S<-2$.

We divide the map using the archived extinction-weighted line fit, which
does not use RM signs. In zero-based FITS pixel coordinates the line is
$y=-0.323911x+697.042858$. North and south denote positive and negative
$y$ offsets from that line. Table~\ref{tab:spatial-comparison} gives the counts.
The positive fraction is 67/92 (73\%) to the north and 55/105 (52\%) to the
south. Thus, the full sample shows a regional contrast, but the southern
half is not predominantly negative under this division.

In 20,000 realizations we perturb ON RMs by their measurement errors and
draw one shared reference RM per realization. The central 95\% range of
the north-minus-south positive-fraction difference is 0.061--0.315.
These are conditional propagated-error ranges for a fixed axis and sample,
not spatial-null probabilities; intrinsic source contributions and spatially
varying foregrounds are not included. In particular, the global 122/75
split alone is not a test of a coherent field reversal.
\input{PaperRevision/tables/spatial_comparison.tex}

\subsection{Reference-Selection Sensitivity}
\subsubsection{Exhaustive Eight-Point Reference Combinations}''')
needle='choice.\n\n\\subsubsection{Sensitivity to the ON-Point Extinction Cut}'
p=p.replace(needle,r'''choice.

Applying the adopted separation exclusion first leaves 13 candidates and
$\binom{13}{8}=1287$ fixed-count subsets. Their reference RMs span
23.5--43.9~rad~m$^{-2}$. We compare only sources remaining ON for every
subset, including its extinction cut: the 189 common sources include 77
persistently positive, 41 persistently negative, and 71 reference-sensitive
directions. These subsets respect the separation exclusion but are not all
outputs of the stability selector. They define a robustness envelope,
not a probability distribution over foreground models.
Figure~\ref{fig:spatial-robustness} compares this persistence map with the
earlier Faraday measurements.
\begin{figure*}
\centering
\includegraphics[width=0.8\textwidth]{spatial_robustness.pdf}
\caption{Direction persistence across the 1287 separation-eligible eight-point subsets. Blue and red circles retain positive and negative signs, respectively; gray circles change sign. Open squares show the nominal directions from \citet{tahani2018}. The dashed line is the extinction-derived axis. Only the 189 sources that remain ON in every subset enter the persistence counts.}
\label{fig:spatial-robustness}
\end{figure*}

\subsubsection{Sensitivity to the ON-Point Extinction Cut}''')
p=p.replace('Comparisons here use\nnominal fields, not the multiplier-3 uncertainty estimates, whose\nsensitivity tables require alignment by source ID before propagation.',
 'The revised multiplier-3 uncertainty table is also recomputed using source-ID\nalignment. Its error propagation is consistent with the main revised catalog.\nThe north/south sign contrast becomes weaker under this cut\n(Table~\\ref{tab:spatial-comparison}).')
discussion=r'''
\subsection{Comparison with Previous Faraday Measurements}
\label{sec:comparison}
We recovered the 24 Perseus measurements in Table 6 of \citet{tahani2018},
including their signed fields and asymmetric excursions. Their rounded
coordinates were first associated with the full-precision \citet{taylor2009}
catalog, verifying the tabulated RMs. A $10\arcsec$ match to the VLA catalog
then gives 13 unique associations, all separated by less than $2.2\arcsec$.
The adopted radius is a positional association criterion, not an assumption
that the two surveys resolve identical source structure.
Table~\ref{tab:faraday-comparison} and Figure~\ref{fig:faraday-comparison}
compare these observations.

Eleven of the 13 pairs have the same nominal field sign. The two exceptions
are published points 4 and 10, corresponding to local IDs 60 and 125.
Both revised cloud RMs are consistent with zero under Equation~\ref{eq:sign-score},
so neither pair establishes a significant reversal between epochs or methods.
The median observed-RM difference, VLA minus NVSS, is
$-0.16$~rad~m$^{-2}$, although three pairs (published IDs 4, 9, and 10)
differ by more than three times their quadrature measurement error.
These residuals require source-level interpretation and cannot be explained
by changing the cloud reference, because they precede reference subtraction.
For point 10, for example, observed RM changes from $-8.3$ to
$+34.92$~rad~m$^{-2}$; its inferred field changes from $-196$ to
$+16.5~\mu$G. We do not attribute the difference uniquely to intrinsic
variability, unresolved structure, or an older narrow-band RM ambiguity.

The similar reference zero points (our $31.6$~rad~m$^{-2}$ and the
$31.1$~rad~m$^{-2}$ subtraction implied by the published table) do not
guarantee agreement of individual cloud RMs. Furthermore, the two field
analyses share extinction and chemical-model assumptions. Their agreement
therefore tests reproducibility and consistency more directly than it
provides independent validation of the electron column.
The $+136$ and $-90~\mu$G sign-selected, error-weighted averages quoted by
\citet{tahani2022b} are different statistics from our median absolute field
of $116~\mu$G; their similar scale is contextual rather than a quantitative
agreement test.
\input{PaperRevision/tables/faraday_comparison.tex}
\begin{figure*}
\centering
\includegraphics[width=\textwidth]{faraday_comparison.pdf}
\caption{Positional associations with earlier Perseus observations. Left: observed RMs, before cloud-reference subtraction. Right: published and revised signed fields. Dashed lines mark equality. Orange denotes a nonzero Paper I quality flag; blue denotes F1=F2=0. Selected labels identify points in the 2018 table. The upward arrow on point 2 denotes unbounded extinction sensitivity, not a finite upper uncertainty. Field excursions are model sensitivities, not Gaussian confidence intervals.}
\label{fig:faraday-comparison}
\end{figure*}

\subsection{Local Zeeman and Plane-of-Sky Comparisons}
\label{sec:zeeman}
We recover the original Barnard~1 observing position from Figure~1 of
\citet{goodman1989measurement}: $03^{\rm h}30^{\rm m}12^{\rm s}$,
$+30^\circ57\arcmin26\arcsec$ in B1950. Transforming FK4 B1950 to ICRS gives
$(53.32429^\circ,31.12499^\circ)$. This differs from the approximately
$51.32^\circ$ RA quoted in the later Faraday paper; the original observing
position is used here. The nearest VLA sight line is local ID 169, offset
by $9.54\arcmin$, with a nominal field of $+21.5~\mu$G. Although its sign
and magnitude resemble the $+27\pm4~\mu$G Zeeman result, it lies well outside
the $2.9\arcmin$ FWHM Arecibo beam. This is a regional comparison and cannot
validate equality of the fields in the same gas.

For L1448-CO and L1448-COe, we use the J2000 positions and OH fields in
\citet{troland2008magnetic}. The nearest VLA sight line to both is ID 55,
at separations of $9.90\arcmin$ and $12.73\arcmin$, compared with a
$3\arcmin$ FWHM beam. It has F2=1 and a nominal $B_\parallel=+104.6~\mu$G.
Neither pointing has a VLA counterpart within its half-power radius.
Consequently these observations establish no direct, beam-matched Zeeman
test of our field strengths. Table~\ref{tab:zeeman-comparison} and
Figure~\ref{fig:zeeman-local} make the spatial mismatch explicit.

Dust-polarization estimates in Barnard~1, IC~348, and SVS~13A constrain
$B_\perp$ on their respective spatial scales
\citep{coude2019jcmt,choi2024jcmt,cortes2025first}. We use them to establish
physical context, without combining unmatched $B_\perp$ and $B_\parallel$
values into a total field or inclination angle.
\input{PaperRevision/tables/zeeman_comparison.tex}
\begin{figure*}
\centering
\includegraphics[width=\textwidth]{zeeman_local_maps.pdf}
\caption{VLA sight lines around the original Arecibo Zeeman pointings. Stars mark the pointings and circles their half-power radii (FWHM/2). Blue/red dots denote nominal toward/away VLA fields; labels are local IDs. The pointing locations, rather than the cloud-wide field distribution, determine the relevant comparison.}
\label{fig:zeeman-local}
\end{figure*}

\subsection{Sensitivity to Source Quality}
The cross-match to the published Paper I table supplies the diffuse-emission
flag F1 and Faraday-complexity flag F2. Requiring F1=F2=0 leaves 128 ON
sight lines, with 76 positive and 52 negative nominal fields and a median
absolute field of $109~\mu$G. We deliberately use a conservative cut that
also removes F1=2, even though that class exceeds the diffuse-mask polarized
intensity threshold. With the reference held fixed, the positive fractions
are 43/54 (80\%) north of the extinction-derived axis and 33/74 (45\%) south.
Their difference has a conditional propagated central 95\% range of
0.198--0.450 under the shared-reference simulation. Thus the regional
contrast is not produced solely by the flagged ON sources.

Seven of the eight adopted references also satisfy F1=F2=0. Recomputing
the scalar mean from those seven gives $32.91$~rad~m$^{-2}$ and changes six
nominal signs in the full ON sample. This is a reference-quality sensitivity
test, not a new stability-selected reference solution. The numerical output
also recomputes field strengths using the corresponding mean reference
extinction.

\subsection{Foreground Structure and Limits on Morphology}
Reference-subset experiments vary a single scalar zero point. They do not
test a spatially varying foreground. As a diagnostic, we fit an unweighted
plane to the eight reference RMs using angular coordinates
$x=(\alpha-52^\circ)\cos31^\circ$ and $y=\delta-31^\circ$, expressed in degrees:
\begin{equation}
{\rm RM}_{\rm plane}=51.18-1.04x+20.16y
\quad {\rm rad\,m^{-2}}.
\end{equation}
Leave-one-reference-out prediction gives RMS residuals of 10.3~rad~m$^{-2}$
for the plane and 18.4~rad~m$^{-2}$ for a constant mean. However, only 44 of
197 ON positions lie inside the references' convex hull, so most plane
predictions are extrapolations. Subtracting this plane changes 73 nominal
field signs. These eight references do not validate the plane as a physical
foreground model, but its effect demonstrates that scalar-reference
persistence is insufficient to establish foreground-independent geometry.

The observed north/south contrast and persistent opposite-sign groups are
qualitatively compatible with the earlier suggestion of changing field
direction across Perseus. They do not independently establish the concave
three-dimensional morphology inferred by \citet{tahani2022b}, or uniquely
select a shock--cloud interaction history. A quantitative reconstruction
requires wider OFF-cloud coverage, a constrained spatial foreground, and
matched plane-of-sky observations. We do not infer a transition width from
the sight-line spacing.

\subsection{Field-Strength Interpretation and Remaining Limitations}
The corrected median and mean absolute fields are $116$ and $178~\mu$G.
These are summaries of nominal, electron-weighted estimates. They should
not be interpreted as a population of uniformly precise detections:
13 sight lines have unbounded magnitude sensitivity when the local
extinction window reaches zero cloud extinction. The numerical correction
is small for the median but larger for individual shallow sight lines.
Uncertainty in the foreground, the extinction-to-column conversion, the
chemical model, and the assumed symmetric geometry remains shared or
systematic and is not removed by increasing the number of sources.

Because extinction enters the denominator through the electron-column
model, a correlation between $|B_\parallel|$ and $A_V$ cannot by itself
establish a physical magnetic scaling law. Similarly, an extinction
measurement is a column-density proxy and cannot be substituted for the
volume density in the Zeeman-based field--density analysis of
\citet{crutcher2010magnetic}. The precise provenance and effective angular
resolution of the reprocessed extinction map, and the input-catalog
discrepancy in Section~\ref{sec:catalog-provenance}, remain to be resolved
before submission. The present numerical tables preserve these limitations
explicitly rather than interpreting literature compatibility as validation.
'''
p=p.replace(r'\label{sec:discussion}',r'\label{sec:discussion}'+'\n'+discussion)
conclusion=r'''
We derive revised Faraday-based field estimates for 197 sight lines using
the archived Perseus input and eight OFF references. The main results are:
\begin{enumerate}
\item The corrected median absolute field is $116~\mu$G. Numerical boundary
corrections preserve every nominal sign but change some shallow-source
strengths appreciably. Thirteen extinction sensitivity ranges allow an
unbounded field magnitude.
\item Thirteen positional associations with the earlier Faraday catalog
give 11 nominal sign agreements. Three observed-RM differences exceed
three times the combined catalog measurement error; the two nominal
field-sign disagreements are inconclusive in the revised RM-based
direction diagnostic.
\item Of 189 sight lines common to all 1287 separation-eligible eight-point
reference subsets, 77 remain positive and 41 remain negative. The positive
fraction is higher north of an independently extinction-derived axis,
including after a conservative Paper I quality cut. This is evidence for
spatial variation conditional on the adopted foreground treatment.
\item None of the VLA sight lines lies within the Arecibo half-power beam
at the three Zeeman pointings examined. These data therefore provide
regional context rather than direct local validation of field strength.
\item A spatial foreground-plane diagnostic changes 73 nominal signs.
The denser RM sampling constrains the observed pattern, but additional
foreground information is required for a robust cloud-only reversal or
three-dimensional interpretation. The one-source input discrepancy and
extinction-product provenance must also be reconciled before final release.
\end{enumerate}
'''
p=p.replace(r'\label{sec:conclusions}',r'\label{sec:conclusions}'+'\n'+conclusion)
abstract=r'''
We investigate the line-of-sight magnetic field in the Perseus molecular
cloud using VLA Faraday rotation measurements, extinction, and chemical-model
electron columns. The archived analysis sample contains 205 sources, of
which eight define a reference RM of $31.6\pm6.1$~rad~m$^{-2}$ (standard error)
and 197 yield field estimates. Numerical boundary corrections give a median
absolute field of $116~\mu$G; 13 sight lines have unbounded extinction-related
magnitude sensitivity. Thirteen positional matches to earlier Faraday
measurements give 11 nominal field-sign agreements. Across 1287
separation-eligible eight-reference subsets, 77 positive and 41 negative
directions persist among 189 common sight lines. The positive-field fraction
is higher north of an extinction-derived axis, and the contrast survives a
conservative source-quality cut. However, a diagnostic spatial foreground
plane changes 73 nominal signs, limiting a foreground-independent claim of
a cloud-scale reversal. No VLA sight line samples the half-power beam of the
three Arecibo Zeeman pointings considered. We provide reproducible numerical,
quality, and literature comparisons; a one-source discrepancy with the
published input catalog and the extinction-product provenance remain explicit
limitations of this working revision.
'''
p=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}'+'\n'+abstract+r'\end{abstract}',p,flags=re.S)
p=p.replace(r'\bibliographystyle{aasjournal}',r'\bibliographystyle{aasjournalv7}')
p=p.replace(r'\input{blos_full_catalog_table.tex}',r'\input{PaperRevision/tables/corrected_full_catalog.tex}')
p=p.replace('The asymmetric uncertainties arise from the\ncombination of RM measurement errors, which can change the sign of the derived\nfield, and extinction and chemical model uncertainties, which affect only the\nmagnitude.',
 'The asymmetric excursions combine RM, extinction, and chemical sensitivities\nas described in Section~\\ref{sec:method}. They are not Gaussian intervals;\ninfinite entries denote an unbounded extinction-related magnitude excursion.\nThe published source identifiers and quality flags are retained in the\nmachine-readable cross-match, with unknown flags marked explicitly.')
p=p.replace('H.H. acknowledges the use of Claude (Anthropic) for assistance with code',
 'H.H. acknowledges the use of Claude (Anthropic) and Codex (OpenAI) for assistance with code')

# Finalize against published membership, preserving the archived scenario separately.
provenance=r"""\label{sec:catalog-provenance}
The configured archival RM file contained 206 entries rather than the 205
published in Paper I. Its saved extinction-matched sample retained an extra
source (local ID 121, $\alpha=52.52029^\circ$, $\delta=31.19632^\circ$,
RM $18.96$~rad~m$^{-2}$) and omitted published source
VCPMC J032941.7+313346 (RM $50.70$~rad~m$^{-2}$). We adopt the published
membership: the extra source is removed and the missing source is restored
as local ID 205. The remaining 204 sources match the published positions
within $0.1\arcsec$, and their existing higher-precision RMs agree with the
published values to rounding precision.

The restored source falls on an invalid extinction pixel ($A_V=-1$).
We interpolate linearly from valid pixels in its surrounding $5\times5$
window, obtaining $A_V=6.12$~mag; its nominal field is $+78.9~\mu$G.
The extinction sensitivity uses the valid minimum and maximum in this
window, and the machine-readable catalog marks the central extinction as
interpolated. It does not enter the low-extinction reference pool. The
revised sample therefore still contains 205 input sources and 197 ON
sight lines, with 123 positive and 74 negative nominal fields. The archived
input gives 122/75 and the same median absolute field. We preserve that
comparison separately. The restored source has F1=1 and is excluded from
the conservative quality-selected sample.

""".replace('\n+','\n')
p=re.sub(r'\\label\{sec:catalog-provenance\}.*?(?=\\subsection\{Extinction Map\})',lambda _:provenance,p,flags=re.S)
p=p.replace('the archived analysis input has a one-source discrepancy with the published catalog, documented below.',
 'the archived input is reconciled with the published catalog as documented below.')
p=p.replace('All 205 sources in the archived input are matched to the extinction\n  map; the published-catalog discrepancy is described',
 'All 205 published sources are represented after the input correction and\n  explicit interpolation described')
p=p.replace('We retain the archived 205-source input for traceability in this revision.',
 'We use the published 205-source membership.')
p=p.replace('We find 77 sight lines with $S>2$', 'We find 78 sight lines with $S>2$')
p=p.replace('67/92 (73\\%)','68/92 (74\\%)').replace('0.061--0.315','0.070--0.326')
p=p.replace('0.198--0.450','0.198--0.447')
p=p.replace('global 122/75','global 123/74')
p=p.replace('77 remain positive\nand 35 remain negative','78 remain positive\nand 34 remain negative')
p=p.replace('77\npersistently positive, 41 persistently negative','78\npersistently positive, 40 persistently negative')
p=p.replace('with 87 positive and 47 negative fields (65\\% and 35\\%)',
 'with 88 positive and 46 negative fields (66\\% and 34\\%)')
p=p.replace('source 121 because its published flags are unavailable.','the interpolated source because it has F1=1.')
p=p.replace('73 nominal','74 nominal')
p=p.replace('The precise provenance and effective angular\nresolution of the reprocessed extinction map, and the input-catalog\ndiscrepancy in Section~\\ref{sec:catalog-provenance}, remain to be resolved\nbefore submission.',
 'The precise provenance and effective angular\nresolution of the reprocessed extinction map remain to be confirmed\nbefore submission; its FITS header alone does not establish these properties.')
p=p.replace('using\nthe archived Perseus input and eight OFF references.',
 'using\nthe published Perseus sample, an explicit interpolation for one extinction\npixel, and eight OFF references.')
p=p.replace('77 remain positive and 41 remain negative','78 remain positive and 40 remain negative')
p=p.replace('The one-source input discrepancy and\nextinction-product provenance must also be reconciled before final release.',
 'The extinction-product provenance must also be confirmed before final release.')
p=p.replace('The archived analysis sample contains 205 sources, of',
 'After reconciling the archival input with the published catalog, the sample\ncontains 205 sources, of')
p=p.replace('77 positive and 41 negative','78 positive and 40 negative')
p=p.replace('quality, and literature comparisons; a one-source discrepancy with the\npublished input catalog and the extinction-product provenance remain explicit\nlimitations of this working revision.',
 'quality, and literature comparisons. Absolute field strengths remain\nsensitive to the electron-column model and extinction-map systematics.')
p=p.replace('The sample divides 62\\% positive to 38\\% negative.',
 'The revised sample contains 123 positive and 74 negative estimates (62\\% and 38\\%).')
p=p.replace('with unknown flags marked explicitly.', 'with the interpolated source identified explicitly.')
# AAS double-column floats can otherwise remain deferred indefinitely.
p=p.replace(r'\begin{figure*}',r'\begin{figure*}[!htbp]')
p=p.replace(r'\begin{figure*}[!htbp][t]',r'\begin{figure*}[!htbp]')
p=p.replace(r'\begin{figure*}[!htbp][th!]',r'\begin{figure*}[!htbp]')
p=p.replace(r'\begin{figure*}[!htbp][ht!]',r'\begin{figure*}[!htbp]')

p=p.replace(r'width=0.98\textwidth',r'width=0.80\textwidth')
p=p.replace('Symbol size is proportional to', 'Symbol area increases with')
p=p.replace('$|B_\\parallel|$ and color indicates', '$|B_\\parallel|$ with display limits at both ends, and color indicates')
# End the prose paragraph before deluxetable changes \hsize; otherwise
# the preceding paragraph can silently extend beyond a two-column margin.
p=p.replace(r'\input{', '\n\\par\n'+r'\input{')
# Render the archived audit as a normal float too; deluxetable's mid-document
# grid changes can strand double-column figures in this TeX installation.
audit=pd.read_csv(ROOT/'FileOutput_ImprovedPlots/Perseus/PaperTables/off_candidate_audit.csv')
arows=[]
for _,r in audit.iterrows():
    arows.append([str(int(r['ID#'])),f'{r["Ra(deg)"]:.4f}',f'{r["Dec(deg)"]:.4f}',
                  f'{r["Rotation_Measure(rad/m2)"]:.1f}',f'{r["RM_Err(rad/m2)"]:.1f}',
                  f'{r.Extinction_Value:.3f}',r.Status])
table('off_candidate_audit.tex','rrrrrrl',r'Low-extinction candidates and adopted reference selection.\label{tab:off-audit}',
      r'ID & RA (deg) & Dec (deg) & RM (rad m$^{-2}$) & $\delta$RM & $A_V$ (mag) & Status',arows,
      r'Coordinates are J2000. The proximity test uses a box extending 20 pixels in each coordinate. ID 197 is excluded in favor of 198 by the $1.2\arcmin$ separation rule. OFF exclusion does not itself exclude an ON measurement.')
p=p.replace('FileOutput_ImprovedPlots/Perseus/PaperTables/off_candidate_audit.tex','PaperRevision/tables/off_candidate_audit.tex')
p=re.sub(r'\\begin\{figure\*\}\[!htbp\](?:(?!\\end\{figure\*\}).)*BLOS_histogram\.pdf.*?\\end\{figure\*\}',
         lambda m:m.group().replace(r'\begin{figure*}[!htbp]',r'\begin{figure}[!htbp]')
                    .replace(r'width=0.6\textwidth',r'width=0.98\columnwidth')
                    .replace(r'\end{figure*}',r'\end{figure}'),p,flags=re.S)
p=p.replace(r'\begin{figure*}[!htbp]',r'\begin{figure*}[t]')
p=p.replace('with a mean of 2.43~mag.',f'with a mean of {b.Extinction.mean():.2f}~mag.')
p=p.replace(r'\section{Complete $B_\parallel$ Catalog}',
            r'\section{Complete \texorpdfstring{$B_\parallel$}{B parallel} Catalog}')
p=p.replace(r'\shortauthors{Hajizadeh et al.}',r'''\shortauthors{Hajizadeh et al.}
\hypersetup{pdftitle={Line-of-Sight Magnetic Field in the Perseus Molecular Cloud},pdfauthor={Haleh Hajizadeh et al.}}''')
# The inherited single-pixel value has no recoverable sampling record.
p=re.sub(r'For comparison, we sampled the version-2 Galactic Faraday rotation map.*?magnetic field calculation\.',
         lambda m:r"The Galactic Faraday reconstruction of \citet{hutschenreuter2022galactic} provides context for the total Galactic rotation toward Perseus. It can include a contribution from the cloud itself, whereas our selected OFF-cloud measurements estimate the contribution from material outside the cloud. We therefore retain the OFF-cloud reference for the magnetic field calculation; the reconstruction is not an independent measurement of the cloud foreground.", p, flags=re.S)
(ROOT/'paper2_haleh.tex').write_text('\n'.join(line.rstrip() for line in p.splitlines())+'\n')
print('Wrote revised manuscript and four generated tables.')
