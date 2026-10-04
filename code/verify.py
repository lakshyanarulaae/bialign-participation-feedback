"""Verify numerical reproduction, not PDF metadata or elapsed runtime."""
import argparse
import json
from pathlib import Path

import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--reference-dir", type=Path, required=True)
    args = parser.parse_args()
    actual = json.loads((args.results_dir / "simulation.json").read_text())
    reference = json.loads((args.reference_dir / "simulation.json").read_text())
    for cohort in ("baseline", "near_threshold"):
        assert len(actual[cohort]) == len(reference[cohort])
        for got, expected in zip(actual[cohort], reference[cohort]):
            assert got.keys() == expected.keys()
            for key, value in expected.items():
                if isinstance(value, float):
                    assert np.isclose(got[key], value, rtol=1e-12, atol=1e-14), (cohort, key)
                else:
                    assert got[key] == value, (cohort, key)
    with np.load(args.results_dir / "endpoint_samples.npz") as actual_arrays, \
         np.load(args.reference_dir / "endpoint_samples.npz") as expected_arrays:
        assert set(actual_arrays.files) == set(expected_arrays.files)
        for name in expected_arrays.files:
            assert np.array_equal(actual_arrays[name], expected_arrays[name]), name
    assert json.loads((args.results_dir / "rng_states.json").read_text()) == \
        json.loads((args.reference_dir / "rng_states.json").read_text())
    for name in ("variance_table.tex", "horizon_table.tex", "variance_rows.tex", "horizon_rows.tex"):
        assert (args.results_dir / name).read_text() == (args.reference_dir / name).read_text(), name
    print("PASS: all accepted/new numerical summaries, endpoint arrays, random states, and table rows match.")


if __name__ == "__main__":
    main()
