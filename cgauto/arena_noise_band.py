#!/usr/bin/env python3
"""Estimate the Arena's within-source score noise from repeated mature runs.

The question this answers: when the same byte-identical source is submitted more
than once and each deployment is allowed to mature, how much does its settled
score move?  That number is the floor on any A-vs-B comparison we can make on
the ladder, and until 2026-08-12 it had never been computed -- the +-0.5-1 band
in docs/STATE.md section 3 was an estimate, not a measurement.

Method: pooled within-source standard deviation over every source family in the
submission registry with two or more mature observations of at least 100
finished games.  Pooling is the point -- one family's spread is a sample of two
and tells you almost nothing, which is exactly the error the 2026-08-12 read of
a single 24.76/22.46 pair invited.

Reads the derived registry, which is rebuilt by:
    python3 cgauto/submission_history.py build
"""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_REGISTRY = os.path.join(
    REPO_ROOT, "data", "analysis", "arena-submission-history.json"
)

MATURE = frozenset({"later_confirmed", "mature", "terminal"})

# Two-sided chi-square quantiles, df -> (0.025, 0.975).  Only the degrees of
# freedom this dataset can plausibly reach are tabulated; anything else falls
# back to reporting no interval rather than interpolating silently.
CHI2 = {
    1: (0.001, 5.024), 2: (0.051, 7.378), 3: (0.216, 9.348),
    4: (0.484, 11.143), 5: (0.831, 12.833), 6: (1.237, 14.449),
    7: (1.690, 16.013), 8: (2.180, 17.535), 9: (2.700, 19.023),
    10: (3.247, 20.483), 11: (3.816, 21.920), 12: (4.404, 23.337),
    13: (5.009, 24.736), 14: (5.629, 26.119), 15: (6.262, 27.488),
    16: (6.908, 28.845), 17: (7.564, 30.191), 18: (8.231, 31.526),
    19: (8.907, 32.852), 20: (9.591, 34.170),
}


def families(registry: dict, min_games: int) -> dict[str, list[dict]]:
    """Group mature observations by source family, ONE observation per submission.

    The unit of this estimate is a *deployment*, not an observation row.  The
    registry legitimately holds several checkpoints of a single run -- e.g.
    submission 41012256 at 122 and at 160 games -- and the first version of this
    function counted each as an independent sample.  They are not: they are the
    same deployment measured twice, so their difference is within-run maturation
    drift, which is a different quantity from the re-submission noise this tool
    exists to estimate.  Including them inflated n from 10 to 13, inflated the
    degrees of freedom, and mixed a maturation component into the variance.

    Keeping the most mature observation per submission is the conservative
    choice: it is the reading closest to a settled score, and it is the one the
    registry's own ranking treats as the run's result.
    """
    source_of = {s["submission_id"]: s["source_id"] for s in registry["submissions"]}
    best_per_submission: dict[int, dict] = {}
    for obs in registry["observations"]:
        if obs.get("evidence_maturity") not in MATURE:
            continue
        if (obs.get("games_finished") or 0) < min_games:
            continue
        if source_of.get(obs["submission_id"]) is None:
            continue
        sid = obs["submission_id"]
        seen = best_per_submission.get(sid)
        if seen is None or (obs.get("games_finished") or 0) > (seen.get("games_finished") or 0):
            best_per_submission[sid] = obs

    grouped: dict[str, list[dict]] = {}
    for sid, obs in best_per_submission.items():
        grouped.setdefault(source_of[sid], []).append(obs)
    return {k: v for k, v in grouped.items() if len(v) >= 2}


def pooled_sd(grouped: dict[str, list[dict]]) -> tuple[float, int, int]:
    """Pooled within-source SD, its observation count, and its d.o.f."""
    squares: list[float] = []
    n_obs = 0
    for observations in grouped.values():
        scores = [o["score"] for o in observations]
        mean = statistics.mean(scores)
        squares += [(s - mean) ** 2 for s in scores]
        n_obs += len(scores)
    dof = n_obs - len(grouped)
    if dof <= 0:
        raise ValueError("not enough repeated observations to estimate a variance")
    return math.sqrt(sum(squares) / dof), n_obs, dof


def sd_interval(sd: float, dof: int) -> tuple[float, float] | None:
    bounds = CHI2.get(dof)
    if bounds is None:
        return None
    lower_q, upper_q = bounds
    return sd * math.sqrt(dof / upper_q), sd * math.sqrt(dof / lower_q)


def runs_needed(sd: float, target_se: float) -> int:
    """Runs per arm so that the SE of an A-minus-B difference hits target_se."""
    return math.ceil(2 * (sd / target_se) ** 2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default=DEFAULT_REGISTRY)
    parser.add_argument("--min-games", type=int, default=100)
    parser.add_argument("--hours-per-run", type=float, default=2.0)
    args = parser.parse_args()

    registry = json.load(open(args.registry))
    grouped = families(registry, args.min_games)
    if not grouped:
        raise SystemExit("no source family has two mature observations")

    print(f"{'source family':<42}{'n':>3}  {'settled scores':<34}{'range':>7}")
    print("-" * 88)
    for source_id, observations in sorted(grouped.items()):
        scores = sorted(o["score"] for o in observations)
        spread = scores[-1] - scores[0]
        shown = str([round(s, 2) for s in scores])
        print(f"{source_id:<42}{len(scores):>3}  {shown:<34}{spread:>7.2f}")

    sd, n_obs, dof = pooled_sd(grouped)
    print("-" * 88)
    print(
        f"{len(grouped)} families, {n_obs} mature observations, {dof} d.o.f."
    )
    print(f"POOLED WITHIN-SOURCE SD = {sd:.3f} score points")
    interval = sd_interval(sd, dof)
    if interval:
        print(f"95% CI for the SD        = [{interval[0]:.3f}, {interval[1]:.3f}]")
    print(f"SD of an A-minus-B difference at n=1 each = {sd * math.sqrt(2):.3f}")

    print("\nruns per arm to resolve a difference:")
    for target in (1.0, 0.5, 0.3):
        n = runs_needed(sd, target)
        hours = n * 2 * args.hours_per_run
        print(
            f"  SE = {target:>3} -> n = {n:>2} per arm "
            f"({n * 2} runs, ~{hours:.0f}h sequential ladder time)"
        )


if __name__ == "__main__":
    main()
