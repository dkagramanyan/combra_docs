# Angle extraction end to end

Extract {term}`vertex angle` distributions for every class of the bundled
dataset, write them to parquet, and plot the per-class densities with their
bimodal-Gaussian fits.

For what the steps mean, see {doc}`/user_guide/angles`; for the primitives, see
{py:func}`combra.angles.vertex_angles` and
{py:meth}`combra.data.MicrostructureDataset.generate_angles`.

## Extract

`generate_angles` runs the per-image extraction in parallel over every class and
writes one parquet, named for the per-class image count.

```{doctest}
>>> from combra import data
>>> dataset = data.MicrostructureDataset(
...     path=data.microstructure_data_dir(),
...     max_per_class=2,          # the bundled sample; None uses every image
... )
>>> # Maps each class directory to the display label used in plot legends.
>>> class_types = {
...     'Ultra_Co11':  'medium grains',
...     'Ultra_Co25':  'fine grains',
...     'Ultra_Co8':   'medium-fine grains',
...     'Ultra_Co6_2': 'coarse grains',
...     'Ultra_Co15':  'medium-fine grains',
... }
>>> out_path = dataset.generate_angles(
...     save_path='./angles',
...     class_types=class_types,
...     step=[5],                 # one or more bin widths, in degrees
...     workers=2,
...     angles_tol=3,
...     min_segment_len=5.0,
... )
>>> out_path.name
'angles_n2.parquet'
```

Passing several values in `step` writes one density per bin width into the same
file, so a later comparison can select the one it needs without re-extracting.

## Inspect

Each row carries its identity in `meta` and its computed payload in `prep`.
{py:func}`combra.io.load_rows` is the loader:

```{doctest}
>>> from combra import io
>>> rows = io.load_rows(out_path)
>>> len(rows)
5
>>> sorted(rows[0]['meta'])
['image_paths', 'n_images', 'name', 'path', 'step', 'type']
```

## Plot

{py:func}`combra.angles.plot_density` draws one cell per class, overlaying the
measured density and its fit. Pass the parquet path and the `step` to select:

```{doctest}
>>> from combra import angles
>>> fig = angles.plot_density(
...     parquet_path=str(out_path),
...     step=5.0,
...     n_rows=3, n_cols=2,
...     show=False,               # return the figure instead of rendering it
... )
>>> type(fig).__name__
'Figure'
```

Every `plot_*` in combra returns its figure and takes the same tail arguments:
`save_path=None` to write a PNG, and `show=True` to render.
