#!/usr/bin/env python3
"""Controls K0-K5 for the real-game dance attribution.

Definitions of record: `claude_1/dance1/definitions-g1-r3-2026-08-24.md` §3, accepted by codex_1
`20260824T172730Z`.  A vacuous pass is a failure: every control reports the number it fired on,
and `PASS` prints only when every control fired.

K0 is not in the definitions and is not a substitute for one: it is the self-check the definitions'
F7 paragraph implies -- the re-stated `progress_event` must report NO progress event on every
transition strictly inside every window `detect_d1` emitted.  If it disagreed with the detector's
own closure, every F7 label would be measured against a different rule than the windows were.
"""

from __future__ import annotations

import glob
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in (HERE, REPO / "claude_1" / "adapter1", REPO / "claude_1" / "banana-restoration-r2",
           REPO / "claude_1" / "narrate1", REPO):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import dance_facts as df                                      # noqa: E402
import replay_to_trace as rt                                  # noqa: E402
import trace_detectors as td                                  # noqa: E402

#: the frozen library copy carrying the 38 D-1 episodes the definitions name
FROZEN_LIBRARY = REPO / "claude_1" / "banana-restoration-r2" / "oscillation-library-98628e98" / "library"

#: K3's positive fixtures: the MANUFACTURED / swap rows of the idleness adjudication
IDLE_ADJUDICATION = REPO / "claude_1" / "narrate2" / "results" / "idle-adjudication-2026-08-23.json"

#: K3's negative corpus: the tracked replays, our pre-cure lineage, both seats
RAW_GAMES = REPO / "data" / "raw" / "games"
OLD_LINEAGE_AGENTS = (6536563, 6536359)


# --------------------------------------------------------------------------

def k0_progress_agreement(rows_by_game):
    """Re-stated `progress_event` vs the detector's own closure, inside every emitted window."""
    checked = 0
    disagreements = []
    for (game, seat), (tr, episodes) in rows_by_game.items():
        for ep in episodes:
            uid, t0, t1 = ep["unit"], ep["turn_start"], ep["turn_end"]
            for t in range(t0, t1):
                checked += 1
                if df.progress_event(tr, uid, t):
                    disagreements.append({"game": game, "seat": seat, "unit": uid, "turn": t})
    return {
        "control": "K0 progress() agreement with detect_d1",
        "transitions_checked": checked,
        "disagreements": disagreements[:20],
        "disagreement_count": len(disagreements),
        "fired": checked > 0,
        "passed": checked > 0 and not disagreements,
    }


def k1_identity(batch1_counts, expected=(22, 17, 0, 0)):
    """Batch 1 must reproduce D-1 22 episodes / 17 games, D-2 0, D-3 0, exactly."""
    got = (batch1_counts["d1"], batch1_counts["d1_games"],
           batch1_counts["d2"], batch1_counts["d3"])
    return {
        "control": "K1 batch-1 detector identity",
        "expected": {"d1": expected[0], "d1_games": expected[1],
                     "d2": expected[2], "d3": expected[3]},
        "observed": {"d1": got[0], "d1_games": got[1], "d2": got[2], "d3": got[3]},
        "fired": True,
        "passed": got == expected,
    }


