#!/usr/bin/env python3
r"""The 34, re-graded on the champion with episode identity ENFORCED.

Card `20260821-episode-identity-regrade`, deliverables 2 and 3. Two arms, both through the
shared harness now that the gate lives there:

- **subject** (`submitted-agent6593838-readable-no-orchard.rs`, 98628e98) — the bot that produced
  the 34 recorded windows. It must be accepted 34/34; anything less means the replay pipeline no
  longer reconstructs the recorded episodes and no row in the champion arm is trustworthy. This
  is also the gate's positive control: a gate that has only ever rejected is as useless as one
  that has only ever accepted.
- **champion** (`claude_1/chop4c/candidate-door1.rs`, 547fa706) — the arm the existing
  `claude_1/picker2/sweep34-door1-base.json` was produced from, re-graded here side by side.

Every row carries the real-end annotation the re-grade card asked for (deliverable 3): the frozen
`has_stalled` end turn and the conservative grace-only bound. Those numbers are **read from the
ACCEPTED artifact** `claude_1/regrade1/real-end-regrade-2026-08-21.json`, subject arm, not
recomputed here — recomputing an accepted measurement invites two numbers for one fact. They are
an annotation and they change no verdict.

What this does NOT do: re-rule anything. The 18 BUG, the six BUG and the owner's OSC-032/033
disposition are the owner's. This file changes what the word FIXED is allowed to be said about.

Run:  python3 claude_1/regrade2/regrade34.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/hstarve1", "claude_1/banana-restoration-r2",
          "claude_1/pipeline"):
    sys.path.insert(0, str(REPO / p))
import fixture_harness as H     # noqa: E402

CHAMPION = REPO / "claude_1/chop4c/candidate-door1.rs"
CHAMPION_SHA256 = "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0"
SUBJECT_SHA256 = "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29"
PRIOR = REPO / "claude_1/picker2/sweep34-door1-base.json"
REAL_END = REPO / "claude_1/regrade1/real-end-regrade-2026-08-21.json"
OUT = HERE / "regrade34-identity-2026-08-21.json"


class RegradeError(Exception):
    """Anything that would make a number here mean something other than it says."""


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def annotations():
    """Real-end annotation per fixture, from the ACCEPTED artifact's subject arm."""
    art = json.loads(REAL_END.read_text())
    rows = art["arms"]["subject"] if isinstance(art.get("arms"), dict) else None
    if rows is None:
        rows = art["rows"]["subject"] if isinstance(art.get("rows"), dict) else art["rows"]
    out = {}
    for row in rows:
        out[row["id"]] = {
            "real_end_turn": row["real_end"]["first_stalled_turn"],
            "grace_only_end_turn": row["real_end"]["grace_only_end_turn"],
            "window_turns_past_the_real_end":
                row["regrade"]["window_turns_past_the_real_end"],
            "real_end_verdict": row["regrade"]["verdict"],
        }
    return out, art["task"]


def arm(label, source, sits, cfg, workdir, enforce_identity):
    binary = H.compile_candidate(source, workdir)
    rows = []
    for sit in sorted(sits, key=lambda s: s["id"]):
        tr, eps, p4, _, lines = H.run_situation_ex(sit, binary, cfg)
        ident = H.episode_identity(sit["id"], sit, tr, lines)
        if enforce_identity and not ident["reproduces_the_recorded_episode"]:
            raise RegradeError(
                f"{sit['id']}: the SUBJECT arm does not reproduce its own recorded episode "
                f"({ident['reasons']}). The library recorded it from this bot; if the replay "
                f"cannot reproduce it, no row in either arm is trustworthy.")
        row = H.grade(sit, tr, eps, p4, ident)
        row["identity_reasons"] = ident["reasons"]
        rows.append(row)
        print(f"  [{label}] {row['id']}  {row['verdict']}")
    return rows


