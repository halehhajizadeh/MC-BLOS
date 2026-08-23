# Quick Start: Editing Figures

## The Problem (Before)
You had to describe what you wanted changed in figures, and I had to guess which hardcoded value in which file to modify. This led to confusion and back-and-forth.

## The Solution (Now)
All plot styling is now centralized in **`configPlotting.ini`**. You can edit any visual aspect of your figures by changing values in this one file.

## How to Edit a Figure

### Step 1: Identify What You Want to Change
Look at your figure and identify the element you want to modify:
- Background colormap?
- Marker colors?
- Marker sizes?
- Grid appearance?
- Font sizes?
- Legend styling?

### Step 2: Open the Config File
```bash
cd MolecularClouds
nano configPlotting.ini
# or use your favorite editor: vim, emacs, VSCode, etc.
```

### Step 3: Find the Right Section
The config file is organized by plot type:
- `[Figure]` - Overall figure size and resolution
- `[Heatmap]` - Background extinction/column density map
- `[Axes]` - Coordinate axes and grid lines
- `[Colorbar]` - The color scale bar on the side
- `[RMMap]` - RM point markers and legend
- `[RefPoints]` - Reference point markers
- `[BLOSMap]` - BLOS results
- `[Publication]` - Clean figures without titles/labels

### Step 4: Change the Value
Each parameter has a descriptive name and inline comment:
```ini
# Example: Make RM markers bigger
[RMMap]
legend_size_10 = 20      # was 10
legend_size_50 = 100     # was 50
```

### Step 5: Re-run the Script
```bash
python 02bRMMapping.py
```

The new figure will use your updated settings!

## Common Edits

### "Make the green dots bigger"
```ini
[RefPoints]
marker_size = 100    # was 50
```

### "Change background to grayscale"
```ini
[Heatmap]
colormap = gray      # was BrBG
```

### "Use purple and orange for RM colors"
```ini
[RMMap]
rm_negative_color = purple   # was red
rm_positive_color = orange   # was blue
```

### "Remove title and labels for publication"
```ini
[Publication]
show_title = False
show_labels = False
```
Then in the plotting script, use:
```python
show_title = pc.PUB_SHOW_TITLE
show_labels = pc.PUB_SHOW_LABELS
```

### "Make all fonts bigger"
```ini
[Axes]
ra_label_fontsize = 20     # was 16
dec_label_fontsize = 20    # was 16
ra_tick_fontsize = 16      # was 14
dec_tick_fontsize = 16     # was 14

[Colorbar]
av_label_fontsize = 16     # was 14
```

### "Change figure resolution for publication"
```ini
[Figure]
dpi = 300    # was 120 (higher = sharper but larger file)
```

## Communication Template

When you want me to help with a change, just tell me:

**Section:** [which section in the config]
**Parameter:** [which parameter name]
**New value:** [what you want it to be]

**Example:**
```
Section: RMMap
Parameter: marker_edge_width
New value: 2.0
```

I'll understand exactly what you mean!

## Files Modified

This new system changed the following files:
1. **`configPlotting.ini`** (NEW) - All plot styling parameters
2. **`LocalLibraries/PlotConfig.py`** (NEW) - Loads the config
3. **`LocalLibraries/PlotTemplates.py`** (UPDATED) - Uses PlotConfig defaults
4. **`LocalLibraries/PlotUtils.py`** (UPDATED) - Uses configurable RM colors
5. **`02bRMMapping.py`** (UPDATED) - Uses PlotConfig for RM map
6. **`PLOT_CUSTOMIZATION_GUIDE.md`** (NEW) - Detailed visual guide

## Need Help?

See **`PLOT_CUSTOMIZATION_GUIDE.md`** for:
- Visual diagram of what each parameter controls
- Complete color reference
- Marker shape options
- Line style options
- More examples

## Testing

To verify the system works:
```bash
cd MolecularClouds

# Test 1: Change background colormap
# Edit configPlotting.ini: colormap = viridis
python 02bRMMapping.py
# Check that the background changed to viridis colors

# Test 2: Change RM colors
# Edit configPlotting.ini: rm_negative_color = purple, rm_positive_color = orange
python 02bRMMapping.py
# Check that negative RMs are purple and positive are orange
```
