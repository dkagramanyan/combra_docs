"""
Benchmarking an angle method
============================

Generate a canvas of pools with an exact truth, render it, score one method on
it, then compare P0, P6 and P7 over the same canvas.

For what the metrics mean, see :doc:`/user_guide/synth`; for the entry points,
see :func:`combra.synth.make_canvas` and :func:`combra.synth.benchmark`.
"""

# %%
# Generate and render
# -------------------
#
# A canvas is fixed by its seed. It holds the coverage map the renderer takes
# and one truth region per pool.

import numpy as np
import plotly.io as pio

from combra import synth

cv = synth.make_canvas(0)
print(cv.coverage.shape)
print(len(cv.regions))
region = cv.regions[0]  # the largest pool
print(region.polygon.shape, round(float(region.diameter), 1))
img = synth.render(cv.coverage, np.random.default_rng(300))
print(img.dtype, img.shape)

# %%
# The truth polygons store every vertex, so their angles are known exactly. The
# default draw keeps half of them reflex:

truth = np.concatenate([synth.interior_angles(r.polygon) for r in cv.regions])
print(round(float((truth > 180).mean()), 3))

# %%
# Score one method on one canvas
# ------------------------------
#
# A method is any function that returns ``(mask, polygons)`` for an image.
# :func:`combra.angles.extract_polygons` is P6 in that form:

from combra import angles

score = synth.score_canvas(*angles.extract_polygons(img), cv)
summary, by_bin = synth.summarize([score])
print(f"found {summary['found']:.3f}, IoU {summary['iou_truth']:.3f}")
print(f"RMS edge error {summary['rms']:.2f} px")
print(list(by_bin)[:3])

# %%
# Compare methods
# ---------------
#
# :func:`~combra.synth.benchmark` generates, renders and scores in one call.
# ``seeds=[0]`` scores the single canvas above; the reference numbers use
# ``range(20)``.

from combra import experimental, legacy

methods = {
    "P0": legacy.extract_polygons,
    "P6": angles.extract_polygons,
    "P7": experimental.extract_polygons,
}
results = {name: synth.benchmark(m, seeds=[0]) for name, m in methods.items()}
recovery = {name: r.summary["corner_recovery"] for name, r in results.items()}
print({name: round(v, 3) for name, v in recovery.items()})

# %%
# :func:`~combra.synth.plot_benchmark` draws the four metrics by region size,
# one line per method:

fig = synth.plot_benchmark(results)
pio.show(fig)

# %%
# To score a variant of a method, wrap it so it keeps the same signature. Here
# P6 runs at a coarser simplification tolerance, and recovers fewer corners:

coarse = synth.benchmark(lambda im: angles.extract_polygons(im, tol=3.0), seeds=[0])
print(round(coarse.summary["corner_recovery"], 3), "<", round(recovery["P6"], 3))

# %%
# Look at the canvas
# ------------------
#
# :func:`~combra.synth.plot_canvas` shows a crop of the rendering with the true
# outlines and the P6 mask:

fig = synth.plot_canvas(cv, img)
pio.show(fig)

# %%
# :func:`~combra.synth.plot_pools` shows a gallery of generated pool shapes:

fig = synth.plot_pools(40, rng=5)
pio.show(fig)
