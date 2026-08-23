# LaTeX Figure Updates for Paper 2

All figures have been generated without titles in the `figures/` directory.

## Changes to make in your LaTeX file:

### 1. UPDATE Figure \ref{fig:reference-selection} (around line 250)

**REPLACE the current figure code with:**

```latex
\begin{figure*}[htbp]
  \centering
  \includegraphics[width=0.95\textwidth]{figures/rm_map.png}
  \caption{Spatial distribution of rotation measures toward the Perseus molecular cloud. All 205 RM sources matched to the extinction map are shown overlaid on the Herschel $A_V$ map. Green filled circles mark the 8 selected reference (OFF) points used to determine $\mathrm{RM_{ref}} = 40.0 \pm 1.3~\mathrm{rad\,m^{-2}}$ (indicated in the text box). The map uses equatorial coordinates (J2000) with the galactic coordinate grid overlaid in grey. \textit{(An interactive version of this figure with individual source properties is available in the online journal.)}}
  \label{fig:rm-map}
\end{figure*}
```

### 2. ADD NEW Figure after the reference point table (around line 294)

**ADD this new figure:**

```latex
\begin{figure*}[htbp]
  \centering
  \includegraphics[width=0.95\textwidth]{figures/reference_classification.png}
  \caption{Classification of potential reference (OFF) points. The figure shows all 18 candidate OFF points identified by the extinction threshold filter, overlaid on the Perseus extinction map. Green filled circles mark the 8 points selected by the stability-trend algorithm for the final reference sample (Section~\ref{sec:method-rmref}). Red crosses indicate the 4 candidates rejected for being too close to high-extinction ($A_V > 5 \times \langle A_V \rangle$) regions. Yellow open circles show the 6 remaining candidates that passed all filters but were not selected by the stability criterion. No points were rejected for anomalous RM values or for being too far from high-extinction regions.}
  \label{fig:reference-classification}
\end{figure*}
```

### 3. ADD NEW Figure in Section 3.1 (after discussing the stability-trend algorithm)

**ADD this new figure around line 200 in the methods section:**

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.48\textwidth]{figures/stability_trend.png}
  \caption{Stability trend analysis for selecting the optimal number of reference points. Each colored line shows how the calculated $B_\parallel$ for one ON-point sight line varies as candidate OFF points are added one at a time (ordered by increasing extinction). The vertical dashed line marks the selected number of reference points (N = 8), chosen as the point beyond which most $B_\parallel$ values stabilize. Beyond this threshold, adding more OFF points does not significantly change the derived magnetic field strengths, indicating that the reference RM estimate has converged.}
  \label{fig:stability-trend}
\end{figure}
```

### 4. UPDATE Figure \ref{fig:blos-map} (around line 350)

**REPLACE the current BLOS map figure code with:**

```latex
\begin{figure*}[htbp]
  \centering
  \includegraphics[width=0.95\textwidth]{figures/blos_map.png}
  \caption{Map of line-of-sight magnetic field $B_\parallel$ across the Perseus Molecular Cloud, overlaid on the Herschel visual extinction map. Circle size is proportional to $|B_\parallel|$ (see legend), and color indicates field direction: blue for positive $B_\parallel$ (toward observer), red for negative $B_\parallel$ (away from observer). Green circles mark the reference (OFF) points used to determine $\mathrm{RM_{ref}}$. A clear spatial pattern is visible, with predominantly positive fields in the north/west and negative fields in the south/east, indicating a field reversal across the cloud's minor axis. The reference RM and extinction values are shown in the upper-left text box.}
  \label{fig:blos-map}
\end{figure*}
```

### 5. UPDATE Figure \ref{fig:blos-vs-av} (around line 380)

**NO CHANGE NEEDED** - this figure is already without a title.

## Text additions to accompany the new figures:

### In Section 3.1 (Methods - Isolating cloud contribution), after discussing stability-trend:

Add this paragraph around line 215:

```latex
Figure~\ref{fig:stability-trend} illustrates this stability-trend selection process for the Perseus data. Each line in the figure represents one ON-point sight line, showing how its derived $B_\parallel$ value evolves as additional OFF points are incorporated into the reference sample. The algorithm identifies N = 8 as the optimal number of reference points (indicated by the vertical dashed line), the point at which the majority of $B_\parallel$ values have converged and additional OFF points contribute primarily noise rather than improved accuracy. This data-driven approach ensures that the reference RM estimate is both statistically robust and not biased by over-sampling regions with atypical foreground structure.
```

### In Section 4.1 (Results - Catalog matching), after Table 2:

Add this paragraph around line 305:

```latex
Figure~\ref{fig:reference-classification} shows the spatial distribution and classification of all candidate reference points. Of the 18 candidates that passed the initial extinction threshold and proximity filters, 4 were rejected for lying within $2 \times A_{V,\rm highext}$ of high-extinction regions (red crosses), where $A_{V,\rm highext} = 5 \times \langle A_V \rangle = 2.4$~mag. These rejected points sample sight lines potentially contaminated by cloud edges or diffuse extended structure associated with the main molecular complex. The remaining 14 candidates (green filled circles and yellow open circles combined) were all considered suitable OFF points based on their extinction values and spatial separation from the cloud, but the stability-trend algorithm selected only 8 of these (green filled circles) for the final reference sample, as these were sufficient to yield a converged $\mathrm{RM_{ref}}$ estimate. No candidates were excluded due to anomalous RM values (all candidate RMs fell within the expected range for this Galactic sightline) or for being too far from high-extinction regions.
```

## Summary of figures for your paper:

1. **Figure 1** (or renumber as needed): `rm_map.png` - RM distribution map
2. **Figure 2**: `reference_classification.png` - Reference point classification (NEW)
3. **Figure 3** (in methods): `stability_trend.png` - Stability trend analysis (NEW)
4. **Figure 4**: `blos_map.png` - BLOS map
5. **Figure 5**: `BLOS_vs_Av.png` - BLOS vs extinction scatter plot
6. **Figures 6-7**: Sensitivity plots (BDensitySensitivity.png, BTemperatureSensitivity.png) - already exist

All figures are publication-ready with no titles, consistent fonts (18pt labels, 16pt ticks), and are available in both PNG (300 dpi) and PDF formats.
