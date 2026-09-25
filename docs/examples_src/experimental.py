"""
The facet method (P7)
=====================

Run P7 on a bundled image, inspect its regions and stages, and compare its
angles with P6.

For what the stages do, see :doc:`/user_guide/experimental`; for the entry
point, see :func:`combra.experimental.vertex_angles`. The module is
experimental: its API and output may change without a deprecation period.
"""

# %%
# Extract
# -------
#
# :func:`~combra.experimental.vertex_angles` takes the image directly and
# returns the angles with one facet polygon per region. The facet stage is
# Python, so this takes a few seconds per image.

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

from combra import data, experimental

image = data.load_microstructure().images[0]
angles_p7, polygons = experimental.vertex_angles(image)
print(angles_p7.dtype, polygons[0].shape[1])
print(angles_p7.min(), angles_p7.max())

# %%
# Inspect the regions
# -------------------
#
# :func:`~combra.experimental.pool_regions` returns the detection mask and, for
# every region, the gradient-snapped contour, the facet polygon and its angles:

mask, regions = experimental.pool_regions(image)
print(mask.dtype, len(regions))
r = max(regions, key=lambda r: len(r.contour))  # the longest boundary
print(len(r.polygon) == len(r.angles))
print(len(r.polygon), "facet vertices on", len(r.contour), "edge points")

# %%
# The facet polygon of that region over its contour:

fig = go.Figure(
    [
        go.Scatter(
            x=r.contour[:, 0], y=r.contour[:, 1], mode="lines", line_width=6, opacity=0.4, name="contour"
        ),
        go.Scatter(
            x=np.r_[r.polygon[:, 0], r.polygon[:1, 0]],
            y=np.r_[r.polygon[:, 1], r.polygon[:1, 1]],
            mode="lines+markers",
            name="facet polygon",
        ),
    ]
)
fig.update_yaxes(autorange="reversed", scaleanchor="x")  # image coordinates
fig.update_layout(height=500)
pio.show(fig)

# %%
# The stages one at a time
# ------------------------
#
# :func:`~combra.experimental.facets` splits an ordered contour and merges the
# pieces by a line fit. It returns the contour index of every facet vertex and
# one line per facet:

indices, lines = experimental.facets(r.contour.astype(np.float64))
print(len(indices), len(lines))

# %%
# :func:`~combra.experimental.gradient_snap` is the edge locator on its own: it
# moves each point of a contour to the sub-pixel gradient maximum nearby, at
# most ``reach`` px along the normal.

from combra import angles

contour = angles.pool_regions(image)[1][0].contour
(snapped,) = experimental.gradient_snap([contour], image)
print(snapped.shape == contour.shape)
print(round(float(np.abs(snapped - contour).max()), 2))

# %%
# Compare with P6
# ---------------
#
# On the same image P7 puts a vertex on more of the boundary's corners and reads
# a larger share of them as reflex:

angles_p6, _ = angles.vertex_angles(image)
print(len(angles_p7), ">", len(angles_p6))
print(f"reflex share: P7 {(angles_p7 > 180).mean():.2f}, P6 {(angles_p6 > 180).mean():.2f}")

# %%
# The densities of all three methods on this image, with P0 from
# :func:`combra.legacy.vertex_angles` over its preprocessed map:

from combra import legacy

angles_p0, _ = legacy.vertex_angles(legacy.preprocess_image(image), min_segment_len=10.0)
bins = np.arange(0, 365, 5)
fig = go.Figure()
for name, values in [("P0", angles_p0), ("P6", angles_p6), ("P7", angles_p7)]:
    density, _ = np.histogram(values, bins=bins, density=True)
    fig.add_trace(go.Scatter(x=bins[:-1] + 2.5, y=density, mode="lines", name=f"{name} ({len(values)} angles)"))
fig.add_vline(x=180, line_dash="dot", line_color="gray")
fig.update_layout(xaxis_title="vertex angle, degrees", yaxis_title="density", height=400)
pio.show(fig)

# %%
# Whether that larger reflex share is the material's or the method's is the
# open question that keeps P7 experimental.
# :func:`~combra.experimental.extract_polygons` gives P7 in the form
# :func:`combra.synth.benchmark` scores; see :doc:`synth`.
