# Participation Feedback Creates Alignment Lock-In

**Who Keeps Giving Feedback? Participation Feedback Creates Alignment Lock-In**

Lakshya Narula · University of Minnesota-Twin Cities · narul014@umn.edu

Camera-ready revision for the BiAlign 2026 workshop, *Dynamic Alignment in Human–AI Coupled Systems*.

A deployed alignment policy can change who supplies its next feedback round. This paper studies how representative recruitment changes the stability of a two-group participation loop, separating the effective weight of representative feedback from update speed, audit bias, and sampling variability.

## Paper and complete workflow

- [Camera-ready paper](paper/bialign_camera_ready.pdf)
- [Executable simulation workflow and full conventions](code/README.md)
- [Machine-readable results](results/simulation.json)
- [Camera-ready revision notes](REVISION_NOTES.md)

The paper has nine main pages, 36 references, and a supporting appendix. The source uses the unchanged NeurIPS 2026 workshop style. All computations are CPU-only simulations; no external dataset, model, service, API credential, or GPU is required.

Using Python 3.13.5, from the repository root:

```sh
python -m pip install -r code/requirements.txt
cd code
python reproduce.py --output-dir ../results_reproduced
python verify.py --results-dir ../results_reproduced --reference-dir ../results
```

The workflow refuses to overwrite existing output directories. It reproduces the six original simulation conditions, runs all six added near-threshold conditions through three horizons, computes Monte Carlo standard errors, and generates the figures and table rows. The supplied endpoint arrays and random-generator states support direct inspection. `SHA256SUMS.json` records all release-file hashes; `results/checksums.json` records the result-file hashes.

The longer-horizon checks diagnose approximation error; they do not assert that a finite run proves stationarity. The deterministic threshold theorem and the original printed results are unchanged.
