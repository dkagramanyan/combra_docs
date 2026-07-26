# Angles

End-to-end angle extraction on the bundled dataset, then a grid plot of the per-class
distributions. See {py:func}`combra.angles.vertex_angles` and
{py:meth}`combra.data.MicrostructureDataset.generate_angles` for the underlying primitives.

```pycon
>>> from combra import data, angles
>>> import pyarrow.parquet as pq
>>> dataset = data.MicrostructureDataset(
...     path=data.microstructure_data_dir(),
...     max_per_class=None,   # use every available image per class
... )
>>> class_types = {'Ultra_Co11': 'средние зерна',
...               'Ultra_Co25': 'мелкие зерна',
...               'Ultra_Co8': 'средне-мелкие зерна',
...               'Ultra_Co6_2': 'крупные зерна',
...               'Ultra_Co15': 'средне-мелкие зерна'}
>>> # Compute angle distributions and write them to ./angles/angles_n{N}.parquet.
>>> out_path = dataset.generate_angles(
...     save_path='./angles',
...     class_types=class_types,
...     step=[5],                # one or more histogram steps (degrees)
...     workers=20,
...     angles_tol=3,
...     min_segment_len=5.0,
... )
>>> rows = pq.read_table(out_path).to_pydict()
>>> angles.plot_density(
...     rows, save_name='orig_step=5', N=15, M=7,
...     step=5.0, save=False, indices=None, font_size=20, scatter_size=20,
... )
```
