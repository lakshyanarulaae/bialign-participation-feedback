# BiAlign camera-ready simulation workflow

Paper: **Who Keeps Giving Feedback? Participation Feedback Creates Alignment Lock-In**

Author: Lakshya Narula, University of Minnesota-Twin Cities.

This package reproduces the accepted simulations and the additional near-threshold checks requested during review. It includes all source code, reference endpoint arrays, random-generator states, numerical summaries, figures, and manuscript source. It requires no external data, model weights, API keys, or GPU.

## Direct execution

From this `code` directory, use Python 3.13.5 and the pinned dependencies:

```sh
python -m pip install -r requirements.txt
python reproduce.py --output-dir ../results_reproduced
python verify.py --results-dir ../results_reproduced --reference-dir ../results
```

The output directory must not already exist. The workflow refuses to overwrite it. A complete run took about 27 seconds on the recorded Apple Silicon machine; other machines may take longer. `simulation.json` records the actual Python, NumPy, Matplotlib, platform, and elapsed time for each execution.

The verifier checks every reported numerical summary, all endpoint arrays, initial/checkpoint random-generator states, and generated table rows. PDF creation dates, rendering-library differences, and elapsed times can change without changing the scientific results. Use the pinned Python/NumPy environment for exact random-stream replay; a different NumPy version is not an exact-reproduction claim.

## Output-to-paper mapping

| Paper item | Source/output |
| --- | --- |
| Figure 1: deterministic trajectories and attractors | `accepted_simulation.py`; `accepted/participation_phase.pdf` |
| Table 1: original finite-feedback endpoints | `simulation.json`, `baseline` records; replay assertions compare all six conditions with `accepted_simulation.json` |
| Figure 2: lock-in distributions and variance checks | `participation_noise_camera_ready_v2.pdf`; `endpoint_samples.npz` |
| Table 2: mechanism/repair summary | Conceptual summary of the stated equations, not a separate dataset |
| Table 3: near-threshold variance, MCSE, and predictions | `variance_table.tex`, `variance_rows.tex`; baseline and near-threshold records at round 1,500 |
| Table 4: longer-horizon checks | `horizon_table.tex`, `horizon_rows.tex`; near-threshold records at rounds 1,500, 5,000, and 15,000 |
| Unequal-population and delayed-feedback numerical checks | `unequal_and_delay.py`; `unequal_and_delay.txt` |
| Critical convergence checks | Executable assertions in `accepted_simulation.py`; successful completion recorded in `accepted_checks.txt` |

The budget calculations and analytical proofs are algebraic, not additional trained-model experiments. There are no excluded simulation conditions or hidden datasets.

## Estimands and Monte Carlo uncertainty

Every stochastic condition uses beta=5, adjustment rate lambda=0.35, endogenous and audit sample sizes n=m=500, initial service share 0.5, and R=2,000 independent deployments. Sample variance at a declared horizon uses denominator R-1. The target is the variance of deployment endpoints under this model, not uncertainty in a fitted human-response parameter.

`variance_jackknife` computes the delete-one jackknife Monte Carlo standard error (MCSE) of the sample variance. It is checked against literal deletion on a small test array. This MCSE estimates the uncertainty caused by a finite number of independent simulation repetitions; it is not the standard deviation of service shares. Figure 2 displays approximate 95% Monte Carlo bars, plus/minus 1.96 MCSE. Table 4 displays plus/minus **one** MCSE. MCSEs for mean absolute deviation use its sample standard deviation divided by sqrt(R).

The stationary linear prediction is evaluated only when d<1. The finite-horizon linear prediction accounts for the zero initial variance. The nonlinear process remains bounded even where the stationary linear prediction is undefined. Longer-horizon agreement is a diagnostic, not proof of stationarity. Paired horizon-contrast MCSEs use the same deleted deployment at each checkpoint and are stored in `rng_states.json`.

## Exact random-number conventions

The generator is NumPy `Generator` with bit generator `PCG64`.

Original scenarios run in order `[0, 0.4, 0.6, 0.7, 0.9, 1]`, sharing `Generator(PCG64(20260904))` without reseeding between conditions. Each condition has 1,500 rounds. In every round, draw the full length-2,000 endogenous binomial vector first, the full length-2,000 audit binomial vector second, and then update all states simultaneously. Deployment indices are in ascending array order. Both vectors are drawn even when their effective weight is zero. This convention preserves the accepted results exactly.

New scenarios run in order `[0.6001, 0.601, 0.605, 0.61, 0.62, 0.65]`. They use the six children of `SeedSequence(20261004).spawn(6)`, each supplied to a separate `PCG64`. Draw order is otherwise unchanged. Each scenario continues the same trajectories to round 15,000, saving endpoints and generator states at rounds 1,500, 5,000, and 15,000. Those horizons are paired, not independent runs. `DESIGN.md` records the extension specified before execution.

## Manuscript build

The supplied `paper` directory uses the unchanged NeurIPS 2026 workshop style. It requires a standard LaTeX installation only if rebuilding the PDF:

```sh
cd ../paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

This uses the supplied `results` directory. To build against a fresh reproduction, replace the `../results/` figure and table paths in a **copy** of the manuscript source with `../results_reproduced/`. The plotting and table generation occur in the same executable workflow.

## Methodological reference

Morris, T. P., White, I. R., and Crowther, M. J. (2019). Using simulation studies to evaluate statistical methods. *Statistics in Medicine*, 38(11), 2074–2102. https://doi.org/10.1002/sim.8086

The paper motivates reporting simulation uncertainty and executable code. The jackknife estimator used here is explicitly defined in Appendix C and in this package rather than attributed to that paper as a specific formula.