def main() -> int:
    if sha256_of(CHAMPION) != CHAMPION_SHA256:
        raise RegradeError("the champion file is not the champion of record.")
    if sha256_of(H.RESIDENT) != SUBJECT_SHA256:
        raise RegradeError("the resident is not the library's subject bytes; the replay would "
                           "not reproduce the recorded episodes.")
    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations()
    if len(sits) != 34:
        raise RegradeError(f"the card's scope IS the 34; got {len(sits)}.")
    ann, ann_task = annotations()

    with tempfile.TemporaryDirectory(prefix="regrade34-") as wd:
        sub_dir, champ_dir = Path(wd) / "subject", Path(wd) / "champion"
        sub_dir.mkdir(); champ_dir.mkdir()
        subject_rows = arm("subject", H.RESIDENT, sits, cfg, sub_dir, enforce_identity=True)
        champion_rows = arm("champion", CHAMPION, sits, cfg, champ_dir, enforce_identity=False)

    prior = {r["id"]: r for r in json.loads(PRIOR.read_text())["results"]}
    champ = {r["id"]: r for r in champion_rows}
    if sorted(prior) != sorted(champ):
        raise RegradeError("the prior sweep and this one do not cover the same fixtures.")

    table, changed = [], []
    for fid in sorted(champ):
        before, now = prior[fid]["verdict"], champ[fid]["verdict"]
        row = {"id": fid, "kind": champ[fid]["kind"],
               "verdict_before_the_gate": before, "verdict_with_identity_enforced": now,
               "changed": before != now,
               "reason": ("; ".join(champ[fid]["identity_reasons"]) if before != now
                          else "unchanged"),
               "real_end_annotation": ann.get(fid)}
        table.append(row)
        if before != now:
            changed.append(row)

    repro = sorted(fid for fid in champ
                   if champ[fid]["verdict"] != "NOT_REPRODUCIBLE_ON_BASE")
    lost_fixed = sorted(fid for fid in champ
                        if prior[fid]["verdict"] == "FIXED" and champ[fid]["verdict"] != "FIXED")
    still_fixed = sorted(fid for fid in champ if champ[fid]["verdict"] == "FIXED")
    subject_repro = sum(1 for r in subject_rows
                        if r["verdict"] != "NOT_REPRODUCIBLE_ON_BASE")

    if subject_repro != 34:
        raise RegradeError(f"the subject arm reproduces only {subject_repro}/34.")
    if len(repro) == 34:
        raise RegradeError(
            "the gate accepted the champion on all 34, so it has never been observed "
            "rejecting on this arm and its acceptances are not evidence.")

    art = {
        "task": "20260821-episode-identity-regrade", "deliverables": [2, 3],
        "scope": "measurement and tooling only; no fix to any bot, no re-ruling of any case",
        "arms": {"subject": {"source": str(H.RESIDENT.relative_to(REPO)),
                             "sha256": SUBJECT_SHA256,
                             "reproduces": subject_repro},
                 "champion": {"source": str(CHAMPION.relative_to(REPO)),
                              "sha256": CHAMPION_SHA256,
                              "reproduces": len(repro)}},
        "prior_artifact": str(PRIOR.relative_to(REPO)),
        "real_end_annotation_source": {"artifact": str(REAL_END.relative_to(REPO)),
                                       "task": ann_task, "arm": "subject",
                                       "note": "read, not recomputed; annotation only"},
        "champion_reproduces": repro,
        "champion_does_not_reproduce": sorted(set(champ) - set(repro)),
        "fixed_before_the_gate": sorted(fid for fid in prior
                                        if prior[fid]["verdict"] == "FIXED"),
        "fixed_with_identity_enforced": still_fixed,
        "fixed_lost_to_the_gate": lost_fixed,
        "verdicts_changed": len(changed),
        "table": table,
        "subject_rows": subject_rows,
        "champion_rows": champion_rows,
    }
    OUT.write_text(json.dumps(art, indent=2) + "\n")

    print(f"\n  subject arm: {subject_repro}/34 reproduce (required 34)")
    print(f"  champion arm: {len(repro)}/34 reproduce, "
          f"{34 - len(repro)} NOT_REPRODUCIBLE_ON_BASE")
    print(f"  FIXED before the gate: {len(art['fixed_before_the_gate'])} "
          f"{art['fixed_before_the_gate']}")
    print(f"  FIXED with identity enforced: {len(still_fixed)} {still_fixed}")
    print(f"  FIXED lost to the gate: {len(lost_fixed)} {lost_fixed}")
    print(f"  verdicts changed: {len(changed)} -> {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
