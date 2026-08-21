#!/usr/bin/env python3
"""Independent replay check of this library's episode-identity records (card G-1).

For every case: rebuild the game from its own provenance, re-run the CHAMPION binary,
and put the result through `claude_1/t1/fixture_harness.episode_identity` -- the shared
gate, called, not paraphrased. The champion recorded these episodes, so every case must
reproduce; a failure here means the replay pipeline no longer reconstructs what the
harvest froze and the library's turn numbers describe games the harness cannot re-enter.

It also re-derives each case's `identity_sha256` from the FROZEN payload and checks it
against `identity.json`, so the digest file cannot drift from the situations it indexes.

    python3 verify_identity.py [--only OSC-003,OSC-007] [--json out.json]
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
R2 = HERE.parent
REPO = R2.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "t1"))
sys.path.insert(0, str(REPO / "claude_1" / "pipeline"))
sys.path.insert(0, str(R2))

import fixture_harness as fh                 # noqa: E402
import oscillation_library as ol             # noqa: E402
import build_subject_library as bsl          # noqa: E402

LIB = HERE / "library"
IDENT = HERE / "identity.json"
SUBJECT = REPO / bsl.SUBJECT_PATH


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--panel-config", default=str(HERE / "panel-config.json"))
    args = ap.parse_args(argv)

    sits = ol.load_library(str(LIB))
    ident = json.loads(IDENT.read_text())
    by_id = {c["id"]: c for c in ident["cases"]}
    if args.only:
        want = set(args.only.split(","))
        sits = [s for s in sits if s["id"] in want]

    cfg = json.loads(Path(args.panel_config).read_text())
    rows, bad = [], 0
    with tempfile.TemporaryDirectory(prefix="champlib-verify-") as wd:
        binary = fh.compile_candidate(SUBJECT, Path(wd))
        for s in sits:
            rec = by_id[s["id"]]
            # (a) the digest file matches the frozen payload it claims to index
            cmds = bsl._canonical_commands(s["window"])
            entry = bsl._canonical_entry(s["world_state_at_entry"])
            digest_ok = (bsl._sha(cmds) == rec["window_commands_sha256"]
                         and bsl._sha(entry) == rec["entry_state_sha256"]
                         and rec["content_sha256"] == s["content_sha256"])
            # (b) the champion, replayed, IS this episode
            tr, eps, p4, spec, lines = fh.run_situation_ex(s, binary, cfg)
            v = fh.episode_identity(s["id"], s, tr, lines)
            ok = digest_ok and v["reproduces_the_recorded_episode"]
            if not ok:
                bad += 1
            rows.append({
                "id": s["id"],
                "digest_matches_frozen_payload": digest_ok,
                "reproduces_the_recorded_episode": v["reproduces_the_recorded_episode"],
                "reasons": v["reasons"],
                "window_turns_checked": (v["window_commands"] or {}).get("window_turns_checked"),
                "command_mismatches": (v["window_commands"] or {}).get("mismatches"),
                "entry_state_matches": (v["entry_state"] or {}).get("matches"),
                "d1_episodes_in_replay": len(eps),
                "p4_violations_in_replay": len(p4.get("violations", []) if isinstance(p4, dict) else p4),
            })
            print("  %s %s  commands %s/%s  entry=%s"
                  % ("OK  " if ok else "FAIL", s["id"],
                     rows[-1]["window_turns_checked"] - (rows[-1]["command_mismatches"] or 0),
                     rows[-1]["window_turns_checked"], rows[-1]["entry_state_matches"]))
    out = {
        "subject": bsl.SUBJECT_GIT_REF,
        "library_sha256": ident["library_sha256"],
        "cases": len(rows),
        "reproduced": sum(1 for r in rows if r["reproduces_the_recorded_episode"]),
        "failures": bad,
        "rows": rows,
    }
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print("%d/%d cases reproduce on the champion; %d failures"
          % (out["reproduced"], out["cases"], bad))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
