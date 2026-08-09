#!/usr/bin/env python3
"""I-30 paired analyzer: schedule / opponent-production exposure.

Authoritative specification:
  chatgpt_1/schedule-opponent-production-invariant-spec-2026-08-08.md
  (branch agent/chatgpt_1), sections 3, 4, 6, 8, 9 and 11.
Governing ruling:
  chatgpt_1/i30-d1-d5-spec-ruling-2026-08-08.md (schema version 2 -> 3).
Governing review (revision 3 closes its ten blocking defects):
  chatgpt_1/i30-revision-2-review-2026-08-08.md
  sha256 2be671a34a24010d00d5f7fb8c1ce3953bffe6475bee86d05e32e2fed61abdbc.

WHERE A VALUE VERDICT LIVES
---------------------------
Revision 2 evaluated `mean_*` bounds inside `analyze_pair`, so `Bound.population`
was dead, `mean_*` silently meant "this one game's value", `all_pairs` and
`banana_active` decided identically, and one game could FAIL a population
contract (review I30R2-1). Revision 3 splits the two levels absolutely:

    analyze_pair()      accounting + evaluability for ONE pair.
                        Statuses: GATE_UNREADY / NOT_APPLICABLE / UNPROVEN /
                        MEASURED. It takes no bound and never emits PASS, and
                        never emits FAIL from a value comparison.
    aggregate_report()  selects the population the bound names, computes the
                        exact metric over it, verifies owner authority, and is
                        the ONLY place a PASS or a value FAIL can be produced.

Aggregate precedence (review I30R2-2), evaluated strictly in this order:

    any pair GATE_UNREADY / instrument unready -> GATE_UNREADY
    bound absent, invalid or not owner-verified -> GATE_UNREADY
                                                   (MEASURED_UNTHRESHOLDED)
    population empty or insufficient            -> GATE_UNREADY
    any pair-level hard-limit FAIL              -> FAIL
    owner-frozen aggregate bound exceeded       -> FAIL
    otherwise                                   -> PASS

Per class c the ledger reports GDEP_c (gross deposits), WDR_c (withdrawals)
and NBF_c = GDEP_c - WDR_c (net bank flow), separately, and `baseline` (the
opponent's opening endowment) is a class of its own that is NOT production:

    D_DIRECT_NET   = dNBF_OURS
    D_SCHEDULE_NET = dNBF_OPP + dNBF_NATURAL
    D_BASELINE_NET = dNBF_BASELINE
    D_UNKNOWN_NET  = dNBF_UNKNOWN
    D_TRAIN        = dTRAIN_SPEND
    D_OPP          = opponent_terminal_score(candidate) - ...(parent)

    SCHEDULE_WINDFALL_NET = D_SCHEDULE_NET - D_TRAIN
    RESIDUAL = D_OPP - (D_DIRECT_NET + D_SCHEDULE_NET + D_BASELINE_NET
                        + D_UNKNOWN_NET - D_TRAIN)

    D_DIRECT_GROSS     = dGDEP_OURS
    D_PRODUCTION_GROSS = dGDEP_OPP + dGDEP_NATURAL      (baseline excluded)

Gross terms are `None`, with a feasible interval beside them, whenever the
deposit/withdrawal split was not identifiable (review I30R2-4).

Raw-zero instrument requirements: RESIDUAL == 0 and every per-run residual
== 0; no unknown score-bearing atom anywhere; every attribution uniquely
derivable; content identity derived and matching; and the harness declaring
that every emitted command was executed. Integers only, no tolerance.

Scope: measurement only -- no bot, candidate, parent, gate, host game,
submission or Arena state is read or written.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i30_ledger as ledger  # noqa: E402
from i30_ledger import (SCHEMA_VERSION, SOURCE_CLASSES,  # noqa: E402
                        PRODUCTION_CLASSES, SCHEDULE_CLASSES, canonical_json,
                        sha256_bytes, sha256_text)

HERE = os.path.dirname(os.path.abspath(__file__))

# spec sec. 8 status model
NOT_APPLICABLE = "NOT_APPLICABLE"
UNPROVEN = "UNPROVEN"
GATE_UNREADY = "GATE_UNREADY"
PASS = "PASS"
FAIL = "FAIL"
MEASURED_UNTHRESHOLDED = "MEASURED_UNTHRESHOLDED"
# a pair that is instrument-valid and fully accounted for, carrying no value
# verdict of its own (review I30R2-1)
MEASURED = "MEASURED"
# arithmetic from a bound that no owner ratified: reportable, never a verdict
NON_PRODUCTION_MEASUREMENT = "NON_PRODUCTION_MEASUREMENT"

# spec sec. 3: every field a pair must share exactly. The referee/engine
# identity is part of it: revision 2 could compare a trace made by a referee
# that discarded TRAIN against one made by a referee that executed it
# (review I30R2-8).
SHARED_IDENTITY_FIELDS = (
    "map_sha256", "seat", "opponent_source_sha256", "opponent_binary_sha256",
    "opponent_config_sha256", "engine_sha256", "initial_state_sha256",
    "rng_seed", "turn_cap", "termination_rule", "toolchain_sha256",
    "harness_sha256", "analyzer_config_sha256", "detector_config_sha256",
    "referee_sha256", "verb_manifest_sha256", "instrument_version",
    "corpus_version",
)
# spec sec. 3: the only allowed difference (and, in a declared self-pair,
# these must be equal too)
PAIR_VARIABLE_FIELDS = (
    "bot_source_sha256", "bot_binary_sha256", "command_stream_sha256",
    # derived from the transcript bytes: two different worlds may not declare
    # one transcript identity in a self-pair (review I30R2-6)
    "transcript_sha256",
)

OPERATORS = {
    "<=": lambda a, b: a <= b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    ">": lambda a, b: a > b,
    "==": lambda a, b: a == b,
}

# The frozen populations a bound may name (spec sec. 9). Revision 2 stored
# `Bound.population` and never used it.
POPULATIONS = {
    "all_pairs": lambda rows: list(rows),
    "banana_active": lambda rows: [r for r in rows if r["banana_active"]],
}

# metric name -> {"key": per-pair field, "reducer": population reducer}.
#
# Ruling D1 change 4: every name states gross or net. Review I30R2-1: every
# name also states its REDUCER, so a per-pair safety limit can never be
# smuggled in under `mean_*`.
def _mean(values):
    return Fraction(sum(values), len(values))


def _max(values):
    return Fraction(max(values))


REDUCERS = {"mean": _mean, "max": _max}

SUPPORTED_METRICS = {
    "mean_schedule_windfall_net": {"key": "schedule_windfall_net",
                                   "reducer": "mean"},
    "mean_d_opp": {"key": "d_opp", "reducer": "mean"},
    "mean_d_train": {"key": "d_train", "reducer": "mean"},
    "mean_d_direct_net": {"key": "d_direct_net", "reducer": "mean"},
    "mean_d_schedule_net": {"key": "d_schedule_net", "reducer": "mean"},
    "mean_d_baseline_net": {"key": "d_baseline_net", "reducer": "mean"},
    "mean_d_unknown_net": {"key": "d_unknown_net", "reducer": "mean"},
    "mean_d_direct_gross": {"key": "d_direct_gross", "reducer": "mean"},
    "mean_production_gross": {"key": "d_production_gross", "reducer": "mean"},
    "max_per_pair_schedule_windfall_net": {"key": "schedule_windfall_net",
                                           "reducer": "max"},
    "max_per_pair_production_gross": {"key": "d_production_gross",
                                      "reducer": "max"},
}


def metric_is_ambiguous(metric):
    """True for a bound metric name that does not state gross or net.

    `mean_schedule_windfall` is exactly the name the ruling rejects: it reads
    as a gross production term but resolves to a net one.
    """
    return any("%s_%s" % (metric, q) in SUPPORTED_METRICS
               for q in ("net", "gross"))


# --------------------------------------------------------------------------
# Owner authority (review I30R2-3)
#
# Revision 2 treated `{"provenance": "owner_frozen"}` as authority, so any
# caller could manufacture a production PASS by adding a string. Authority is
# now a BLOB AT A PINNED REF that must independently name the bound.
# --------------------------------------------------------------------------

PRODUCTION_AUTHORITY_REF = "refs/remotes/origin/main"
PRODUCTION_AUTHORITY_ID = "user"
PRODUCTION_DECISION_PATH = "coordination/decisions/i30-bound-decision.json"


class OwnerAuthority:
    """Resolves decision blobs from one frozen, named source.

    `loader(path) -> bytes | None` is the only way in; nothing else in this
    module may declare a decision.
    """

    def __init__(self, loader, ref, authority_id):
        self._loader = loader
        self.ref = ref
        self.authority_id = authority_id

    def resolve(self, path):
        try:
            return self._loader(path)
        except Exception:
            return None

    def to_json(self):
        return {"authority_ref": self.ref, "authority_id": self.authority_id,
                "authority_kind": type(self).__name__}


class GitRefAuthority(OwnerAuthority):
    """The owner decision must be a blob committed on a named git ref."""

    def __init__(self, repo_root, ref, authority_id):
        self.repo_root = repo_root

        def loader(path):
            proc = subprocess.run(
                ["git", "cat-file", "blob", "%s:%s" % (ref, path)],
                cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if proc.returncode != 0:
                return None
            return proc.stdout

        OwnerAuthority.__init__(self, loader, ref, authority_id)


class MappingAuthority(OwnerAuthority):
    """An explicit path -> bytes mapping (fixtures and tests only)."""

    def __init__(self, blobs, ref, authority_id):
        OwnerAuthority.__init__(self, lambda p: blobs.get(p), ref,
                                authority_id)


def production_authority(repo_root):
    """The only authority a production run may consult."""
    return GitRefAuthority(repo_root, PRODUCTION_AUTHORITY_REF,
                           PRODUCTION_AUTHORITY_ID)


def verify_owner_decision(bound, authority, observed_utc):
    """Structurally verify that an owner froze exactly this bound, first.

    Every clause is a separate named reason so a reviewer can see which link
    of the chain is missing rather than a bare boolean.
    """
    out = {"verified": False, "reasons": [], "decision": None,
           "authority": authority.to_json() if authority is not None else None,
           "decision_path": (bound.spec.get("owner_decision_path")
                             if bound is not None else None),
           "observed_utc": observed_utc}
    reasons = out["reasons"]

    if bound is None:
        reasons.append("bound_absent")
        return out
    if "self_declared_owner_provenance_rejected" in bound.invalid_reasons:
        reasons.append("self_declared_owner_provenance_rejected")
    if authority is None:
        reasons.append("owner_authority_absent")
        return out

    path = bound.spec.get("owner_decision_path")
    blob = authority.resolve(path) if path else None
    if blob is None:
        reasons.append("owner_decision_unresolved")
        return out
    if sha256_bytes(blob) != bound.spec.get("owner_decision_blob"):
        reasons.append("owner_decision_blob_mismatch")
    try:
        decision = json.loads(blob.decode("utf-8"))
    except Exception:
        reasons.append("owner_decision_unparseable")
        return out
    out["decision"] = decision

    if decision.get("bound_body_sha256") != bound.body_sha256:
        reasons.append("owner_decision_bound_sha_mismatch")
    if decision.get("invariant") != "I-30":
        reasons.append("owner_decision_invariant_mismatch")
    if decision.get("authority") != authority.authority_id:
        reasons.append("owner_decision_authority_mismatch")
    frozen = decision.get("frozen_utc")
    if not frozen or not observed_utc or str(frozen) > str(observed_utc):
        # a bound chosen after the results were seen is not a bound
        reasons.append("owner_decision_not_frozen_before_observation")

    out["verified"] = not reasons
    return out


class Bound:
    """Aggregate value bound, validated before it may decide anything.

    The spec deliberately does not choose a threshold, so this class only
    validates and evaluates whatever object it is handed. Authority is NOT a
    property of the object: it is `verify_owner_decision`'s verdict against an
    `OwnerAuthority`, and until that verdict is `verified` the bound can emit
    neither PASS nor a production FAIL (review I30R2-3).
    """

    REQUIRED_FIELDS = ("schema_version", "population", "metric", "operator",
                       "threshold", "owner_decision_path",
                       "owner_decision_blob")

    def __init__(self, spec, pinned_sha256=None):
        self.spec = dict(spec)
        self.canonical = canonical_json(self.spec)
        self.sha256 = sha256_text(self.canonical)
        # The decision names the bound and the bound names the decision, so
        # one link must be over a projection: `body_sha256` is the bound
        # MINUS its own decision pointer, and it is what an owner decision
        # must pin. Editing any operative field (metric, operator, threshold,
        # population, schema) changes it.
        self.body_sha256 = sha256_text(canonical_json(
            {k: v for k, v in self.spec.items()
             if k not in ("owner_decision_path", "owner_decision_blob")}))
        self.pinned_sha256 = pinned_sha256
        self.provenance = self.spec.get("provenance", "unspecified")
        self.population = self.spec.get("population")
        self.metric = self.spec.get("metric")
        self.operator = self.spec.get("operator")
        self.threshold = self.spec.get("threshold")

        self.invalid_reasons = []
        if [f for f in self.REQUIRED_FIELDS if f not in self.spec]:
            self.invalid_reasons.append("bound_schema_incomplete")
        if self.spec.get("schema_version") != SCHEMA_VERSION:
            self.invalid_reasons.append("bound_schema_version_unsupported")
        if pinned_sha256 is not None and pinned_sha256 != self.sha256:
            self.invalid_reasons.append("bound_hash_mismatch")
        if self.population not in POPULATIONS:
            self.invalid_reasons.append("bound_population_unsupported")
        if self.metric not in SUPPORTED_METRICS:
            if metric_is_ambiguous(self.metric):
                self.invalid_reasons.append(
                    "bound_metric_ambiguous_gross_or_net")
            else:
                self.invalid_reasons.append("bound_metric_unsupported")
        if self.operator not in OPERATORS:
            self.invalid_reasons.append("bound_operator_unsupported")
        if self.provenance == "owner_frozen":
            # a self-attested string is not authority; it is now an error
            self.invalid_reasons.append(
                "self_declared_owner_provenance_rejected")

    @property
    def valid(self):
        return not self.invalid_reasons

    @property
    def reducer(self):
        return SUPPORTED_METRICS[self.metric]["reducer"]

    @property
    def metric_key(self):
        return SUPPORTED_METRICS[self.metric]["key"]

    def select(self, rows):
        return POPULATIONS[self.population](rows)

    def evaluate(self, rows):
        """Exact population metric. Fractions only -- never a float compare."""
        out = {"population": self.population, "metric": self.metric,
               "reducer": self.reducer, "operator": self.operator,
               "threshold": self.threshold, "population_pairs": len(rows),
               "metric_value_exact": None, "metric_numerator": None,
               "metric_denominator": None, "metric_value_float": None,
               "bound_satisfied": None, "reasons": []}
        if not rows:
            out["reasons"].append("population_empty")
            return out
        values = [r.get(self.metric_key) for r in rows]
        if any(v is None for v in values):
            # a non-identifiable quantity may never be reduced to a point
            out["reasons"].append("metric_not_identifiable")
            return out
        value = REDUCERS[self.reducer]([Fraction(v) for v in values])
        out["metric_numerator"] = value.numerator
        out["metric_denominator"] = value.denominator
        out["metric_value_exact"] = str(value)
        out["metric_value_float"] = float(value)
        out["bound_satisfied"] = OPERATORS[self.operator](value,
                                                          Fraction(
                                                              self.threshold))
        return out

    def to_json(self):
        return {"bound_sha256": self.sha256,
                "bound_body_sha256": self.body_sha256,
                "bound_pinned_sha256": self.pinned_sha256,
                "bound_provenance": self.provenance,
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
    """Spec sec. 3. A mismatch is a transport/instrument error, not a drop.

    Content identity is compared on DERIVED values (review I30R2-6): two
    callers declaring one `transcript_sha256` over two different transcripts
    are caught here, not trusted.
    """
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
    pin_mismatches = sorted(set(candidate.identity_pin_mismatches)
                            | set(parent.identity_pin_mismatches))
    return {
        "valid": not mismatched and not missing and not pin_mismatches,
        "self_pair": bool(self_pair),
        "mismatched": mismatched,
        "missing": missing,
        "identity_pin_mismatches": pin_mismatches,
        "candidate_identity": dict(candidate.identity),
        "parent_identity": dict(parent.identity),
        "candidate_derived_identity": dict(candidate.derived_identity),
        "parent_derived_identity": dict(parent.derived_identity),
    }


# --------------------------------------------------------------------------
# Activation (spec sec. 4; review I30R2-7)
#
# Revision 2 saw only extra `PLANT/PICK ... BANANA` command strings and extra
# own banana plant events, so a candidate that changed only harvest timing,
# chopped an existing banana, banked harvested fruit differently, or entered a
# Banana controller state without planting was labelled NOT_APPLICABLE. The
# contract below is versioned and enumerates every frozen cause.
# --------------------------------------------------------------------------

ACTIVATION_CONTRACT_VERSION = 2
ACTIVATION_CAUSES = ("banana_command", "own_banana_plant", "banana_harvest",
                     "banana_chop", "banana_banking", "controller_state",
                     "integration_seam")
# causes that can only be evidenced by harness telemetry
TELEMETRY_CAUSES = ("controller_state", "integration_seam")


def _delta_list(a, b):
    """Members of `a` that `b` does not have, order preserved."""
    rest = list(b)
    out = []
    for item in a:
        if item in rest:
            rest.remove(item)
        else:
            out.append(item)
    return out


def detect_activation(candidate, parent):
    """Spec sec. 4 activation and first divergence, over successful events."""
    cand_banana = candidate.banana_commands()
    par_banana = parent.banana_commands()
    extra_commands = _delta_list(cand_banana, par_banana)

    ce, pe = candidate.banana_state_events(), parent.banana_state_events()
    plant_delta = _delta_list(ce["banana_plants"], pe["banana_plants"])
    own_plant_delta = [e for e in plant_delta
                       if e[2] == ledger.OWN_PLAYER or e[2] is None]
    harvest_delta = _delta_list(ce["banana_harvests"], pe["banana_harvests"])
    chop_delta = _delta_list(ce["banana_chops"], pe["banana_chops"])
    bank_delta = _delta_list(ce["banana_bankings"], pe["banana_bankings"])

    ct, pt = candidate.activation_telemetry, parent.activation_telemetry
    controller_delta = (ct.get("controller_states")
                        != pt.get("controller_states"))
    seam_delta = ct.get("seam_signature") != pt.get("seam_signature")

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
    if own_plant_delta:
        causes.append("own_banana_plant")
    if harvest_delta:
        causes.append("banana_harvest")
    if chop_delta:
        causes.append("banana_chop")
    if bank_delta:
        causes.append("banana_banking")
    if controller_delta:
        causes.append("controller_state")
    if seam_delta:
        causes.append("integration_seam")

    # A claimed mechanism whose only possible evidence is telemetry that was
    # never bound must not be answered with NOT_APPLICABLE (review I30R2-7).
    claimed = set(candidate.claimed_mechanisms) | set(parent.claimed_mechanisms)
    unbound = sorted(c for c in claimed & set(TELEMETRY_CAUSES)
                     if not ct.get({"controller_state": "controller_states",
                                    "integration_seam": "seam_signature"}[c]))
    unsupported_claims = sorted(claimed - set(ACTIVATION_CAUSES))

    return {
        "activation_contract_version": ACTIVATION_CONTRACT_VERSION,
        "banana_active": bool(causes),
        "activation_causes": causes,
        "claimed_mechanisms": sorted(claimed),
        "unbound_telemetry_claims": unbound,
        "unsupported_activation_claims": unsupported_claims,
        "banana_command_delta": [[t, raw] for (t, raw) in extra_commands],
        "own_banana_plant_delta": [list(e) for e in own_plant_delta],
        "banana_harvest_delta": [list(e) for e in harvest_delta],
        "banana_chop_delta": [list(e) for e in chop_delta],
        "banana_banking_delta": [list(e) for e in bank_delta],
        "controller_state_delta": bool(controller_delta),
        "integration_seam_delta": bool(seam_delta),
        "first_divergence_turn": first_divergence,
    }


def _sub(a, b):
    """Delta that propagates non-identifiability instead of inventing a point."""
    if a is None or b is None:
        return None
    return a - b


def _isub(a, b):
    """Interval subtraction: [a_lo - b_hi, a_hi - b_lo]."""
    return [a[0] - b[1], a[1] - b[0]]


def _iadd(a, b):
    return [a[0] + b[0], a[1] + b[1]]


def analyze_pair(candidate, parent, self_pair=False,
                 banana_mechanism_claimed=None, pair_id=None):
    """Exact paired I-30 accounting for one candidate/parent pair.

    NOTE: there is deliberately no `bound` parameter. A pair is not a
    population, so no value operator may be applied here (review I30R2-1).
    """
    identity = check_pair_identity(candidate, parent, self_pair=self_pair)
    activation = detect_activation(candidate, parent)
    if banana_mechanism_claimed is None:
        banana_mechanism_claimed = (candidate.banana_mechanism_claimed
                                    or parent.banana_mechanism_claimed
                                    or bool(activation["claimed_mechanisms"]))

    result = {
        "invariant": "I-30",
        "schema_version": SCHEMA_VERSION,
        "pair_id": pair_id or ("%s|%s" % (candidate.run_id, parent.run_id)),
        "candidate_run_id": candidate.run_id,
        "parent_run_id": parent.run_id,
        "pair_identity": identity,
        "banana_mechanism_claimed": bool(banana_mechanism_claimed),
        "counted_in_denominator": True,
        "candidate_execution": candidate.execution.to_json(),
        "parent_execution": parent.execution.to_json(),
    }
    result.update(activation)

    unready = []
    if not identity["valid"]:
        unready.append("pair_identity")
    if identity["identity_pin_mismatches"]:
        unready.append("identity_pin_mismatch")
    if activation["unbound_telemetry_claims"]:
        unready.append("activation_telemetry_unbound")
    if activation["unsupported_activation_claims"]:
        unready.append("activation_claim_unsupported")

    # ---- INPUT GATE: did the referee actually execute the commands? -------
    # This runs BEFORE any ledger is built. On a transcript from the referee
    # that silently discarded TRAIN, the ledger's spawn-derived TRAIN spend is
    # a fabrication, and no downstream arithmetic can notice (review I30R2-8).
    if not candidate.execution.valid or not parent.execution.valid:
        unready.append("input_execution_validity")
        for key in ("d_direct_net", "d_schedule_net", "d_baseline_net",
                    "d_unknown_net", "d_direct_gross", "d_production_gross",
                    "d_unknown_gross", "d_train", "d_opp", "residual",
                    "schedule_windfall_net", "candidate", "parent",
                    "candidate_ledger_sha256", "parent_ledger_sha256"):
            result[key] = None
        for c in SOURCE_CLASSES:
            result["d_gdep_" + c] = None
            result["d_wdr_" + c] = None
            result["d_nbf_" + c] = None
        result["status"] = GATE_UNREADY
        result["unready_reasons"] = unready
        return result

    cl = candidate.ledger
    pl = parent.ledger

    d_gdep = {c: _sub(cl.gross_deposits(c), pl.gross_deposits(c))
              for c in SOURCE_CLASSES}
    d_wdr = {c: _sub(cl.gross_withdrawals(c), pl.gross_withdrawals(c))
             for c in SOURCE_CLASSES}
    d_nbf = {c: cl.net_bank_flow(c) - pl.net_bank_flow(c)
             for c in SOURCE_CLASSES}
    d_gdep_interval = {c: _isub(cl.gdep_class_interval[c],
                                pl.gdep_class_interval[c])
                       for c in SOURCE_CLASSES}
    d_wdr_interval = {c: _isub(cl.wdr_class_interval[c],
                               pl.wdr_class_interval[c])
                      for c in SOURCE_CLASSES}

    # net bank flow: what actually reached the opponent's terminal score
    d_direct_net = d_nbf["ours"]
    d_schedule_net = sum(d_nbf[c] for c in SCHEDULE_CLASSES)
    d_baseline_net = d_nbf["baseline"]
    d_unknown_net = d_nbf["unknown"]
    # gross production: whether the candidate expanded opponent production.
    # `baseline` is excluded by construction: recycling the opening endowment
    # through the bank is not production (review I30R2-5).
    d_direct_gross = d_gdep["ours"]
    d_production_gross = (
        None if any(d_gdep[c] is None for c in SCHEDULE_CLASSES)
        else sum(d_gdep[c] for c in SCHEDULE_CLASSES))
    d_unknown_gross = d_gdep["unknown"]

    d_train = cl.train_spend - pl.train_spend
    d_opp = cl.terminal_score - pl.terminal_score
    residual = d_opp - (d_direct_net + d_schedule_net + d_baseline_net
                        + d_unknown_net - d_train)

    result.update({
        "d_direct_net": d_direct_net,
        "d_schedule_net": d_schedule_net,
        "d_baseline_net": d_baseline_net,
        "d_unknown_net": d_unknown_net,
        "d_direct_gross": d_direct_gross,
        "d_production_gross": d_production_gross,
        "d_unknown_gross": d_unknown_gross,
        "d_direct_gross_interval": d_gdep_interval["ours"],
        "d_production_gross_interval": [
            sum(d_gdep_interval[c][0] for c in SCHEDULE_CLASSES),
            sum(d_gdep_interval[c][1] for c in SCHEDULE_CLASSES)],
        "d_baseline_gross_interval": d_gdep_interval["baseline"],
        "gross_identifiable": (cl.gross_identifiable and pl.gross_identifiable),
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
        "candidate": cl.to_json(),
        "parent": pl.to_json(),
    })
    for c in SOURCE_CLASSES:
        result["d_gdep_" + c] = d_gdep[c]
        result["d_wdr_" + c] = d_wdr[c]
        result["d_nbf_" + c] = d_nbf[c]
        result["d_gdep_interval_" + c] = d_gdep_interval[c]
        result["d_wdr_interval_" + c] = d_wdr_interval[c]
    for key in ("drop_events", "train_events", "plant_events",
                "harvest_events", "chop_events", "pick_events",
                "ambiguity_events"):
        result["d_" + key] = cl.counts.get(key, 0) - pl.counts.get(key, 0)

    # SCHEDULE_WINDFALL_NET through the module namespace (see bite-test 15)
    result["schedule_windfall_net"] = compute_schedule_windfall_net(
        d_schedule_net, d_train)

    # raw-ledger binding (review I30R2-9)
    result["candidate_ledger_sha256"] = sha256_text(canonical_json(
        result["candidate"]))
    result["parent_ledger_sha256"] = sha256_text(canonical_json(
        result["parent"]))

    # ---- fail-closed instrument gates (spec sec. 2 / 6; ruling D5) -------
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

    if unready:
        status = GATE_UNREADY
    elif not activation["banana_active"]:
        status = UNPROVEN if banana_mechanism_claimed else NOT_APPLICABLE
    else:
        # instrument-valid, fully attributed, active -- and carrying no value
        # verdict of its own. The bound is an aggregate concern.
        status = MEASURED

    result["status"] = status
    result["unready_reasons"] = unready
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


def _mean_or_none(values):
    values = [v for v in values if v is not None]
    if not values:
        return None
    return sum(values) / float(len(values))


# --------------------------------------------------------------------------
# Provenance closure (review I30R2-9)
# --------------------------------------------------------------------------

SPEC_PATH = ("chatgpt_1/schedule-opponent-production-invariant-spec"
             "-2026-08-08.md")
RULING_PATH = "chatgpt_1/i30-d1-d5-spec-ruling-2026-08-08.md"
REVIEW_PATH = "chatgpt_1/i30-revision-2-review-2026-08-08.md"
SPEC_REF = "origin/agent/chatgpt_1"
ENGINE_PATH = "rust/src/game/engine.rs"
MODULE_FILES = ("i30_ledger.py", "i30_analyzer.py", "i30_fixtures.py",
                "test_i30_invariant.py", "trace_detectors.py")
# the protocol the referee and this analyzer must agree on
COMMAND_PROTOCOL_VERBS = ("MOVE", "PLANT", "PICK", "DROP", "HARVEST", "CHOP",
                          "TRAIN", "MINE", "MSG", "WAIT")


def _git_blob_sha(repo_root, ref, path):
    proc = subprocess.run(["git", "cat-file", "blob", "%s:%s" % (ref, path)],
                          cwd=repo_root, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    if proc.returncode != 0:
        return "UNRESOLVED"
    return sha256_bytes(proc.stdout)


def provenance_manifest(repo_root):
    """Transitive closure over every input that can change a result.

    Revision 2 hashed three modules. A reviewer could not tell which spec,
    which parser, which engine or which interpreter produced the numbers.
    """
    manifest = {}
    for name in MODULE_FILES:
        path = os.path.join(HERE, name)
        with open(path, "rb") as fh:
            manifest[name] = sha256_bytes(fh.read())
    manifest["spec:" + SPEC_PATH] = _git_blob_sha(repo_root, SPEC_REF,
                                                  SPEC_PATH)
    manifest["ruling:" + RULING_PATH] = _git_blob_sha(repo_root, SPEC_REF,
                                                      RULING_PATH)
    manifest["review:" + REVIEW_PATH] = _git_blob_sha(repo_root, SPEC_REF,
                                                      REVIEW_PATH)
    engine = os.path.join(repo_root, ENGINE_PATH)
    if os.path.exists(engine):
        with open(engine, "rb") as fh:
            manifest["engine:" + ENGINE_PATH] = sha256_bytes(fh.read())
    else:
        manifest["engine:" + ENGINE_PATH] = "UNRESOLVED"
    manifest["python_version"] = sys.version.split()[0]
    manifest["platform"] = platform.platform()
    manifest["command_protocol_sha256"] = ledger.verb_manifest_sha256(
        COMMAND_PROTOCOL_VERBS)
    manifest["schema_version"] = SCHEMA_VERSION
    manifest["activation_contract_version"] = ACTIVATION_CONTRACT_VERSION
    return manifest


def aggregate_report(pair_results, bound=None, manifest=None, authority=None,
                     observed_utc=None, raw_ledger_index=None):
    """Spec sec. 9 aggregate contract, and the ONLY place a verdict is made.

    No post-hoc exclusion is performed: every row counts in the denominator.
    """
    def summarise(rows, label):
        wind = [r["schedule_windfall_net"] for r in rows
                if r.get("schedule_windfall_net") is not None]
        out = {
            "population": label,
            "pairs": len(rows),
            "maps": len({r["pair_identity"]["candidate_identity"]
                         .get("map_sha256") for r in rows}),
            "seats": sorted({str(r["pair_identity"]["candidate_identity"]
                                 .get("seat")) for r in rows}),
            "opponent_families": sorted(
                {str(r["pair_identity"]["candidate_identity"]
                     .get("opponent_source_sha256")) for r in rows}),
            "active_games": sum(1 for r in rows if r["banana_active"]),
            "positive_windfall_net_games": sum(1 for w in wind if w > 0),
            "positive_windfall_net_mass": sum(w for w in wind if w > 0),
            "worst_schedule_windfall_net": max(wind) if wind else None,
            "p10_schedule_windfall_net": _quantile(wind, 0.10),
            "p50_schedule_windfall_net": _quantile(wind, 0.50),
            "p90_schedule_windfall_net": _quantile(wind, 0.90),
            "unknown_source_pairs": sum(
                1 for r in rows
                if r.get("d_unknown_net") != 0 or r.get("d_unknown_gross") != 0
                or (r.get("candidate") or {}).get("unknown_atoms")
                or (r.get("parent") or {}).get("unknown_atoms")),
            "non_identifiable_pairs": sum(
                1 for r in rows
                if not (r.get("candidate") or {}).get("identifiable", False)
                or not (r.get("parent") or {}).get("identifiable", False)),
            "non_identifiable_gross_pairs": sum(
                1 for r in rows if r.get("gross_identifiable") is not True),
            "conservation_residual_pairs": sum(1 for r in rows
                                               if r.get("residual") != 0),
            "gate_unready_pairs": sum(1 for r in rows
                                      if r["status"] == GATE_UNREADY),
            "execution_invalid_pairs": sum(
                1 for r in rows
                if not r["candidate_execution"]["valid"]
                or not r["parent_execution"]["valid"]),
        }
        for key in ("d_opp", "d_direct_net", "d_schedule_net",
                    "d_baseline_net", "d_train", "schedule_windfall_net",
                    "d_direct_gross", "d_production_gross"):
            out["mean_" + key] = _mean_or_none([r.get(key) for r in rows])
        by_seat, by_family, by_map = {}, {}, {}
        for r in rows:
            ident = r["pair_identity"]["candidate_identity"]
            by_seat.setdefault(str(ident.get("seat")), []).append(
                r.get("schedule_windfall_net"))
            by_family.setdefault(str(ident.get("opponent_source_sha256")),
                                 []).append(r.get("schedule_windfall_net"))
            by_map.setdefault(str(ident.get("map_sha256")), []).append(
                r.get("schedule_windfall_net"))
        out["mean_windfall_net_by_seat"] = {k: _mean_or_none(v)
                                            for k, v in by_seat.items()}
        out["mean_windfall_net_by_opponent_family"] = {
            k: _mean_or_none(v) for k, v in by_family.items()}
        out["mean_windfall_net_by_map"] = {k: _mean_or_none(v)
                                           for k, v in by_map.items()}
        return out

    rows = list(pair_results)
    active = [r for r in rows if r["banana_active"]]
    owner = verify_owner_decision(bound, authority, observed_utc)
    selected = bound.select(rows) if (bound is not None and bound.valid) else []
    evaluation = (bound.evaluate(selected) if (bound is not None
                                               and bound.valid)
                  else {"population": getattr(bound, "population", None),
                        "metric": getattr(bound, "metric", None),
                        "population_pairs": 0, "metric_value_exact": None,
                        "metric_numerator": None, "metric_denominator": None,
                        "metric_value_float": None, "bound_satisfied": None,
                        "reasons": ["bound_absent_or_invalid"]})

    report = {
        "invariant": "I-30",
        "schema_version": SCHEMA_VERSION,
        "all_pairs": summarise(rows, "all_pairs"),
        "banana_active": summarise(active, "banana_active"),
        "event_episodes": sum((r.get("candidate") or {}).get("event_count", 0)
                              + (r.get("parent") or {}).get("event_count", 0)
                              for r in rows),
        "statuses": sorted({r["status"] for r in rows}),
        "bound": bound.to_json() if bound is not None else None,
        "bound_evaluation": evaluation,
        "owner_decision": owner,
        "observed_utc": observed_utc,
        "sha_manifest": dict(manifest or {}),
        "raw_ledger_index": dict(raw_ledger_index or {}),
        "pair_result_sha256": {
            r["pair_id"]: sha256_text(canonical_json(r)) for r in rows},
        "pairs": rows,
    }

    # ---- verdict precedence (review I30R2-2) -----------------------------
    unready, fail_reasons = [], []
    if any(r["status"] == GATE_UNREADY for r in rows):
        unready.append("pair_gate_unready")
    if any(not r["candidate_execution"]["valid"]
           or not r["parent_execution"]["valid"] for r in rows):
        unready.append("input_execution_validity")
    if bound is None:
        unready.append("absent_bound")
    elif not bound.valid:
        unready.extend(bound.invalid_reasons)
    if bound is not None and not owner["verified"]:
        unready.append("bound_not_owner_verified")
    # ONE guard, so a mutation of it cannot be masked by a duplicate:
    # an empty corpus and an empty selected population are both "there is
    # nothing here to have passed" (review I30R2-2).
    if (not rows) or (bound is not None and bound.valid and not selected):
        unready.append("population_empty")
    for reason in evaluation.get("reasons", []):
        if reason not in ("bound_absent_or_invalid",):
            unready.append(reason)

    if any(r["status"] == FAIL for r in rows):
        fail_reasons.append("pair_fail")
    if evaluation.get("bound_satisfied") is False:
        fail_reasons.append("bound_exceeded")

    sub_status = None
    if unready:
        status = GATE_UNREADY
        if ("bound_not_owner_verified" in unready or "absent_bound" in unready
                or any(r.startswith("bound_") for r in unready)):
            # measured, but no ratified threshold exists: the arithmetic is
            # published as an explicitly non-production measurement, never as
            # a production FAIL (review I30R2-3)
            sub_status = MEASURED_UNTHRESHOLDED
    elif fail_reasons:
        status = FAIL
    else:
        status = PASS

    report["aggregate_status"] = status
    report["aggregate_sub_status"] = sub_status
    report["aggregate_unready_reasons"] = unready
    report["aggregate_fail_reasons"] = fail_reasons if status == FAIL else []
    report["unratified_bound_evaluation"] = (
        None if (bound is None or owner["verified"])
        else dict(evaluation, status=NON_PRODUCTION_MEASUREMENT))
    return report


def main(argv=None):
    """Emit the fixture corpus as a per-pair + aggregate JSON artifact."""
    import argparse
    import i30_fixtures as fx

    ap = argparse.ArgumentParser(description="I-30 fixture analyzer")
    ap.add_argument("--report", required=True)
    ap.add_argument("--ledger-dir", default=None,
                    help="directory for the raw per-run ledgers (I30R2-9)")
    ap.add_argument("--observed-utc", default=fx.OBSERVED_UTC)
    args = ap.parse_args(argv)

    bound = Bound(fx.TEST_BOUND_WINDFALL)
    pairs = []
    corpus = [(n, n, ()) for n in sorted(n for n in dir(fx)
                                         if n.startswith("fixture_"))]
    corpus += list(fx.PARAMETERISED_VARIANTS)
    ledger_dir = args.ledger_dir or os.path.join(HERE, "i30", "ledgers")
    os.makedirs(ledger_dir, exist_ok=True)
    raw_index = {}
    for pair_id, name, fixture_args in corpus:
        cand, par = getattr(fx, name)(*fixture_args)
        self_pair = name.startswith(("fixture_01", "fixture_11"))
        res = analyze_pair(cand, par, self_pair=self_pair, pair_id=pair_id)
        pairs.append(res)
        for side, run in (("candidate", cand), ("parent", par)):
            if res[side] is None:
                continue
            blob = canonical_json(res[side]) + "\n"
            path = os.path.join(ledger_dir, "%s.json" % run.run_id)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(blob)
            raw_index[run.run_id] = {
                "path": os.path.relpath(path, HERE),
                "sha256": sha256_text(blob),
                "pair_id": pair_id, "side": side,
            }

    repo_root = os.environ.get("I30_REPO_ROOT") or os.path.abspath(
        os.path.join(HERE, "..", ".."))
    report = aggregate_report(
        pairs, bound=bound, manifest=provenance_manifest(repo_root),
        # the production authority: no owner decision exists, so the corpus
        # can only be GATE_UNREADY
        authority=production_authority(repo_root),
        observed_utc=args.observed_utc, raw_ledger_index=raw_index)
    with open(args.report, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