def k2_mechanism_reproduction():
    """`mech` over the frozen library's D-1 episodes vs the frozen `classify` label.

    Telemetry may not enter this control at any point.  The library transcripts carry none, and
    `mech` is a function of the frozen `all_own_peers_at_entry` / `blocker` records alone -- the
    exact output shape of the imported `measure_blocker`.  The assertion below is that no frozen
    situation carries any telemetry field, so a telemetry-bearing class could not have rescued a
    mechanism mismatch even in principle.
    """
    files = sorted(glob.glob(str(FROZEN_LIBRARY / "OSC-*.json")))
    rows, mismatches, episodes = [], [], 0
    telemetry_keys_seen = []
    for path in files:
        doc = json.loads(Path(path).read_text())
        if doc["kind"] != "D1_EPISODE":
            continue
        cls = doc["classification"]
        for key in ("narrate", "telemetry", "intent", "chosen", "available"):
            if key in cls or key in doc:
                telemetry_keys_seen.append((doc["id"], key))
        peers = cls["all_own_peers_at_entry"]
        blocker = cls["blocker"]
        m = df.mech(blocker, peers)
        legacy = df.MECH_TO_LEGACY[m]
        frozen = cls["mechanism"]
        n = doc["multiplicity"]["episodes"]
        episodes += n
        row = {"id": doc["id"], "episodes": n, "mech": m,
               "crosswalk": legacy, "frozen": frozen,
               "deciding_field": _deciding_field(blocker, peers)}
        rows.append(row)
        if legacy != frozen:
            mismatches.append(row)
    return {
        "control": "K2 mechanism-layer reproduction of the frozen classifier",
        "library": str(FROZEN_LIBRARY.relative_to(REPO)),
        "situations": len(rows),
        "episodes": episodes,
        "telemetry_fields_present_in_library": telemetry_keys_seen,
        "mismatches": mismatches,
        "mismatch_count": len(mismatches),
        "rows": rows,
        "fired": episodes > 0,
        "passed": episodes > 0 and not mismatches and not telemetry_keys_seen,
    }


def _deciding_field(blocker, peers):
    if not peers:
        return "peers empty"
    if blocker is None:
        return "peers non-empty, blocker None"
    return ("blocker idle=%s plant=%s"
            % (blocker["idle_by_analysis_criterion"],
               blocker["plant_on_cell_at_entry"] is not None))


def k3_negative():
    """K3's negative side, run BEFORE anything is graded so the class 3 name is fixed blind.

    Scans the tracked replays under `data/raw/games/` for our pre-cure lineage on either seat and
    reports every swap tick the F5 predicate finds.  Also reports, per tick, a NEW diagnostic that
    enters no predicate and no class: whether BOTH units carried a `MOVE` command onto each
    other's cell on that turn (`command_pair`), which is the shape a resolver-issued exchange
    would take, against ticks with no such command pair, which is the shape a coincidental
    exchange of two adjacent units would take.  It is published as a fact for the owner, not as a
    reading of intent -- neither shape proves what the transport level meant.
    """
    games_with_ticks, scanned, refusals = [], 0, []
    ticks_total = pair_commanded = 0
    for path in sorted(glob.glob(str(RAW_GAMES / "*.json"))):
        game = json.loads(Path(path).read_text())
        for agent in game.get("agents") or []:
            if agent.get("agentId") not in OLD_LINEAGE_AGENTS:
                continue
            try:
                tr, _meta = rt.adapt_to_trace(game, agent_id=agent["agentId"])
            except rt.AdapterError as exc:
                refusals.append({"game": game.get("gameId"), "reason": str(exc)})
                continue
            scanned += 1
            ticks = df.swap_ticks_whole_trace(tr)
            if not ticks:
                continue
            commanded = 0
            for tick in ticks:
                a, b = tick["pair"]
                ca, cb = tr.cmd_of(a, tick["turn"]), tr.cmd_of(b, tick["turn"])
                pa, pb = tr.pos(a, tick["turn"]), tr.pos(b, tick["turn"])
                if (ca is not None and cb is not None
                        and ca.verb == "MOVE" and cb.verb == "MOVE"
                        and tuple(ca.args[0]) == pb and tuple(cb.args[0]) == pa):
                    commanded += 1
                    tick["command_pair"] = True
                else:
                    tick["command_pair"] = False
            ticks_total += len(ticks)
            pair_commanded += commanded
            games_with_ticks.append({"game": game.get("gameId"), "agent": agent["agentId"],
                                     "tick_count": len(ticks),
                                     "ticks_with_command_pair": commanded,
                                     "ticks": ticks[:5]})
    return {
        "pairs_scanned": scanned,
        "adapter_refusals": refusals,
        "games_with_ticks": len(games_with_ticks),
        "ticks_total": ticks_total,
        "ticks_with_move_command_pair": pair_commanded,
        "clean": ticks_total == 0,
        "detail": games_with_ticks[:20],
    }


