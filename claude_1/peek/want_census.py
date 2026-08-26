#!/usr/bin/env python3
r"""PEEK follow-on card — the WANT census on the CHAMPION, over the 989 peek encounters.

Card: `coordination/messages/local_claude_1/20260823T055832Z-20260822-peek-planner-target-map-policy.md`

> re-run this classification on the **champion**, over the **989 peek encounters** rather than
> the benching set: for each encounter, the partner's own best candidate at that tick and its
> destination, classified against the contested square. Read-only, probe only, no candidate edit.
> If a meaningful population of "wanted a different square" exists there, displacement has a
> target after all and this ruling reopens on that evidence.

## The two artifacts joined, and why the join is exact

- The **encounter set** is frozen: the 989 `peek_rows` of
  `claude_1/peek/g1-sweep-rev3-2026-08-22.json`, one row per partner encounter the rev-3 seam
  saw, carrying `(turn, m, u, landing, mover_target, u_cmd)`.
- The **candidate lists** come from a fresh champion run through
  `claude_1/peek/probe-champion-picker.rs`.

Those are two different binaries, so the join needs a licence. It has one: rev 3 measured
**0 fires over 12,981 unit-turns and 34/34 fixtures byte-identical to the base**, and the base is
the champion (`547fa706…`) — so the rev-3 run and the champion run are the same game, tick for
tick, and `(fixture, turn, unit)` addresses the same world in both. This runner does not take
that on trust: it re-checks whole-stream identity between the champion and the rev-3 candidate
per fixture, and refuses the fixture if they differ.

## The classification, and the geometry warning that goes with it

For each encounter the partner is `u`, and **the contested square is `landing`, which is `u`'s own
current cell** — the seam only reaches the partner block when an own unit stands on the mover's
landing. So on this case set:

    NO_WANT               u's candidate list held nothing but WAIT — genuinely nothing to do.
    WANT_NOT_A_MOVE       u's best real candidate is not a MOVE: stay on the contested square
                          and work. Displacing interrupts real work.
    WANT_MOVE_TO_OWN_CELL u's best real candidate is a MOVE whose destination is the contested
                          square itself. Degenerate; reported so it cannot hide in a bucket.
    WANT_MOVE_ELSEWHERE   u's best real candidate is a MOVE to some OTHER square. This is the
                          class the card says would reopen the ruling.

**This is NOT the same predicate as the coordinator's 235-class, and the difference is
geometric, not a matter of degree.** On the benching case set the reference square was the square
the *winning partner* was taking, so "same square" meant contention between two units' wants.
Here the reference square is the standing troll's *own cell*, so any MOVE want is by construction
"a different square". The honest reading of `WANT_MOVE_ELSEWHERE` on this set is therefore "the
standing troll was not wedded to the square being contested", which is the thing displacement
would need — not "two trolls wanted the same third square". A `WANT_MOVE_ELSEWHERE` count here
must not be compared numerically to the 0 of the benching set.

Two further breakdowns are reported because they are what a rev-4 predicate would actually key on:
`want_dest == mover_target` (u wants where the mover is going — head-on contention) and
`selector_chose` vs the emitted `u_cmd` (whether the WAIT was issued by the *selector* or
manufactured later by the *resolver*; the two are different facts about intent).

## Gates, all fail-closed

1. champion digest `547fa706…`; probe built by `make_champion_picker_probe.py`.
2. per fixture, probe stream == plain champion stream (`coverage.check_parity`).
3. per fixture, champion stream == rev-3 candidate stream (the join licence).
4. one `PS1TURN` block per observed turn, no gaps, no duplicates.
5. the join must be TOTAL: every one of the encounter rows must find its turn block and find
   `u` in that block's candidate map. A partial join is a refusal, not a smaller N.
6. anti-inertness: the classifier is exercised on constructed records that must produce all four
   labels, and the corpus must actually offer MOVE candidates. A census whose discriminating
   branch is unreachable reports nothing, however clean its zeros look.

Run:  python3 claude_1/peek/want_census.py [--only OSC-005,OSC-027] [--out PATH]
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/hstarve1", "claude_1/banana-restoration-r2",
          "claude_1/pipeline", "claude_1/picker1"):
    sys.path.insert(0, str(REPO / p))
import coverage as C            # noqa: E402
import fixture_harness as H     # noqa: E402
import fuzz_panel as fp         # noqa: E402
import regression_tests as rt   # noqa: E402
import semantic_harness as sh   # noqa: E402
import probe as PK              # noqa: E402  -- parse()/chosen_for(), the Phase-1 reader

CHAMPION = REPO / "cgauto/submissions/candidate-door1-pure-deletion.rs"
CHAMPION_SHA = "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0"
REV3 = REPO / "cgauto/submissions/candidate-swap-r1-rev3.rs"
PROBE = HERE / "probe-champion-picker.rs"
SWEEP = HERE / "g1-sweep-rev3-2026-08-22.json"
OUT = HERE / "want-census-champion-2026-08-23.json"

CLASSES = ["NO_WANT", "WANT_NOT_A_MOVE", "WANT_MOVE_TO_OWN_CELL", "WANT_MOVE_ELSEWHERE"]


class CensusError(Exception):
    """Anything that would make a number mean something other than it says."""


def move_dest(cmd: str):
    """`MOVE <id> <x> <y>` -> (x, y); anything else -> None. Mirrors the bot's move_command."""
    fields = cmd.split()
    if len(fields) != 4 or fields[0].upper() != "MOVE":
        return None
    try:
        return (int(fields[2]), int(fields[3]))
    except ValueError:
        return None


