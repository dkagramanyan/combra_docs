# Citing combra

If combra contributes to published work, please cite the software, and the
papers behind the methods you used.

## The software

The citation metadata is `CITATION.cff` at the root of the
[combra repository](https://github.com/dkagramanyan/combra). GitHub's
*Cite this repository* button reads it and gives APA and BibTeX; the same
entry in BibTeX:

```bibtex
@software{combra,
  author  = {D.G.Kagramanyan},
  title   = {combra},
  version = {0.16.0},
  url     = {https://github.com/dkagramanyan/combra},
}
```

Cite the version the results were produced with. It is `combra.__version__`,
and every angle parquet records it in its {term}`run_meta` column.

## The methods

combra implements published algorithms, and a paper that relies on one of them
should cite it as well. These are the references given in the reference pages
and the user guide, grouped by the part of combra that uses them.

Pool detection and vertex angles ({py:mod}`combra.angles`, {py:mod}`combra.legacy`)
: N. Otsu, "A Threshold Selection Method from Gray-Level Histograms",
  *IEEE Transactions on Systems, Man, and Cybernetics* 9(1), 1979.
: D. H. Douglas and T. K. Peucker, "Algorithms for the Reduction of the Number
  of Points Required to Represent a Digitized Line or its Caricature",
  *Cartographica* 10(2), 112–122, 1973.

Contours ({py:mod}`combra.legacy`, {py:mod}`combra.ellipse`, {py:mod}`combra.graph`)
: J. Canny, "A Computational Approach to Edge Detection", *IEEE TPAMI* 8(6),
  679–698, 1986.
: S. Suzuki and K. Abe, "Topological Structural Analysis of Digitized Binary
  Images by Border Following", *CVGIP* 30(1), 32–46, 1985.

Experimental angle method ({py:mod}`combra.experimental`)
: F. Devernay, "A Non-Maxima Suppression Method for Edge Detection with
  Sub-Pixel Accuracy", INRIA Research Report 2724, 1995.
: T. Pavlidis and S. L. Horowitz, "Segmentation of Plane Curves", *IEEE
  Transactions on Computers* C-23(8), 860–870, 1974.

Beams ({py:mod}`combra.ellipse`)
: L. G. Khachiyan, "Rounding of polytopes in the real number model of
  computation", *Mathematics of Operations Research* 21(2), 307–320, 1996.

Fractal dimension ({py:mod}`combra.image`)
: K. Falconer, *Fractal Geometry: Mathematical Foundations and Applications*,
  3rd ed., Wiley, 2014.

Transport distances ({py:mod}`combra.metrics`)
: C. Villani, *Optimal Transport: Old and New*, Springer, 2009.
: R. Flamary et al., "POT: Python Optimal Transport", *JMLR* 22(78), 2021.
: J. Delon, J. Salomon and A. Sobolevski, "Fast Transport Optimization for
  Monge Costs on the Circle", *SIAM Journal on Applied Mathematics* 70(7), 2010.

Image-feature metrics ({py:mod}`combra.metrics`)
: M. Heusel, H. Ramsauer, T. Unterthiner, B. Nessler and S. Hochreiter, "GANs
  Trained by a Two Time-Scale Update Rule Converge to a Local Nash
  Equilibrium", NeurIPS 2017 (FID).
: D. C. Dowson and B. V. Landau, "The Fréchet distance between multivariate
  normal distributions", *Journal of Multivariate Analysis* 12(3), 1982.
: S. Jayasumana et al., "Rethinking FID: Towards a Better Evaluation Metric
  for Image Generation", CVPR 2024 (CMMD).
: M. Oquab et al., "DINOv2: Learning Robust Visual Features without
  Supervision", *TMLR* 2024 (FD-DINOv2).

Crack paths ({py:mod}`combra.graph`)
: J. Y. Yen, "Finding the k shortest loopless paths in a network",
  *Management Science* 17(11), 712–716, 1971.