def k3_swap_detector(batch1_traces, negative):
    """Positive: fire on the 9 MANUFACTURED / swap rows.  Negative: `k3_negative`, already run.

    The premise of the negative side is weaker than the card implies: `docs/RULES-LEDGER.md` R-1
    records "today's resident never generates them, which is self-imposed" as of 2026-08-16 --
    a statement about that date's resident, not a verified property of these replays.  So the
    negative side is a JOINT test of detector and premise.  Any non-zero negative result prevents
    the causal name `SWAP_FLAP`; the definitions pre-commit the class to the descriptive name
    `POSITIONAL_EXCHANGE` in that case, and the panel applies that rename before it grades.
    """
    adj = json.loads(IDLE_ADJUDICATION.read_text())
    fixtures = [r for r in adj["rows"] if r["verdict"] == "MANUFACTURED"]
    hits, misses = [], []
    for row in fixtures:
        found = None
        for (game, seat), (tr, _eps) in batch1_traces.items():
            if game != row["game"]:
                continue
            for tick in df.swap_ticks_whole_trace(tr):
                if row["unit"] in tick["pair"] and abs(tick["turn"] - row["turn"]) <= 1:
                    found = {"turn": tick["turn"], "pair": tick["pair"], "seat": seat}
                    break
            if found:
                break
        entry = {"row": {k: row[k] for k in ("game", "turn", "unit")}, "tick": found}
        (hits if found else misses).append(entry)
    causal_name_permitted = bool(negative["clean"])
    return {
        "control": "K3 swap-tick detector",
        "positive_fixtures": len(fixtures),
        "positive_hits": len(hits),
        "positive_misses": [m["row"] for m in misses],
        "hits": hits,
        "negative": negative,
        "negative_side_clean": negative["clean"],
        "causal_name_permitted": causal_name_permitted,
        "class_3_name_in_force": df.SWAP_CLASS,
        "consequence_applied": (
            "none needed: the negative side was silent, so class 3 keeps the causal name SWAP_FLAP"
            if causal_name_permitted else
            "class 3 renamed to POSITIONAL_EXCHANGE and graded under that name, per the "
            "definitions' pre-committed remedy; the causal reading is withdrawn, not footnoted"),
        "premise_note": ("the negative side is a joint test of detector and the R-1 premise; a "
                         "non-zero result names both as in doubt and does not pick the "
                         "convenient one"),
        "fired": len(fixtures) > 0 and negative["pairs_scanned"] > 0,
        "passed": (len(fixtures) > 0 and not misses and negative["pairs_scanned"] > 0
                   and df.SWAP_CLASS == ("SWAP_FLAP" if causal_name_permitted
                                         else "POSITIONAL_EXCHANGE")),
    }


def k4_telemetry_decode(decode_report):
    """The v2 panel's decode over batches 1-2 and the v3 decode over batch 3, both accounted.

    The v3 grammar is IMPORTED from `run_gp3_parity.decode` under a recorded source SHA-256
    rather than copied, so "prove equivalence before using it" is discharged by identity.
    """
    import narrate3_decode as n3
    digest, ok = n3.imported_grammar_identity()
    total = sum(b["games"] for b in decode_report)
    refused = sum(b["refused"] for b in decode_report)
    return {
        "control": "K4 telemetry decode",
        "v3_grammar_source_sha256": digest,
        "v3_grammar_matches_reviewed": ok,
        "v3_grammar_provenance": "imported from claude_1/narrate3/run_gp3_parity.py:decode",
        "batches": decode_report,
        "games": total,
        "refused_games": refused,
        "fired": total > 0,
        "passed": ok and total > 0,
    }


def k5_exhaustiveness(batches):
    """Per batch: classes sum to the DETECTOR's episode count, refusals included in that sum."""
    rows = []
    ok = True
    for b in batches:
        classes_total = sum(b["classes"].values())
        identity = classes_total == b["detector_episodes"]
        ok = ok and identity
        rows.append({
            "batch": b["batch"],
            "detector_episodes": b["detector_episodes"],
            "classified_episodes": classes_total,
            "telemetry_refused_episodes": b.get("telemetry_refused_episodes", 0),
            "classes_total_equals_detector_total": identity,
        })
    return {
        "control": "K5 exhaustiveness and refusal accounting",
        "rows": rows,
        "fired": bool(rows),
        "passed": bool(rows) and ok,
    }
