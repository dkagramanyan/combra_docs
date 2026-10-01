# Experimental methods

{py:mod}`combra.experimental` holds two candidates that the datasets and the
metrics do not use: P6, an angle extraction method, and the mass-share model,
a five-parameter variant of the angle fit. The API and output of this module
may change without a deprecation period.

For a worked run, see {doc}`/examples/experimental`.

## The sub-pixel method (P6)

P6 detects the
cobalt pools itself, locates their boundary to sub-pixel precision and reads
each angle from lines fitted to the boundary. From 0.15.0 to 0.20.2 it was the
method of `combra.angles`; the datasets and the metrics now use P0,
{py:func}`combra.angles.vertex_angles`. The two methods' densities are not
comparable, so a comparison always extracts both sides with the same method.

### Pipeline

{py:func}`~combra.experimental.vertex_angles` performs the measurement on one
grey image $I$ in five stages. Each stage is stated with its input, its output
and its own parameters.

**Stage 1 — detection mask.** $I \mapsto M$, a boolean image, true on the
cobalt ({py:func}`~combra.experimental.pool_mask`). With $\tilde I$ the image after a
$3 \times 3$ median filter (`median`),

$$
M_0 = \{\tilde I \le t_{\mathrm{Otsu}}\} \;\cup\;
      \{\tilde I \le G_b * \tilde I - c\},
$$

where $t_{\mathrm{Otsu}}$ is Otsu's global threshold, $G_b * \tilde I$ the
Gaussian-weighted local mean over an odd window $b \approx 0.1 W$ of the image
width $W$, and $c = 8$ grey levels. The global term finds the interiors of large
pools, the local one the faint pools under an illumination gradient. The
8-connected components of $M_0$ smaller than `min_area` (10 px) are removed and
the result is dilated once by the 4-connected cross, giving $M$.

**Stage 2 — sub-pixel boundary.** $M \mapsto \{C_r\}$, one closed curve per
region boundary, holes included. The pixel contours of $M$ are traced, a hole's
reversed so that every curve has the cobalt on the same side. With the blurred
mask $F = G_\sigma * M$ ($\sigma$ = `sigma`, 0.7 px), each contour point
$\mathbf{p}$ with unit normal $\mathbf{n}$ is moved to

$$
\mathbf{p}' = \mathbf{p} + t^\ast \mathbf{n},
\qquad
t^\ast = \arg\min_{|t| \le \rho} \{\, |t| : F(\mathbf{p} + t\mathbf{n}) = \tfrac12 \,\},
$$

the crossing of the $\tfrac12$ level nearest the point within the reach
$\rho$ (`reach`, 1.5 px), located by linear interpolation between samples
0.5 px apart. A point with no crossing stays where it is.

**Stage 3 — vertices.** $\{C_r\} \mapsto \{(V_1, \dots, V_m)_r\}$. A curve whose
bounding box comes within `border_eps` px of the frame is dropped: a pool
clipped by the frame has vertices that are artefacts of the crop.
Douglas–Peucker at tolerance `tol` (1.75 px) selects the vertices $V_k$ from the
points of $C_r$, and a region left with fewer than four is dropped. The vertices
lie on the curve, so each edge $V_k V_{k+1}$ owns the arc of $C_r$ between them.

**Stage 4 — angles.** $\{(V_k), C_r\} \mapsto \{\alpha_k\}$. Every edge $k$
gets a line fitted by total least squares to the points of its arc, leaving
out those within $\varepsilon$ (`fit_exclusion`, 0.5 px) of arclength from
either vertex, where the corner rounds the boundary (all points are used when
fewer than three remain). With $\mathbf{m}_k$ and $\Sigma_k$ the mean and
covariance of those points, the line is $\mathbf{m}_k + s\,\mathbf{d}_k$, where
$\mathbf{d}_k$ is the leading eigenvector of $\Sigma_k$, oriented along the chord
$V_{k+1} - V_k$. At vertex $k$, between edges $k-1$ and $k$,

$$
\mathbf{u}_1 = -\mathbf{d}_{k-1}, \quad \mathbf{u}_2 = \mathbf{d}_k,
\qquad
\theta_k = \arccos \langle \mathbf{u}_1, \mathbf{u}_2 \rangle,
\qquad
\alpha_k =
\begin{cases}
\theta_k, & \det(\mathbf{u}_1, \mathbf{u}_2) > 0 \;\text{(convex)}, \\
360^\circ - \theta_k, & \text{otherwise (reflex)},
\end{cases}
$$

so $\alpha_k \in [0^\circ, 360^\circ)$. The vertex is then moved to the
intersection of the two lines, when they are not near-parallel
($|\mathbf{d}_{k-1} \times \mathbf{d}_k| > 0.05$) and the intersection lies
within 3 px of $V_k$. The angle does not depend on where along the curve
Douglas–Peucker placed the vertex, only on which edges it separates.

