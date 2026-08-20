# Get started

## Installation

Combra is a standard Python package — all dependencies are pure-pip and install automatically, with no system packages required. combra uses the headless OpenCV build (`opencv-python-headless`), so no `libGL`/`libglib` system libraries are needed; it runs out of the box in minimal containers and HPC environments where you can only install Python packages.

combra is not on PyPI yet, so install it from source:

```bash
git clone https://github.com/dkagramanyan/combra.git
cd combra
pip install .          # or:  pip install -e .   for an editable install
```

### Optional extras

| Extra         | Install                          | Adds                                          |
| ------------- | -------------------------------- | --------------------------------------------- |
| `metrics`     | `pip install ".[metrics]"`       | torch stack for the image-feature metrics (FID / CMMD / FD-DINOv2) |
| `tests`       | `pip install ".[tests]"`         | pytest + pytest-cov                           |
| `docs`        | `pip install ".[docs]"`          | Sphinx docs toolchain                         |
| `dev`         | `pip install -e ".[dev]"`        | the `tests` extra + ruff + mypy               |

The image-feature metrics (`[metrics]` extra) score in-memory image batches and run on
CUDA when available, falling back to CPU. `compute_fid` uses the
[pytorch-fid](https://github.com/mseitzer/pytorch-fid) InceptionV3 backbone, which
downloads/caches its own weights on first use; the DINOv2 backbone for `compute_fd_dinov2` is fetched
from `torch.hub` on first use — no manual model setup. See {doc}`combra.metrics <api/metrics>`.

The angle-Wasserstein training metrics use [POT](https://pythonot.github.io/) (`pot`), also a core dependency.

## Testing

After a development install you can run the full test suite, the linter, and the formatter:

```bash
pip install -e ".[dev]"

pytest                           # run the test suite
ruff check combra tests          # lint
ruff format combra tests         # format
```

Two suites are deselected from a bare `pytest` (and therefore from CI) because
they are not pass/fail checks a push should pay for:

```bash
pytest -m slow                   # ~11 s: ground-truth check of the angle metrics
                                 # against synthetic images whose vertex angles
                                 # are known exactly. Run after touching the angle
                                 # pipeline, the bimodal fit, or the gauss metrics.

pytest -m visual -s              # writes interactive plotly HTML for you to look
                                 # at: the bimodal-Gaussian fit on synthetic angle
                                 # data, and whether each fit was judged usable.
                                 # Paths are printed; COMBRA_VISUAL_DIR overrides
                                 # where they are written.
```

CI (GitHub Actions) runs the ruff lint + format checks and `pytest` on Python 3.10, 3.11, and 3.12.

For a quick post-install sanity check that doesn't need the dev tools, run the bundled self-validation helper — it estimates the fractal dimension of reference shapes with known answers (see {doc}`combra.validation <api/validation>`):

```pycon
>>> import numpy as np
>>> from combra import validation
>>> validation.check_fractal_dimension(np.array([2, 3, 4, 6, 8, 12, 16, 24, 32]))
```

## Smoke test

A few lines that exercise the full pipeline — load a bundled image, preprocess it, extract angles:

```pycon
>>> import cv2
>>> from combra import data, angles
>>> img = data.load_microstructure().images[0]
>>> _, processed = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
>>> arr, contours = angles.vertex_angles(processed, border_eps=5, tol=3, min_segment_len=10.0)
>>> print(f'{len(arr)} angles, mean={arr.mean():.2f}°')
```

## First parquet

End-to-end: run angle extraction on every class in the bundled dataset, write one parquet with full provenance.

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

The output file's `run_meta` column records who/when/what — including the git commit and exact extraction params — so the parquet is fully self-describing.

## Module map

See the {doc}`landing page <index>` for the full module grid, and
{doc}`glossary` for the domain vocabulary (`step`, beam, MVEE, N-sweep).

## What changed in 0.6

0.6 is an API-convention release: functions were renamed to `verb_noun` form,
two modules moved (`combra.approx` → {doc}`combra.fitting <api/fitting>`,
`combra.mvee` → {doc}`combra.ellipse <api/ellipse>`), and every plotter now
returns its figure and takes `save_path=` / `show=`. **There are no
compatibility aliases** — see the release notes in the repository `CHANGELOG.md`
for the full rename table.
