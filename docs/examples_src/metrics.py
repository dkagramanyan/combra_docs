"""
Scoring a generated microstructure
==================================

Compare a generated :term:`angle density` against a reference one, and read
what each family of numbers says. For the concepts behind them, see
:doc:`/user_guide/metrics`.

Every two-input metric takes the **reference first**, then the generated
sample.
"""

# %%
# Two densities
# -------------
#
# A real comparison reduces images to densities with
# :func:`~combra.metrics.images_to_angle_density`. Here the densities are built
# analytically instead, so the answers are known in advance: two bimodal curves
# whose first mode differs by 5°, and a unimodal one used further down.

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

from combra import metrics, stats

x = np.arange(0.0, 360.0, 5.0)
reference = (x, stats.bimodal_gaussian(x, 100.0, 250.0, 20.0, 20.0, 3.0, 1.0))
generated = (x, stats.bimodal_gaussian(x, 105.0, 250.0, 20.0, 20.0, 3.0, 1.0))
unimodal = (x, stats.gaussian(x, 100.0, 20.0, 3.0))

fig = go.Figure(
    [
        go.Scatter(x=x, y=y, mode="lines+markers", name=name)
        for name, (_, y) in [
            ("reference", reference),
            ("generated", generated),
            ("unimodal", unimodal),
        ]
    ]
)
fig.update_layout(xaxis_title="angle, degrees", yaxis_title="density", height=400)
pio.show(fig)

# %%
# Transport distances
# -------------------
#
# :func:`~combra.metrics.compute_wasserstein_metrics` scores the whole
# distribution with one number per variant. The circular forms treat angles on
# the circle, which is the correct geometry — on the line, mass at 1° and mass
# at 359° look maximally far apart instead of 2°.

distances = metrics.compute_wasserstein_metrics(reference, generated)
print(sorted(distances))
print(round(distances["w1"], 3))

# %%
# The value is below the 5° mode shift because only the first mode moved, and
# it carries three quarters of the mass.
#
# Parametric errors
# -----------------
#
# :func:`~combra.metrics.compute_gauss_metrics` fits a bimodal Gaussian to each
# density and reports the relative error of each fitted parameter. Where the
# transport distances say *how far apart*, these say *which part is wrong*:

errors = metrics.compute_gauss_metrics(reference, generated)
print(sorted(errors))
print(round(errors["mu1"], 3))
print(round(abs(errors["mu2"]), 3))

# %%
# ``mu1`` is 0.05 — the first mode is 5% off its reference position of 100° —
# while the untouched second mode reads 0.
#
# When the parametric metrics go undefined
# ----------------------------------------
#
# A generator whose grains are near-convex produces a density with only one
# mode. The bimodal model still returns two, so the second is a solver artefact
# and every relative error computed from it would be meaningless. combra returns
# ``nan`` instead:

errors = metrics.compute_gauss_metrics(reference, unimodal)
print(bool(np.all(np.isnan(list(errors.values())))))

# %%
# The transport distances remain defined, which is why they are the ones to
# watch early in training:

distances = metrics.compute_wasserstein_metrics(reference, unimodal)
print(round(distances["w1"], 3))

# %%
# :func:`~combra.metrics.degenerate_fit_reason` reports why a fit was rejected:

from combra import fitting

_, mus, sigmas, shares, _ = fitting.fit_bimodal_gaussian(*unimodal)
print(metrics.degenerate_fit_reason(mus, sigmas, shares, density=unimodal))

# %%
# The full set of rejection criteria is in :ref:`undefined-rather-than-wrong`.
#
# In a training loop
# ------------------
#
# :func:`~combra.metrics.compute_all_metrics` runs both angle families on
# in-memory image batches, and adds the image-feature metrics (FID, CMMD,
# FD-DINOv2) when asked. Those need at least two images per side. The batches
# below are placeholders, so the session is not run:
#
# .. code-block:: pycon
#
#    >>> scores = metrics.compute_all_metrics(
#    ...     real_batch, generated_batch, image_metrics=True,
#    ... )
#    >>> scores['w1'], scores['mu1'], scores['fid']
#
# Pass a shared ``reference_cache`` dict across calls to compute the reference
# side once. See :mod:`combra.metrics` for the sharded evaluation harness and
# the convergence tools.