def best_want(cands):
    """u's own best REAL candidate: highest score among non-WAIT, ties to the first enumerated.

    Ties go to the lower index because that is what the selector's strict `score > best_score`
    does: the first pair enumerated keeps the crown. Reading a tie the other way would name a
    want the selector would never have reached.
    """
    real = [c for c in cands if c["cmd"] != "WAIT"]
    if not real:
        return None
    return min(real, key=lambda c: (-c["score"], c["idx"]))


def classify(want, contested):
    if want is None:
        return "NO_WANT"
    dest = move_dest(want["cmd"])
    if dest is None:
        return "WANT_NOT_A_MOVE"
    return "WANT_MOVE_TO_OWN_CELL" if dest == contested else "WANT_MOVE_ELSEWHERE"


# --------------------------------------------------------------------------------------
# GATE 6a — the classifier's four branches, exercised on constructed records.
#
# The rev-3 gate failed on anti-inertness and this census is a smaller instrument of the same
# family, so the discriminating branch is proven reachable BEFORE any corpus number is printed.
def control_classifier():
    contested = (4, 2)
    cases = [
        ([{"idx": 0, "score": 0.0, "cmd": "WAIT"}], "NO_WANT"),
        ([{"idx": 0, "score": 0.0, "cmd": "WAIT"},
          {"idx": 1, "score": 1.0, "cmd": "CHOP 3"}], "WANT_NOT_A_MOVE"),
        ([{"idx": 0, "score": 0.0, "cmd": "WAIT"},
          {"idx": 1, "score": 1.0, "cmd": "MOVE 3 4 2"}], "WANT_MOVE_TO_OWN_CELL"),
        ([{"idx": 0, "score": 0.0, "cmd": "WAIT"},
          {"idx": 1, "score": 1.0, "cmd": "MOVE 3 9 9"}], "WANT_MOVE_ELSEWHERE"),
        # a tie must go to the lower index, so the CHOP at idx 1 wins over the MOVE at idx 2
        ([{"idx": 0, "score": 0.0, "cmd": "WAIT"},
          {"idx": 1, "score": 2.0, "cmd": "CHOP 3"},
          {"idx": 2, "score": 2.0, "cmd": "MOVE 3 9 9"}], "WANT_NOT_A_MOVE"),
        # and a strictly better MOVE must beat a CHOP, so score really is read
        ([{"idx": 0, "score": 0.0, "cmd": "WAIT"},
          {"idx": 1, "score": 2.0, "cmd": "CHOP 3"},
          {"idx": 2, "score": 3.0, "cmd": "MOVE 3 9 9"}], "WANT_MOVE_ELSEWHERE"),
    ]
    got = [classify(best_want(cands), contested) for cands, _ in cases]
    want = [expect for _, expect in cases]
    if got != want:
        raise CensusError(f"CLASSIFIER CONTROL FAILED: {got} != {want}")
    if set(want) != set(CLASSES):
        raise CensusError("CLASSIFIER CONTROL is not exhaustive: it does not exercise "
                          f"{sorted(set(CLASSES) - set(want))}")
    return {"cases": len(cases), "labels_exercised": sorted(set(want)), "result": "PASS"}


