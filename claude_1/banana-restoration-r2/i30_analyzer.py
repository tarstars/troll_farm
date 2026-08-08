#!/usr/bin/env python3
"""I-30 paired analyzer: schedule / opponent-production exposure.

Authoritative specification:
  chatgpt_1/schedule-opponent-production-invariant-spec-2026-08-08.md
  (branch agent/chatgpt_1, artifact_commit cad16c4d), sections 3, 4, 6, 8,
  9 and 11.

Frozen per-pair accounting (spec sec. 6):

    D_DIRECT   = dDEP_OURS
    D_SCHEDULE = dDEP_OPP + dDEP_NATURAL
    D_UNKNOWN  = dDEP_UNKNOWN
    D_TRAIN    = dTRAIN_SPEND
    D_OPP      = opponent_terminal_score(candidate) - ...(parent)

    SCHEDULE_WINDFALL = D_SCHEDULE - D_TRAIN
    RESIDUAL = D_OPP - (D_DIRECT + D_SCHEDULE + D_UNKNOWN - D_TRAIN)

Raw-zero instrument requirements: D_UNKNOWN == 0 and RESIDUAL == 0 (and every
per-run residual == 0). Integers only, no tolerance. Failing either is an
instrument failure -> GATE_UNREADY, never a candidate PASS and never a
report-only warning.

No numerical value threshold is chosen here. A bound object must be supplied,
hash-pinned, and marked owner-frozen; anything else is GATE_UNREADY with the
diagnostic sub-status MEASURED_UNTHRESHOLDED (spec sec. 8 / 11).

Scope: measurement only -- no bot, candidate, parent, gate, host game,
submission or Arena state is read or written.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i30_ledger as ledger  # noqa: E402
from i30_ledger import SOURCE_CLASSES, sha256_text  # noqa: E402

# spec sec. 8 status model
NOT_APPLICABLE = "NOT_APPLICABLE"
UNPROVEN = "UNPROVEN"
GATE_UNREADY = "GATE_UNREADY"
PASS = "PASS"
FAIL = "FAIL"
MEASURED_UNTHRESHOLDED = "MEASURED_UNTHRESHOLDED"

# spec sec. 3: every field a pair must share exactly
SHARED_IDENTITY_FIELDS = (
    "map_sha256", "seat", "opponent_source_sha256", "opponent_binary_sha256",
    "opponent_config_sha256", "engine_sha256", "initial_state_sha256",
    "rng_seed", "turn_cap", "termination_rule", "toolchain_sha256",
    "harness_sha256", "analyzer_config_sha256", "detector_config_sha256",
)
# spec sec. 3: the only allowed difference (and, in a declared self-pair,
# these must be equal too)
PAIR_VARIABLE_FIELDS = (
    "bot_source_sha256", "bot_binary_sha256", "command_stream_sha256",
)

OPERATORS = {
    "<=": lambda a, b: a <= b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    ">": lambda a, b: a > b,
    "==": lambda a, b: a == b,
}

# metric name -> key in the per-pair result
SUPPORTED_METRICS = {
    "mean_schedule_windfall": "schedule_windfall",
    "mean_d_opp": "d_opp",
    "mean_d_direct": "d_direct",
    "mean_d_schedule": "d_schedule",
}


class Bound:
    """Hash-pinned owner-frozen bound object (spec sec. 11).

    The spec deliberately does not choose a threshold, so this class only
    validates and evaluates whatever object it is handed. `provenance` must be
    the literal string "owner_frozen" before any PASS can be produced; every
    other value (including the fixtures' "test_fixture") is measured and
    reported but maps the gate to GATE_UNREADY.
    """

    REQUIRED_FIELDS = ("schema_version", "population", "metric", "operator",
                       "threshold", "owner_decision_path",
                       "owner_decision_blob")

    def __init__(self, spec, pinned_sha256=None):
        self.spec = dict(spec)
        self.canonical = json.dumps(self.spec, sort_keys=True,
                                    separators=(",", ":"))
        self.sha256 = sha256_text(self.canonical)
        self.pinned_sha256 = pinned_sha256
        self.provenance = self.spec.get("provenance", "unspecified")
        self.owner_frozen = (self.provenance == "owner_frozen")
        self.population = self.spec.get("population")
        self.metric = self.spec.get("metric")
        self.operator = self.spec.get("operator")
        self.threshold = self.spec.get("threshold")

        self.invalid_reasons = []
        if [f for f in self.REQUIRED_FIELDS if f not in self.spec]:
            self.invalid_reasons.append("bound_schema_incomplete")
        if pinned_sha256 is not None and pinned_sha256 != self.sha256:
            self.invalid_reasons.append("bound_hash_mismatch")
        if self.metric not in SUPPORTED_METRICS:
            self.invalid_reasons.append("bound_metric_unsupported")
        if self.operator not in OPERATORS:
            self.invalid_reasons.append("bound_operator_unsupported")

    @property
    def valid(self):
        return not self.invalid_reasons

    def measured_value(self, result):
        return result[SUPPORTED_METRICS[self.metric]]

    def satisfied(self, result):
        return OPERATORS[self.operator](self.measured_value(result),
                                        self.threshold)

    def to_json(self):
        return {"bound_sha256": self.sha256,
                "bound_pinned_sha256": self.pinned_sha256,
                "bound_provenance": self.provenance,
                "bound_owner_frozen": self.owner_frozen,
                "bound_valid": self.valid,
                "bound_invalid_reasons": list(self.invalid_reasons),
                "bound_spec": dict(self.spec)}


def compute_schedule_windfall(d_schedule, d_train):
    """SCHEDULE_WINDFALL = D_SCHEDULE - D_TRAIN (spec sec. 6).

    Resolved through the module namespace by `analyze_pair`, so bite-test 15
    can delete the indirect-production calculation and watch the blind-spot
    fixture stop biting. The conservation residual is computed from the ledger
    aggregates directly and does NOT route through this function -- otherwise
    the mutation would be caught by a neighbouring check instead of by the
    blind-spot assertion itself.
    """
    return d_schedule - d_train


def check_pair_identity(candidate, parent, self_pair=False):
    """Spec sec. 3. A mismatch is a transport/instrument error, not a drop."""
    mismatched, missing = [], []
    fields = list(SHARED_IDENTITY_FIELDS)
    if self_pair:
        fields += list(PAIR_VARIABLE_FIELDS)
    for f in list(SHARED_IDENTITY_FIELDS) + list(PAIR_VARIABLE_FIELDS):
        if candidate.identity.get(f) is None or parent.identity.get(f) is None:
            missing.append(f)
    for f in fields:
        if f in missing:
            continue
        if candidate.identity.get(f) != parent.identity.get(f):
            mismatched.append(f)
    return {
        "valid": not mismatched and not missing,
        "self_pair": bool(self_pair),
        "mismatched": mismatched,
        "missing": missing,
        "candidate_identity": dict(candidate.identity),
        "parent_identity": dict(parent.identity),
    }


def detect_activation(candidate, parent):
    """Spec sec. 4 activation and first divergence."""
    cand_banana = candidate.banana_commands()
    par_banana = parent.banana_commands()
    extra_commands = [c for c in cand_banana if c not in par_banana]

    cand_plants, _ = candidate.trace.own_banana_history()
    par_plants, _ = parent.trace.own_banana_history()
    plant_delta = [[t, uid, list(c)] for (t, uid, c) in cand_plants
                   if (t, uid, c) not in par_plants]

    cl, pl = candidate.command_lines(), parent.command_lines()
    first_divergence = None
    for i in range(max(len(cl), len(pl))):
        a = cl[i] if i < len(cl) else None
        b = pl[i] if i < len(pl) else None
        if a != b:
            first_divergence = i + 1
            break

    causes = []
    if extra_commands:
        causes.append("banana_command")
    if plant_delta:
        causes.append("own_banana_event")
    return {
        "banana_active": bool(causes),
        "activation_causes": causes,
        "banana_command_delta": [[t, raw] for (t, raw) in extra_commands],
        "own_banana_plant_delta": plant_delta,
        "first_divergence_turn": first_divergence,
    }


def analyze_pair(candidate, parent, bound=None, self_pair=False,
                 banana_mechanism_claimed=None, pair_id=None):
    """Exact paired I-30 result for one candidate/parent pair."""
    cl = candidate.ledger
    pl = parent.ledger

    d = {c: cl.dep(c) - pl.dep(c) for c in SOURCE_CLASSES}
    d_direct = d["ours"]
    d_schedule = d["opponent"] + d["natural"]
    d_unknown = d["unknown"]
    d_train = cl.train_spend - pl.train_spend
    d_opp = cl.terminal_score - pl.terminal_score
    residual = d_opp - (d_direct + d_schedule + d_unknown - d_train)

    identity = check_pair_identity(candidate, parent, self_pair=self_pair)
    activation = detect_activation(candidate, parent)
    if banana_mechanism_claimed is None:
        banana_mechanism_claimed = (candidate.banana_mechanism_claimed
                                    or parent.banana_mechanism_claimed)

    result = {
        "invariant": "I-30",
        "pair_id": pair_id or ("%s|%s" % (candidate.run_id, parent.run_id)),
        "candidate_run_id": candidate.run_id,
        "parent_run_id": parent.run_id,
        "d_direct": d_direct,
        "d_schedule": d_schedule,
        "d_unknown": d_unknown,
        "d_train": d_train,
        "d_opp": d_opp,
        "residual": residual,
        "d_terminal_turn": cl.terminal_turn - pl.terminal_turn,
        "d_first_productive_turn": _delta(cl.first_productive_turn,
                                          pl.first_productive_turn),
        "d_productive_turns": cl.productive_turns - pl.productive_turns,
        "d_opp_live_assets": cl.opp_live_assets - pl.opp_live_assets,
        "d_direct_interactions": (cl.direct_interactions
                                  - pl.direct_interactions),
        "pair_identity": identity,
        "banana_mechanism_claimed": bool(banana_mechanism_claimed),
        "counted_in_denominator": True,
        "candidate": cl.to_json(),
        "parent": pl.to_json(),
    }
    for c in SOURCE_CLASSES:
        result["d_dep_" + c] = d[c]
    for key in ("drop_events", "train_events", "plant_events",
                "harvest_events", "chop_events", "pick_events"):
        result["d_" + key] = cl.counts.get(key, 0) - pl.counts.get(key, 0)
    result.update(activation)

    # SCHEDULE_WINDFALL through the module namespace (see bite-test 15)
    result["schedule_windfall"] = compute_schedule_windfall(d_schedule,
                                                            d_train)

    # ---- fail-closed instrument gates (spec sec. 2 / 6) ------------------
    unready = []
    if not identity["valid"]:
        unready.append("pair_identity")
    if d_unknown != 0 or cl.unknown_atoms != 0 or pl.unknown_atoms != 0:
        unready.append("unknown_provenance")
    if residual != 0 or cl.residual != 0 or pl.residual != 0:
        unready.append("conservation_residual")

    sub_status = None
    if unready:
        status = GATE_UNREADY
    elif not activation["banana_active"]:
        status = UNPROVEN if banana_mechanism_claimed else NOT_APPLICABLE
    elif bound is None:
        unready.append("absent_bound")
        sub_status = MEASURED_UNTHRESHOLDED
        status = GATE_UNREADY
    elif not bound.valid:
        unready.extend(bound.invalid_reasons)
        sub_status = MEASURED_UNTHRESHOLDED
        status = GATE_UNREADY
    elif not bound.satisfied(result):
        status = FAIL
    elif bound.owner_frozen:
        status = PASS
    else:
        # measured, thresholded only by a non-owner object: never PASS
        unready.append("bound_not_owner_frozen")
        sub_status = MEASURED_UNTHRESHOLDED
        status = GATE_UNREADY

    result["status"] = status
    result["sub_status"] = sub_status
    result["unready_reasons"] = unready
    result["bound"] = bound.to_json() if bound is not None else None
    if bound is not None and bound.valid:
        result["bound_metric_value"] = bound.measured_value(result)
        result["bound_satisfied"] = bound.satisfied(result)
    return result


def _delta(a, b):
    if a is None or b is None:
        return None
    return a - b


def _quantile(values, q):
    if not values:
        return None
    xs = sorted(values)
    idx = int(round(q * (len(xs) - 1)))
    return xs[idx]


def _mean(values):
    if not values:
        return None
    return sum(values) / float(len(values))


def aggregate_report(pair_results, bound=None, manifest=None):
    """Spec sec. 9 aggregate contract. No post-hoc exclusion is performed."""
    def summarise(rows, label):
        wind = [r["schedule_windfall"] for r in rows]
        out = {
            "population": label,
            "pairs": len(rows),
            "maps": len({r["pair_identity"]["candidate_identity"]
                         .get("map_sha256") for r in rows}),
            "seats": sorted({r["pair_identity"]["candidate_identity"]
                             .get("seat") for r in rows}),
            "opponent_families": sorted(
                {r["pair_identity"]["candidate_identity"]
                 .get("opponent_source_sha256") for r in rows}),
            "active_games": sum(1 for r in rows if r["banana_active"]),
            "positive_windfall_games": sum(1 for w in wind if w > 0),
            "positive_windfall_mass": sum(w for w in wind if w > 0),
            "worst_schedule_windfall": max(wind) if wind else None,
            "p10_schedule_windfall": _quantile(wind, 0.10),
            "p50_schedule_windfall": _quantile(wind, 0.50),
            "p90_schedule_windfall": _quantile(wind, 0.90),
            "unknown_source_pairs": sum(1 for r in rows
                                        if r["d_unknown"] != 0),
            "conservation_residual_pairs": sum(1 for r in rows
                                               if r["residual"] != 0),
            "gate_unready_pairs": sum(1 for r in rows
                                      if r["status"] == GATE_UNREADY),
        }
        for key in ("d_opp", "d_direct", "d_schedule", "d_train",
                    "schedule_windfall"):
            out["mean_" + key] = _mean([r[key] for r in rows])
        by_seat, by_family, by_map = {}, {}, {}
        for r in rows:
            ident = r["pair_identity"]["candidate_identity"]
            by_seat.setdefault(str(ident.get("seat")), []).append(
                r["schedule_windfall"])
            by_family.setdefault(str(ident.get("opponent_source_sha256")),
                                 []).append(r["schedule_windfall"])
            by_map.setdefault(str(ident.get("map_sha256")), []).append(
                r["schedule_windfall"])
        out["mean_windfall_by_seat"] = {k: _mean(v) for k, v in by_seat.items()}
        out["mean_windfall_by_opponent_family"] = {k: _mean(v)
                                                   for k, v in by_family.items()}
        out["mean_windfall_by_map"] = {k: _mean(v) for k, v in by_map.items()}
        return out

    rows = list(pair_results)
    active = [r for r in rows if r["banana_active"]]
    report = {
        "invariant": "I-30",
        "all_pairs": summarise(rows, "all_pairs"),
        "banana_active": summarise(active, "banana_active"),
        "event_episodes": sum(r["candidate"]["event_count"]
                              + r["parent"]["event_count"] for r in rows),
        "statuses": sorted({r["status"] for r in rows}),
        "bound": bound.to_json() if bound is not None else None,
        "sha_manifest": dict(manifest or {}),
        "pairs": rows,
    }
    blocking = [r for r in rows if r["status"] == GATE_UNREADY]
    report["aggregate_status"] = GATE_UNREADY if (
        blocking or bound is None or not bound.owner_frozen) else PASS
    return report


def main(argv=None):
    """Emit the fixture corpus as a per-pair + aggregate JSON artifact."""
    import argparse
    import i30_fixtures as fx

    ap = argparse.ArgumentParser(description="I-30 fixture analyzer")
    ap.add_argument("--report", required=True)
    args = ap.parse_args(argv)

    bound = Bound(fx.TEST_BOUND_ZERO_WINDFALL)
    pairs = []
    for name in sorted(n for n in dir(fx) if n.startswith("fixture_")):
        cand, par = getattr(fx, name)()
        self_pair = name.startswith("fixture_01") or name.startswith("fixture_11")
        pairs.append(analyze_pair(cand, par, bound=bound, self_pair=self_pair,
                                  pair_id=name))
    report = aggregate_report(pairs, bound=bound, manifest={
        "i30_ledger.py": sha256_text(open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "i30_ledger.py")).read()),
        "i30_analyzer.py": sha256_text(open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "i30_analyzer.py")).read()),
        "i30_fixtures.py": sha256_text(open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "i30_fixtures.py")).read()),
    })
    with open(args.report, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
