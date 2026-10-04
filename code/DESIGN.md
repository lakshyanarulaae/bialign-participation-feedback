# Camera-ready extension specified before running

Date: 4 October 2026. The accepted analyses use beta=5, lambda=0.35, n=m=500, 2,000 independent deployments, initial service share 0.5, and 1,500 rounds. Reproduce the six accepted scenarios and their original random stream exactly before adding scenarios.

New audit weights: 0.6001, 0.601, 0.605, 0.61, 0.62, 0.65. These test distances from the deterministic threshold spanning 0.0001 to 0.05. All other settings stay fixed. Compare endpoint sample variance at round 1,500 with both the local stationary prediction and the local finite-horizon prediction, which accounts for the zero initial variance. Report a Monte Carlo standard error for sample variance using the delete-one jackknife across independent deployments; this avoids a Gaussian endpoint-distribution assumption.

Continue these same new trajectories to rounds 5,000 and 15,000. Report all checkpoints, whether they improve or weaken agreement. Differences across horizons help diagnose transients but do not prove stationarity. Preserve pairing for uncertainty on horizon contrasts. No tuning of model parameters, sample sizes, or reported weights after observing results.

The accepted stream is Generator(PCG64(20260904)) with audit weights [0, .4, .6, .7, .9, 1] in order. New scenarios use Generator(PCG64(child)), where children are SeedSequence(20261004).spawn(6), paired in the listed new-weight order. Each round draws the complete endogenous vector first, then the complete audit vector, then updates all 2,000 states simultaneously. Save initial and checkpoint generator states and endpoint samples. Simulation uncertainty is conditional on these model settings.
