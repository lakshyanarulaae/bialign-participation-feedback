"""Reproduce accepted results and the camera-ready near-threshold variance checks.

Run: python reproduce.py --output-dir ../results
The output directory must not exist. No datasets, trained models, or GPU are used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASELINE_ALPHAS = (0., .4, .6, .7, .9, 1.)
NEAR_ALPHAS = (.6001, .601, .605, .61, .62, .65)
REPS, N, M, BETA, LAM = 2000, 500, 500, 5., .35
HORIZONS = (1500, 5000, 15000)


def variance_jackknife(values):
    """Sample variance and its delete-one jackknife MCSE; no Gaussian assumption."""
    values = np.asarray(values, dtype=np.float64)
    r = len(values)
    centered = values - values.mean()
    ss = centered @ centered
    variance = ss / (r - 1)
    leave_one = (ss - r / (r - 1) * centered**2) / (r - 2)
    mcse = np.sqrt((r - 1) / r * np.sum((leave_one - leave_one.mean())**2))
    return float(variance), float(mcse), leave_one


def local_predictions(alpha, rounds):
    d = 1 - LAM + LAM * (1 - alpha) * BETA / 2
    innovation = LAM**2 * ((1 - alpha)**2 / (4 * N) + alpha**2 / (4 * M))
    if d >= 1:
        return d, None, None
    stationary = innovation / (1 - d*d)
    # Initial allocation is exactly parity, hence zero initial variance.
    finite = stationary * (-np.expm1(2 * rounds * np.log(d)))
    return d, float(stationary), float(finite)


def summarize(x, alpha, rounds, cohort):
    variance, mcse, _ = variance_jackknife(x)
    d, stationary, finite = local_predictions(alpha, rounds)
    deviations = np.abs(x - .5)
    return dict(alpha=alpha, rounds=rounds, cohort=cohort, replicates=REPS,
                mean=float(x.mean()), mean_abs_deviation=float(deviations.mean()),
                se_abs_deviation=float(deviations.std(ddof=1)/np.sqrt(REPS)),
                variance=variance, variance_mcse=mcse, local_d=d,
                stationary_prediction=stationary, finite_prediction=finite,
                relative_error=None if stationary is None else variance/stationary-1,
                finite_relative_error=None if finite is None else variance/finite-1)


def simulate(alpha, rng, checkpoints):
    """Round-major draws: endogenous vector, audit vector, then simultaneous update."""
    x = np.full(REPS, .5, dtype=np.float64)
    saved = {}
    states = {"0": rng.bit_generator.state}
    for t in range(1, max(checkpoints) + 1):
        p = 1 / (1 + np.exp(-BETA * (2*x - 1)))
        endogenous = rng.binomial(N, p) / N
        audit = rng.binomial(M, .5, size=REPS) / M
        x = (1-LAM)*x + LAM*((1-alpha)*endogenous + alpha*audit)
        if t in checkpoints:
            saved[t] = x.copy()
            states[str(t)] = rng.bit_generator.state
    return saved, states


def check_statistics():
    # Check the O(R) expression against literal delete-one variances.
    x = np.array([.01, .03, .2, .52, .8, .99])
    variance, _, leave = variance_jackknife(x)
    assert np.allclose(leave, [np.delete(x, i).var(ddof=1) for i in range(len(x))])
    assert np.isclose(variance, x.var(ddof=1))
    assert np.isclose(leave.mean(), variance)
    d, stationary, finite = local_predictions(1., 1500)
    assert np.isclose(d, 1-LAM) and np.isclose(finite, stationary)


def plot_results(output, baseline, near, samples):
    plt.rcParams.update({"font.size":10, "font.family":"DejaVu Sans", "pdf.fonttype":42,
                         "axes.spines.top":False, "axes.spines.right":False})
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8))
    for alpha, color in [(.4,"#B7483A"),(.6,"#8B62A6"),(.7,"#23826A")]:
        axes[0].hist(samples[f"baseline_{alpha:g}_1500"], bins=np.linspace(0,1,61),
                     histtype="step", density=True, label=f"alpha={alpha:g}", color=color)
    axes[0].set(xlabel="Endpoint policy share", ylabel="Density",
                title="A balanced mean can hide lock-in")
    axes[0].legend(frameon=False, fontsize=9)
    rows = sorted([r for r in baseline + near if r["rounds"] == 1500
                   and r["stationary_prediction"] is not None], key=lambda r:r["alpha"])
    axes[1].errorbar([r["alpha"]-.6 for r in rows], [r["variance"] for r in rows],
                     yerr=[1.96*r["variance_mcse"] for r in rows], fmt="o", color="#23826A",
                     ms=4, label="Observed (95% MC bars)")
    axes[1].plot([r["alpha"]-.6 for r in rows], [r["stationary_prediction"] for r in rows],
                 "x--", color="#B7483A", label="Local: stationary")
    axes[1].plot([r["alpha"]-.6 for r in rows], [r["finite_prediction"] for r in rows],
                 ":", color="#2963A4", label="Local: round 1,500")
    axes[1].set(xscale="log", yscale="log", xlabel=r"Distance above threshold, $\alpha - 0.6$",
                ylabel="Across-deployment variance", title="Linearization fails near the threshold")
    axes[1].legend(frameon=False, fontsize=9, loc="upper right")
    fig.tight_layout()
    fig.savefig(output/"participation_noise_camera_ready_v2.pdf")
    plt.close(fig)


def write_tex_tables(output, baseline, near):
    # Units 10^-4 keep the uncertainty columns readable without reducing the font.
    rows = sorted([r for r in baseline + near if r["rounds"] == 1500 and
                   r["stationary_prediction"] is not None], key=lambda r:r["alpha"])
    table = []
    for r in rows:
        table.append(f"{r['alpha']:g} & {r['variance']*1e4:.3f} & "
                     f"{r['variance_mcse']*1e4:.3f} & {r['finite_prediction']*1e4:.3f} & "
                     f"{r['stationary_prediction']*1e4:.3f} & {r['relative_error']*100:+.1f}\\%\\\\")
    (output/"variance_table.tex").write_text("\n".join(table)+"\n")
    (output/"variance_rows.tex").write_text("\\newcommand{\\variancerows}{%\n"+"\n".join(table)+"\n}\n")
    horizon = []
    for alpha in NEAR_ALPHAS:
        rows_a = [r for r in near if r["alpha"] == alpha]
        values = {r["rounds"]:r for r in rows_a}
        cells = [f"{values[t]['variance']*1e4:.3f} $\\pm$ {values[t]['variance_mcse']*1e4:.3f}"
                 for t in HORIZONS]
        horizon.append(f"{alpha:g} & "+" & ".join(cells)+"\\\\")
    (output/"horizon_table.tex").write_text("\n".join(horizon)+"\n")
    (output/"horizon_rows.tex").write_text("\\newcommand{\\horizonrows}{%\n"+"\n".join(horizon)+"\n}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    check_statistics()
    here = Path(__file__).resolve().parent
    # The unchanged accepted script recreates Figure 1 and verifies the critical case.
    accepted = subprocess.run([sys.executable, str(here/"accepted_simulation.py"),
                               "--output-dir", str(output/"accepted")],
                              check=True, capture_output=True, text=True)
    (output/"accepted_checks.txt").write_text(accepted.stdout)
    diagnostic = subprocess.run([sys.executable, str(here/"unequal_and_delay.py")],
                                check=True, capture_output=True, text=True)
    (output/"unequal_and_delay.txt").write_text(diagnostic.stdout)
    baseline, near, samples, states = [], [], {}, {}
    expected = json.loads((here/"accepted_simulation.json").read_text())["rows"]
    rng = np.random.Generator(np.random.PCG64(20260904))
    for alpha, old in zip(BASELINE_ALPHAS, expected):
        saved, state = simulate(alpha, rng, (1500,))
        row = summarize(saved[1500], alpha, 1500, "accepted")
        for key in ("mean", "mean_abs_deviation", "se_abs_deviation", "variance"):
            assert abs(row[key]-old[key]) < 1e-14, (alpha, key, row[key], old[key])
        baseline.append(row)
        samples[f"baseline_{alpha:g}_1500"] = saved[1500]
        states[f"baseline_{alpha:g}"] = state
    # One documented independent stream per NEW scenario; no change to accepted draws.
    children = np.random.SeedSequence(20261004).spawn(len(NEAR_ALPHAS))
    for alpha, child in zip(NEAR_ALPHAS, children):
        rng = np.random.Generator(np.random.PCG64(child))
        saved, state = simulate(alpha, rng, HORIZONS)
        states[f"near_{alpha:g}"] = dict(spawn_key=list(child.spawn_key), states=state)
        for rounds, x in saved.items():
            near.append(summarize(x, alpha, rounds, "camera_ready"))
            samples[f"near_{alpha:g}_{rounds}"] = x
        # The two horizon estimates are paired because they share deployments.
        _, _, early = variance_jackknife(saved[1500])
        _, _, late = variance_jackknife(saved[15000])
        difference = late-early
        states[f"near_{alpha:g}"]["horizon_contrast"] = dict(
            variance_difference=float(saved[15000].var(ddof=1)-saved[1500].var(ddof=1)),
            paired_mcse=float(np.sqrt((REPS-1)/REPS*np.sum((difference-difference.mean())**2))))
        print(f"completed alpha={alpha:g}", flush=True)
    plot_results(output, baseline, near, samples)
    write_tex_tables(output, baseline, near)
    np.savez_compressed(output/"endpoint_samples.npz", **samples)
    (output/"rng_states.json").write_text(json.dumps(states, indent=2)+"\n")
    record = dict(generator="numpy.random.Generator(PCG64)", baseline_seed=20260904,
                  baseline_alpha_order=list(BASELINE_ALPHAS), new_seed=20261004,
                  new_alpha_order=list(NEAR_ALPHAS), horizons=list(HORIZONS),
                  replicates=REPS, beta=BETA, lambda_=LAM, n=N, m=M,
                  draw_order="alpha; round; endogenous length-2000 vector; audit length-2000 vector; update",
                  variance_denominator=REPS-1, variance_mcse="delete-one jackknife across deployments",
                  baseline=baseline, near_threshold=near,
                  environment=dict(python=sys.version, numpy=np.__version__,
                                   matplotlib=matplotlib.__version__, platform=platform.platform(),
                                   machine=platform.machine()), elapsed_seconds=time.perf_counter()-started)
    (output/"simulation.json").write_text(json.dumps(record, indent=2)+"\n")
    hashes = {p.relative_to(output).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
              for p in output.rglob("*") if p.is_file()}
    (output/"checksums.json").write_text(json.dumps(hashes, indent=2)+"\n")
    print(f"PASS: accepted numbers reproduced; all near-threshold scenarios completed in {record['elapsed_seconds']:.1f}s.")


if __name__ == "__main__":
    main()
