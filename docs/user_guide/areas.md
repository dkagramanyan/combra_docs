# Cobalt regions

The third descriptor is the cobalt binder itself: the area of every pool of cobalt
between the carbide grains, the share of the image they cover, and how thick the pools
are, the binder mean free path.

## The mask and its regions

{py:func}`combra.contours.cobalt_mask` is the dark side of the Otsu threshold of the
median-filtered image. The median is 0.4 µm of the sample
({py:func}`combra.contours.median_radius`: 2, 4 and 8 px at 256, 512 and 1024 px WC-Co
crops), larger than the 0.1 µm of the angle binary: it removes the noise specks that the
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
{py:func}`combra.metrics.fit_area_distribution` fits it from the mode or a given start
on, and {py:func}`combra.metrics.area_metrics` compares two samples, both fitted from
the mode of the reference; see {doc}`metrics`.
{py:func}`combra.contours.plot_area_grid` draws the distributions of several sources
in a grid, as {py:func}`~combra.angles.plot_density_grid` draws the angles.

## Mean free path

The area does not tell a compact pool from a thin film of the same area. The mean
length of the chords that straight lines cut in a region does: by the Cauchy–Crofton
relation it is $\ell = \pi S / P$ for a region of area $S$ and boundary length $P$,
and over the regions of an image $\lambda_{\mathrm{Co}} = \pi \sum S / \sum P$ is the
binder mean free path. {py:func}`combra.contours.free_paths` returns both for one image:

```pycon
>>> r = contours.free_paths(data.load_microstructure().images[0],
...                         pixel_size=data.SEM_PIXEL_SIZE)
>>> r.lengths  # chord length of every kept region, px
>>> r.mean  # mean free path of the image, px
```

The regions are those of the cobalt mask, with two kinds left out: those touching the
image frame, whose boundary would include the cut, and those under 0.16 µm² (the
square of the 0.4 µm median), which the median leaves as noise. $P$ is the
4-direction Crofton perimeter and includes the boundaries of the carbide grains inside
a region.

Past 0.5 µm the chord lengths follow a Weibull distribution,

$$p(\ell) = \frac{k}{\lambda} \left( \frac{\ell}{\lambda} \right)^{k-1}
\exp\left[ \left( \frac{\ell_0}{\lambda} \right)^k
- \left( \frac{\ell}{\lambda} \right)^k \right], \qquad \ell \ge \ell_0 = 0.5~\text{µm};$$

below it the area cut and the median shape the histogram.
{py:func}`combra.metrics.fit_free_path_distribution` fits the scale $\lambda$ and the
shape $k$ by maximum likelihood, and {py:func}`combra.metrics.free_path_metrics`
compares two samples; see {doc}`metrics`. On the WC-Co training crops the fit keeps 79–91 %
of the regions, with $\lambda$ = 0.77 / 0.86 / 1.05 µm and $k$ = 2.3 / 1.8 / 1.8 for
small / medium / large grains, the same at 256 and 512 px within 2.4 %. The mean
$\langle \ell \rangle$ of the fit, compared as `mfp_mean`, is 0.84 / 0.97 / 1.14 µm at
256 px and 0.83 / 0.97 / 1.13 µm at 512 px, and equals the sample mean of the lengths
past 0.5 µm to 0.02 %.

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

{py:meth}`~combra.data.MicrostructureDataset.generate_free_paths` does the same for the
mean free path and writes `free_paths_n{N}.parquet`
({py:data}`combra.io.FREE_PATHS_SCHEMA`): the area and the perimeter of every kept
region in pixels (`raw`), the mean $\lambda_{\mathrm{Co}}$ of the class in µm (`meta`),
and per histogram step the chord-length density and the Weibull fit in µm
(`prep_per_step`).

```{note}
Read compressed HDF5 images in blocks of whole chunks. A chunk is decompressed whole,
so a loop that reads one image at a time decompresses its chunk once per image: for
the 256-image lzf chunks of the 512 px generated sets that is 0.65 s per image, 25
times the 26 ms of the mask. `generate_areas` hands each worker a block aligned to the
chunks and builds no image cache, so 10 000 images per class of three classes take
about 50 s with 16 workers.
```
