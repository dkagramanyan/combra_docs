# Quickstart

Two short sessions: one that exercises the pipeline on a single bundled image,
one that produces a parquet of {term}`angle density` curves for a whole dataset.
For what the steps mean, read {doc}`../user_guide/index`.

## A single image

Load a bundled SEM image, binarize it, and extract its {term}`vertex angle`
values:

```pycon
>>> import cv2
>>> from combra import data, angles
>>> img = data.load_microstructure().images[0]
>>> _, processed = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
>>> arr, contours = angles.vertex_angles(processed, border_eps=5, tol=3, min_segment_len=10.0)
>>> print(f'{len(arr)} angles, mean={arr.mean():.2f}°')
```

{py:func}`~combra.angles.vertex_angles` returns the angles concatenated across
contours, and the simplified contours that produced them.

## A dataset

{py:meth}`~combra.data.MicrostructureDataset.generate_angles` runs the same
extraction over every image of every class in parallel and writes one parquet
holding the per-class densities, their bimodal-Gaussian fits, and full
provenance:

```pycon
>>> from combra import data
>>> ds = data.MicrostructureDataset(
...     path=data.microstructure_data_dir(),
...     max_per_class=50,
... )
>>> ds.generate_angles(
...     save_path='./smoke_test',
...     class_types={'Ultra_Co11': 'medium', 'Ultra_Co25': 'fine'},
...     step=[1, 5, 10],
...     workers=8, min_segment_len=5.0, keep_contours=False,
...     run_meta={'family': 'real', 'resolution': 1024, 'notes': 'smoke'},
... )
```

The `step` argument is the histogram bin width in degrees, and passing several
writes one density per step. The {term}`run_meta` column records the source
files, the extraction parameters, the git commit, the user and the timestamp, so
the parquet describes exactly how it was produced.

## Where to go next

{doc}`../user_guide/index`
: The pipeline end to end — what each stage computes and why.

{doc}`../user_guide/glossary`
: The domain vocabulary (`step`, beam, MVEE, N-sweep) used throughout the
  reference.

{doc}`../api/data`
: The API reference, one page per module.

{doc}`../examples/angles`
: Worked examples.
