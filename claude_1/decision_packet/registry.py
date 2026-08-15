#!/usr/bin/env python3
"""Decision Packet — code-owned registries and the source-site drift guard.

P-1 increment 1 — **`PARTIAL_FOUNDATION`. Rollout step 1 is NOT complete and acceptance item 1
stays OPEN.** (Relabelled 2026-08-15 per `codex_1` review
`codex_1/reviews/decision-packet-p1-increment1-review-2026-08-15.md`, whose two concrete claims
I reproduced by execution before accepting them.)

Step 1 is *"freeze schema, source registry and exact candidate SHA."* This module freezes the
exact candidate SHA and a **versioned partial** source registry. It is not the frozen step-1
registry, because §5.4 also requires ids for every filter, score term and early return — no
`FILTER_*` or `TERM_*` id exists yet — and adding them necessarily changes
`source_registry_sha256`. `ENVELOPE_CONTRACT` is the §4 envelope *field shape* only: there is no
event schema, reason-code schema, or canonicalization contract here.

Two spec rules shape this module:

- **§5** the registries are code-owned and prose is a projection of them, never the authority.
  So the registries live here as data, and any document is generated from `render_prose()`.
- **§5.4** *"A drift checker fails when a source fingerprint moves or changes without a registry
  update."* That checker is `check_drift()`, and every way it can fail is exercised by
  `--self-test` before it is trusted.

- **§4** the packet envelope is a machine-verifiable structure, so it is code here
  (`ENVELOPE_CONTRACT`, `check_envelope()`), not a JSON example in a document.

**Subject identity is exact, never a prefix (§4).** Instrumenting the neighbouring resident
`fff6669b…` does not satisfy this task, so that SHA is rejected by name.

**What increment 1 does NOT do.** It freezes identity and binds source spans. It captures no turn,
emits no packet and reads no game state — rollout steps 2 onward. `check_envelope()` validates the
*shape and trust claims* of an envelope handed to it; nothing yet produces one.

**A hazard this file exists to prevent:** the subject defines `bank_candidates` **twice**
(lines 371 and 947). Binding a site by function name alone silently anchors whichever the lookup
happens to reach. Every site therefore pins `start_line` and the checker verifies the function
name found *at that line*.

Run:
    python3 claude_1/decision_packet/registry.py --freeze     # write the frozen registry
    python3 claude_1/decision_packet/registry.py --check      # drift check against the subject
    python3 claude_1/decision_packet/registry.py --self-test  # every failure mode must fail
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUBJECT_PATH = "cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs"
SUBJECT_SHA256 = ("98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29")
#: The neighbouring resident `rust/src/bin/yamo_orchard_live.rs`, verified by `sha256sum`
#: 2026-08-15. Explicitly NOT a valid subject (§4): "instrumenting a neighbouring resident
#: (`fff6669b`) does not satisfy this task". Held at full length — a truncated constant compared
#: with `startswith` would also match unrelated files sharing the prefix.
FORBIDDEN_SUBJECT_SHA256 = "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"
FROZEN_PATH = "claude_1/decision_packet/source-registry-frozen.json"

SCHEMA = "troll-farm-decision-packet/v1"

#: Carried into the frozen artifact so the label cannot be lost when the JSON is read without
#: this file. `codex_1` review 2026-08-15: relabel increment 1 and keep acceptance item 1 open.
STATUS = "PARTIAL_FOUNDATION"
STATUS_NOTE = (
    "Rollout step 1 INCOMPLETE and acceptance item 1 OPEN. This is a versioned partial source "
    "registry, not a frozen one: no FILTER_*/TERM_* sub-function ids exist, so adding the "
    "required sites will change source_registry_sha256. ENVELOPE_CONTRACT is the §4 field shape "
    "only, not the packet/event schema."
)

#: What `validate_registry()` does NOT catch. Reproduced by execution 2026-08-15, not conceded
#: on argument: relabelling GEN_FRUIT_CANDIDATES's intent HARVEST_FRUIT -> MINE_IRON yields 0
#: failures, and deleting three sites outright yields 0 failures. Both are wrong-at-freeze
#: errors, and both are invisible to every check in this module.
SEMANTIC_GAPS = [
    "A site may name a VALID but WRONG stage or intent; nothing here checks that the mapping "
    "describes what the function actually does.",
    "A required site may be OMITTED; expected coverage is derived from SITES itself, so the "
    "registry cannot notice its own holes. Drift only catches removal AFTER a freeze.",
    "A site_id may not describe its function's semantics; the id is not checked against the code.",
    "Closing these needs an independently curated required-site inventory, NOT a comparison "
    "against the same SITES list used to build the registry.",
]

HEX40 = re.compile(r"\A[0-9a-f]{40}\Z")
HEX64 = re.compile(r"\A[0-9a-f]{64}\Z")

# --- §5.1 stage registry -----------------------------------------------------------------
STAGES = ["STATE_RECONCILE", "OPENING_INITIALIZE", "TRAIN_DEADLINE", "MODE_SELECT",
          "CANDIDATE_GENERATE", "FORCED_REPLACEMENT", "PAIR_SELECT", "GREEDY_SELECT",
          "MOVE_RESOLVE", "COMMITMENT_UPDATE", "EMIT", "EXECUTE"]

# --- §5.2 intent registry ----------------------------------------------------------------
# `status` is OBSERVED | HYPOTHESIZED | OWNER_RATIFIED. Nothing here is OWNER_RATIFIED: the
# spec is explicit that these names are not an owner-ratified priority hierarchy, and the
# owner's goal-hierarchy doctrine (D3) is still a draft awaiting correction.
#
# §5.2 also requires `source_sites`, `completion_predicate`, `progress_predicate` and
# `invalidation_predicate` on every entry.
#
# - `source_sites` is DERIVED from the site registry at build time (`attach_intent_sites`),
#   never hand-written, so it cannot disagree with the sites.
# - The three predicates are present and explicitly `null` with
#   `predicate_status: "UNSPECIFIED"`. **They are unspecified because I have not yet read them
#   out of the subject, not because the subject lacks them.** Writing a plausible predicate here
#   would be exactly the transcript-inference this task exists to replace — a packet would then
#   "confirm" a predicate I invented. They are filled in rollout step 2+, each against the code.
#   `validate_registry()` requires the keys to exist; the prose projection reports how many are
#   still unspecified so the gap is visible rather than quiet.
INTENTS = [
    {"intent_id": "WAIT", "human_label": "hold position", "status": "OBSERVED"},
    {"intent_id": "BANK", "human_label": "deposit carried goods at a door", "status": "OBSERVED"},
    {"intent_id": "EQUIP_FOR_TRAIN", "human_label": "gather the training cost", "status": "OBSERVED"},
    {"intent_id": "CLEAR_SHACK_FOR_TRAIN", "human_label": "vacate the shack cell to train", "status": "OBSERVED"},
    {"intent_id": "HARVEST_FRUIT", "human_label": "take fruit from a tree", "status": "OBSERVED"},
    {"intent_id": "MINE_IRON", "human_label": "mine iron", "status": "OBSERVED"},
    {"intent_id": "CHOP_WOOD", "human_label": "chop a tree for wood", "status": "OBSERVED"},
    {"intent_id": "DENY_FOCUS_SPECIES", "human_label": "deny the opponent the focus species", "status": "HYPOTHESIZED"},
    {"intent_id": "REGENERATE_CARRIED_FRUIT", "human_label": "replant carried fruit to regrow it", "status": "OBSERVED"},
    {"intent_id": "CONVERT_BANKED_FRUIT", "human_label": "convert banked fruit at end of game", "status": "HYPOTHESIZED"},
    {"intent_id": "COMMIT_CURRENT_CHOP", "human_label": "continue an in-progress chop", "status": "OBSERVED"},
    {"intent_id": "IDLE_HARVEST", "human_label": "harvest opportunistically while idle", "status": "OBSERVED"},
    {"intent_id": "UNBLOCK_UNIQUE_DOOR", "human_label": "clear the only shack door", "status": "OBSERVED"},
]

# --- §5.3 priority-class registry --------------------------------------------------------
# Explicit metadata, never inferred from numeric magnitude. All HYPOTHESIZED until the owner
# ratifies an ordering: a packet must never turn "score 7000" into "higher intention" (§5.3).
PRIORITY_CLASSES = [
    {"class_id": "FORCED", "rank_hint": 0, "status": "HYPOTHESIZED",
     "note": "structurally forced replacement; not chosen by score"},
    {"class_id": "COMMITMENT", "rank_hint": 1, "status": "HYPOTHESIZED",
     "note": "honours a persistent commitment made on an earlier turn"},
    {"class_id": "ECONOMIC", "rank_hint": 2, "status": "HYPOTHESIZED",
     "note": "ordinary score-ranked production or banking"},
    {"class_id": "FALLBACK", "rank_hint": 3, "status": "HYPOTHESIZED",
     "note": "emitted when nothing else qualifies"},
]

# --- §5.4 source-site registry -----------------------------------------------------------
# Each entry pins the exact start line at the subject SHA. `end_line` and `fingerprint` are
# DERIVED at freeze time, never hand-written, so they cannot silently disagree with the file.
SITES = [
    {"site_id": "STATE_RECONCILE_REGENERATION", "fn": "reconcile_regeneration_commitments",
     "start_line": 1094, "stage": "STATE_RECONCILE", "intent": "REGENERATE_CARRIED_FRUIT"},
    {"site_id": "OPENING_ENSURE", "fn": "ensure_opening",
     "start_line": 796, "stage": "OPENING_INITIALIZE", "intent": "EQUIP_FOR_TRAIN"},
    {"site_id": "TRAIN_DEADLINE_ENFORCE", "fn": "enforce_training_deadline",
     "start_line": 914, "stage": "TRAIN_DEADLINE", "intent": "EQUIP_FOR_TRAIN"},
    {"site_id": "MODE_CHOOSE_SECOND_TROLL", "fn": "choose_second_troll",
     "start_line": 865, "stage": "MODE_SELECT", "intent": "EQUIP_FOR_TRAIN"},
    {"site_id": "GEN_MAIN_CANDIDATES", "fn": "main_candidates",
     "start_line": 1167, "stage": "CANDIDATE_GENERATE", "intent": None},
    {"site_id": "GEN_CHOP_CANDIDATES", "fn": "chop_candidates",
     "start_line": 582, "stage": "CANDIDATE_GENERATE", "intent": "CHOP_WOOD"},
    {"site_id": "GEN_YAMO_CHOP_CANDIDATES", "fn": "yamo_chop_candidates",
     "start_line": 1128, "stage": "CANDIDATE_GENERATE", "intent": "CHOP_WOOD"},
    {"site_id": "GEN_FRUIT_CANDIDATES", "fn": "fruit_candidates",
     "start_line": 463, "stage": "CANDIDATE_GENERATE", "intent": "HARVEST_FRUIT"},
    {"site_id": "GEN_IRON_CANDIDATES", "fn": "iron_candidates",
     "start_line": 485, "stage": "CANDIDATE_GENERATE", "intent": "MINE_IRON"},
    {"site_id": "GEN_EARLY_CANDIDATES", "fn": "early_candidates",
     "start_line": 432, "stage": "CANDIDATE_GENERATE", "intent": "EQUIP_FOR_TRAIN"},
    # NOTE: two functions are named `bank_candidates` (371 and 947). Both are registered
    # separately and keyed by line, which is the whole reason `start_line` is authoritative.
    {"site_id": "GEN_BANK_CANDIDATES_FREE", "fn": "bank_candidates",
     "start_line": 371, "stage": "CANDIDATE_GENERATE", "intent": "BANK"},
    {"site_id": "GEN_BANK_CANDIDATES_YAMO", "fn": "bank_candidates",
     "start_line": 947, "stage": "CANDIDATE_GENERATE", "intent": "BANK"},
    {"site_id": "GEN_WAIT", "fn": "wait",
     "start_line": 638, "stage": "CANDIDATE_GENERATE", "intent": "WAIT"},
    {"site_id": "FORCED_UNIQUE_DOOR_CLEAR", "fn": "force_unique_door_clear",
     "start_line": 978, "stage": "FORCED_REPLACEMENT", "intent": "UNBLOCK_UNIQUE_DOOR"},
    {"site_id": "PAIR_COMPATIBLE", "fn": "compatible",
     "start_line": 643, "stage": "PAIR_SELECT", "intent": None},
    {"site_id": "PAIR_STOCK_COMPATIBLE", "fn": "stock_compatible",
     "start_line": 659, "stage": "PAIR_SELECT", "intent": None},
    {"site_id": "PAIR_SELECT_ARBITRATE", "fn": "select",
     "start_line": 665, "stage": "PAIR_SELECT", "intent": None},
    {"site_id": "REWRITE_MOVE_CONFLICTS", "fn": "resolve_move_conflicts",
     "start_line": 720, "stage": "MOVE_RESOLVE", "intent": None},
    {"site_id": "REWRITE_MOVE_CONFLICTS_PRIORITY", "fn": "resolve_move_conflicts_with_priority",
     "start_line": 723, "stage": "MOVE_RESOLVE", "intent": None},
    {"site_id": "REWRITE_MOVE_CONFLICTS_FORBIDDEN",
     "fn": "resolve_move_conflicts_with_priority_and_forbidden",
     "start_line": 726, "stage": "MOVE_RESOLVE", "intent": None},
    {"site_id": "COMMIT_REMEMBER_REGENERATION", "fn": "remember_selected_regeneration",
     "start_line": 1112, "stage": "COMMITMENT_UPDATE", "intent": "REGENERATE_CARRIED_FRUIT"},
    {"site_id": "EMIT_MAIN", "fn": "main",
     "start_line": 1458, "stage": "EMIT", "intent": None},
]

FN_RE = re.compile(r"^\s*(pub )?fn ([a-z_0-9]+)")

# --- §4 identity and trust envelope -------------------------------------------------------
# The envelope is machine-verifiable, so its contract is code. `check_envelope()` is the checker.
ENVELOPE_CONTRACT = {
    "top": ["schema", "packet_id", "subject", "input"],
    "subject": ["path", "sha256", "instrumentation_sha256", "tool_commit",
                "source_registry_sha256"],
    "input": ["map_sha256", "state_sha256", "turn", "seat", "source", "source_ref", "trust"],
}
INPUT_SOURCES = ["literal_fixture", "recorded_game", "manual_state"]

#: §4: "A packet must say PROVISIONAL_EXECUTION or EXECUTION_UNAVAILABLE until the referee is
#: accepted." The referee is NOT accepted for this purpose, so `ACCEPTED_EXECUTION` is a
#: recognised value that is refused rather than an unknown one — the distinction matters,
#: because refusing it as "unknown" would silently start passing the day someone adds it.
TRUST_ALLOWED = ["SOURCE_EXACT", "PROVISIONAL_EXECUTION", "EXECUTION_UNAVAILABLE"]
TRUST_WITHHELD = ["ACCEPTED_EXECUTION"]

#: §4's JSON example lists the trust enum as `SOURCE_EXACT|PROVISIONAL_EXECUTION|
#: ACCEPTED_EXECUTION`, while §4's prose requires `PROVISIONAL_EXECUTION or
#: EXECUTION_UNAVAILABLE` until the referee is accepted — so `EXECUTION_UNAVAILABLE` appears in
#: the prose but not the enum. I implement the prose (the binding sentence) and raise the
#: discrepancy for the conformance reviewer rather than choosing silently.
#: Every failure this module can report. `--self-test` asserts that each one is OBSERVED firing,
#: so a check that becomes unreachable fails the suite instead of quietly passing forever. This is
#: the project's standing guards rule applied to the guard itself.
FAILURE_TYPES = [
    # check_drift
    "FORBIDDEN_SUBJECT", "SUBJECT_SHA_MISMATCH", "SITE_MISSING", "SITE_MOVED",
    "SPAN_CHANGED", "FINGERPRINT_CHANGED", "UNREGISTERED_SITE",
    # validate_registry
    "DUPLICATE_SITE_ID", "SITE_DECLARATION_MISMATCH", "UNKNOWN_STAGE", "UNKNOWN_INTENT",
    "UNKNOWN_INTENT_STATUS",
    # check_envelope
    "ENVELOPE_NOT_OBJECT", "ENVELOPE_FIELD_MISSING", "SCHEMA_MISMATCH",
    "SUBJECT_SHA_NOT_EXACT", "TOOL_COMMIT_NOT_EXACT", "REGISTRY_SHA_MISMATCH",
    "TRUST_OVERSTATED", "UNKNOWN_TRUST", "UNKNOWN_INPUT_SOURCE",
]

SPEC_DISCREPANCIES = [
    "§4 example enum omits EXECUTION_UNAVAILABLE, which §4 prose requires; implemented the prose.",
]


def subject_lines(text=None):
    if text is None:
        with open(os.path.join(REPO, SUBJECT_PATH), encoding="utf-8") as fh:
            text = fh.read()
    return text.split("\n")


def fn_starts(lines):
    out = []
    for i, line in enumerate(lines, start=1):
        m = FN_RE.match(line)
        if m:
            out.append((i, m.group(2)))
    return out


def normalize(block):
    """Whitespace-insensitive fingerprint input: indentation churn is not semantic drift."""
    return "\n".join(" ".join(l.split()) for l in block)


def signature_of(lines, start):
    """§5.4 'expected input/output shape', DERIVED from the subject's own fn signature.

    Every signature in the subject opens on one line and ends at the first `{`. Taking the text
    rather than hand-writing a shape means the registry cannot describe a signature the file does
    not have; a signature edit moves the fingerprint too, so drift catches it either way.
    """
    text = lines[start - 1]
    return " ".join(text.split("{", 1)[0].split())


def derive(lines):
    """Derive end_line + fingerprint for every site from the file itself."""
    starts = fn_starts(lines)
    start_lines = [i for i, _ in starts]
    name_at = dict(starts)
    derived = []
    for site in SITES:
        s = site["start_line"]
        after = [x for x in start_lines if x > s]
        end = (after[0] - 1) if after else len(lines)
        block = lines[s - 1:end]
        derived.append({
            **site,
            "path": SUBJECT_PATH,
            "end_line": end,
            "line_count": end - s + 1,
            "fn_at_start_line": name_at.get(s),
            "io_shape": signature_of(lines, s) if s <= len(lines) else None,
            "fingerprint": hashlib.sha256(normalize(block).encode()).hexdigest(),
        })
    return derived


def attach_intent_sites(intents, sites):
    """§5.2 `source_sites`, DERIVED from the site registry so the two cannot disagree.

    The predicate keys are materialised here as explicit `null`s: the spec requires the fields,
    and an absent key and an honestly-empty one are different claims.
    """
    by_intent = {}
    for s in sites:
        if s["intent"]:
            by_intent.setdefault(s["intent"], []).append(s["site_id"])
    out = []
    for entry in intents:
        out.append({
            **entry,
            "source_sites": sorted(by_intent.get(entry["intent_id"], [])),
            "completion_predicate": None,
            "progress_predicate": None,
            "invalidation_predicate": None,
            "predicate_status": "UNSPECIFIED",
        })
    return out


def validate_registry(lines, sites=None):
    """Freeze-time validation. Returns typed failures; empty means the registry is internally sound.

    This exists because **drift checking alone cannot catch a registry that was wrong from the
    start.** `derive()` builds the frozen copy and the current copy the same way, so a site
    pinned to the wrong line freezes the wrong span and every later drift check agrees with it
    forever. These checks compare the registry against the *subject*, not against itself.
    """
    sites = derive(lines) if sites is None else sites
    failures = []
    seen = set()
    stages = set(STAGES)
    intents = {i["intent_id"] for i in INTENTS}

    for s in sites:
        if s["site_id"] in seen:
            failures.append({"type": "DUPLICATE_SITE_ID", "site_id": s["site_id"],
                             "detail": "site_id registered more than once"})
        seen.add(s["site_id"])
        if s["fn_at_start_line"] != s["fn"]:
            failures.append({"type": "SITE_DECLARATION_MISMATCH", "site_id": s["site_id"],
                             "detail": f"line {s['start_line']} declares "
                                       f"{s['fn_at_start_line']!r}, registry says {s['fn']!r}"})
        if s["stage"] not in stages:
            failures.append({"type": "UNKNOWN_STAGE", "site_id": s["site_id"],
                             "detail": f"stage {s['stage']!r} is not in the stage registry"})
        if s["intent"] is not None and s["intent"] not in intents:
            failures.append({"type": "UNKNOWN_INTENT", "site_id": s["site_id"],
                             "detail": f"intent {s['intent']!r} is not in the intent registry"})

    for entry in INTENTS:
        if entry["status"] not in ("OBSERVED", "HYPOTHESIZED", "OWNER_RATIFIED"):
            failures.append({"type": "UNKNOWN_INTENT_STATUS", "site_id": entry["intent_id"],
                            "detail": f"status {entry['status']!r} is not a §5.2 status"})
    return failures


def check_envelope(env, frozen=None):
    """§4 envelope checker. Returns typed failures; empty means the envelope is well-formed."""
    failures = []

    def miss(where, keys, obj):
        for k in keys:
            if k not in obj:
                failures.append({"type": "ENVELOPE_FIELD_MISSING", "site_id": f"{where}.{k}",
                                 "detail": "required by §4"})

    if not isinstance(env, dict):
        return [{"type": "ENVELOPE_NOT_OBJECT", "detail": f"got {type(env).__name__}"}]
    miss("", ENVELOPE_CONTRACT["top"], env)
    subject = env.get("subject") or {}
    inp = env.get("input") or {}
    miss("subject", ENVELOPE_CONTRACT["subject"], subject)
    miss("input", ENVELOPE_CONTRACT["input"], inp)

    if env.get("schema") != SCHEMA:
        failures.append({"type": "SCHEMA_MISMATCH",
                         "detail": f"expected {SCHEMA!r}, got {env.get('schema')!r}"})

    sha = subject.get("sha256")
    if sha is not None:
        if not HEX64.match(str(sha)):
            # §4: "The subject SHA is exact, never a prefix." An abbreviated SHA is the
            # single most likely way this rule gets broken, so it is refused by shape.
            failures.append({"type": "SUBJECT_SHA_NOT_EXACT",
                             "detail": f"{sha!r} is not 64 lowercase hex characters"})
        elif sha == FORBIDDEN_SUBJECT_SHA256:
            failures.append({"type": "FORBIDDEN_SUBJECT",
                             "detail": "subject is the neighbouring resident fff6669b…; §4 forbids it"})
        elif sha != SUBJECT_SHA256:
            failures.append({"type": "SUBJECT_SHA_MISMATCH",
                             "detail": f"expected {SUBJECT_SHA256[:16]}…, got {str(sha)[:16]}…"})

    tc = subject.get("tool_commit")
    if tc is not None and not HEX40.match(str(tc)):
        failures.append({"type": "TOOL_COMMIT_NOT_EXACT",
                         "detail": f"{tc!r} is not a 40-hex commit"})

    if frozen is not None and "source_registry_sha256" in subject:
        if subject["source_registry_sha256"] != frozen["source_registry_sha256"]:
            failures.append({"type": "REGISTRY_SHA_MISMATCH",
                             "detail": "envelope does not bind the frozen source registry"})

    trust = inp.get("trust")
    if trust in TRUST_WITHHELD:
        failures.append({"type": "TRUST_OVERSTATED",
                         "detail": f"{trust} is not permitted until the referee is accepted (§4)"})
    elif trust is not None and trust not in TRUST_ALLOWED:
        failures.append({"type": "UNKNOWN_TRUST", "detail": f"{trust!r} is not a §4 trust value"})

    src = inp.get("source")
    if src is not None and src not in INPUT_SOURCES:
        failures.append({"type": "UNKNOWN_INPUT_SOURCE", "detail": f"{src!r} is not a §4 source"})

    return failures


def build(lines=None):
    lines = subject_lines() if lines is None else lines
    sites = derive(lines)
    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "status_note": STATUS_NOTE,
        "semantic_gaps": SEMANTIC_GAPS,
        "subject": {"path": SUBJECT_PATH, "sha256": SUBJECT_SHA256,
                    # Recorded so the registry's own incompleteness is a number in the artifact,
                    # not something a reader has to go and measure.
                    "fn_definitions": len(fn_starts(lines))},
        "stages": STAGES,
        "intents": attach_intent_sites(INTENTS, sites),
        "priority_classes": PRIORITY_CLASSES,
        "envelope_contract": ENVELOPE_CONTRACT,
        "trust_allowed": TRUST_ALLOWED,
        "trust_withheld": TRUST_WITHHELD,
        "spec_discrepancies": SPEC_DISCREPANCIES,
        "sites": sites,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["source_registry_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return payload


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def check_drift(frozen, subject_text=None, subject_sha=None):
    """§5.4 drift checker. Returns a list of typed failures; empty means no drift."""
    failures = []
    actual_sha = (subject_sha if subject_sha is not None
                  else sha256_file(os.path.join(REPO, SUBJECT_PATH)))

    if actual_sha.startswith(FORBIDDEN_SUBJECT_SHA256):
        failures.append({"type": "FORBIDDEN_SUBJECT",
                         "detail": "subject is the neighbouring resident fff6669b…; §4 forbids it"})
    if actual_sha != frozen["subject"]["sha256"]:
        failures.append({"type": "SUBJECT_SHA_MISMATCH",
                         "detail": f"expected {frozen['subject']['sha256'][:16]}…, found {actual_sha[:16]}…"})
        return failures  # every span below is meaningless against a different file

    lines = subject_lines(subject_text)
    current = {s["site_id"]: s for s in derive(lines)}
    frozen_sites = {s["site_id"]: s for s in frozen["sites"]}

    for site_id, was in frozen_sites.items():
        now = current.get(site_id)
        if now is None:
            failures.append({"type": "SITE_MISSING", "site_id": site_id,
                             "detail": "registered site absent from the registry build"})
            continue
        if now["fn_at_start_line"] != was["fn"]:
            failures.append({"type": "SITE_MOVED", "site_id": site_id,
                             "detail": f"line {was['start_line']} holds "
                                       f"{now['fn_at_start_line']!r}, expected {was['fn']!r}"})
            continue
        if now["end_line"] != was["end_line"]:
            failures.append({"type": "SPAN_CHANGED", "site_id": site_id,
                             "detail": f"span {was['start_line']}-{was['end_line']} became "
                                       f"{now['start_line']}-{now['end_line']}"})
        if now["fingerprint"] != was["fingerprint"]:
            failures.append({"type": "FINGERPRINT_CHANGED", "site_id": site_id,
                             "detail": f"body changed at {was['start_line']}-{was['end_line']}"})

    registered = set(frozen_sites)
    for site_id in current:
        if site_id not in registered:
            failures.append({"type": "UNREGISTERED_SITE", "site_id": site_id,
                             "detail": "site built but not present in the frozen registry"})

    # A sound frozen registry is not enough: the registry must still describe the subject.
    failures.extend(validate_registry(lines))
    return failures


def render_prose(reg):
    """Prose is a PROJECTION of the registry (§5.4), never the authority."""
    out = [f"# Decision Packet source registry (generated — do not edit)", "",
           f"> **STATUS: `{reg['status']}`.** {reg['status_note']}", "",
           f"- schema: `{reg['schema']}`",
           f"- subject: `{reg['subject']['path']}`",
           f"- subject sha256: `{reg['subject']['sha256']}`",
           f"- source_registry_sha256: `{reg['source_registry_sha256']}`",
           f"- stages: {len(reg['stages'])} · intents: {len(reg['intents'])} · "
           f"priority classes: {len(reg['priority_classes'])} · sites: {len(reg['sites'])}",
           ""]

    unspec = [i["intent_id"] for i in reg["intents"] if i["predicate_status"] == "UNSPECIFIED"]
    nositz = [i["intent_id"] for i in reg["intents"] if not i["source_sites"]]
    out += ["## Known gaps at this increment", "",
            f"- **{len(unspec)} of {len(reg['intents'])} intents carry no completion / progress / "
            f"invalidation predicate yet** — the §5.2 fields are present and explicitly null. "
            f"They are read out of the subject in rollout step 2+, never inferred here: "
            f"{', '.join(f'`{i}`' for i in unspec) or 'none'}.",
            f"- **The site registry is NOT yet §5.4-complete, and this increment does not claim "
            f"it is.** {len(reg['sites'])} sites are pinned against "
            f"{reg['subject']['fn_definitions']} function definitions in the subject. §5.4 also "
            f"requires ids for every *filter*, *score term* and *early return*; no `FILTER_*` or "
            f"`TERM_*` id exists yet, because those are sub-function spans and this increment "
            f"pins whole functions only. They arrive with rollout steps 2–3. What is frozen is "
            f"exact; it is not complete.",
            f"- **{len(nositz)} intents have no source site bound**: "
            f"{', '.join(f'`{i}`' for i in nositz) or 'none'}. An intent with no site is a name "
            f"with nothing behind it, and is listed rather than dropped.",
            ""]
    out += ["## What the drift guard and validator CANNOT catch", "",
            "Reproduced by execution, not conceded on argument:", ""]
    out += [f"- {g}" for g in reg["semantic_gaps"]] + [""]

    if reg.get("spec_discrepancies"):
        out += ["## Spec discrepancies raised, not resolved silently", ""]
        out += [f"- {d}" for d in reg["spec_discrepancies"]] + [""]

    out += ["## Source sites", "",
            "| site_id | stage | intent | lines | io_shape | fingerprint |",
            "|---|---|---|---|---|---|"]
    for s in sorted(reg["sites"], key=lambda x: x["start_line"]):
        out.append(f"| `{s['site_id']}` | {s['stage']} | {s['intent'] or '—'} | "
                   f"{s['start_line']}–{s['end_line']} | `{s['io_shape']}` | "
                   f"`{s['fingerprint'][:12]}…` |")
    return "\n".join(out) + "\n"


def _self_test():
    """Every way the checker can fail must be demonstrated failing (guards standing rule)."""
    frozen = build()
    lines = subject_lines()
    cases = []
    observed = set()

    def record(label, found, expect):
        """`found` is the checker's real output, so coverage is measured, not declared."""
        observed.update(x["type"] for x in found)
        passed = (not found) if expect == "no failures" else any(x["type"] == expect
                                                                for x in found)
        cases.append((label, passed, expect))

    record("baseline (unmodified subject)", check_drift(frozen), "no failures")
    record("wrong subject SHA", check_drift(frozen, subject_sha="0" * 64),
           "SUBJECT_SHA_MISMATCH")
    record("neighbouring resident fff6669b as subject",
           check_drift(frozen, subject_sha=FORBIDDEN_SUBJECT_SHA256), "FORBIDDEN_SUBJECT")

    # body edit inside a registered span -> fingerprint changes, span does not
    mutated = list(lines)
    mutated[1094] = mutated[1094] + " // MUTANT"
    record("edited body inside a registered span",
           check_drift(frozen, subject_text="\n".join(mutated)), "FINGERPRINT_CHANGED")

    # A line inserted ABOVE every site shifts each pinned start line onto other code.
    moved = list(lines)
    moved.insert(300, "    // inserted line shifts everything below")
    record("inserted line shifts registered sites",
           check_drift(frozen, subject_text="\n".join(moved)), "SITE_MOVED")

    # SPAN_CHANGED needs a site whose fn name still sits at its pinned line but whose body grew.
    # Appending inside the LAST registered span (EMIT_MAIN, which runs to end-of-file) moves
    # end_line without moving any start line — otherwise SITE_MOVED masks it and SPAN_CHANGED
    # would never be seen on its own.
    grown = list(lines) + ["// appended past the end of the final registered span"]
    record("body grows without moving any start line",
           check_drift(frozen, subject_text="\n".join(grown)), "SPAN_CHANGED")

    # a registered site vanishing from the frozen set -> UNREGISTERED_SITE
    trimmed = json.loads(json.dumps(frozen))
    dropped = trimmed["sites"].pop()
    record(f"site {dropped['site_id']} dropped from the registry", check_drift(trimmed),
           "UNREGISTERED_SITE")

    # a frozen site the current build no longer produces -> SITE_MISSING.
    # Without this control SITE_MISSING would be a branch that never executes, which this
    # project has already shipped once and does not intend to ship again.
    extra = json.loads(json.dumps(frozen))
    extra["sites"].append({**extra["sites"][0], "site_id": "GHOST_SITE_NOT_IN_CODE"})
    record("frozen site absent from the current build", check_drift(extra), "SITE_MISSING")

    # --- validate_registry: the checks drift alone cannot make ---------------------------
    # These mutate the module-level SITES, because a registry that was wrong at freeze time is
    # exactly what drift checking cannot see.
    def with_sites(mutated_sites, expect_type, label):
        original = globals()["SITES"]
        globals()["SITES"] = mutated_sites
        try:
            found = validate_registry(lines)
        finally:
            globals()["SITES"] = original
        record(label, found, expect_type)

    base = json.loads(json.dumps(SITES))
    record("baseline registry validates against the subject", validate_registry(lines),
           "no failures")

    wrong_line = json.loads(json.dumps(base))
    wrong_line[0]["start_line"] = base[0]["start_line"] + 3
    with_sites(wrong_line, "SITE_DECLARATION_MISMATCH",
               "site pinned to a line that declares nothing")

    dupe = json.loads(json.dumps(base)) + [json.loads(json.dumps(base[0]))]
    with_sites(dupe, "DUPLICATE_SITE_ID", "same site_id registered twice")

    bad_stage = json.loads(json.dumps(base))
    bad_stage[0]["stage"] = "NOT_A_STAGE"
    with_sites(bad_stage, "UNKNOWN_STAGE", "site names a stage outside the registry")

    bad_intent = json.loads(json.dumps(base))
    bad_intent[0]["intent"] = "NOT_AN_INTENT"
    with_sites(bad_intent, "UNKNOWN_INTENT", "site names an intent outside the registry")

    original_intents = globals()["INTENTS"]
    globals()["INTENTS"] = [{**original_intents[0], "status": "PROBABLY_FINE"}] + \
        list(original_intents[1:])
    try:
        record("intent carries a status outside the §5.2 set", validate_registry(lines),
               "UNKNOWN_INTENT_STATUS")
    finally:
        globals()["INTENTS"] = original_intents

    # --- §4 envelope ---------------------------------------------------------------------
    def good_envelope():
        return {
            "schema": SCHEMA,
            "packet_id": "sha256:" + "0" * 64,
            "subject": {"path": SUBJECT_PATH, "sha256": SUBJECT_SHA256,
                        "instrumentation_sha256": "0" * 64, "tool_commit": "0" * 40,
                        "source_registry_sha256": frozen["source_registry_sha256"]},
            "input": {"map_sha256": "0" * 64, "state_sha256": "0" * 64, "turn": 17, "seat": 0,
                      "source": "literal_fixture", "source_ref": "fixture:m110-s1",
                      "trust": "EXECUTION_UNAVAILABLE"},
        }

    def env_case(label, expect, mutate):
        env = good_envelope()
        mutate(env)
        record(label, check_envelope(env, frozen), expect)

    record("baseline envelope is accepted", check_envelope(good_envelope(), frozen),
           "no failures")
    record("envelope that is not an object", check_envelope("nope"), "ENVELOPE_NOT_OBJECT")
    env_case("required field removed", "ENVELOPE_FIELD_MISSING",
             lambda e: e["input"].pop("state_sha256"))
    env_case("wrong schema string", "SCHEMA_MISMATCH",
             lambda e: e.update(schema="troll-farm-decision-packet/v2"))
    env_case("abbreviated subject SHA (a prefix, §4 forbids)", "SUBJECT_SHA_NOT_EXACT",
             lambda e: e["subject"].update(sha256=SUBJECT_SHA256[:12]))
    env_case("neighbouring resident fff6669b as envelope subject", "FORBIDDEN_SUBJECT",
             lambda e: e["subject"].update(sha256=FORBIDDEN_SUBJECT_SHA256))
    env_case("some other file as subject", "SUBJECT_SHA_MISMATCH",
             lambda e: e["subject"].update(sha256="1" * 64))
    env_case("tool_commit that is not a 40-hex commit", "TOOL_COMMIT_NOT_EXACT",
             lambda e: e["subject"].update(tool_commit="HEAD"))
    env_case("envelope binding a different source registry", "REGISTRY_SHA_MISMATCH",
             lambda e: e["subject"].update(source_registry_sha256="2" * 64))
    env_case("claims ACCEPTED_EXECUTION before the referee is accepted", "TRUST_OVERSTATED",
             lambda e: e["input"].update(trust="ACCEPTED_EXECUTION"))
    env_case("unrecognised trust value", "UNKNOWN_TRUST",
             lambda e: e["input"].update(trust="TOTALLY_FINE"))
    env_case("unrecognised input source", "UNKNOWN_INPUT_SOURCE",
             lambda e: e["input"].update(source="vibes"))

    allok = True
    for label, passed, expect in cases:
        print(f"  {'OK  ' if passed else 'BAD '} {label:58} -> expected {expect}")
        allok = allok and passed

    # Coverage is measured from what the checkers actually emitted, not from the case labels.
    unfired = [t for t in FAILURE_TYPES if t not in observed]
    unknown = sorted(observed - set(FAILURE_TYPES))
    print()
    print(f"  {'OK  ' if not unfired else 'BAD '} every declared failure type observed firing"
          f" ({len(FAILURE_TYPES) - len(unfired)}/{len(FAILURE_TYPES)})")
    if unfired:
        print(f"       never fired: {', '.join(unfired)}")
    if unknown:
        print(f"  BAD  emitted but undeclared: {', '.join(unknown)}")
    allok = allok and not unfired and not unknown

    print(f"\nself-test: {len(cases)} cases —", "PASS — every failure mode fires" if allok
          else "FAIL — a check cannot fail and is therefore not a check")
    return 0 if allok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--freeze", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--prose")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    if args.freeze:
        reg = build()
        path = os.path.join(REPO, FROZEN_PATH)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(reg, fh, indent=1, sort_keys=True)
            fh.write("\n")
        print(f"froze {len(reg['sites'])} sites; source_registry_sha256 = "
              f"{reg['source_registry_sha256']}")
        if args.prose:
            with open(os.path.join(REPO, args.prose), "w", encoding="utf-8") as fh:
                fh.write(render_prose(reg))
            print(f"wrote prose projection {args.prose}")
        return 0

    if args.check:
        with open(os.path.join(REPO, FROZEN_PATH), encoding="utf-8") as fh:
            frozen = json.load(fh)
        failures = check_drift(frozen)
        for f in failures:
            print(f"  DRIFT {f['type']}: {f.get('site_id','-')} — {f['detail']}")
        print(f"\ndrift check: {'PASS — no drift' if not failures else f'FAIL — {len(failures)} finding(s)'}")
        return 0 if not failures else 2

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
