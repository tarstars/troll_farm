#!/usr/bin/env python3
"""I-30 paired analyzer: schedule / opponent-production exposure.

Authoritative specification:
  chatgpt_1/schedule-opponent-production-invariant-spec-2026-08-08.md
  (branch agent/chatgpt_1, artifact_commit cad16c4d), sections 3, 4, 6, 8,
  9 and 11.

Revised per the spec-author ruling
  chatgpt_1/i30-d1-d5-spec-ruling-2026-08-08.md (branch agent/chatgpt_1),
which replaced the spec's gross-only identity. Result schema version 2.

Per class c, the ledger reports GDEP_c (gross deposits), WDR_c (bank
withdrawals) and NBF_c = GDEP_c - WDR_c (net bank flow), separately. Paired
candidate-minus-parent quantities:

    D_DIRECT_NET   = dNBF_OURS
    D_SCHEDULE_NET = dNBF_OPP + dNBF_NATURAL
    D_UNKNOWN_NET  = dNBF_UNKNOWN
    D_TRAIN        = dTRAIN_SPEND
    D_OPP          = opponent_terminal_score(candidate) - ...(parent)

    SCHEDULE_WINDFALL_NET = D_SCHEDULE_NET - D_TRAIN
    RESIDUAL = D_OPP - (D_DIRECT_NET + D_SCHEDULE_NET + D_UNKNOWN_NET
                        - D_TRAIN)

Gross production stays a mandatory separate diagnostic and is never
substituted for the net flows:

    D_DIRECT_GROSS     = dGDEP_OURS
    D_PRODUCTION_GROSS = dGDEP_OPP + dGDEP_NATURAL
    D_WDR_c            = dWDR_c

Raw-zero instrument requirements: RESIDUAL == 0 and every per-run residual
== 0; no unknown score-bearing atom anywhere; and every attribution uniquely
derivable from the recorded state. Integers only, no tolerance. Failing any
of them is an instrument failure -> GATE_UNREADY, never a candidate PASS and
never a report-only warning. Note that `D_UNKNOWN_NET == 0` is NOT evidence
of complete provenance: unknown deposits and withdrawals can cancel.

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
from i30_ledger import SCHEMA_VERSION, SOURCE_CLASSES, sha256_text  # noqa: E402

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

# metric name -> key in the per-pair result.
#
# Ruling D1 change 4: "Make every future bound name the exact metric ... the
# unqualified `mean_schedule_windfall` name is no longer sufficient." Every
# name below either carries `_net` / `_gross` or names a quantity to which the
# distinction does not apply (`mean_d_opp` is a terminal-score delta,
# `mean_d_train` a spend).
SUPPORTED_METRICS = {
    "mean_schedule_windfall_net": "schedule_windfall_net",
    "mean_d_opp": "d_opp",
    "mean_d_train": "d_train",
    "mean_d_direct_net": "d_direct_net",
    "mean_d_schedule_net": "d_schedule_net",
    "mean_d_unknown_net": "d_unknown_net",
    "mean_d_direct_gross": "d_direct_gross",
    "mean_production_gross": "d_production_gross",
}


def metric_is_ambiguous(metric):
    """True for a bound metric name that does not state gross or net.

    `mean_schedule_windfall` is exactly the name the ruling rejects: it reads
    as a gross production term but resolves to a net one.
    """
    return any("%s_%s" % (metric, q) in SUPPORTED_METRICS
               for q in ("net", "gross"))


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
            if metric_is_ambiguous(self.metric):
                self.invalid_reasons.append(
                    "bound_metric_ambiguous_gross_or_net")
            else:
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


def compute_schedule_windfall_net(d_schedule_net, d_train):
    """SCHEDULE_WINDFALL_NET = D_SCHEDULE_NET - D_TRAIN (ruling D1).

    Resolved through the module namespace by `analyze_pair`, so bite-test 15
    can delete the indirect-production calculation and watch the blind-spot
    fixture stop biting. The conservation residual is computed from the ledger
    aggregates directly and does NOT route through this function -- otherwise
    the mutation would be caught by a neighbouring check instead of by the
    blind-spot assertion itself.
    """
    return d_schedule_net - d_train


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

    d_gdep = {c: cl.gdep[c] - pl.gdep[c] for c in SOURCE_CLASSES}
    d_wdr = {c: cl.wdr[c] - pl.wdr[c] for c in SOURCE_CLASSES}
    d_nbf = {c: cl.net_bank_flow(c) - pl.net_bank_flow(c)
             for c in SOURCE_CLASSES}

    # net bank flow: what actually reached the opponent's terminal score
    d_direct_net = d_nbf["ours"]
    d_schedule_net = d_nbf["opponent"] + d_nbf["natural"]
    d_unknown_net = d_nbf["unknown"]
    # gross production: whether the candidate expanded opponent production
    d_direct_gross = d_gdep["ours"]
    d_production_gross = d_gdep["opponent"] + d_gdep["natural"]
    d_unknown_gross = d_gdep["unknown"]

    d_train = cl.train_spend - pl.train_spend
    d_opp = cl.terminal_score - pl.terminal_score
    residual = d_opp - (d_direct_net + d_schedule_net + d_unknown_net
                        - d_train)

    identity = check_pair_identity(candidate, parent, self_pair=self_pair)
    activation = detect_activation(candidate, parent)
    if banana_mechanism_claimed is None:
        banana_mechanism_claimed = (candidate.banana_mechanism_claimed
                                    or parent.banana_mechanism_claimed)

    result = {
        "invariant": "I-30",
        "schema_version": SCHEMA_VERSION,
        "pair_id": pair_id or ("%s|%s" % (candidate.run_id, parent.run_id)),
        "candidate_run_id": candidate.run_id,
        "parent_run_id": parent.run_id,
        "d_direct_net": d_direct_net,
        "d_schedule_net": d_schedule_net,
        "d_unknown_net": d_unknown_net,
        "d_direct_gross": d_direct_gross,
        "d_production_gross": d_production_gross,
        "d_unknown_gross": d_unknown_gross,
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
        result["d_gdep_" + c] = d_gdep[c]
        result["d_wdr_" + c] = d_wdr[c]
        result["d_nbf_" + c] = d_nbf[c]
    for key in ("drop_events", "train_events", "plant_events",
                "harvest_events", "chop_events", "pick_events",
                "ambiguity_events"):
        result["d_" + key] = cl.counts.get(key, 0) - pl.counts.get(key, 0)
    result.update(activation)

    # SCHEDULE_WINDFALL_NET through the module namespace (see bite-test 15)
    result["schedule_windfall_net"] = compute_schedule_windfall_net(
        d_schedule_net, d_train)

    # ---- fail-closed instrument gates (spec sec. 2 / 6; ruling D5) -------
    unready = []
    if not identity["valid"]:
        unready.append("pair_identity")
    # any unproved score-bearing atom, even when unknown deposits and
    # withdrawals cancel numerically (ruling D1: "`D_UNKNOWN_NET == 0` is not
    # sufficient evidence of complete provenance")
    if (d_unknown_net != 0 or d_unknown_gross != 0
            or cl.unknown_atoms != 0 or pl.unknown_atoms != 0):
        unready.append("unknown_provenance")
    # and any attribution that was not uniquely derivable from the recorded
    # state, whatever the arithmetic says (ruling D5)
    if not cl.identifiable or not pl.identifiable:
        unready.append("non_identifiable_attribution")
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
        wind = [r["schedule_windfall_net"] for r in rows]
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
            "positive_windfall_net_games": sum(1 for w in wind if w > 0),
            "positive_windfall_net_mass": sum(w for w in wind if w > 0),
            "worst_schedule_windfall_net": max(wind) if wind else None,
            "p10_schedule_windfall_net": _quantile(wind, 0.10),
            "p50_schedule_windfall_net": _quantile(wind, 0.50),
            "p90_schedule_windfall_net": _quantile(wind, 0.90),
            "unknown_source_pairs": sum(
                1 for r in rows
                if r["d_unknown_net"] != 0 or r["d_unknown_gross"] != 0
                or r["candidate"]["unknown_atoms"]
                or r["parent"]["unknown_atoms"]),
            "non_identifiable_pairs": sum(
                1 for r in rows if not r["candidate"]["identifiable"]
                or not r["parent"]["identifiable"]),
            "conservation_residual_pairs": sum(1 for r in rows
                                               if r["residual"] != 0),
            "gate_unready_pairs": sum(1 for r in rows
                                      if r["status"] == GATE_UNREADY),
        }
        for key in ("d_opp", "d_direct_net", "d_schedule_net", "d_train",
                    "schedule_windfall_net", "d_direct_gross",
                    "d_production_gross"):
            out["mean_" + key] = _mean([r[key] for r in rows])
        by_seat, by_family, by_map = {}, {}, {}
        for r in rows:
            ident = r["pair_identity"]["candidate_identity"]
            by_seat.setdefault(str(ident.get("seat")), []).append(
                r["schedule_windfall_net"])
            by_family.setdefault(str(ident.get("opponent_source_sha256")),
                                 []).append(r["schedule_windfall_net"])
            by_map.setdefault(str(ident.get("map_sha256")), []).append(
                r["schedule_windfall_net"])
        out["mean_windfall_net_by_seat"] = {k: _mean(v)
                                            for k, v in by_seat.items()}
        out["mean_windfall_net_by_opponent_family"] = {
            k: _mean(v) for k, v in by_family.items()}
        out["mean_windfall_net_by_map"] = {k: _mean(v)
                                           for k, v in by_map.items()}
        return out

    rows = list(pair_results)
    active = [r for r in rows if r["banana_active"]]
    report = {
        "invariant": "I-30",
        "schema_version": SCHEMA_VERSION,
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
    corpus = [(n, n, ()) for n in sorted(n for n in dir(fx)
                                         if n.startswith("fixture_"))]
    corpus += list(fx.PARAMETERISED_VARIANTS)
    for pair_id, name, fixture_args in corpus:
        cand, par = getattr(fx, name)(*fixture_args)
        self_pair = name.startswith("fixture_01") or name.startswith("fixture_11")
        pairs.append(analyze_pair(cand, par, bound=bound, self_pair=self_pair,
                                  pair_id=pair_id))
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
