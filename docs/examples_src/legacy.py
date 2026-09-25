"""
The previous angle method (P0)
==============================

Extract P0 angles from a bundled image, see how ``min_segment_len`` changes
them, and compare the result with P6 on the same image.

For what the steps do, see :doc:`/user_guide/legacy`; for the entry point, see
:func:`combra.legacy.vertex_angles`.
"""

# %%
# Preprocess
# ----------
#
# P0 works on the three-level map of :func:`~combra.legacy.preprocess_image`:
# the thresholded mask and its boundary in one ``uint8`` array.

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

from combra import data, legacy

image = data.load_microstructure().images[0]
prep = legacy.preprocess_image(image)
print(prep.shape, prep.dtype)
print(np.unique(prep).tolist())

# %%
# Extract
# -------
#
# :func:`~combra.legacy.vertex_angles` returns every vertex angle in degrees and
# the simplified contours that produced them.

angles_p0, contours = legacy.vertex_angles(prep, min_segment_len=10.0)
print(angles_p0.min(), angles_p0.max())
print(contours[0].shape[1], contours[0].dtype)

# %%
# A larger ``min_segment_len`` prunes more of the short, pixel-staircase
# segments, so fewer angles survive:

counts = {m: len(legacy.vertex_angles(prep, min_segment_len=m)[0]) for m in (5, 10, 20)}
print(counts)

# %%
# Because of that, the value is part of a result's name.
# :func:`~combra.legacy.output_directory` builds the folder P0 parquets are kept
# in:

print(legacy.output_directory("./data/angles", "./data/h5/gen_san_N10000.h5", 5.0))

# %%
# Compare with P6
# ---------------
#
# P6 takes the image itself, finds the faint pools that Otsu's threshold alone
# misses, and puts a vertex on many more true corners, so it returns far more
# angles from the same image:

from combra import angles

angles_p6, polygons = angles.vertex_angles(image)
print(len(angles_p0), len(angles_p6))

# %%
# Their densities over the same 5° bins:

bins = np.arange(0, 365, 5)
fig = go.Figure()
for name, values in [("P0", angles_p0), ("P6", angles_p6)]:
    density, _ = np.histogram(values, bins=bins, density=True)
    fig.add_trace(go.Scatter(x=bins[:-1] + 2.5, y=density, mode="lines", name=f"{name} ({len(values)} angles)"))
fig.update_layout(xaxis_title="vertex angle, degrees", yaxis_title="density", height=400)
pio.show(fig)

# %%
# The two densities are different measurements, so compare images only within
# one method. :func:`~combra.legacy.extract_polygons` gives P0 in the form
# :func:`combra.synth.benchmark` scores; see :doc:`synth` for the comparison on
# synthetic images.
