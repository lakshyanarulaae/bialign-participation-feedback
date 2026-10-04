# Camera-ready revision: 4 October 2026

The accepted analysis is preserved. This revision addresses the review's requests for near-threshold validation, uncertainty in simulation summaries, and a directly executable public workflow.

## W1: near-threshold approximation and simulation uncertainty

- Added audit weights 0.6001, 0.601, 0.605, 0.61, 0.62, and 0.65, all above the deterministic threshold 0.6. Other original settings remain beta=5, lambda=0.35, n=m=500, 2,000 independent deployments, and initial allocation 0.5.
- At round 1,500, compare the observed endpoint variance with both the stationary linear prediction and its finite-horizon version, which accounts for zero initial variance.
- Report a delete-one jackknife Monte Carlo standard error for each estimated variance. Figure 2 uses approximate 95% Monte Carlo bars. Appendix C gives the explicit estimator and expanded Table 3.
- Continue the same trajectories to rounds 5,000 and 15,000. Table 4 reports all six added conditions at every checkpoint with one MCSE. Paired horizon contrasts preserve the same deployment index.
- At alpha=0.6001, observed variance at round 1,500 is 0.0015732, versus stationary prediction 0.1820220 and finite-horizon prediction 0.0420257. At round 15,000 observed variance is 0.0016292. The near-critical gap is not explained solely by the short original horizon.
- At alpha=0.65, observed variance is only 3.1% below the local prediction, a discrepancy comparable to one MCSE. This identifies the tested accuracy boundary without treating deterministic stability as a sufficient condition for accurate linear-noise predictions.
- The main text explains the omitted restoring cubic term and the state-dependent endogenous innovation variance. It contains the design, headline checks, MCSE interpretation, and conclusions; reading the appendix is not required to understand the finding.
- Added the verified Morris, White, and Crowther (2019) reference, DOI 10.1002/sim.8086. Its full methodological text was checked for the claims about predictions beyond initial mechanisms, simulation uncertainty, random-number conventions, and executable code.

## W2: exact conventions and public reproduction

- Specify NumPy Generator/PCG64, seeds, scenario order, round order, vector draw order, simultaneous updates, and draws even when a stream's policy weight is zero.
- Preserve the original shared stream and all six accepted numerical conditions. The workflow checks their summaries against the saved accepted results to tighter than printed precision.
- Separate new scenarios using the documented SeedSequence child streams. Save initial/checkpoint generator states and endpoint arrays.
- Provide one execution entry point, pinned dependencies, numerical assertions, the original simulation scripts, an independent reproduction verifier, machine-readable summaries, figures, table rows, and source manuscript.
- Public repository: https://github.com/lakshyanarulaae/bialign-participation-feedback

## Presentation and scope

Add the author's name, affiliation, and contact details. Keep the main paper within nine pages, use the unchanged workshop style in final mode, place table captions above tables and figure captions below figures, and retain the workshop's checklist-free version. The abstract and core theorems are unchanged. The reference count is 36. The supporting appendix is organized around calibration, boundary cases, simulation precision, and budget derivations rather than an unstructured result dump.
