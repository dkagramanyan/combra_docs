# Cobalt regions

The third descriptor is the cobalt binder itself: the area of every pool of cobalt
between the carbide grains, and the share of the image they cover.

## The mask and its regions

{py:func}`combra.contours.cobalt_mask` is the dark side of the Otsu threshold of the
median-filtered image. The median is 0.4 µm of the sample
({py:func}`combra.contours.median_radius`: 2, 4 and 8 px at 256, 512 and 1024 px WC-Co
crops), larger than the 0.1 µm of the angle map: it removes the noise specks that the
angles tolerate but an area count does not. With it the cobalt fraction of the
training crops is within 2.4 % of the alloys' cobalt volume fraction at every
resolution.

A region is an 8-connected component of the mask and its area is its pixel count;
{py:func}`combra.contours.areas` returns the areas and the cobalt fraction of one image:

```pycon
>>> from combra import contours, data
>>> r = contours.areas(data.load_microstructure().images[0],
...                    pixel_size=data.SEM_PIXEL_SIZE)
>>> r.fraction  # share of cobalt pixels
```

Regions cut by the image frame are kept with their visible area, as the semi-axes
keep their ellipses.

## The distribution

Past a peak at a few pixels the areas follow a lognormal distribution.
{py:func}`combra.metrics.fit_area_distribution` fits it from the mode on, and
{py:func}`combra.metrics.area_metrics` compares two samples; see {doc}`metrics`.
{py:func}`combra.contours.plot_area_grid` draws the distributions of several sources
in a grid, as {py:func}`~combra.angles.plot_density_grid` draws the angles.

## A whole dataset

{py:meth}`combra.data.MicrostructureDataset.generate_areas` runs the same extraction
over every image of an HDF5 file and writes one parquet row per class
({py:data}`combra.io.AREAS_SCHEMA`), as `generate_angles` and `generate_beams` do:

```python
from combra import data

ds = data.MicrostructureDataset(path="data/h5/gen_san_512x512_N100_000.h5",
                                max_per_class=10_000)  # pixel size from the h5
out = ds.generate_areas(save_path="data/areas/gen_san_512",
                        class_types={"Ultra_Co25": "small grains"},
                        run_meta={"family": "san", "resolution": 512})
```

The row holds the area of every region in pixels, whether it touches the frame, the
regions of each image and its cobalt fraction (`raw`); the pixel size and the mean
cobalt fraction (`meta`); and per histogram step the area density and the lognormal
fit, in µm² (`prep_per_step`). {py:func}`combra.io.load_rows` reads it like the other
parquets.

```{note}
Read compressed HDF5 images in blocks of whole chunks. A chunk is decompressed whole,
so a loop that reads one image at a time decompresses its chunk once per image: for
the 256-image lzf chunks of the 512 px generated sets that is 0.65 s per image, 25
times the 26 ms of the mask. `generate_areas` hands each worker a block aligned to the
chunks and builds no image cache, so 10 000 images per class of three classes take
about 50 s with 16 workers.
```
