# Plot Customization Guide

This guide shows you exactly what each parameter in `configPlotting.ini` controls.

## How to Edit Figures

1. **Open** `configPlotting.ini`
2. **Find** the section for the type of figure you want to edit
3. **Change** the parameter value
4. **Re-run** the plotting script

## Quick Examples

### "I want the RM points to be bigger"
```ini
[RMMap]
legend_size_10 = 20      # was 10
legend_size_50 = 100     # was 50
legend_size_100 = 200    # was 100
legend_size_200 = 400    # was 200
```

### "I want green reference points instead of green"
```ini
[RefPoints]
marker_facecolor = cyan   # was green
```

### "I want a different background colormap"
```ini
[Heatmap]
colormap = viridis    # was BrBG
```
Options: `BrBG`, `viridis`, `plasma`, `RdYlBu`, `gist_heat`, `gray`, `inferno`

### "I want cleaner figures with no titles or labels"
```ini
[Publication]
show_title = False
show_labels = False
```

### "I want thicker grid lines"
```ini
[Axes]
ra_grid_alpha = 0.8       # was 0.5 (more opaque)
dec_grid_alpha = 0.8      # was 0.5
```

### "I want larger fonts everywhere"
```ini
[Axes]
ra_label_fontsize = 20    # was 16
dec_label_fontsize = 20   # was 16
ra_tick_fontsize = 16     # was 14
dec_tick_fontsize = 16    # was 14

[Colorbar]
av_label_fontsize = 16    # was 14
av_tick_fontsize = 14     # was 12
```

### "I want different RM colors (e.g., purple for negative, orange for positive)"
```ini
[RMMap]
rm_negative_color = purple   # was red
rm_positive_color = orange   # was blue
```

## Figure Element Map

```
┌─────────────────────────────────────────────────────────────────┐
│                         [RMMap] title                           │  ← title_fontsize, title_pad
├─────────────────────────────────────────────────────────────────┤
│  Galactic  ┌───────────────────────────────────────┐ Colorbar  │
│  overlay   │                                       │     ↓      │
│    ↓       │    [Heatmap]                          │  [Colorbar]│
│  [Axes]    │     colormap: BrBG                    │   av_label │
│  gal_*     │     interpolation: nearest            │   h_label  │
│            │                                       │            │
│            │      ● ● ●  ← [RMMap] markers         │  tick size │
│  RA/Dec    │    ● ● ● ●    marker_shape            │  pad       │
│  labels    │      ● ●      marker_edge_color       │  shrink    │
│  [Axes]    │               marker_edge_width       │            │
│  ra_label  │                                       │            │
│  dec_label │    Legend:                            │            │
│            │    ○ 10  ← legend_size_10             │            │
│  Grid:     │    ○ 50  ← legend_size_50             │            │
│  grid_color│    ○ 100 ← legend_size_100            │            │
│  grid_alpha│    ○ 200 ← legend_size_200            │            │
│            │    ○ Negative RM ← rm_negative_color  │            │
│            │    ○ Positive RM ← rm_positive_color  │            │
│            └───────────────────────────────────────┘            │
│                   [Axes] tick labels                            │
│                   ra_tick_fontsize                              │
│                   dec_tick_fontsize                             │
└─────────────────────────────────────────────────────────────────┘
     [Figure] width, height, dpi
```

## Color Reference

### Named Colors
Common: `red`, `blue`, `green`, `cyan`, `magenta`, `yellow`, `black`, `white`, `gray`, `orange`, `purple`, `pink`, `brown`

### Hex Colors
Use `#RRGGBB` format: `#FF0000` (red), `#00FF00` (green), `#0000FF` (blue)

### Colormaps (for background heatmap)
- **Sequential**: `viridis`, `plasma`, `inferno`, `magma`, `cividis`, `Greys`
- **Diverging**: `RdBu`, `BrBG`, `RdYlBu`, `seismic`, `coolwarm`, `PuOr`
- **Perceptually uniform**: `viridis`, `plasma`, `inferno`, `cividis`
- **Classic**: `jet` (avoid for publications), `rainbow`, `gist_heat`

## Marker Shapes
- `o` = circle (default)
- `s` = square
- `^` = triangle up
- `v` = triangle down
- `*` = star
- `D` = diamond
- `+` = plus
- `x` = x

## Line Styles
- `solid` or `-`
- `dashed` or `--`
- `dotted` or `:`
- `dashdot` or `-.`

## Communication Template

When you want to change something, use this format:

**Example 1:**
```
Change the RM map marker colors:
- Section: [RMMap]
- Parameter: rm_negative_color
- New value: purple
```

**Example 2:**
```
Make reference point markers larger:
- Section: [RefPoints]
- Parameter: marker_size
- New value: 100
```

**Example 3:**
```
Change background colormap to grayscale:
- Section: [Heatmap]
- Parameter: colormap
- New value: gray
```

This makes it crystal clear what you want changed!
