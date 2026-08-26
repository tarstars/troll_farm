#!/usr/bin/env python3
r"""G1 idleness panel — classification + adjudication + controls, PASS only if all three hold.

Card: `local_claude_1` `20260823T110000Z`.  Run:

    python3 claude_1/narrate2/run_idle_panel.py --games-dir DIR [--bin-dir DIR]

PASS requires: the six classes exhaust the join rows exactly; the divergence number equals the
three classes that compose it and is reported separately from the idleness headline; every
adjudicable divergence row carries a verdict and a tagged rewrite site (no `(untagged)`); and 8/8
controls fire.
"""
from __future__ import annotations

import argparse, glob, hashlib, json, os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import idle_adjudicate                              # noqa: E402
import idle_classify                                # noqa: E402
import idle_controls                                # noqa: E402


def corpus_digest(paths):
    sha = hashlib.sha256()
    for path in paths:
        sha.update(os.path.basename(path).encode())
        sha.update(hashlib.sha256(Path(path).read_bytes()).hexdigest().encode())
    return sha.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--games-dir", required=True)
    ap.add_argument("--bin-dir", default="~/.cache/troll-farm/gb-real")
    ap.add_argument("--out", default=str(HERE / "results" / "idle-panel-2026-08-23.json"))
    args = ap.parse_args(argv)

    games_dir = Path(args.games_dir).expanduser()
    bins = Path(args.bin_dir).expanduser()
    probe, plain = bins / "probe-idle", bins / "instrument"

    corpus = idle_classify.classify_games(games_dir)
    adj = idle_adjudicate.adjudicate(games_dir, probe)
    controls = idle_controls.run(games_dir, probe, plain, corpus)

    classes = corpus["classes"]
    verdicts = adj["verdicts"]
    adjudicable = sum(v for k, v in verdicts.items()
                      if not k.startswith("site:") and k != "NOT_VERIFIED")
    sites = sum(v for k, v in verdicts.items() if k.startswith("site:"))
    untagged = verdicts.get("site:(untagged)", 0)

    passed = (
        sum(classes.values()) == corpus["rows"]
        and corpus["divergence_rows"] == (classes["NO_WANT_COMMANDED"]
                                          + classes["WANT_SILENT_TEAM"]
                                          + classes["WANT_SILENT_PARTIAL"])
        and adjudicable == sites and untagged == 0
        and all(row["fired"] for row in controls))

    result = {
        "corpus": {"games": corpus["games"], "rows": corpus["rows"],
                   "digest_sha256": corpus_digest(sorted(glob.glob(str(games_dir / "*.json.gz")))),
                   "agent_id": idle_classify.AGENT_ID, "refused": corpus["refused"]},
        "classes": classes,
        "idle_rows_want_something_did_nothing": corpus["idle_rows"],
        "divergence_rows": corpus["divergence_rows"],
        "joint_intent_verb": corpus["joint_intent_verb"],
        "adjudication": {k: v for k, v in adj.items() if k != "rows"},
        "adjudication_rows_adjudicable": adjudicable,
        "controls": controls,
        "status": "PASS" if passed else "FAIL",
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "controls"},
                     indent=2, sort_keys=True))
    print("controls: %d/%d fired" % (sum(c["fired"] for c in controls), len(controls)))
    print("status:", result["status"])
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
