"""
Experimental methods
====================

Run P6 on a bundled image, inspect its regions, compare its angles with P0,
the method of :mod:`combra.angles`, and fit a density with the mass-share
model.

For what the stages do, see :doc:`/user_guide/experimental`; for the entry
point, see :func:`combra.experimental.vertex_angles`. The module is
experimental: its API and output may change without a deprecation period.
"""

# %%
# Extract
# -------
#
# :func:`~combra.experimental.vertex_angles` takes the image directly and
# returns the angles with one sub-pixel polygon per region.

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

from combra import data, experimental

image = data.load_microstructure().images[0]
angles_p6, polygons = experimental.vertex_angles(image)
print(angles_p6.dtype, polygons[0].shape[1])
print(angles_p6.min(), angles_p6.max())

# %%
# Inspect the regions
# -------------------
#
# :func:`~combra.experimental.pool_regions` returns the detection mask and, for
# every region, the sub-pixel contour, the polygon and its angles:

mask, regions = experimental.pool_regions(image)
print(mask.dtype, len(regions))
r = max(regions, key=lambda r: len(r.contour))  # the longest boundary
print(len(r.polygon) == len(r.angles))
print(len(r.polygon), "vertices on", len(r.contour), "boundary points")

# %%
# The polygon of that region over its contour. The polygon is stored inset
# from the mask's boundary, onto the cobalt boundary:

fig = go.Figure(
    [
        go.Scatter(
            x=r.contour[:, 0], y=r.contour[:, 1], mode="lines", line_width=6, opacity=0.4, name="contour"
        ),
        go.Scatter(
            x=np.r_[r.polygon[:, 0], r.polygon[:1, 0]],
            y=np.r_[r.polygon[:, 1], r.polygon[:1, 1]],
            mode="lines+markers",
            name="polygon",
        ),
    ]
)
fig.update_yaxes(autorange="reversed", scaleanchor="x")  # image coordinates
fig.update_layout(height=500)
pio.show(fig)

# %%
# Images of another resolution
# ----------------------------
#
# Three settings are lengths in pixels. ``scale``, the image pixels per native
# micrograph pixel, makes them follow the resolution;
# :func:`~combra.experimental.settings_for_scale` shows the values it selects:

print(experimental.settings_for_scale(512 / 1536))
print(experimental.settings_for_scale(1.0))

# %%
# The scale is part of a result's name.
# :func:`~combra.experimental.output_directory` builds the folder P6 parquets
# are kept in:

print(experimental.output_directory("./data/angles", "./data/h5/gen_san_N10000.h5", scale=0.25))

# %%
# Compare with P0
# ---------------
#
# P0, :func:`combra.angles.vertex_angles`, reads the preprocessed map. P6 takes
# the image itself, finds the faint pools that Otsu's threshold alone misses,
# and puts a vertex on many more true corners, so it returns far more angles
# from the same image:

from combra import angles

angles_p0, _ = angles.vertex_angles(angles.preprocess_image(image), min_segment_len=10.0)
print(len(angles_p0), "<", len(angles_p6))
print(f"reflex share: P0 {(angles_p0 > 180).mean():.2f}, P6 {(angles_p6 > 180).mean():.2f}")

# %%
# Their densities over the same 5° bins:

bins = np.arange(0, 365, 5)
fig = go.Figure()
for name, values in [("P0", angles_p0), ("P6", angles_p6)]:
    density, _ = np.histogram(values, bins=bins, density=True)
    fig.add_trace(go.Scatter(x=bins[:-1] + 2.5, y=density, mode="lines", name=f"{name} ({len(values)} angles)"))
fig.add_vline(x=180, line_dash="dot", line_color="gray")
fig.update_layout(xaxis_title="vertex angle, degrees", yaxis_title="density", height=400)
pio.show(fig)

# %%
# The two densities are different measurements, so compare images only within
# one method. :func:`~combra.experimental.extract_polygons` gives P6 in the form
# :func:`combra.synth.benchmark` scores; see :doc:`synth` for the comparison on
# synthetic images.

# %%
# The mass-share fit
# ------------------
#
# :func:`~combra.experimental.fit_bimodal_gaussian` fits a density with one
# mass share in place of the two amplitudes of
# :func:`combra.fitting.fit_bimodal_gaussian`. Both on the P0 angles of all
# five bundled images:

from combra import fitting, stats

pooled = np.concatenate(
    [angles.vertex_angles(angles.preprocess_image(im))[0] for im in data.load_microstructure().images]
)
x, y = stats.density_histogram(pooled, 5.0)
share_fit = experimental.fit_bimodal_gaussian(x, y)
amp_fit = fitting.fit_bimodal_gaussian(x, y)
print("share fit:", np.round(share_fit.mus, 1), np.round(share_fit.shares, 3), round(share_fit.total, 3))
print("amplitude fit:", np.round(amp_fit.mus, 1), np.round(amp_fit.amps, 3))

# %%
# The share fit holds the sum of the amplitudes at the mass of the histogram,
# here the bin width; the amplitude fit leaves it free:

print(round(sum(amp_fit.amps), 3), "against", round(share_fit.total, 3))
