"""
Beam lengths from enclosing ellipses
====================================

Measure grain size by fitting each contour's :term:`MVEE`, then write the
per-class beam-length distributions to parquet.

For what a beam is and why an enclosing ellipse defines it, see
:doc:`/user_guide/beams`.
"""

# %%
# One image
# ---------
#
# :func:`combra.ellipse.fit_mvee` fits every contour in a preprocessed image and
# returns the semi-axes, orientations, centroids and source contours together:

import cv2
import numpy as np
import plotly.io as pio

from combra import data, ellipse

img = data.load_microstructure().images[0]
_, processed = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
result = ellipse.fit_mvee(processed, tol=0.2)
print(len(result.a))
print(result.angle_rad.shape)

# %%
# The solver returns the semi-axes **ascending**, so ``a`` is the minor one:

print(bool(np.all(result.a <= result.b)))
print(round(float(np.median(result.b)), 2))

# %%
# .. warning::
#
#    This ordering is the opposite of the usual ``(semi-major, semi-minor)``
#    reading, and the ``cv2.fitEllipse`` fallback used for contours the solver
#    cannot handle orders them the other way round. Check which you have before
#    treating a beam length as a grain diameter.
#
# The longest contour, drawn with its fitted ellipse — the points
# ``(a cos t, b sin t)`` rotated by ``angle_rad`` about the centroid:

import plotly.graph_objects as go

i = max(range(len(result.contour)), key=lambda k: len(result.contour[k]))
contour = np.asarray(result.contour[i]).reshape(-1, 2)
xc, yc = result.centroid[i]
a, b, theta = result.a[i], result.b[i], result.angle_rad[i]
t = np.linspace(0, 2 * np.pi, 100)
ex = xc + a * np.cos(t) * np.cos(theta) - b * np.sin(t) * np.sin(theta)
ey = yc + a * np.cos(t) * np.sin(theta) + b * np.sin(t) * np.cos(theta)
fig = go.Figure(
    [
        go.Scatter(x=contour[:, 0], y=contour[:, 1], mode="markers", marker_size=3, name="contour"),
        go.Scatter(x=ex, y=ey, mode="lines", name="MVEE"),
    ]
)
fig.update_yaxes(autorange="reversed", scaleanchor="x")  # image coordinates
fig.update_layout(height=450, title=f"a = {a:.1f} px, b = {b:.1f} px")
pio.show(fig)

# %%
# A dataset
# ---------
#
# :meth:`~combra.data.MicrostructureDataset.generate_beams` runs the fit over
# every class, converts the beam lengths to physical units, fits a straight
# line to each log-density, and writes one parquet:

import tempfile

ds = data.MicrostructureDataset(
    path=data.microstructure_data_dir(),
    max_per_class=2,
)
out_path = ds.generate_beams(
    save_path=tempfile.mkdtemp(),  # scratch folder for the parquet
    class_types={
        "Ultra_Co11": "medium grains",
        "Ultra_Co25": "fine grains",
        "Ultra_Co8": "medium-fine grains",
        "Ultra_Co6_2": "coarse grains",
        "Ultra_Co15": "medium-fine grains",
    },
    step=4,  # bin width for the beam-length histogram
    pixel=50 / 1000,  # physical size of one pixel
)
print(out_path.name)

# %%
# ``pixel`` scales the beam lengths out of pixel units and is recorded on the
# row, so runs taken at different magnifications stay comparable:

from combra import io

rows = io.load_rows(out_path)
print(len(rows))
print(rows[0]["meta"]["pixel2meter"])

# %%
# Reading the fit
# ---------------
#
# The beam-length density is approximately exponential, so each row carries the
# slope of a straight line fitted to its log-density. A steeper (more negative)
# slope means the distribution falls off faster — a finer-grained alloy:

print(round(float(rows[0]["prep"]["a_k"]), 4))

# %%
# :func:`~combra.ellipse.plot_beam_lengths` draws every class's log-density with
# its fitted line, one panel per semi-axis. It takes the rows flattened into one
# dict-of-lists:

flat = {key: [row["meta"][key] for row in rows] for key in ("name", "type")}
for key in ("a_x", "a_y_log", "a_x_pred", "a_y_pred", "b_x", "b_y_log", "b_x_pred", "b_y_pred"):
    flat[key] = [row["prep"][key] for row in rows]
fig = ellipse.plot_beam_lengths(flat, step=4, font_size=14)
pio.show(fig)

# %%
# The ``start`` and ``end`` arguments of ``generate_beams`` trim that fit,
# because both extremes of a binned beam distribution are poorly sampled: the
# smallest bins hold tracing noise and the largest hold a handful of grains. The
# defaults drop the first two and last three bins.
#
# See :mod:`combra.ellipse` for the plotting functions and
# :meth:`~combra.data.MicrostructureDataset.generate_beams` for the batch
# writer.
