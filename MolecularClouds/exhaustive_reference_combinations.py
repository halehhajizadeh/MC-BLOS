"""Make B_LOS maps for every 8-point combination of filtered OFF points.

This is an exploratory workflow.  It reads the normal Perseus inputs but
writes all products to ``FileOutput/Perseus_test`` so the regular analysis is
not changed.

Run from the MolecularClouds directory::

    python exhaustive_reference_combinations.py

The resulting GIF contains one frame per combination, in lexicographic
combination order.  The CSV records the reference values used for every
frame.
"""

from __future__ import annotations

import itertools
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import PillowWriter
from mpl_toolkits.axes_grid1 import make_axes_locatable

from LocalLibraries.CalculateB import CalculateB
from LocalLibraries.MatchedRMExtinctionFunctions import calcFiducialVals, rmLowExtPts, rmMatchingPts
from LocalLibraries.PlotUtils import p2C, p2RGB
from LocalLibraries.RegionOfInterest import Region
from LocalLibraries import config


COMBINATION_SIZE = 8
OUTPUT_DIR = Path(config.FileOutputDir) / "Perseus_test"
FRAME_DIR = OUTPUT_DIR / "frames"
METADATA_FILE = OUTPUT_DIR / "reference_combinations.csv"
MOVIE_FILE = OUTPUT_DIR / "reference_combinations.gif"
VIEWER_FILE = OUTPUT_DIR / "reference_combinations_viewer.html"


