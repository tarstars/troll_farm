#!/usr/bin/env python3
r"""G1 idleness on the NARRATE join — classify every own unit on every turn.

Card: `local_claude_1` `20260823T110000Z`.  G1 names three problems; dancing and contention are
graded off replays, idleness is not, because a replay cannot distinguish a troll that wanted
nothing from a troll that wanted something and was overruled.  The join separates them -- as far
as the grammar allows, which is a boundary this module states rather than papers over.

## The classification, fixed BEFORE any count was looked at

Two primitives, both observable without judgement:

- **want** -- `intent_kind != NONE`.  The telemetry records the target of the candidate that
  `select_recording` CHOSE.
- **commanded** -- the join carries a command verb for that unit on that turn.  A bare `WAIT` line
  carries no unit id, so every unit on such a turn is uncommanded; those rows are the heart of the
  question and are never dropped as missing data.
- **turn_silent** -- no own unit on that turn carries a command, i.e. the emitted line was a bare
  `WAIT`.  It separates "the whole team stood still" from "a sibling was commanded and this unit
  was not".

Six classes, exhaustive and disjoint:

    NO_WANT_SILENT_TEAM      no want, no command, whole team silent
    NO_WANT_SILENT_PARTIAL   no want, no command, a sibling was commanded
    NO_WANT_COMMANDED        no want, a command was issued for this unit
    WANT_COMMANDED           a real want, a command was issued for this unit
    WANT_SILENT_TEAM         a real want, no command, whole team silent
    WANT_SILENT_PARTIAL      a real want, no command, a sibling was commanded

**"Wanted something real, achieved nothing" = WANT_SILENT_TEAM + WANT_SILENT_PARTIAL.**

## What is deliberately NOT defined here

There is no `serves the want` / `does not serve the want` split inside `WANT_COMMANDED`.  Defining
"serves" would mean choosing, for each (target kind, verb) pair, whether it counts -- and every
honest way to do that on this corpus reads the observed joint table first.  A boundary chosen with
the counts in view is not a measurement (the card says so, and it is right).  The full
(intent_kind x verb) joint table is reported instead, with no judgement imposed on it, so a reader
can apply their own rule and see exactly what it costs.

## The instrument's own boundary, which bounds the answer

`NARRATE v2` records `narrate_chosen` -- the target of the candidate that WON selection.  A unit
whose real want lost to `WAIT` (score, or pair incompatibility in the two-unit product loop)
records `NONE`, and is indistinguishable in this telemetry from a unit that had nothing to want.
So **the class where idleness-with-a-discarded-want would hide is exactly `NO_WANT_*`, and v2
cannot look inside it.**  That is a fact about the grammar, not about the bot, and it is the single
most important qualification on every number below.

Run:  python3 claude_1/narrate2/idle_classify.py --games-dir DIR [--out JSON]
"""
from __future__ import annotations

import argparse, collections, glob, json, os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "narrate1"))
sys.path.insert(0, str(REPO / "claude_1" / "adapter1"))

import narrate_decode as nd                         # noqa: E402

AGENT_ID = 6652424

CLASSES = ("NO_WANT_SILENT_TEAM", "NO_WANT_SILENT_PARTIAL", "NO_WANT_COMMANDED",
           "WANT_COMMANDED", "WANT_SILENT_TEAM", "WANT_SILENT_PARTIAL")
IDLE_CLASSES = ("WANT_SILENT_TEAM", "WANT_SILENT_PARTIAL")


def classify_rows(rows):
    """Annotate each row with its class.  Mutates and returns `rows`."""
    commanded_turns = collections.defaultdict(bool)
    for row in rows:
        if row["command_verb"] is not None:
            commanded_turns[row["turn"]] = True
    for row in rows:
        want = row["intent_kind"] != "NONE"
        commanded = row["command_verb"] is not None
        if commanded:
            row["class"] = "WANT_COMMANDED" if want else "NO_WANT_COMMANDED"
        else:
            silent = not commanded_turns[row["turn"]]
            stem = "WANT" if want else "NO_WANT"
            row["class"] = "%s_SILENT_%s" % (stem, "TEAM" if silent else "PARTIAL")
    return rows


def classify_games(games_dir: Path, agent_id=AGENT_ID):
    counts = collections.Counter()
    joint = collections.Counter()
    idle_rows, divergence_rows = [], []
    games, refused = 0, []
    total_rows = 0
    for path in sorted(glob.glob(str(games_dir / "*.json.gz"))):
        try:
            rows, meta = nd.decode_file(path, agent_id)
        except nd.NarrateError as exc:
            refused.append({"game": os.path.basename(path), "reason": str(exc)})
            continue
        games += 1
        classify_rows(rows)
        total_rows += len(rows)
        for row in rows:
            counts[row["class"]] += 1
            joint[(row["intent_kind"], row["command_verb"] or "(none)")] += 1
            tagged = dict(row, game=meta["game_id"])
            if row["class"] in IDLE_CLASSES:
                idle_rows.append(tagged)
            # The divergence set of the decoder handoff: a real want with no command, or no want
            # with a command.  Reported as its own number, never folded into the idleness headline.
            if (row["intent_kind"] != "NONE") != (row["command_verb"] is not None):
                divergence_rows.append(tagged)
    if sum(counts.values()) != total_rows:
        raise RuntimeError("classes sum to %d over %d rows" % (sum(counts.values()), total_rows))
    return {
        "games": games, "refused": refused, "rows": total_rows,
        "classes": {name: counts.get(name, 0) for name in CLASSES},
        "idle_rows": counts["WANT_SILENT_TEAM"] + counts["WANT_SILENT_PARTIAL"],
        "joint_intent_verb": {"%s|%s" % k: v for k, v in sorted(joint.items(),
                                                                key=lambda kv: -kv[1])},
        "divergence_rows": len(divergence_rows),
        "divergence_detail": divergence_rows,
        "idle_detail": idle_rows,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--games-dir", required=True)
    ap.add_argument("--agent-id", type=int, default=AGENT_ID)
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    result = classify_games(Path(args.games_dir).expanduser(), args.agent_id)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    summary = {k: v for k, v in result.items()
               if k not in ("divergence_detail", "idle_detail", "refused")}
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
