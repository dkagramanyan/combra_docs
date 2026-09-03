# User guide

combra answers one question: *does a generated WC-Co microstructure have the same
grain geometry as a real one?* It answers it by reducing an image to a small
number of distributions that can be compared numerically, rather than by
comparing pixels.

## The pipeline

```
SEM image
   │  binarize, denoise                          combra.image
   ▼
binary image
   │  Canny + Suzuki, Douglas–Peucker            combra.contours
   ▼
polygon contours
   ├─ angle at every vertex                      combra.angles
   │     ▼
   │  angle density  ── bimodal-Gaussian fit ──▶ combra.fitting
   │
   └─ minimum-volume enclosing ellipse           combra.ellipse
         ▼
      beam lengths ── distribution fit ────────▶ combra.fitting
                                                        │
   reference vs. generated ─────────────────────────────┘
                     ▼
                  metrics                        combra.metrics
```

Each stage is described below, with links into the reference.

## Stages

**Preprocessing.** {doc}`combra.image <../api/image>` reduces an SEM image to a
binary one. The standard sequence is a median filter, Otsu thresholding, and the
addition of the threshold's morphological gradient, which reinstates the grain
boundaries that thresholding merges:

$$
\mathrm{preproc} = 1 - \mathrm{Otsu}(\mathrm{median}(I))
                 + \mathrm{grad}(\mathrm{Otsu}(\mathrm{median}(I)))
$$

**Contours.** {doc}`combra.contours <../api/contours>` extracts closed polygons
with Canny edge detection and Suzuki contour following, then simplifies each with
the Douglas–Peucker algorithm. Simplification is not cosmetic: it sets how many
vertices survive, and therefore how many angles the next stage measures.

**Descriptors.** Two independent reductions of the same contours:

- {doc}`angles` — the interior angle at every vertex, pooled into an
  {term}`angle density`. This is combra's primary descriptor.
- {doc}`beams` — the {term}`MVEE` of every contour, giving each grain a size and
  an orientation, pooled into a beam-length distribution.

**Fitting.** {doc}`combra.fitting <../api/fitting>` fits parametric models to
those distributions. WC-Co angle densities are bimodal, so the
bimodal-Gaussian fit carries most of the interpretive weight: its two means
and widths and the mixing coefficient summarize a microstructure in five
numbers.

**Comparison.** {doc}`metrics` scores a generated distribution against a
reference one — Wasserstein distances on the densities, relative errors on the
fitted parameters, and Fréchet distances on deep image features.

## Other tooling

{doc}`combra.graph <../api/graph>` is a separate analysis: it converts a
binarized crack image into a directed graph whose edges are classified by the
phase they cross (Co, WC-Co, WC, WC-WC), then searches for minimum-energy
propagation paths.

{doc}`combra.io <../api/io>` owns the on-disk formats — the angle and beam
parquet schemas, HDF5 image containers, and the {term}`run_meta` provenance
struct written on every row.

```{toctree}
:maxdepth: 1
:hidden:

angles
angle_fit
beams
metrics
glossary
```
