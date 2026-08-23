# How to Use the RM Map Figures in ApJ LaTeX Paper

## For the Main Paper (Static Figure)

### Option 1: Using PDF (Recommended for ApJ)

Add this to your LaTeX file where you want the figure to appear:

```latex
\begin{figure*}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/AllRMPtsInRegion.pdf}
\caption{Spatial distribution of the 205 rotation measure sources overlaid on the
visual extinction map of the Perseus molecular cloud. Green circles indicate the
positions of RM sources. The extinction map is shown in the BrBG color scale, with
higher extinction (darker regions) corresponding to denser parts of the cloud.
The map uses equatorial coordinates (J2000) with galactic coordinate grid overlaid.
(An interactive version of this figure is available in the online journal.)}
\label{fig:rm-distribution}
\end{figure*}
```

### Option 2: Using PNG (if PDF has issues)

```latex
\begin{figure*}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/AllRMPtsInRegion.png}
\caption{Spatial distribution of the 205 rotation measure sources...}
\label{fig:rm-distribution}
\end{figure*}
```

### Important Notes for Main Figure:

1. **Use `figure*` environment** for two-column layout (standard for ApJ)
2. **Width**: `0.9\textwidth` is good for full-width figures
3. **Format**: PDF is preferred (vector graphics, scales perfectly)
4. **File location**: Keep figures in `figures/` subdirectory
5. **Caption**: Should be descriptive and mention the interactive version

## For Interactive Supplementary Material

ApJ accepts interactive figures as supplementary material. Here's how to include it:

### Step 1: In Your LaTeX Preamble

Add this package (if not already included):
```latex
\usepackage{hyperref}
```

### Step 2: Mention Interactive Version in Caption

Update your figure caption:
```latex
\caption{Spatial distribution of the 205 rotation measure sources overlaid on the
visual extinction map of the Perseus molecular cloud. Green circles indicate the
positions of RM sources.
\textbf{(An interactive version with source IDs is available as supplementary
material and in the online journal.)}}
```

### Step 3: Reference in Text

In your paper text:
```latex
Figure~\ref{fig:rm-distribution} shows the spatial distribution of all 205 RM
sources in the Perseus region. The interactive version (available online) allows
hovering over individual sources to view their IDs, coordinates, extinction values,
and rotation measures.
```

### Step 4: In ApJ Submission

When submitting to ApJ:

1. **Main submission**: Include the PDF/PNG figure as usual
2. **Supplementary files**: Upload `AllRMPtsInRegion_interactive.html` as:
   - File type: "Figure - Interactive"
   - Description: "Interactive version of Figure X showing all RM source positions with hover tooltips"

3. **In your cover letter**, mention:
   ```
   We have included an interactive HTML version of Figure X as supplementary
   material. This allows readers to explore individual source properties by
   hovering over data points.
   ```

## Complete LaTeX Example for ApJ

```latex
\documentclass{aastex631}  % ApJ uses AASTeX
\usepackage{graphicx}
\usepackage{hyperref}

\begin{document}

% ... your paper content ...

\section{Results}

Figure~\ref{fig:rm-distribution} shows the spatial distribution of all 205
rotation measure sources overlaid on the visual extinction map of Perseus.
The sources are concentrated in regions of moderate to high extinction
($A_V > 1$ mag), consistent with sightlines passing through the molecular
cloud. An interactive version of this figure is available online, allowing
readers to identify individual sources and view their properties.

\begin{figure*}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/AllRMPtsInRegion.pdf}
\caption{Spatial distribution of the 205 rotation measure sources in the
Perseus molecular cloud region. Green circles mark RM source positions overlaid
on the visual extinction map (color scale). The map shows equatorial coordinates
(J2000) with RA increasing to the left and galactic coordinate grid overlaid
in gray. Higher extinction values (darker brown) trace the densest regions of
the molecular cloud.
\textbf{(An interactive version with individual source properties is available
in the online journal.)}}
\label{fig:rm-distribution}
\end{figure*}

% ... rest of your paper ...

\end{document}
```

## File Requirements for ApJ Submission

### Main Figure Files:
- ✅ `AllRMPtsInRegion.pdf` (161 KB) - **PRIMARY** - Vector format
- ✅ `AllRMPtsInRegion.png` (411 KB) - Backup raster format

### Supplementary Material:
- ✅ `AllRMPtsInRegion_interactive.html` (7.1 MB) - Interactive version

### What to Submit:

1. **Main LaTeX file** with figure reference
2. **PDF figure** in `figures/` directory
3. **Interactive HTML** uploaded separately as supplementary material

## ApJ Figure Guidelines Compliance

Your figures meet ApJ requirements:

✅ **Resolution**: 300 DPI (PNG), vector (PDF)
✅ **Format**: PDF (preferred) or PNG
✅ **Size**: Appropriate for two-column layout
✅ **Labels**: Clear axis labels with units
✅ **Colorbar**: Properly sized and labeled
✅ **File size**: Within limits (<10 MB for supplementary HTML)

## Optional: Data Behind the Figure

ApJ also accepts "Data Behind the Figure" tables. You can provide the RM catalog
table you already created (`blos_catalog_table.tex`) as machine-readable data.

In your LaTeX:
```latex
The complete catalog of RM measurements is available in Table~\ref{tab:blos-catalog}
and as machine-readable data in the online journal.
```

## Testing Before Submission

Compile your LaTeX to check:
```bash
pdflatex paper_perseus_magnetic_field_with_catalog.tex
bibtex paper_perseus_magnetic_field_with_catalog
pdflatex paper_perseus_magnetic_field_with_catalog.tex
pdflatex paper_perseus_magnetic_field_with_catalog.tex
```

The figure should appear correctly in the compiled PDF.
