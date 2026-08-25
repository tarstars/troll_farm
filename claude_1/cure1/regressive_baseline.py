#!/usr/bin/env python3
"""G-2 clause (b) — the **v3 baseline for `R`**, reconstructed from positions.

Task: `20260825-dance-cure-candidate-1-hold`, ordered by
`local_claude_1/20260825T103500Z-…-policy.md`:

    "regressive-detour turns per 1,000 turns down by at least half against the v3 read
     (`6652642`) — note: v3 carries no `r=` field, so the v3 baseline for `R` is reconstructed
     from positions (a regressive step = a move that increases BFS distance to the stated
     target); state the method."

This module is the method, and it is published **before the G-2 read exists**, so no number from
the treatment arm can have shaped it.

## The method, stated

For every own unit `u` and every turn `t` of a decoded v3 replay:

  * **eligible** iff the v3 payload's tick-local `chosen` target for `u` at `t` names a cell —
    `BANK(x,y)`, `CELL(x,y)`, `TREE(x,y)`, or `SHACK` resolved to the tent cell `smap.shacks[0]`.
    `NONE` and `ABSENT` are ineligible: there is no stated target to regress from.  The unit must
    also be alive with a known cell at both `t` and `t+1`; the last traced turn has no successor
    and is ineligible.
  * **distance** `d(c) = BFS(walkable, [target])[c]`, falling back to `manhattan(c, target)` when
    `c` is absent from that map.  This is `bfs_distances` from `trace_detectors` — the same
    4-neighbour mirror of `game::nav` the detectors use — and the fallback is the arm's own
    (`toward_goal.get(cell).unwrap_or_else(|| manhattan(cell, target))`, `cure1-hold-v4.rs:891`
    and `:900`).  Seeding BFS at the target reproduces the arm exactly, including a non-walkable
    target such as a tree or the tent: `bfs_distances` seeds the source at 0 unconditionally and
    expands only into walkable cells.
  * **regressive step** iff `d(cell at t+1) > d(cell at t)`, measured against the target stated
    at `t` — the target the move was ordered toward.  A later change of target does not
    retroactively make the step regressive or not.  A unit that does not move cannot be
    regressive: its distance is unchanged.

**Rate.**  The graded denominator is **own troll-turns** — eligible or not, every (own unit, turn)
pair the trace carries — because v4's `r=` is emitted per own unit per turn and the treatment
count will have exactly that denominator.  The per-1,000-*game*-turns rate is reported beside it
so that a quotation of "per 1,000 turns" cannot silently change denominators between the baseline
and the treatment.  Both are printed; the first is the one clause (b) is graded on.

## What this is NOT, and the control that is owed

`R_pos` is an **outcome** measure over positions; v4's `r=R` is a **decision** label emitted by the
resolver (`cure1-hold-v4.rs:916`: a denied mover whose best legal orthogonal detour is strictly
worse than its own cell, and which the hold rule did not hold).  The two populations are not
identical by construction:

  * a `P` (primary) or `L` (lateral) turn can still end farther from the target if the engine's
    own step resolution differs from the projected landing — `R_pos` counts it, `r=R` does not;
  * an `r=R` turn whose ordered detour is rejected by the engine leaves the unit in place —
    `r=R` counts it, `R_pos` does not.

So the comparison clause (b) is graded on is **`R_pos` on the v3 read against `R_pos` on the G-2
read**, one instrument on both sides.  `r=R` from the G-2 read is reported alongside, and the
**crosswalk control** — per-turn agreement between `R_pos` and `r=R` on the G-2 replays, which
carry both — is owed at grading time and cannot be run before the read, because no corpus in hand
carries positions and `r=` together.  I am not claiming agreement now.

    python3 claude_1/cure1/regressive_baseline.py [--games <v3.jsonl.gz>] [--agent 6652642]
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in (REPO / "claude_1" / "dance1", REPO / "claude_1" / "narrate1",
           REPO / "claude_1" / "narrate3", REPO / "claude_1" / "adapter1",
           REPO / "claude_1" / "banana-restoration-r2", REPO / "claude_1" / "pipeline",
           REPO):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import narrate3_decode as n3          # noqa: E402
import replay_to_trace as rt          # noqa: E402
import trace_detectors as td          # noqa: E402

DEFAULT_GAMES = Path("/tmp/claude-1000/cure1/g2base/v3.jsonl.gz")
DEFAULT_AGENT = 6652642
#: SHA-256 of the pinned v3 package (`local_claude_1/narrate/v3/…` @`3256dafb`), the same digest
#: the 08-24 G-2 execution recorded against the shipping manifest.
GAMES_SHA256 = "0116994468cb6d23702511d0cefce28eeaeeb049eb8e7fc24ccdc29b886c3ceb"
OUT = HERE / "results" / "regressive-baseline-v3.json"

CELL_KINDS = ("BANK", "CELL", "TREE")


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def target_cell(text: str, tent):
    """v3 target spelling -> the cell it names, or None when it names none."""
    kind, cell = n3.parse_v3_target(text)
    if kind == "SHACK":
        return tent
    if kind in CELL_KINDS:
        return cell
    return None                      # NONE, ABSENT


def poison_target(turn_rows: dict, uid, tent, shift: int):
    """K-P negative control: the SAME step scored against ANOTHER unit's stated target.

    A measure that reports the same regressive count under a deliberately mislabelled target is
    not measuring the target at all.  The rotation is over the turn's own roster, so the poisoned
    target is always a target some own unit really stated on that turn -- a mislabelling, not a
    random cell.  Falls back to None (the step is skipped) when the turn has one unit or the
    rotated unit stated no cell.
    """
    ids = sorted(turn_rows)
    if len(ids) < 2:
        return None
    other = ids[(ids.index(uid) + shift) % len(ids)]
    if other == uid:
        return None
    return target_cell(turn_rows[other]["chosen"], tent)


def measure_game(game: dict, agent_id: int, poison_shift: int = 0) -> dict:
    """Return the per-game census, or raise `Narrate3Error` / `AdapterError` (refusal)."""
    rows, meta = n3.decode_game(game, agent_id)
    trace, _tmeta = rt.adapt_to_trace(game, agent_id=agent_id)
    walkable = trace.smap.walkable
    tent = trace.tent

    cells = {}                       # (turn, unit) -> cell
    by_turn = collections.defaultdict(dict)
    for row in rows:
        if row["unit_cell"] is not None:
            cells[(row["turn"], row["unit"])] = tuple(row["unit_cell"])
        by_turn[row["turn"]][row["unit"]] = row

    dist_cache = {}
    poisoned = [0]
    fallback_rows = [0]              # K-F: moved-eligible rows where a cell is off the BFS map
    regressive_no_fallback = [0]     # ... and the count restricted to rows that need no fallback

    def distances(target):
        if target not in dist_cache:
            dist_cache[target] = td.bfs_distances(walkable, [target])
        return dist_cache[target]

    troll_turns = len(rows)
    eligible = 0
    regressive = 0
    progressive = 0
    equal = 0
    moved = 0
    per_unit_regressive = collections.Counter()
    per_unit_turns = collections.Counter()
    for row in rows:
        per_unit_turns[row["unit"]] += 1
        t, uid = row["turn"], row["unit"]
        here = cells.get((t, uid))
        there = cells.get((t + 1, uid))
        if here is None or there is None:
            continue
        target = target_cell(row["chosen"], tent)
        if target is None:
            continue
        eligible += 1
        if there != here:
            moved += 1
        dmap = distances(target)
        both_mapped = here in dmap and there in dmap
        if there != here and not both_mapped:
            fallback_rows[0] += 1
        d_here = dmap.get(here, manhattan(here, target))
        d_there = dmap.get(there, manhattan(there, target))
        if there != here and both_mapped and d_there > d_here:
            regressive_no_fallback[0] += 1
        if there == here:
            pass
        elif d_there > d_here:
            regressive += 1
            per_unit_regressive[uid] += 1
        elif d_there < d_here:
            progressive += 1
        else:
            equal += 1
        if poison_shift and there != here:
            other = poison_target(by_turn[t], uid, tent, poison_shift)
            if other is not None:
                pmap = distances(other)
                if pmap.get(there, manhattan(there, other)) > pmap.get(here, manhattan(here, other)):
                    poisoned[0] += 1

    return {
        "game_id": meta["game_id"],
        "seat": meta["seat"],
        "turns": trace.T,
        "troll_turns": troll_turns,
        "eligible_turns": eligible,
        "moved_eligible_turns": moved,
        "regressive_turns": regressive,
        "progressive_turns": progressive,
        "equal_turns": equal,
        "poison_regressive_turns": poisoned[0],
        "fallback_rows": fallback_rows[0],
        "regressive_turns_no_fallback": regressive_no_fallback[0],
        "per_unit_regressive": dict(per_unit_regressive),
        "per_unit_turns": dict(per_unit_turns),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--games", type=Path, default=DEFAULT_GAMES)
    ap.add_argument("--agent", type=int, default=DEFAULT_AGENT)
    ap.add_argument("--expect-sha256", default=GAMES_SHA256,
                    help="'' to skip; the corpus digest is asserted by default")
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--label", default="v3 read (agent 6652642)")
    ap.add_argument("--poison-shift", type=int, default=1,
                    help="K-P negative control: score each step against the target stated by the "
                         "unit this many places along the turn's roster; 0 disables")
    args = ap.parse_args(argv)

    digest = hashlib.sha256(args.games.read_bytes()).hexdigest()
    if args.expect_sha256 and digest != args.expect_sha256:
        raise SystemExit("corpus SHA-256 %s != expected %s; refusing to publish a baseline off "
                         "an unpinned corpus" % (digest, args.expect_sha256))

    grammar_sha, grammar_ok = n3.imported_grammar_identity()
    if not grammar_ok:
        raise SystemExit("imported v3 grammar has source sha256 %s, not the reviewed one"
                         % grammar_sha)

    games, refused = [], []
    opener = gzip.open if args.games.suffix == ".gz" else open
    with opener(args.games, "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            game = json.loads(line)
            try:
                games.append(measure_game(game, args.agent, args.poison_shift))
            except (n3.Narrate3Error, rt.AdapterError) as exc:
                refused.append({"game_id": game.get("gameId"), "reason": str(exc)})

    troll_turns = sum(g["troll_turns"] for g in games)
    game_turns = sum(g["turns"] for g in games)
    eligible = sum(g["eligible_turns"] for g in games)
    moved = sum(g["moved_eligible_turns"] for g in games)
    regressive = sum(g["regressive_turns"] for g in games)
    progressive = sum(g["progressive_turns"] for g in games)
    equal = sum(g["equal_turns"] for g in games)
    poisoned = sum(g["poison_regressive_turns"] for g in games)
    fallback_rows = sum(g["fallback_rows"] for g in games)
    regressive_nf = sum(g["regressive_turns_no_fallback"] for g in games)
    exhaustive = (regressive + progressive + equal) == moved

    per_troll = collections.Counter()
    per_troll_turns = collections.Counter()
    for g in games:
        for uid, n in g["per_unit_regressive"].items():
            per_troll[(g["game_id"], int(uid))] += n
        for uid, n in g["per_unit_turns"].items():
            per_troll_turns[(g["game_id"], int(uid))] += n
    worst = max(per_troll.items(), key=lambda kv: kv[1], default=(None, 0))

    result = {
        "task": "20260825-dance-cure-candidate-1-hold",
        "clause": "G-2 (b) baseline",
        "label": args.label,
        "corpus": {"path": str(args.games), "sha256": digest, "agent_id": args.agent,
                   "games_decoded": len(games), "games_refused": len(refused)},
        "grammar": {"v3_payload_decoder_sha256": grammar_sha, "matches_reviewed": grammar_ok},
        "denominators": {"troll_turns": troll_turns, "game_turns": game_turns,
                         "eligible_troll_turns": eligible,
                         "moved_eligible_troll_turns": moved},
        "regressive_turns": regressive,
        "controls": {
            "K-E exhaustiveness": {
                "moved_eligible_troll_turns": moved,
                "progressive": progressive, "equal": equal, "regressive": regressive,
                "classes_total_equals_moved": exhaustive,
                "result": "PASS" if exhaustive else "FAIL",
            },
            "K-F manhattan fallback": {
                "moved_eligible_rows_needing_the_fallback": fallback_rows,
                "regressive_with_fallback": regressive,
                "regressive_restricted_to_rows_needing_none": regressive_nf,
                "regressive_turns_that_depend_on_it": regressive - regressive_nf,
                "result": "FIRES" if fallback_rows else "INERT",
                "criterion": "reported, not gated: the fallback mirrors the arm's own "
                             "(cure1-hold-v4.rs:891/:900), so it is kept whichever way it fires; "
                             "an inert one would have to be reported as inert rather than "
                             "quoted as if it had been exercised",
            },
            "K-P poison target": {
                "shift": args.poison_shift,
                "regressive_under_mislabelled_target": poisoned,
                "true_regressive": regressive,
                "ratio": round(poisoned / regressive, 3) if regressive else None,
                "result": ("PASS" if args.poison_shift and poisoned > 2 * regressive
                           else "FAIL" if args.poison_shift else "SKIPPED"),
                "criterion": "a mislabelled target must produce strictly more than twice the "
                             "regressive count, or the measure is not reading the target",
            },
        },
        "rate_per_1000_troll_turns": round(1000.0 * regressive / troll_turns, 4)
                                     if troll_turns else None,
        "rate_per_1000_game_turns": round(1000.0 * regressive / game_turns, 4)
                                    if game_turns else None,
        "share_of_eligible_pct": round(100.0 * regressive / eligible, 4) if eligible else None,
        "share_of_moved_eligible_pct": round(100.0 * regressive / moved, 4) if moved else None,
        "graded_denominator": "troll_turns",
        "worst_troll": {"game_id": worst[0][0] if worst[0] else None,
                        "unit": worst[0][1] if worst[0] else None,
                        "regressive_turns": worst[1],
                        "troll_turns": per_troll_turns.get(worst[0], 0) if worst[0] else 0},
        "refusals": refused,
        "per_game": games,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    print("corpus            %s (%d games decoded, %d refused)"
          % (digest[:12], len(games), len(refused)))
    print("troll-turns       %d over %d game turns" % (troll_turns, game_turns))
    print("eligible          %d (moved on %d of them)" % (eligible, moved))
    print("REGRESSIVE        %d turns" % regressive)
    print("  per 1,000 troll-turns  %.4f   <-- GRADED denominator"
          % (1000.0 * regressive / troll_turns if troll_turns else float("nan")))
    print("  per 1,000 game turns   %.4f"
          % (1000.0 * regressive / game_turns if game_turns else float("nan")))
    print("  share of eligible      %.4f %%"
          % (100.0 * regressive / eligible if eligible else float("nan")))
    print("K-E exhaustive    %s (%d progressive + %d equal + %d regressive == %d moved)"
          % ("PASS" if exhaustive else "FAIL", progressive, equal, regressive, moved))
    print("K-P poison target %s (%d regressive under a mislabelled target vs %d true, x%.2f)"
          % ("PASS" if args.poison_shift and poisoned > 2 * regressive else
             "SKIPPED" if not args.poison_shift else "FAIL",
             poisoned, regressive, poisoned / regressive if regressive else float("nan")))
    print("K-F fallback      %s on %d moved-eligible rows; %d of the %d regressive turns depend "
          "on it (%d without)" % ("FIRES" if fallback_rows else "INERT", fallback_rows,
                                  regressive - regressive_nf, regressive, regressive_nf))
    print("worst troll       game %s unit %s: %d of %d turns"
          % (worst[0][0] if worst[0] else "-", worst[0][1] if worst[0] else "-", worst[1],
             per_troll_turns.get(worst[0], 0) if worst[0] else 0))
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