def write_viewer(total_combinations):
    """Write a browser-based high-resolution frame viewer with controls."""
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Perseus BLOS reference combinations</title>
<style>
  body {{ margin: 0; padding: 18px; background: #202124; color: #eee;
         font-family: system-ui, sans-serif; text-align: center; }}
  #frame {{ max-width: min(1500px, 96vw); max-height: 78vh; object-fit: contain;
            background: white; border: 1px solid #555; }}
  .controls {{ max-width: 1100px; margin: 14px auto 0; display: flex;
               align-items: center; gap: 10px; flex-wrap: wrap; }}
  button {{ font-size: 16px; padding: 7px 14px; cursor: pointer; }}
  input[type=range] {{ flex: 1; min-width: 260px; }}
  #counter {{ min-width: 130px; text-align: right; font-variant-numeric: tabular-nums; }}
  .hint {{ color: #bbb; font-size: 13px; margin-top: 8px; }}
</style>
</head>
<body>
<h2>Perseus B<sub>parallel</sub> — reference combinations</h2>
<img id="frame" alt="BLOS frame">
<div class="controls">
  <button id="prev">◀ Previous</button>
  <button id="play">▶ Play</button>
  <button id="next">Next ▶</button>
  <label>Speed:
    <select id="speed">
      <option value="0.25">0.25×</option>
      <option value="0.5">0.5×</option>
      <option value="1" selected>1×</option>
      <option value="2">2×</option>
      <option value="4">4×</option>
    </select>
  </label>
  <input id="slider" type="range" min="1" max="{total_combinations}" value="1">
  <span id="counter"></span>
</div>
<div class="hint">Space: play/pause · Left/Right arrows: previous/next frame · Use the slider to jump.</div>
<script>
const total = {total_combinations};
let current = 1;
let timer = null;
let speed = 1;
const image = document.getElementById('frame');
const slider = document.getElementById('slider');
const counter = document.getElementById('counter');
const playButton = document.getElementById('play');
function filename(n) {{ return 'frames/frame_' + String(n).padStart(4, '0') + '.png'; }}
function show(n) {{
  current = Math.max(1, Math.min(total, n));
  slider.value = current;
  image.src = filename(current);
  counter.textContent = current + ' / ' + total;
}}
function stop() {{ if (timer !== null) {{ clearInterval(timer); timer = null; }} playButton.textContent = '▶ Play'; }}
function togglePlay() {{
  if (timer !== null) {{ stop(); return; }}
  playButton.textContent = '⏸ Pause';
  timer = setInterval(() => {{
    if (current >= total) {{ stop(); return; }}
    show(current + 1);
  }}, 250 / speed);
}}
document.getElementById('prev').onclick = () => {{ stop(); show(current - 1); }};
document.getElementById('next').onclick = () => {{ stop(); show(current + 1); }};
playButton.onclick = togglePlay;
slider.oninput = () => {{ stop(); show(Number(slider.value)); }};
document.getElementById('speed').onchange = e => {{
  speed = Number(e.target.value);
  if (timer !== null) {{ stop(); togglePlay(); }}
}};
document.addEventListener('keydown', e => {{
  if (e.code === 'Space') {{ e.preventDefault(); togglePlay(); }}
  if (e.key === 'ArrowLeft') {{ stop(); show(current - 1); }}
  if (e.key === 'ArrowRight') {{ stop(); show(current + 1); }}
}});
show(1);
</script>
</body>
</html>
'''
    VIEWER_FILE.write_text(html)
    print(f"Saved interactive viewer: {VIEWER_FILE}")


def encode_movie(total_combinations):
    """Encode the already-rendered PNG frames into a GIF."""
    print(f"Writing movie: {MOVIE_FILE}")
    writer = PillowWriter(fps=4)
    # Keep the source PNGs high resolution, but use a compact movie canvas so
    # Pillow can encode all 3,003 frames without exhausting memory.
    movie_fig = plt.figure(figsize=(4, 4), dpi=75)
    with writer.saving(movie_fig, str(MOVIE_FILE), dpi=75):
        movie_ax = movie_fig.add_subplot(111)
        for frame_number in range(1, total_combinations + 1):
            frame = plt.imread(FRAME_DIR / f"frame_{frame_number:04d}.png")
            movie_ax.imshow(frame)
            movie_ax.axis("off")
            writer.grab_frame()
            movie_ax.clear()
            movie_ax.axis("off")
            if frame_number % 250 == 0 or frame_number == total_combinations:
                print(f"  movie frame {frame_number}/{total_combinations}")
    plt.close(movie_fig)
    print(f"Saved movie: {MOVIE_FILE}")


def _pixel_coordinates(region, table):
    """Return image-pixel coordinates for a table with RA/Dec columns."""
    if table.empty:
        return np.array([]), np.array([])
    return region.wcs.wcs_world2pix(
        table["Ra(deg)"].to_numpy(), table["Dec(deg)"].to_numpy(), 0
    )


def _format_frame(ax, region, image, blos_scatter, ref_scatter,
                  combo_number, total_combinations, reference_ids, rm_ref,
                  extinction_ref):
    """Create the fixed map decorations and return the annotation text."""
    ax.imshow(image, origin="lower", cmap="BrBG", interpolation="nearest",
              vmin=0, vmax=15)
    if not math.isnan(region.xmax) and not math.isnan(region.xmin):
        ax.set_xlim(region.xmin, region.xmax)
    if not math.isnan(region.ymax) and not math.isnan(region.ymin):
        ax.set_ylim(region.ymin, region.ymax)

    ra = ax.coords[0]
    dec = ax.coords[1]
    ra.set_major_formatter("d")
    dec.set_major_formatter("d")
    ra.set_axislabel("RA (degree)", fontsize=12)
    dec.set_axislabel("Dec (degree)", fontsize=12)
    ra.set_ticks(number=8)
    dec.set_ticks(number=6)
    ra.display_minor_ticks(True)
    dec.display_minor_ticks(True)
    ra.set_ticklabel(size=9)
    dec.set_ticklabel(size=9)
    dec.set_ticks_position("l")
    dec.set_ticklabel_position("l")
    dec.set_axislabel_position("l")
    ra.grid(color="white", alpha=0.45, linestyle="solid")
    dec.grid(color="white", alpha=0.45, linestyle="solid")

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="4%", pad=0.35, axes_class=plt.Axes)
    cb = plt.colorbar(ax.images[0], cax=cax)
    cb.set_label("$A_V$", rotation=270, labelpad=16, fontsize=10)
    cb.ax.tick_params(labelsize=8)

    # Empty legend handles keep the map readable while documenting the colors.
    handles = [
        ax.scatter([], [], s=30, c="blue", edgecolors="black", label="BLOS > 0"),
        ax.scatter([], [], s=30, c="red", edgecolors="black", label="BLOS < 0"),
        ax.scatter([], [], s=45, c="lime", edgecolors="darkgreen", marker="o",
                   label="OFF points"),
    ]
    ax.legend(handles=handles, loc="lower left", fontsize=8, framealpha=0.65)
    title = ax.figure.suptitle(
        f"Perseus B$_\\parallel$: combination {combo_number}/{total_combinations}\n"
        f"OFF IDs: {', '.join(map(str, reference_ids))}",
        fontsize=13,
        y=0.97,
    )
    annotation = ax.text(
        0.02,
        0.98,
        f"RM$_{{OFF}}$ = {rm_ref:+.2f} rad m$^{{-2}}$\n"
        f"A$_V$(OFF) = {extinction_ref:.2f} mag",
        transform=ax.transAxes,
        fontsize=9,
        va="top",
        bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.65},
    )
    return annotation, title


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)

    candidates = pd.read_csv(config.FilteredRefPointsFile, sep=config.dataSeparator)
    matched = pd.read_csv(config.MatchedRMExtinctionFile, sep=config.dataSeparator)
    if len(candidates) < COMBINATION_SIZE:
        raise ValueError(
            f"Only {len(candidates)} filtered OFF candidates are available; "
            f"{COMBINATION_SIZE} are required."
        )

    combinations = list(itertools.combinations(range(len(candidates)), COMBINATION_SIZE))
    total_combinations = len(combinations)
    print(f"Using {len(candidates)} filtered OFF candidates.")
    print(f"Generating {total_combinations} combinations of {COMBINATION_SIZE} points.")
    print(f"Outputs: {OUTPUT_DIR}")
    if "--viewer-only" in sys.argv:
        write_viewer(total_combinations)
        return
    if "--movie-only" in sys.argv:
        encode_movie(total_combinations)
        return

    region = Region(config.cloud)
    image = np.asarray(region.hdu.data)
    matched_x, matched_y = _pixel_coordinates(region, matched)
    matched_coordinates = {
        int(row["ID#"]): (x, y)
        for (_, row), x, y in zip(matched.iterrows(), matched_x, matched_y)
    }
    ref_x, ref_y = _pixel_coordinates(region, candidates)

    # Build the figure once and update only the point artists for each frame.
    # Keep the exploratory frames large enough for detailed inspection.
    fig = plt.figure(figsize=(10, 10), dpi=150)
    fig.subplots_adjust(left=0.10, right=0.88, bottom=0.10, top=0.86)
    ax = fig.add_subplot(111, projection=region.wcs)
    annotation, title = _format_frame(
        ax, region, image, None, None, 0, total_combinations,
        [], 0.0, 0.0
    )
    blos_scatter = ax.scatter([], [], marker="o", linewidth=0.5,
                              edgecolors="black", zorder=4)
    ref_scatter = ax.scatter([], [], marker="o", linewidth=1.2,
                             edgecolors="darkgreen", zorder=5)

    metadata = []
    for frame_number, combination in enumerate(combinations, start=1):
        reference = candidates.iloc[list(combination)].copy()
        reference_ids = reference["ID#"].tolist()
        rm_ref, rm_avg_err, rm_std, extinction_ref = calcFiducialVals(reference)

        remaining = rmMatchingPts(matched, reference)
        extinction_limit = config.onPtsExtMultipleThreshold * extinction_ref
        remaining = rmLowExtPts(remaining, extinction_limit)
        blos = CalculateB(
            region.AvFilePath,
            remaining,
            rm_ref,
            rm_avg_err,
            rm_std,
            extinction_ref,
            NegativeExtinctionEntriesChange=config.negScaledExtOption,
        )
        # Match the original BLOS map: OFF-marker area is proportional to the
        # magnitude of the field calculated at each selected OFF position.
        reference_blos = CalculateB(
            region.AvFilePath,
            reference,
            rm_ref,
            rm_avg_err,
            rm_std,
            extinction_ref,
            NegativeExtinctionEntriesChange="None",
        )

        # BLOS points retain the IDs and sky coordinates of the matched table;
        # reuse the cached coordinates instead of converting them per frame.
        blos_coordinates = [matched_coordinates[int(point_id)] for point_id in blos["ID#"]]
        bx, by = np.asarray(blos_coordinates).T
        values = pd.to_numeric(blos["Magnetic_Field(uG)"], errors="coerce").to_numpy()
        finite = np.isfinite(values) & np.isfinite(bx) & np.isfinite(by)
        colors, sizes = p2RGB(values[finite], size_cap=1000, scale_factor=0.5, alpha=0.72)
        blos_scatter.set_offsets(np.column_stack((bx[finite], by[finite])))
        blos_scatter.set_facecolors(colors)
        blos_scatter.set_sizes(sizes)

        ref_scatter.set_offsets(np.column_stack((ref_x[list(combination)], ref_y[list(combination)])))
        ref_values = pd.to_numeric(
            reference_blos["Magnetic_Field(uG)"], errors="coerce"
        ).fillna(0).to_numpy()
        ref_colors, ref_sizes = p2C(
            ref_values, colour=(0, 1, 0), size_cap=1000, scale_factor=0.5, alpha=0.8
        )
        ref_scatter.set_facecolors(ref_colors)
        ref_scatter.set_sizes(ref_sizes)
        annotation.set_text(
            f"RM$_{{OFF}}$ = {rm_ref:+.2f} rad m$^{{-2}}$\n"
            f"A$_V$(OFF) = {extinction_ref:.2f} mag"
        )
        title.set_text(
            f"Perseus B$_\\parallel$: combination {frame_number}/{total_combinations}\n"
            f"OFF IDs: {', '.join(map(str, reference_ids))}"
        )

        frame_path = FRAME_DIR / f"frame_{frame_number:04d}.png"
        fig.savefig(frame_path)
        metadata.append({
            "frame": frame_number,
            "frame_file": frame_path.name,
            "reference_ids": ",".join(map(str, reference_ids)),
            "reference_rm": rm_ref,
            "reference_rm_avg_err": rm_avg_err,
            "reference_rm_sem": rm_std,
            "reference_extinction": extinction_ref,
            "on_point_extinction_limit": extinction_limit,
            "n_blos_points": int(len(blos)),
        })

        if frame_number == 1 or frame_number % 100 == 0 or frame_number == total_combinations:
            print(f"  frame {frame_number}/{total_combinations}")

    plt.close(fig)
    pd.DataFrame(metadata).to_csv(METADATA_FILE, index=False)

    encode_movie(total_combinations)
    print(f"Saved metadata: {METADATA_FILE}")


if __name__ == "__main__":
    main()
