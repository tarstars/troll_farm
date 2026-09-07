#!/usr/bin/env python3
"""Read-only arithmetic and optional source-pin audit for the 2026-09-07 review.

No network, bot execution, evaluation panels, seal access, or third-party packages.
The default reproduces arithmetic from explicitly transcribed report inputs.
--source-root additionally checks the COMPLETE original JSONL against its Git blob
and the sixteen final readings below. It never reads early_looks as experiments.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import unittest

SOURCE_PIN = "fb7801a740c8c16eca7e3e22cb2c008fd9e58b17"
READINGS_PATH = "local_claude_1/ladder-queue/readings.jsonl"
READINGS_BLOB = "2909dab7526e157f2cbb1f2d9ae04cc2c09c70f0"
CHAMPION_SHA = "0e92f8fa1e9097dd3df81989e222be8810f3cebdcd3efc950f84353f0bd1d57c"
# submission_id, final rating, rank; chronological JSONL order, not early polls.
READINGS = [
    (41206680, 11.71, 169), (41206957, 12.03, 167),
    (41207673, 14.65, 144), (41207963, 13.51, 159),
    (41208249, 17.59, 99), (41208579, 18.19, 85),
    (41209711, 18.84, 70), (41209967, 16.66, 114),
    (41210228, 16.64, 117), (41230202, 17.04, 110),
    (41234498, 17.98, 89), (41234663, 18.14, 86),
    (41236483, 14.59, 147), (41236823, 18.72, 72),
    (41239996, 14.07, 154), (41240269, 19.23, 60),
]
CHAMPION_IDS = {41208579, 41230202, 41234663, 41236823, 41240269}
CHAMPION = [score for sid, score, _ in READINGS if sid in CHAMPION_IDS]


def known_sigma_half_width(sd: float, n_per_arm: int) -> float:
    """Illustrative independent equal-size arm means, NOT a calibrated ladder CI."""
    if not math.isfinite(sd) or sd < 0 or n_per_arm < 1:
        raise ValueError("Need finite nonnegative SD and at least one reading per arm")
    return 1.96 * sd * math.sqrt(2 / n_per_arm)


def minimum_n(sd: float, half_width: float) -> int:
    if half_width <= 0 or not math.isfinite(half_width):
        raise ValueError("half_width must be finite and positive")
    known_sigma_half_width(sd, 1)
    return max(1, math.ceil(2 * (1.96 * sd / half_width) ** 2))


def parse_final_readings(text: str) -> list[dict]:
    result = []
    seen = set()
    for line_no, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        item = json.loads(line)
        for field in ("submission_id", "score", "rank", "read_at", "sha256",
                      "games_done", "games_in_package"):
            if field not in item:
                raise ValueError(f"Line {line_no}: missing {field}")
        sid = item["submission_id"]
        if sid in seen:
            raise ValueError(f"Duplicate final submission {sid}; do not pool polls")
        seen.add(sid)
        if not math.isfinite(float(item["score"])):
            raise ValueError(f"Line {line_no}: invalid rating")
        if item["games_done"] != item["games_in_package"]:
            raise ValueError(f"Line {line_no}: package count mismatch")
        if item["games_done"] < 160:
            raise ValueError(f"Line {line_no}: incomplete rollout")
        # Historical >160 records are flagged by audit_source, not silently dropped.
        result.append(item)
    return result


def audit_source(root: Path) -> dict:
    path = root / READINGS_PATH
    raw = path.read_bytes()
    digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if digest != READINGS_BLOB:
        raise ValueError(f"Wrong source blob {digest}; expected {READINGS_BLOB} at {SOURCE_PIN}")
    rows = parse_final_readings(raw.decode("utf-8"))
    got = [(r["submission_id"], r["score"], r["rank"]) for r in rows]
    if got != READINGS:
        raise ValueError("Final-reading transcription differs from the pinned source")
    identical = [r["score"] for r in rows if r["sha256"] == CHAMPION_SHA]
    if identical != CHAMPION:
        raise ValueError("Same-file champion group differs from the stated five readings")
    return {
        "status": "PASS", "blob": digest, "final_records": len(rows),
        "nonstandard_game_counts": [
            {"submission_id": r["submission_id"], "games": r["games_done"]}
            for r in rows if r["games_done"] != 160
        ],
        "scope": "Source identity/transcription only; raw games and actual maturity not independently rechecked",
    }


def calculations() -> dict:
    recent_sd = statistics.stdev(CHAMPION)
    old_sd = 1.501  # reported pooled within-family SD, instrument-audit.md
    # codex_1/sealed-holdout/README.md: LOCAL score-margin distributions only.
    arm_sd = 40.20345625425082
    paired_sd = 47.93079340191414
    sealed_n = 512
    resolution = []
    for n in (1, 4, 6, 21):
        resolution.append({
            "readings_per_arm": n, "total_rollout_games_at_160": 2 * n * 160,
            "recent_sd_normal_half_width": known_sigma_half_width(recent_sd, n),
            "old_sd_normal_half_width": known_sigma_half_width(old_sd, n),
        })
    return {
        "source_pin": SOURCE_PIN,
        "input_provenance": "Manually transcribed document data; no games rerun",
        "main_final_records": len(READINGS),
        "recent_identical_champion": {
            "values": CHAMPION, "n": len(CHAMPION),
            "mean": statistics.mean(CHAMPION), "sample_sd": recent_sd,
            "range": max(CHAMPION) - min(CHAMPION),
        },
        "rating_resolution_sensitivity_not_empirical_confidence": resolution,
        "normal_n_per_arm_for_rating_half_width": {
            "recent_sd_1_point": minimum_n(recent_sd, 1),
            "recent_sd_half_point": minimum_n(recent_sd, .5),
            "old_sd_1_point": minimum_n(old_sd, 1),
            "old_sd_half_point": minimum_n(old_sd, .5),
        },
        "sealed_bank": {
            "independent_map_blocks": sealed_n, "one_assigned_opponent_per_map": True,
            "two_arm_player0_games": 2 * sealed_n,
            "two_arm_both_seats_games_if_runner_extended": 4 * sealed_n,
            "local_margin_half_width_using_arm_sd": 1.96 * arm_sd * math.sqrt(2 / sealed_n),
            "local_margin_half_width_using_paired_sd": 1.96 * paired_sd / math.sqrt(sealed_n),
            "local_margin_approx_80pct_power_effect": (1.96 + .8416212335729143) * paired_sd / math.sqrt(sealed_n),
            "bounded_paired_match_point_normal_max_half_width": 1.96 / math.sqrt(sealed_n),
            "bounded_paired_match_point_hoeffding_95_half_width": math.sqrt(2 * math.log(40) / sealed_n),
            "warning": "Local margin SD is not real-agent match-point SD. These do not calibrate ladder rating.",
        },
        "descriptive_mechanisms": {
            "v440_own_fellings_size1_fraction": 1702 / 1931,
            "putibuzu_two_worker_fraction": 114 / 116,
            "tonigineer_two_worker_fraction": 121 / 122,
            "same_v368_reported_rating_difference": 25.21 - 21.06,
            "same_putibuzu_agent_rating_change": 26.99 - 24.92,
            "banana_size1_to4_wood_per_chop_factor_at_power2": (4 / 3) / (1 / 2),
            "native_vs_port_end_wood_points_ratio_unpaired": 334.16 / 99.95,
        },
        "proposed_offline_game_budget": 32 * 2 * 6 * 2,
        "proposed_real_instrument_AA_games": 5 * 2 * 2,
        "proposed_real_pilot_games": 12 * 2 * 2,
        "proposed_sealed_comparison_games": 512 * 2,
        "proposed_maximum_real_unranked_games": 20 + 48 + 1024,
    }


class Tests(unittest.TestCase):
    def test_values(self):
        self.assertEqual(len(READINGS), 16)
        self.assertEqual(len({x[0] for x in READINGS}), 16)
        self.assertAlmostEqual(statistics.mean(CHAMPION), 18.264)
        self.assertEqual(len(CHAMPION), 5)
    def test_sample_sd(self):
        m = statistics.mean(CHAMPION)
        manual = math.sqrt(sum((v-m)**2 for v in CHAMPION)/(len(CHAMPION)-1))
        self.assertAlmostEqual(statistics.stdev(CHAMPION), manual)
    def test_n_is_minimum(self):
        for sd in (statistics.stdev(CHAMPION), 1.501):
            for width in (1, .5):
                n = minimum_n(sd, width)
                self.assertLessEqual(known_sigma_half_width(sd, n), width)
                self.assertGreater(known_sigma_half_width(sd, n-1), width)
    def test_no_poll_pseudoreplication(self):
        row = dict(submission_id=1, score=22, rank=30, read_at="x", sha256="a",
                   games_done=160, games_in_package=160,
                   early_looks=[dict(score=99), dict(score=100)])
        self.assertEqual(len(parse_final_readings(json.dumps(row))), 1)
        with self.assertRaises(ValueError):
            parse_final_readings(json.dumps(row)+"\n"+json.dumps(row))
        row["games_done"] = row["games_in_package"] = 129
        with self.assertRaises(ValueError):
            parse_final_readings(json.dumps(row))
    def test_game_counts(self):
        r = calculations()
        self.assertEqual(r["sealed_bank"]["two_arm_player0_games"], 1024)
        self.assertEqual(r["proposed_maximum_real_unranked_games"], 1092)
    def test_invalid_arguments(self):
        with self.assertRaises(ValueError):
            known_sigma_half_width(1, 0)
        with self.assertRaises(ValueError):
            minimum_n(1, 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    result = calculations()
    try:
        result["source_verification"] = audit_source(args.source_root) if args.source_root else {
            "status": "NOT_RUN", "reason": "Pass --source-root pointing to the pinned checkout"}
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"SOURCE AUDIT FAILED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
