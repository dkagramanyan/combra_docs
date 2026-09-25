"""
Polyamide fracture frames
=========================

Measure the fractal dimension and the size of the fracture contours in a series
of polyamide frames, group by group, and plot how their distributions change
along the series.

The frames are not bundled with combra, so the sessions below name a folder
(``poliamid_data/autumn/images``) rather than run, and this page has no output.

The frames
----------

:class:`combra.data.PolyamideFractureDataset` reads every ``*.JPG`` in one
folder whose file name is a plain integer (``1.JPG``, ``2.JPG``, …), and buckets
the frames into groups of ``group_size`` consecutive indices. A group, not a
frame, is the unit every measure is pooled over:

.. code-block:: pycon

   >>> from combra import data
   >>> ds = data.PolyamideFractureDataset(
   ...     'poliamid_data/autumn/images', group_size=250
   ... )
   >>> [(label, len(paths)) for label, paths in ds.image_groups[:2]]
   [('0001-0250', 250), ('0251-0500', 250)]

Groups follow the frame index, not the file order: ``'0001-0250'`` holds frames
1 to 250, whichever of them are on disk. Files with any other name are ignored.

Measuring the groups
--------------------

:meth:`~combra.data.PolyamideFractureDataset.generate` measures every frame in
parallel and writes one parquet row per group. Each frame is cut to its central
region — 400 px off the top and bottom, 1300 px off each side, so a frame must
be larger than 800 × 2600 px — thresholded with Otsu's method and contoured.
Every contour of at least ``N`` points contributes its box-counting fractal
dimension, its point count, its arc length and its area; the frame contributes
the fractal dimension of its whole binary image.

``N`` decides which contours count, so it is worth sweeping:

.. code-block:: pycon

   >>> for N in [50, 100, 500, 1000]:
   ...     ds.generate(f'poliamid_group250_n{N}.parquet', n_jobs=23, N=N)

The parquet holds one row per group:

.. list-table::
   :header-rows: 1

   * - column
     - content
   * - ``group_label``
     - the group, e.g. ``'0001-0250'``
   * - ``n_images``
     - frames in the group
   * - ``n_contours_total``, ``n_contours_fd``
     - contours found; contours at least ``N`` points long
   * - ``fd_list``
     - fractal dimension of every such contour
   * - ``fd_image_list``
     - fractal dimension of every whole frame
   * - ``len_nodes_list``, ``len_pixels_list``, ``area_list``
     - point count, arc length and area of every such contour

Fractal dimension by group
--------------------------

:func:`~combra.data.plot_polyamide_fractal` draws one panel per group: the
density of the contour fractal dimensions, with the two modes of a two-Gaussian
fit written in the panel title.

.. code-block:: pycon

   >>> fig = data.plot_polyamide_fractal(
   ...     'poliamid_group250_n500.parquet',
   ...     step=0.01,
   ...     save_path='poliamid_fractal_n500.png',
   ... )

A group with no contour of ``N`` points is titled ``(no data)``; one with too
few occupied bins for the six fit parameters is titled ``(too few bins to
fit)`` rather than given invented numbers.

Contour size by group
---------------------

:func:`~combra.data.plot_polyamide_contour` draws the density of one size
measure — ``'area'``, ``'len_nodes'`` or ``'len_pixels'`` — per group, with
several candidate distributions fitted and overlaid. Which family fits is what
the plot is read for:

.. code-block:: pycon

   >>> fig = data.plot_polyamide_contour(
   ...     'poliamid_group250_n1000.parquet',
   ...     metric='area',
   ...     dists=('binomial', 'poisson', 'gauss', 'exponential'),
   ...     step=1,
   ...     save_path='poliamid_area.png',
   ... )

``x_lim`` sets both the axis and the range the fits are evaluated on, so
widening it refits rather than only rescaling.
"""