# --------------------------------------------------------------------------------------
# GATE 6c — the PERMUTATION control on `want_dest == mover_target`.
#
# If that equality comes out at 100%, the number is either a real finding about contention or an
# artifact of a join in which every encounter of a fixture shares one target, where the equality
# would hold for ANY pairing and would mean nothing. So the same comparison is run against a
# DELIBERATELY WRONG pairing: each MOVE want is compared to the mover_target of the NEXT
# encounter in the same fixture, cyclically. A shifted rate near the true rate means the equality
# is structural and carries no information; a shifted rate well below it means the true pairing
# is doing the work.
def permutation_control(results):
    true_hits = shifted_hits = considered = 0
    per_fixture = []
    for r in results:
        rows = [row for row in r["rows"] if row["want_dest"] is not None]
        if len(rows) < 2:
            continue
        t = sum(1 for row in rows if row["want_dest"] == row["mover_target"])
        sft = sum(1 for i, row in enumerate(rows)
                  if row["want_dest"] == rows[(i + 1) % len(rows)]["mover_target"])
        true_hits += t
        shifted_hits += sft
        considered += len(rows)
        per_fixture.append({"fixture": r["fixture"], "move_wants": len(rows),
                            "true_matches": t, "shifted_matches": sft,
                            "distinct_mover_targets": len({tuple(row["mover_target"])
                                                           for row in rows})})
    return {
        "move_wants_considered": considered,
        "true_pairing_matches": true_hits,
        "shifted_pairing_matches": shifted_hits,
        "true_rate": (true_hits / considered) if considered else None,
        "shifted_rate": (shifted_hits / considered) if considered else None,
        "reading": ("the equality is INFORMATIVE — a wrong pairing scores materially lower"
                    if considered and shifted_hits < true_hits else
                    "the equality is STRUCTURAL — a wrong pairing scores as well, so "
                    "'want_dest == mover_target' carries no information on this case set"),
        "per_fixture": per_fixture,
    }


