# User guide

combra answers one question: *does a generated WC-Co microstructure have the same
grain geometry as a real one?* It answers it by reducing an image to a small
number of distributions that can be compared numerically, rather than by
comparing pixels.

## The pipeline

```
SEM image
   │  median filter                               combra.angles.preprocess_image
   ▼
filtered image (cobalt dark, carbide bright)
   │  cobalt boundaries at the Otsu level,        combra.angles
   │  Douglas–Peucker, corner rebuilding, spike removal
   ▼
grain contours
   ├─ angle at every vertex                      combra.angles
   │     ▼
   │  angle density  ── bimodal-Gaussian fit ──▶ combra.fitting
   │
   ├─ minimum-volume enclosing ellipse           combra.ellipse
   │     ▼
   │  beam lengths ── distribution fit ────────▶ combra.fitting
   │
   └─ cobalt regions (0.4 µm median mask)        combra.contours
         ├─ region areas ── lognormal fit ─────▶ combra.metrics
         └─ chord lengths πS/P ── Weibull fit ─▶ combra.metrics
                                                        │
   reference vs. generated ─────────────────────────────┘
                     ▼
                  metrics                        combra.metrics

   generated pools with an exact truth ────────▶ combra.synth
   (which method to trust, and how far)
```

Each stage is described below, with links into the reference.

## Stages

**Thresholding.** {py:func}`combra.angles.preprocess_image` reduces an SEM
image to its median-filtered grey image. Every setting is a length
on the sample, set from the image's pixel size
({py:func}`combra.angles.angle_settings`).

**Contours.** {py:func}`combra.angles.vertex_angles` traces the boundary of every
cobalt region of that image between the pixels, at its Otsu level, simplifies each
with Douglas–Peucker, rebuilds the sides shorter than `min_segment_len` into corners
and removes the thin spikes.
Simplification is not cosmetic: the tolerance and the rebuilding set how many vertices
survive, and therefore how many angles the next stage measures. `combra.contours`
provides the Canny-and-Suzuki contour extraction, which the beam fit and the crack
graph use.

**Descriptors.** Three independent reductions of the same image:

- {doc}`angles` — the interior angle at every vertex, pooled into an
  {term}`angle density`. This is combra's primary descriptor.
- {doc}`beams` — the {term}`MVEE` of every contour of the same map, giving
  each grain a size and an orientation, pooled into a beam-length distribution.
- {doc}`areas` — the area of every cobalt region, the cobalt fraction and the
  binder mean free path, from the cobalt mask with its larger median.

**Fitting.** `combra.fitting` fits parametric models to
those distributions. WC-Co angle densities are bimodal, so the
bimodal-Gaussian fit carries most of the interpretive weight: its two means,
widths and amplitudes summarize a microstructure in six numbers.

**Comparison.** {doc}`metrics` scores a generated distribution against a
reference one — Wasserstein distances between the fitted densities, relative
errors on the fitted parameters, and Fréchet distances on deep image features.

**Ground truth.** {py:mod}`combra.synth` generates pools whose
vertices are known, renders them like the micrographs and scores a method
against that truth by size: the overlap of the polygon with the true region,
where its edge sits, the angle error at the corners it found and the share of
reflex vertices it sees. It is how the settings of the angle pipeline were chosen;
see {doc}`synth`.

## Other tooling

{py:mod}`combra.graph` is a separate analysis: it converts a
binarized crack image into a directed graph whose edges are classified by the
phase they cross (Co, WC-Co, WC, WC-WC), then searches for minimum-energy
propagation paths.

{py:class}`combra.data.PolyamideFractureDataset` applies the fractal-dimension
and contour-size measures to a different material, frames of a polyamide
fracture surface, grouped by frame index; see {doc}`../examples/polyamide`.

{py:mod}`combra.io` owns the on-disk formats — the angle, beam, area and
free-path parquet schemas, HDF5 image containers, and the {term}`run_meta` provenance
struct written on every row.

```{toctree}
:maxdepth: 1
:caption: Getting started
:hidden:

../getting_started/installation
../getting_started/quickstart
../getting_started/citing
```

```{toctree}
:maxdepth: 1
:caption: Fundamentals
:hidden:

angles
angle_fit
beams
areas
metrics
```

```{toctree}
:maxdepth: 1
:caption: Methods and ground truth
:hidden:

synth
```

```{toctree}
:maxdepth: 1
:caption: Extras
:hidden:

glossary
```
