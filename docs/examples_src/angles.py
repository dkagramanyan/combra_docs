"""
Angle extraction end to end
===========================

Extract the :term:`vertex angle` values of one image, then the distributions
for every class of the bundled dataset: write them to parquet, and plot the
per-class densities with their bimodal-Gaussian fits.

For what the steps mean, see :doc:`/user_guide/angles`; for the primitives, see
:func:`combra.angles.vertex_angles` and
:meth:`combra.data.MicrostructureDataset.generate_angles`.
"""

# %%
# One image
# ---------
#
# The extraction works on the filtered image of :func:`~combra.angles.preprocess_image`:
# cobalt is its dark side. Every setting is a length on the sample, turned into
# pixels by :func:`~combra.angles.angle_settings` from the pixel size.

import tempfile
from pathlib import Path

import plotly.io as pio

from combra import angles, data

image = data.load_microstructure().images[0]
px = data.SEM_PIXEL_SIZE  # um per pixel of the bundled images
print(angles.angle_settings(px))
prep = angles.preprocess_image(image, pixel_size=px)
print(prep.shape, prep.dtype)

# %%
# :func:`~combra.angles.vertex_angles` returns every vertex angle in degrees and
# the simplified contours that produced them.

angles_deg, contours = angles.vertex_angles(prep, pixel_size=px)
print(angles_deg.min(), angles_deg.max())
print(contours[0].shape[1], contours[0].dtype)

# %%
# A larger ``min_segment_len`` (in pixels of the image; 0.4 um by default) rebuilds
# longer sides into corners, so fewer angles survive:

counts = {
    m: len(angles.vertex_angles(prep, min_segment_len=m, pixel_size=px)[0]) for m in (8, 16, 32)
}
print(counts)

# %%
# Because of that, the value is part of a result's name.
# ``combra.angles.output_directory`` builds the folder the parquets are
# kept in:

print(angles.output_directory("./data/angles", "./data/h5/gen_san_N10000.h5", 8.1))

# %%
# A dataset
# ---------
#
# ``generate_angles`` runs the per-image extraction in parallel over every class
# and writes one parquet, named for the per-class image count.

work = Path(tempfile.mkdtemp())  # scratch folder for the parquet

dataset = data.MicrostructureDataset(
    path=data.microstructure_data_dir(),
    max_per_class=2,  # the bundled sample; None uses every image
    pixel_size=data.SEM_PIXEL_SIZE,
)
# Maps each class directory to the display label used in plot legends.
class_types = {
    "Ultra_Co11": "medium grains",
    "Ultra_Co25": "fine grains",
    "Ultra_Co8": "medium-fine grains",
    "Ultra_Co6_2": "coarse grains",
    "Ultra_Co15": "medium-fine grains",
}
out_path = dataset.generate_angles(
    save_path=work / "angles",
    class_types=class_types,
    step=[5],  # one or more bin widths, in degrees
    workers=2,  # the angle settings come from the dataset's pixel size
)
print(out_path.name)

# %%
# Passing several values in ``step`` writes one density per bin width into the
# same file, so a later comparison can select the one it needs without
# re-extracting.
#
# Inspect
# -------
#
# Each row carries its identity in ``meta`` and its computed payload in ``prep``.
# :func:`combra.io.load_rows` is the loader:

from combra import io

rows = io.load_rows(out_path)
print(len(rows))
print(sorted(rows[0]["meta"]))

# %%
# Plot
# ----
#
# :func:`combra.angles.plot_density` draws one trace pair per class, overlaying
# the measured density and its fit. Pass the parquet path and the ``step`` to
# select:

fig = angles.plot_density(
    parquet_path=out_path,
    step=5.0,
    n_rows=10,
    n_cols=6,  # figure size, in 80 px units
    font_size=14,
    scatter_size=8,
)
pio.show(fig)

# %%
# Every ``plot_*`` in combra returns its figure and takes the same tail
# arguments: ``save_path`` to write a PNG, and ``show=True`` to render it.