def run_fixture(sit, cfg, plain_bin, probe_bin, rev3_bin, encounters):
    err = C.check_parity(sit, cfg, plain_bin, probe_bin)          # gate 2

    spec = H.spec_for(sit, cfg)
    turns = int(cfg["turns"])
    _, champ_cmds = rt.run_binary_custom(plain_bin, fp.make_referee(spec), turns)
    _, rev3_cmds = rt.run_binary_custom(rev3_bin, fp.make_referee(spec), turns)
    if champ_cmds.strip() != rev3_cmds.strip():                    # gate 3 — the join licence
        raise CensusError(
            f"{sit['id']}: the champion and the rev-3 candidate DIVERGE. The frozen peek "
            f"encounters were recorded in a different game from the one measured here, so no "
            f"(turn, unit) join is valid. Nothing is emitted for this fixture.")

    recs = PK.parse(err)
    seen = collections.Counter(r["turn"] for r in recs)
    dupes = sorted(t for t, n in seen.items() if n > 1)
    if dupes:                                                       # gate 4
        raise CensusError(f"{sit['id']}: DUPLICATE PS1TURN blocks at {dupes[:5]} — select() ran "
                          f"more than once per turn and every per-turn number would double-count.")
    lo, hi = min(seen), max(seen)
    missing = [t for t in range(lo, hi + 1) if t not in seen]
    if missing:
        raise CensusError(f"{sit['id']}: MISSING PS1TURN blocks at {missing[:5]} "
                          f"({len(missing)} of {hi - lo + 1}) — a gap makes any rate wrong.")
    byturn = {r["turn"]: r for r in recs}

    move_cands = sum(1 for r in recs for cl in r["cands"].values()
                     for c in cl if move_dest(c["cmd"]) is not None)
    all_cands = sum(len(cl) for r in recs for cl in r["cands"].values())

    rows, classes = [], collections.Counter()
    for enc in encounters:
        t, u = enc["turn"], enc["u"]
        rec = byturn.get(t)
        if rec is None:                                             # gate 5
            raise CensusError(f"{sit['id']} turn {t}: encounter has no PS1TURN block. The join "
                              f"is partial; a partial join is a refusal, not a smaller N.")
        cands = rec["cands"].get(u)
        if not cands:
            raise CensusError(f"{sit['id']} turn {t}: partner {u} has no candidate list in the "
                              f"selector's own rows. The join is partial.")
        contested = tuple(enc["landing"])
        want = best_want(cands)
        cls = classify(want, contested)
        classes[cls] += 1
        chosen = PK.chosen_for(rec, u)
        dest = move_dest(want["cmd"]) if want else None
        rows.append({
            "turn": t, "m": enc["m"], "u": u,
            "contested_square": list(contested),
            "mover_target": enc["mover_target"],
            "emitted_u_cmd": enc["u_cmd"],
            "selector_chose": None if chosen is None else chosen["cmd"],
            "wait_manufactured_by_resolver": (
                enc["u_cmd"] == "WAIT" and chosen is not None and chosen["cmd"] != "WAIT"),
            "n_candidates": len(cands),
            "n_real_candidates": sum(1 for c in cands if c["cmd"] != "WAIT"),
            "want_cmd": None if want is None else want["cmd"],
            "want_score": None if want is None else want["score"],
            "want_target": None if want is None else want["target"],
            "want_dest": None if dest is None else list(dest),
            "want_dest_is_mover_target": dest is not None and list(dest) == enc["mover_target"],
            "class": cls,
        })
    return {
        "fixture": sit["id"], "kind": sit["kind"],
        "parity": "PASS", "join_licence": "champion stream == rev-3 stream",
        "turn_blocks": len(recs), "turn_range": [lo, hi],
        "encounters": len(encounters),
        "classes": {k: classes.get(k, 0) for k in CLASSES},
        "candidates_offered_all_units": all_cands,
        "move_candidates_offered_all_units": move_cands,
        "rows": rows,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args(argv)

    import hashlib
    got = hashlib.sha256(CHAMPION.read_bytes()).hexdigest()
    if got != CHAMPION_SHA:                                          # gate 1
        raise CensusError(f"REFUSING: champion digest differs, want {CHAMPION_SHA}, got {got}")

    control = control_classifier()                                   # gate 6a
    print(f"  classifier control: {control['result']} "
          f"({control['cases']} constructed cases, all four labels reached)")

    sweep = json.loads(SWEEP.read_text())
    enc_by_fixture = {row["id"]: row["peek_rows"] for row in sweep["rows"]}
    total_frozen = sum(len(v) for v in enc_by_fixture.values())
    wanted = args.only.split(",") if args.only else sorted(enc_by_fixture)

    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations(wanted)

    results = []
    with tempfile.TemporaryDirectory(prefix="peek-want-") as wd:
        wd = Path(wd)
        bins = {}
        for name, src in (("champ", CHAMPION), ("probe", PROBE), ("rev3", REV3)):
            bins[name] = wd / f"{name}.bin"
            sh.compile_text(src.read_text(), bins[name], crate=f"want_{name}")
        for sit in sits:
            r = run_fixture(sit, cfg, bins["champ"], bins["probe"], bins["rev3"],
                            enc_by_fixture[sit["id"]])
            results.append(r)
            print(f"  {r['fixture']}: {r['encounters']} encounters  {r['classes']}")

    totals = collections.Counter()
    for r in results:
        totals.update(r["classes"])
    n = sum(totals.values())
    move_offered = sum(r["move_candidates_offered_all_units"] for r in results)
    if move_offered == 0:                                            # gate 6b
        raise CensusError("ANTI-INERTNESS: the corpus offered ZERO MOVE candidates to any unit "
                          "on any turn, so the MOVE branches of the classification could not "
                          "have fired whatever the trolls intended. The census is uninformative "
                          "and no class count is reported.")
    elsewhere = [row for r in results for row in r["rows"] if row["class"] == "WANT_MOVE_ELSEWHERE"]
    perm = permutation_control(results)                              # gate 6c
    manufactured = sum(1 for r in results for row in r["rows"]
                       if row["wait_manufactured_by_resolver"])
    head_on = sum(1 for r in results for row in r["rows"] if row["want_dest_is_mover_target"])

    verdict = {
        "task": "20260822-peek-planner-target-map",
        "step": "champion want census over the frozen peek encounters (probe only)",
        "card": ("coordination/messages/local_claude_1/"
                 "20260823T055832Z-20260822-peek-planner-target-map-policy.md"),
        "subject": str(CHAMPION.relative_to(REPO)), "subject_sha256": CHAMPION_SHA,
        "probe": str(PROBE.relative_to(REPO)),
        "encounter_source": str(SWEEP.relative_to(REPO)),
        "encounters_frozen": total_frozen,
        "encounters_joined": n,
        "join_total": n == total_frozen if not args.only else None,
        "gates": {
            "champion_digest": "PASS",
            "probe_parity_per_fixture": "PASS",
            "champion_equals_rev3_stream_per_fixture": "PASS",
            "turn_block_coverage": "PASS",
            "join_totality": "PASS",
            "classifier_control": control,
            "corpus_offers_move_candidates": move_offered,
            "permutation_control": perm,
        },
        "classes": {k: totals.get(k, 0) for k in CLASSES},
        "want_dest_is_mover_target": head_on,
        "waits_manufactured_by_resolver_not_selector": manufactured,
        "reopen_criterion": {
            "text": ("the card reopens the ruling if a meaningful population of "
                     "'wanted a different square' exists on the champion"),
            # The card's "wanted a different square" is the coordinator's class, and on the
            # benching set its reference square was the square the OTHER troll was taking. The
            # faithful translation to this geometry is therefore a MOVE want that is neither the
            # contested square NOR the mover's own destination — a genuine THIRD square, the one
            # shape displacement could serve. That, and not `want_move_elsewhere`, is the number
            # the ruling turns on.
            "want_third_square": len([row for row in elsewhere
                                      if not row["want_dest_is_mover_target"]]),
            "want_move_elsewhere": len(elsewhere),
            "want_move_to_the_movers_own_destination": len(
                [row for row in elsewhere if row["want_dest_is_mover_target"]]),
            "geometry_caveat": (
                "on this case set the contested square IS the partner's own cell, so any MOVE "
                "want is 'a different square' by construction. This count is NOT comparable to "
                "the benching set's 0."),
        },
        "fixtures": results,
    }
    Path(args.out).write_text(json.dumps(verdict, indent=2) + "\n")
    print(f"\n  encounters joined: {n}/{total_frozen}")
    print(f"  classes: {dict(verdict['classes'])}")
    print(f"  want_dest == mover_target: {head_on}")
    print(f"  REOPEN CLASS (a genuine THIRD square): "
          f"{len([row for row in elsewhere if not row['want_dest_is_mover_target']])}")
    print(f"  WAITs manufactured by the resolver, not the selector: {manufactured}")
    print(f"  MOVE candidates offered corpus-wide (liveness): {move_offered}")
    print(f"  permutation control: true {perm['true_pairing_matches']}/"
          f"{perm['move_wants_considered']} vs shifted {perm['shifted_pairing_matches']}/"
          f"{perm['move_wants_considered']} — {perm['reading']}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
