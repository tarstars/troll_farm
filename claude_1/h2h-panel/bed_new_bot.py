#!/usr/bin/env python3
"""The bed for a bot that is not the champion's child: the 34 frozen situations, differential
against the champion only for information.

Plain words for the owner
-------------------------
`local_claude_1/denial-ablation/fixtures_diff.py` (and its siblings under the-floor, apple-farm,
third-troll) judges a CHILD of the champion: a few lines changed, so "differs from the champion
on k of 34" is a build check. A ported bot shares no line with the champion, so that count says
nothing about the build. What still has to hold for a new bot before any panel is read:

  plays          every situation runs to its end (no crash, no empty command);
  deterministic  the bot run twice on the same situation produces the same bytes;
  compacted      the compacted file (the one the ladder receives) plays exactly as the readable
                 source does, MSG included;
  telemetry      exactly one MSG token, first on the line, decoding under the v6 grammar
                 (`narrate6.decode`) on every turn -- so `ladder_read.py` can read the collected
                 games. The v6 per-turn invariants of the champion's own rules are NOT enforced:
                 they describe the champion's branches, not a port's.

"differs from the champion" is reported, not gated. The 34 fixtures were retired as gates on
2026-08-26 (row 0-1); this is a validity bed and its numbers are not a behaviour result.

Use
---
    python3 claude_1/h2h-panel/bed_new_bot.py --readable readable/norxondor-port.rs \
        --compacted cgauto/submissions/candidate-norxondor-port-v1.rs
    python3 claude_1/h2h-panel/bed_new_bot.py   # the champion of record on its own bed (a control)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "cure3"))

import containment as ct        # noqa: E402  (its own sys.path inserts bring the harnesses in)
import fixture_harness as fh    # noqa: E402
import semantic_harness as sh   # noqa: E402
import narrate6 as n6           # noqa: E402

CHAMPION_READABLE = REPO / "readable" / "denial-off-champion.rs"
CHAMPION_SUBMISSION = REPO / "cgauto" / "submissions" / "candidate-champion-denial-off-v6-instrument.rs"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def telemetry_errors(command_lines: list[str]) -> list[str]:
    """One MSG token, first, decoding under the v6 grammar, on every turn."""
    errors = []
    for index, line in enumerate(command_lines, 1):
        frags = line.split(";")
        msgs = n6.msg_fragments(line)
        if len(msgs) != 1:
            errors.append(f"turn {index}: {len(msgs)} MSG tokens, expected exactly 1")
            continue
        if not n6.MSG_TOKEN.match(frags[0]):
            errors.append(f"turn {index}: the MSG token is not first in the command list")
        payload = msgs[0].strip()
        if len(payload) > n6.LINE_BUDGET:
            errors.append(f"turn {index}: MSG payload {len(payload)} chars, budget {n6.LINE_BUDGET}")
        try:
            n6.decode(payload)
        except n6.GateError as exc:
            errors.append(f"turn {index}: {exc}")
    return errors


def sidecar_check(path: Path) -> str | None:
    """The sha256 sidecar beside a compacted file, if one exists; None if absent."""
    side = path.parent / (path.name + ".sha256")
    if not side.exists():
        return None
    return side.read_text().split()[0]


def run_bed(readable: Path, compacted: Path, champion: Path, out: Path, only=None) -> dict:
    readable_text, compacted_text, champion_text = (
        readable.read_text(), compacted.read_text(), champion.read_text())
    recorded = sidecar_check(compacted)
    if recorded is not None and recorded != sha(compacted_text):
        raise SystemExit(f"REFUSED: {compacted} is {sha(compacted_text)}, its sidecar says {recorded}")
    cfg = json.loads(fh.CONFIG.read_text())
    sits = fh.load_situations(only)
    rows, tele = [], []
    with tempfile.TemporaryDirectory(prefix="bed-new-bot-") as wd:
        wd = Path(wd)
        champ_bin, read_bin, min_bin = wd / "champion.bin", wd / "readable.bin", wd / "compacted.bin"
        sh.compile_text(champion_text, champ_bin, crate="bed_champion")
        sh.compile_text(readable_text, read_bin, crate="bed_readable")
        sh.compile_text(compacted_text, min_bin, crate="bed_compacted")
        for sit in sits:
            sid = sit["id"]
            champ_lines, champ_state, _ = ct.run_arm(sit, champ_bin, cfg)
            lines, state, _ = ct.run_arm(sit, read_bin, cfg)
            again_lines, again_state, _ = ct.run_arm(sit, read_bin, cfg)
            min_lines, min_state, _ = ct.run_arm(sit, min_bin, cfg)
            stripped = [n6.strip_msg(l) for l in lines]
            champion_stripped = [n6.strip_msg(l) for l in champ_lines]
            plays = len(lines) > 0 and all(n6.strip_msg(l).strip() for l in lines)
            deterministic = lines == again_lines and state == again_state
            compacted_same = lines == min_lines and state == min_state
            errs = telemetry_errors(lines)
            tele.extend(f"{sid}: {e}" for e in errs)
            own = state.get("scores", [None, None])[0] if isinstance(state, dict) else None
            champ_own = champ_state.get("scores", [None, None])[0] if isinstance(champ_state, dict) else None
            rows.append({
                "id": sid, "turns": len(lines), "plays_to_the_end": plays,
                "deterministic_on_rerun": deterministic,
                "compacted_binary_identical": compacted_same,
                "telemetry_errors": len(errs),
                "differs_from_champion_without_msg": stripped != champion_stripped,
                "own_score": own, "own_score_champion": champ_own,
            })
            ok = plays and deterministic and compacted_same and not errs
            print(f"  {'ok  ' if ok else 'FAIL'} {sid:<10} turns {len(lines):>3}  score {own} "
                  f"(champion {champ_own})  telemetry errors {len(errs)}", flush=True)
    n = len(rows)
    plays = sum(r["plays_to_the_end"] for r in rows)
    det = sum(r["deterministic_on_rerun"] for r in rows)
    minsame = sum(r["compacted_binary_identical"] for r in rows)
    differs = sum(r["differs_from_champion_without_msg"] for r in rows)
    ok = plays == det == minsame == n and not tele
    report = {
        "bed": "34 frozen situations; validity only for a bot that is not the champion's child "
               "(plays, deterministic, compacted == readable, v6 telemetry decodes); "
               "'differs from the champion' is informational",
        "readable": str(readable), "readable_sha256": sha(readable_text),
        "compacted": str(compacted), "compacted_sha256": sha(compacted_text),
        "compacted_sidecar_sha256": recorded,
        "champion": str(champion), "champion_sha256": sha(champion_text),
        "fixtures": n, "plays_to_the_end": plays, "deterministic_on_rerun": det,
        "compacted_binary_identical": minsame,
        "telemetry_error_count": len(tele), "telemetry_errors": tele[:100],
        "differs_from_champion_without_msg": differs,
        "own_score_sum": sum(r["own_score"] or 0 for r in rows),
        "champion_score_sum": sum(r["own_score_champion"] or 0 for r in rows),
        "status": "PASS" if ok else "FAIL",
        "rows": rows,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\n  {report['status']}  plays {plays}/{n}, deterministic {det}/{n}, compacted==readable "
          f"{minsame}/{n}, telemetry errors {len(tele)}; differs from the champion on {differs}/{n} "
          f"(informational)  -> {out}")
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--readable", type=Path, default=CHAMPION_READABLE)
    ap.add_argument("--compacted", type=Path, default=CHAMPION_SUBMISSION)
    ap.add_argument("--champion", type=Path, default=CHAMPION_SUBMISSION)
    ap.add_argument("--only", default=None, help="situation ids, comma-separated")
    ap.add_argument("--out", type=Path, default=HERE / "results" / "bed.json")
    args = ap.parse_args()
    report = run_bed(args.readable, args.compacted, args.champion, args.out,
                     args.only.split(",") if args.only else None)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
