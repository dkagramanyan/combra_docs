# User guide

combra answers one question: *does a generated WC-Co microstructure have the same
grain geometry as a real one?* It answers it by reducing an image to a small
number of distributions that can be compared numerically, rather than by
comparing pixels.

## The pipeline

```
SEM image
   │  median, Otsu ∪ adaptive threshold           combra.angles.pool_mask
   ▼
cobalt pools (mask)
   │  sub-pixel boundary, Douglas–Peucker,        combra.angles
   │  lines fitted to every edge
   ▼
pool polygons
   ├─ angle at every vertex                      combra.angles
   │     ▼
   │  angle density  ── bimodal-Gaussian fit ──▶ combra.fitting
   │
   └─ minimum-volume enclosing ellipse           combra.ellipse
         ▼                                       (on combra.legacy.preprocess_image)
      beam lengths ── distribution fit ────────▶ combra.fitting
                                                        │
   reference vs. generated ─────────────────────────────┘
                     ▼
                  metrics                        combra.metrics

   generated pools with an exact truth ────────▶ combra.synth
   (which method to trust, and how far)
```

Each stage is described below, with links into the reference.

## Stages

**Detection.** {py:func}`combra.angles.pool_mask` reduces an SEM image to the
mask of its cobalt pools, the dark phase: a 3×3 median filter, the union of
Otsu's threshold and a Gaussian adaptive threshold (Otsu alone misses the faint
pools, the adaptive threshold alone the interior of the large ones), specks
removed, one pixel of dilation.

**Polygons.** {py:mod}`combra.angles` moves the mask's contours to
the 0.5 level of the blurred mask, chooses the vertices with Douglas–Peucker
and fits a line to the boundary of every edge. Simplification is not cosmetic:
the tolerance sets how many vertices survive, and therefore how many angles the
next stage measures. `combra.contours` still provides
the Canny-and-Suzuki contour extraction the beam fit and the crack graph use.

**Descriptors.** Two independent reductions of the same image:

- {doc}`angles` — the interior angle at every vertex, pooled into an
  {term}`angle density`. This is combra's primary descriptor.
- {doc}`beams` — the {term}`MVEE` of every contour of the P0 map
  ({py:func}`combra.legacy.preprocess_image`), giving each grain a size and an
  orientation, pooled into a beam-length distribution.

**Fitting.** `combra.fitting` fits parametric models to
those distributions. WC-Co angle densities are bimodal, so the
bimodal-Gaussian fit carries most of the interpretive weight: its two means
and widths and the mixing coefficient summarize a microstructure in five
numbers.

**Comparison.** {doc}`metrics` scores a generated distribution against a
reference one — Wasserstein distances on the densities, relative errors on the
fitted parameters, and Fréchet distances on deep image features.

**Ground truth.** {py:mod}`combra.synth` generates pools whose
vertices are known, renders them like the micrographs and scores a method
against that truth by size: the overlap of the polygon with the true region,
where its edge sits, the angle error at the corners it found and the share of
reflex vertices it sees. It is how P6 was chosen over P0
({py:mod}`combra.legacy`) and how P7
({py:mod}`combra.experimental`) is kept in view; see {doc}`synth`,
{doc}`legacy` and {doc}`experimental`.

## Other tooling

{py:mod}`combra.graph` is a separate analysis: it converts a
binarized crack image into a directed graph whose edges are classified by the
phase they cross (Co, WC-Co, WC, WC-WC), then searches for minimum-energy
propagation paths. It needs the `graph` extra
({doc}`../getting_started/installation`).

{py:class}`combra.data.PolyamideFractureDataset` applies the fractal-dimension
and contour-size measures to a different material, frames of a polyamide
fracture surface, grouped by frame index; see {doc}`../examples/polyamide`.

{py:mod}`combra.io` owns the on-disk formats — the angle and beam
parquet schemas, HDF5 image containers, and the {term}`run_meta` provenance
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
metrics
```

```{toctree}
:maxdepth: 1
:caption: Methods and ground truth
:hidden:

synth
legacy
experimental
```

```{toctree}
:maxdepth: 1
:caption: Extras
:hidden:

glossary
```
