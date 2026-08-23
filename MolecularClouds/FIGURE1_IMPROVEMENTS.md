# Figure 1 Improvements

## What Was Fixed

### Original Figure Issues:
1. ❌ Had title "All RM Points in the Region with ID"
2. ❌ Showed all source ID numbers cluttering the plot
3. ❌ Lots of white space
4. ❌ Non-publication-quality fonts
5. ❌ No clear distinction between ON/OFF points by field direction

### New Improved Figure:
1. ✅ **No title** - Clean, publication-ready
2. ✅ **No ID labels** - IDs removed from static figure
3. ✅ **Minimal white space** - Tight layout, properly sized
4. ✅ **Publication fonts** - Times/serif matching journal standards
5. ✅ **Color-coded by B∥ sign**:
   - Blue circles = Positive B∥ (toward observer)
   - Red circles = Negative B∥ (away from observer)
   - Green circles = Reference (OFF) points
6. ✅ **Professional styling**:
   - Clean grid lines
   - Proper colorbar
   - Clear legend
   - Both PNG (300 DPI) and PDF (vector) formats

## Files Generated

### Static Figures (for paper)
```
figures/AllRMPtsInRegion.png  # 300 DPI raster image
figures/AllRMPtsInRegion.pdf  # Vector format for LaTeX
```

### Interactive Version (optional for ApJ)
To create an interactive version where hovering shows IDs:

```bash
# First install plotly if you don't have it:
pip install plotly

# Then run:
python create_interactive_figure1.py
```

This creates:
```
figures/AllRMPtsInRegion_interactive.html  # Interactive version with hover tooltips
```

## How to Use in Your Paper

### Static Figure (Recommended for Main Paper)
Your LaTeX already references the correct path. The figure will show:
- All 205 RM sources color-coded by field direction
- 8 reference points in green
- Clean, professional appearance
- No clutter from ID numbers

### Interactive Figure (Optional Supplementary Material)
**For ApJ Interactive Figures:**

1. **In your paper**, reference it as:
   ```latex
   \begin{figure*}[htbp]
   \centering
   \includegraphics[width=1\textwidth]{AllRMPtsInRegion.png}
   \caption{Spatial distribution of the 205 RM sources...
   (An interactive version of this figure is available in the online journal.)}
   \label{fig:reference-selection}
   \end{figure*}
   ```

2. **In submission**, upload the interactive HTML as:
   - "Supplementary Material" or "Data Behind the Figure"
   - ApJ will host it and link it to your figure

3. **Readers can then**:
   - View the static figure in the PDF
   - Click to see the interactive version online
   - Hover over any point to see its ID, coordinates, B∥, RM, and extinction

## Regenerating the Figure

If you re-run the pipeline and want to update the figure:

```bash
python create_paper_figure1.py
```

This will regenerate both PNG and PDF versions with the latest data.

## Font Notes

The figure uses:
- **Serif fonts** (Times New Roman style) for axes labels and text
- **Math fonts** for symbols like B∥, AV
- **Consistent sizing** matching typical ApJ figures

If you have LaTeX installed on your system, you can enable superior font rendering by setting `text.usetex = True` in the script (line 28).

## Size and Resolution

- **Figure size**: 10" × 8" at 300 DPI
- **File size**: ~2-3 MB PNG, ~500 KB PDF
- **Suitable for**: Full-width two-column layout in ApJ/AAS journals

## Statistics

The improved figure shows:
- Total matched sources: 205
- Reference (OFF) points: 8
- ON points with positive B∥: 88 (45%)
- ON points with negative B∥: 109 (55%)

## Technical Details

**Color scheme:**
- Positive B∥: `#0066CC` (professional blue)
- Negative B∥: `#CC0000` (professional red)
- Reference points: `#00CC00` (green)
- All with black edges for clarity

**Marker sizes:**
- ON points: 30 pt
- OFF points: 80 pt (larger to stand out)

**Grid:**
- RA/Dec: White, 30% alpha
- Galactic overlay: Gray, 25% alpha, dashed

This matches the style of your second reference image while being optimized for publication.