**Stage 5 — stored polygon.** $(V_k) \mapsto (V_k')$. The polygon is inset by

$$
\delta = \min\!\left(\delta_0 + \frac{\kappa}{d},\; \delta_{\max}\right),
\qquad
d = \sqrt{4A/\pi},
$$

with $A$ the polygon's area, $\delta_0$ = `inset` (1 px), $\kappa$ =
`inset_per_diameter` (10 px²) and $\delta_{\max}$ = `inset_cap` (3.5 px). Each
vertex moves along its corner bisector by the offset that shifts both adjacent
edges inward by exactly $\delta$ (along the outgoing edge's normal at a very
sharp corner). This undoes the dilation of stage 1 and the mask's outward
offset, which is larger for small pools. The angles are those of stage 4 and do
not depend on the inset.

The output is the concatenation of the $\alpha_k$ over all kept regions and
the list of the stored polygons, one row per angle.
{py:func}`~combra.experimental.pool_regions` returns the same result with the
mask of stage 1 and the curve of stage 2 attached to every region.

```pycon
>>> from combra import data, experimental
>>> img = data.load_microstructure().images[0]
>>> arr, polygons = experimental.vertex_angles(img, border_eps=5, tol=1.75)
>>> arr.min(), arr.max()
```

### Choosing `tol`

The tolerance decides which bends of the boundary become vertices, so it is
**part of a result's identity**: {py:func}`~combra.experimental.output_directory`
encodes it in the output folder name (`..._tol1.75`) so runs made at different
settings cannot be silently compared. The default was chosen on the synthetic
set of {py:mod}`combra.synth`, where the truth is exact: at 1.75 px
the method recovers about 37% of the true corners with an RMS edge error of
0.67 px and the polygon overlaps the true region with an IoU of 0.81 averaged
over pools of 4–40 px. Below 8 px every corner reads too close to 180°, because
the blur rounds it over the whole edge of the pool; no setting of the stage
removes that, so small pools carry a known bias toward 180° rather than a
tunable one.

### Images of different resolution: `scale`

`tol`, the median filter and the smallest pool kept (`min_area`) are lengths in
pixels, tuned at 512 px of the full 1536 px micrograph field, a third of the
native resolution. Applied unchanged to another resolution they describe a
different physical size: on native 1536 px frames the default 1.75 px cuts the
boundary into about 70% more vertices, most of them nearly straight (160–200°),
and moves the convex mode by about 4°. Pass `scale`, the image pixels per native
micrograph pixel, and the three settings follow it
({py:func}`~combra.experimental.settings_for_scale`); the settings the benchmark
validated at 256, 512 and 1536 px of the 1536 px field are reproduced exactly:

```python
experimental.vertex_angles(img, scale=256 / 1536)   # the full field resized to 256 px
experimental.vertex_angles(img, scale=256 / 1024)   # a native 1024 px crop resized to 256 px
```

The scale is a property of how the images were made, not of their size, so it
cannot be read off the image: a 1024 px crop at native resolution and the full
field resized to 1024 px need different settings. Generated images take the
scale of the training images. With `scale` the output folder is named
`..._scale{scale:.4g}` instead of `..._tol{tol}`. Even with matched settings a
coarser image resolves fewer corners, so a generated set is best compared with
a real set of the same scale.

### How it compares

On the synthetic set of {doc}`synth`, P6 recovers about 37% of the true corners
at an RMS edge error of 0.67 px, against 12% and 1.26 px for P0. It also finds
the faint pools that Otsu's threshold alone does not see.
{py:func}`~combra.experimental.extract_polygons` wraps P6 in the form the
benchmark scores, and {py:func}`combra.angles.extract_polygons` does the same
for P0.

## The mass-share model

{py:func}`~combra.experimental.fit_bimodal_gaussian` fits the angle density
with five parameters in place of the six of
{py:func}`combra.fitting.fit_bimodal_gaussian`: the two amplitudes are replaced
by one share of the mass,

$$
p(x; \boldsymbol{\theta}) =
T \left[ \frac{\pi}{Z_1}\, \varphi(x; \mu_1, \sigma_1)
      + \frac{1 - \pi}{Z_2}\, \varphi(x; \mu_2, \sigma_2) \right]
\mathbf{1}_{D}(x),
$$

with $\boldsymbol{\theta} = (\mu_1, \mu_2, \sigma_1, \sigma_2, \pi)$, and $Z_i$
and $D = [0^\circ, 360^\circ]$ as in {doc}`angles`. $\pi$ is the
share of the mass in mode 1 and $1 - \pi$ that in mode 2. The total $T$ is not
fitted: it is set to the mass of the histogram, $T = h \sum_k y_k$ for bin
width $h$. The fit is the same bounded least squares, with
$\pi \in [0, 1]$, started from $\pi^{(0)} = m_1 / (m_1 + m_2)$, the masses on
either side of $180^\circ$. It is the amplitude model with $a_1 = T\pi$ and
$a_2 = T(1 - \pi)$, that is with $a_1 + a_2$ held at the mass of the data.

The result is a `BimodalGaussianFit(curve, mus, sigmas, shares, total)`;
{py:func}`~combra.experimental.truncated_bimodal_gaussian` evaluates the model.
From 0.13.0 to 0.21.0 this was the fit of `combra.fitting`, and the metrics
reported the relative error of $\pi$ under the key `pi`; they now report
`amp1` and `amp2`. {py:func}`combra.metrics.degenerate_fit_reason` screens a
share fit as it screens an amplitude fit.
