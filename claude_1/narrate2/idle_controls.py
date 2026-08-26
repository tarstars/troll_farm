#!/usr/bin/env python3
r"""Controls for the G1 idleness classification.  Every class is exercised before any count is
believed, and each control corrupts exactly one guarded thing.

The card's warning is the design brief: a classification whose boundary could quietly absorb the
3,613 null-verb rows in whichever direction makes the headline cleaner is not a measurement.
Controls 1-4 exist to make that absorption visible if it happened.

Run:  python3 claude_1/narrate2/idle_controls.py --games-dir DIR --probe BIN --plain BIN
"""
from __future__ import annotations

import argparse, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "claude_1" / "narrate1"))
sys.path.insert(0, str(REPO / "claude_1" / "adapter1"))

import idle_classify                                # noqa: E402
import narrate_decode as nd                         # noqa: E402
import replay_to_trace as rt                        # noqa: E402

CONTROL_GAME = "900089738.json.gz"


def synthetic():
    """One hand-built turn set that reaches all six classes, so none is believed unexercised."""
    return [
        # turn 1: whole team silent, one unit wants, one does not
        {"turn": 1, "unit": 0, "intent_kind": "TREE", "command_verb": None},
        {"turn": 1, "unit": 1, "intent_kind": "NONE", "command_verb": None},
        # turn 2: sibling commanded -> the silent ones are PARTIAL, not TEAM
        {"turn": 2, "unit": 0, "intent_kind": "TREE", "command_verb": None},
        {"turn": 2, "unit": 1, "intent_kind": "NONE", "command_verb": None},
        {"turn": 2, "unit": 2, "intent_kind": "BANK", "command_verb": "MOVE"},
        # turn 3: a command with no want
        {"turn": 3, "unit": 0, "intent_kind": "NONE", "command_verb": "MOVE"},
    ]


def run(games_dir: Path, probe: Path, plain: Path, corpus: dict):
    results = []

    rows = idle_classify.classify_rows(synthetic())
    got = [row["class"] for row in rows]
    want = ["WANT_SILENT_TEAM", "NO_WANT_SILENT_TEAM", "WANT_SILENT_PARTIAL",
            "NO_WANT_SILENT_PARTIAL", "WANT_COMMANDED", "NO_WANT_COMMANDED"]
    results.append({"control": "1 all six classes are reachable and the classifier assigns each",
                    "fired": got == want, "detail": "%r" % got})

    results.append({
        "control": "2 the TEAM/PARTIAL primitive is live: the same row flips when a sibling is commanded",
        "fired": rows[0]["class"] == "WANT_SILENT_TEAM" and rows[2]["class"] == "WANT_SILENT_PARTIAL",
        "detail": "turn1=%s turn2=%s" % (rows[0]["class"], rows[2]["class"])})

    classes = corpus["classes"]
    results.append({
        "control": "3 the classes are exhaustive and disjoint on the real corpus",
        "fired": sum(classes.values()) == corpus["rows"] == 76305,
        "detail": "sum=%d rows=%d" % (sum(classes.values()), corpus["rows"])})

    empty = [name for name, count in classes.items() if count == 0]
    results.append({
        "control": "4 no class is silently merged away: every class is reported, empty or not",
        "fired": len(classes) == len(idle_classify.CLASSES),
        "detail": "empty classes reported as empty: %r" % empty})

    # 5. the divergence number is its own thing: it must equal the three classes that make it up,
    #    and must NOT include the 3,504 rows that want nothing and do nothing.
    expect = (classes["NO_WANT_COMMANDED"] + classes["WANT_SILENT_TEAM"]
              + classes["WANT_SILENT_PARTIAL"])
    none_none = corpus["joint_intent_verb"].get("NONE|(none)", 0)
    results.append({
        "control": "5 divergence is not folded into idleness and excludes want-nothing-do-nothing",
        "fired": corpus["divergence_rows"] == expect and none_none > 0
        and corpus["divergence_rows"] < none_none,
        "detail": "divergence=%d classes=%d NONE|(none)=%d"
                  % (corpus["divergence_rows"], expect, none_none)})

    # 6. absence is never an intention -- the decoder still refuses a payload missing a live unit.
    game = nd.load_game(str(games_dir / CONTROL_GAME))
    try:
        nd.decode_game(game, 1)
        fired, detail = False, "decoder accepted an agent id absent from the table"
    except nd.NarrateError as exc:
        fired, detail = True, str(exc)[:110]
    results.append({"control": "6 an agent id absent from the replay is refused", "fired": fired,
                    "detail": detail})

    # 7. the adjudication probe is inert -- its stream equals the uninstrumented binary's.
    transcript, _, _ = rt.adapt(game, agent_id=idle_classify.AGENT_ID)
    out_probe = subprocess.run([str(probe)], input=transcript, capture_output=True, text=True).stdout
    out_plain = subprocess.run([str(plain)], input=transcript, capture_output=True, text=True).stdout
    results.append({"control": "7 adjudication probe is inert against the uninstrumented binary",
                    "fired": out_probe == out_plain,
                    "detail": "streams equal=%s" % (out_probe == out_plain)})

    # 8. the adjudication parity gate is live -- one own-unit cell moved one step must break it.
    lines = transcript.split("\n")
    for index, line in enumerate(lines):
        fields = line.split()
        if len(fields) == 14 and fields[1] == "0" and index > len(lines) // 2:
            fields[2] = str(int(fields[2]) + 1)
            lines[index] = " ".join(fields)
            break
    corrupted = subprocess.run([str(probe)], input="\n".join(lines),
                               capture_output=True, text=True).stdout
    results.append({"control": "8 the adjudication parity gate can reject a corrupted transcript",
                    "fired": corrupted != out_plain,
                    "detail": "diverged=%s" % (corrupted != out_plain)})
    return results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--games-dir", required=True)
    ap.add_argument("--probe", required=True)
    ap.add_argument("--plain", required=True)
    ap.add_argument("--corpus", required=True, help="idle-classification json")
    args = ap.parse_args(argv)
    corpus = json.loads(Path(args.corpus).read_text())
    rows = run(Path(args.games_dir).expanduser(), Path(args.probe).expanduser(),
               Path(args.plain).expanduser(), corpus)
    print(json.dumps(rows, indent=2))
    return 0 if all(row["fired"] for row in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
