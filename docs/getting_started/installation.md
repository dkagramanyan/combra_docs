# Installation

combra is a pure-pip package: every dependency installs from PyPI, and no system
libraries are required. It uses the headless OpenCV build
(`opencv-python-headless`), so `libGL` and `libglib` are not needed and the
package runs unchanged in minimal containers and on HPC nodes where only Python
packages can be installed.

Every metric works from a plain install. The image-feature metrics
(FID / CMMD / FD-DINOv2) need PyTorch, so `torch`, `torchvision`, `pytorch-fid`
and `open-clip-torch` are core dependencies and a default install is
correspondingly large — on the order of a gigabyte, most of it PyTorch.

```{note}
Installing into an environment that already has a CUDA-specific PyTorch — the
arrangement the {doc}`model repositories </models/spec>` use, where torch comes
from the PyTorch wheel index — leaves that build in place, provided it satisfies
combra's floor of `torch>=2.13`. Install torch first, then combra, so pip has
nothing to resolve.
```

combra is not yet on PyPI. Install from source:

```bash
git clone https://github.com/dkagramanyan/combra.git
cd combra
pip install .          # or:  pip install -e .   for an editable install
```

Python 3.12 or newer is required.

## Optional extras

| Extra     | Install                    | Adds                                                        |
| --------- | -------------------------- | ----------------------------------------------------------- |
| `tests`   | `pip install ".[tests]"`   | pytest + pytest-cov                                          |
| `docs`    | `pip install ".[docs]"`    | Sphinx docs toolchain                                        |
| `dev`     | `pip install -e ".[dev]"`  | the `tests` extra + ruff + mypy                              |
| `metrics` | `pip install ".[metrics]"` | nothing — an empty alias kept so existing installs still work |

The image-feature metrics score in-memory image batches and use CUDA when
available, falling back to CPU. {py:func}`~combra.metrics.compute_fid` uses the
[pytorch-fid](https://github.com/mseitzer/pytorch-fid) InceptionV3 backbone,
which downloads and caches its own weights on first use; the DINOv2 backbone for
{py:func}`~combra.metrics.compute_fd_dinov2` is fetched from `torch.hub` on first
use. Neither needs manual setup. See {doc}`combra.metrics <../api/metrics>`.

The angle-Wasserstein metrics use [POT](https://pythonot.github.io/) (`pot`),
which is a core dependency rather than an extra.

## Verifying the install

The bundled self-check estimates the fractal dimension of reference shapes whose
dimensions are known analytically, and reports the error on each. It needs
nothing beyond the core install.

```{doctest}
>>> import numpy as np
>>> from combra import validation
>>> validation.check_fractal_dimension(np.array([2, 3, 4, 6, 8, 12, 16, 24, 32]))
```

See {py:func}`combra.validation.check_fractal_dimension` for the shapes covered.

For the test suite and linters, see {doc}`../development/testing`.
