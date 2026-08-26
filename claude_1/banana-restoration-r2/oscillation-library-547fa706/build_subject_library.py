#!/usr/bin/env python3
"""Build the CHAMPION's oscillation situation library.

Card `20260821-champion-subject-library`, owner-approved 2026-08-21. The rule it
implements, in one line: **a recorded episode belongs to the bot that produced it.**
The 34 situations of `../oscillation-library-98628e98/` are the exhibits of
`readable__no_orchard`; the champion of record reproduces only 11 of them, so the
champion needs its own exhibit set and this is it.

This is a thin driver over the ACCEPTED method in
``claude_1/banana-restoration-r2/build_oscillation_library.py`` -- the same shape as
``../oscillation-library-98628e98/build_subject_library.py``, which was accepted on
2026-08-11. Nothing in the harvest, the classifier, the idleness criterion, the dedupe
key, the freezing discipline or the integrity hashing is reimplemented, altered or
subclassed here: every one of those is imported from that module and called unmodified.
The driver refuses to run if the builder's bytes are not the accepted ones.

What the driver does, and only this:

1.  **Pins the subject** to the champion of record
    ``claude_1/chop4c/candidate-door1.rs`` (sha256 ``547fa706...``, git
    ``dc43d633...``), and refuses if the panel config names anything else or is not a
    ``floor`` run.
2.  **Repoints the provenance strings** that name the wrong lineage, exactly as the
    98628e98 driver does. Provenance ONLY: no classification, window, world state,
    command line, detector count or dedupe input is touched.
3.  **Excludes the REAL_CORPUS record** that ``harvest`` appends. It was produced by a
    third program (``f26e3781...``), and a library whose declared subject is the
    champion may not contain a situation another bot produced. It is dropped here, not
    deleted from the repo: it remains in the parent-lineage tree, correctly labelled.
4.  **Writes the episode-identity record** (``identity.json``) -- new in this library,
    and the reason the card asks for it. For every case it digests EXACTLY the two
    inputs `claude_1/t1/fixture_harness.episode_identity` reads -- the frozen entry
    board and the frozen window command lines -- so a later bot can be checked against
    this library without re-deriving what "the same episode" means. It is written
    BESIDE the frozen situations, never inside them: adding a field to a payload would
    change its ``content_sha256`` and put the identity record inside the thing it is
    supposed to identify.

Scope, unchanged from the accepted method: **this library freezes situations only.** No
best action, preferred action, recommendation, verdict, fix or remedy is recorded
anywhere, and the M3a silence tests enforce it by walking every key and every string.

Usage
-----
    python3 build_subject_library.py --games <games.jsonl.gz> \
        [--panel-config panel-config.json] [--out library/]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
R2 = HERE.parent
REPO = R2.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "pipeline"))
sys.path.insert(0, str(R2))

import build_oscillation_library as bol      # noqa: E402
from oscillation_library import library_sha256  # noqa: E402

SUBJECT_PATH = "claude_1/chop4c/candidate-door1.rs"
SUBJECT_COMMIT = "dc43d633ab30154d78bad05425b026ca5487d797"
SUBJECT_GIT_REF = SUBJECT_COMMIT + ":" + SUBJECT_PATH
SUBJECT_SHA256 = ("547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef5"
                  "44070b0")
OLD_SUBJECT_SHA256 = ("98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc"
                      "85d41fbc29")

# The accepted builder, by digest. A driver that says "unmodified method" while the
# method has moved underneath it is the exact failure this card exists to prevent.
BUILDER_SHA256 = ("4b9fce4ca49a6ce05b4f3f8cb8f7b81d78b7da3c863a4e1ad32fdd2f1"
                  "6aff9df")

SUBJECT_NOTE = (
    "CHAMPION library. Every situation here was harvested from the CHAMPION OF RECORD "
    "%s (git ref %s, sha256 %s), judged against ITSELF at run_identity `floor` -- "
    "candidate bytes == parent bytes, machine-checked by fuzz_panel._check_run_identity. "
    "THE RULE (owner-approved 2026-08-21): a recorded episode belongs to the bot that "
    "produced it. These are the champion's exhibits. The sibling tree "
    "`oscillation-library-98628e98/` holds the exhibits of `readable__no_orchard` "
    "(sha256 %s), a DIFFERENT program which the champion reproduces only 11 of; its "
    "cases are not this bot's regression set and must never be cited as such. The "
    "owner's rulings taken on those cases are rulings about MECHANISMS and stand "
    "unchanged; a mechanism with no case here has NO EXHIBIT on the champion, which is "
    "not the same statement as `fixed`."
    % (SUBJECT_PATH, SUBJECT_GIT_REF, SUBJECT_SHA256, OLD_SUBJECT_SHA256))

HARVEST_NOTE = (
    "candidate and parent are the SAME source -- the CHAMPION OF RECORD (%s, sha256 %s) "
    "judged against itself. This is the panel FLOOR for the champion, not a candidate "
    "regression, and not the `readable__no_orchard` lineage `98628e98...`."
    % (SUBJECT_GIT_REF, SUBJECT_SHA256))


def check_builder_unmodified():
    src = R2 / "build_oscillation_library.py"
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    if digest != BUILDER_SHA256:
        raise SystemExit(
            "refusing to build: the accepted builder %s has sha256 %s, not the pinned "
            "%s. The method this driver claims to call unmodified has changed; get the "
            "change reviewed before harvesting anything with it."
            % (src, digest, BUILDER_SHA256))
    return digest


def repoint_provenance(sits):
    """Rewrite the provenance strings that name the lineage. Provenance ONLY."""
    for s in sits:
        prov = s["provenance"]
        if prov.get("bot_source_sha256") != SUBJECT_SHA256:
            raise SystemExit(
                "refusing to build: a harvested situation carries bot_source_sha256 "
                "%r, not the subject %r"
                % (prov.get("bot_source_sha256"), SUBJECT_SHA256))
        prov["bot_source"] = SUBJECT_PATH
        prov["bot_source_git_ref"] = SUBJECT_GIT_REF
        prov["subject"] = "door1_champion_547fa706"
        prov["note"] = HARVEST_NOTE
    return sits


def _canonical_entry(ws):
    """The entry board, in the exact canonical form `check_entry_state` compares.

    Same sort, same tuple shape, same fields -- so a digest computed here and a replay
    checked there agree by construction rather than by two authors' good intentions.
    """
    return {
        "turn": int(ws["turn"]),
        "plants": sorted([p[0], p[1], p[2], p[3], p[4], p[5], p[6]] for p in ws["plants"]),
        "units": sorted([u[0], u[1], u[2], u[3], u[4], u[5], u[6], u[7], list(u[8:])]
                        for u in ws["units"]),
        "inventories": [list(ws["inventories"]["own"]),
                        list(ws["inventories"]["opponent"])],
    }


def _canonical_commands(window):
    return [[int(e["turn"]), e["line"].strip()] for e in (window.get("commands") or [])]


def _sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def identity_record(sits, index, panel_cfg_sha):
    """Per-case episode identity: what a later bot must reproduce to BE this episode."""
    cases = []
    for s in sits:
        w, ws = s["window"], s["world_state_at_entry"]
        cmds = _canonical_commands(w)
        entry = _canonical_entry(ws)
        gate_ready, why = True, []
        if not cmds:
            gate_ready = False
            why.append("no frozen window commands: `check_window_commands` fails closed")
        if entry["turn"] != int(w["turn_start"]):
            gate_ready = False
            why.append("frozen entry turn %d != window start %d: `check_entry_state` "
                       "refuses the comparison" % (entry["turn"], int(w["turn_start"])))
        cases.append({
            "id": s["id"],
            "content_sha256": s["content_sha256"],
            "map_id": s["provenance"].get("map_id"),
            "seat": s["provenance"].get("seat"),
            "seed": s["provenance"].get("seed"),
            "opponent_profile": s["provenance"].get("opponent_profile"),
            "unit": w["unit"],
            "window_turns": [w["turn_start"], w["turn_end"]],
            "entry_turn": entry["turn"],
            "window_commands_count": len(cmds),
            "window_commands_sha256": _sha(cmds),
            "entry_state_sha256": _sha(entry),
            "identity_sha256": _sha([_sha(cmds), _sha(entry)]),
            "gate_ready": gate_ready,
            "gate_notes": why,
        })
    return {
        "schema": "troll-farm-oscillation-episode-identity-v1",
        "what_this_is": (
            "The two inputs `claude_1/t1/fixture_harness.episode_identity` reads, digested "
            "per case: the frozen window command lines (turn, line) and the frozen entry "
            "board (turn, plants, units, inventories) in the same canonical form "
            "`check_entry_state` builds. A replay reproduces a case only if BOTH digests "
            "match; neither alone is sufficient (an all-WAIT window agrees between two "
            "different games -- that is why the entry board is here)."),
        "not_a_verdict": (
            "This records WHICH episode a case is. It says nothing about whether any bot "
            "should have acted differently; that judgement is not in this library."),
        "subject": {"path": SUBJECT_PATH, "git_ref": SUBJECT_GIT_REF,
                    "sha256": SUBJECT_SHA256},
        "library_sha256": index["library_sha256"],
        "panel_config_sha256": panel_cfg_sha,
        "gate_source": "claude_1/t1/fixture_harness.py::episode_identity",
        "case_count": len(cases),
        "gate_ready_count": sum(1 for c in cases if c["gate_ready"]),
        "cases": cases,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--games", required=True)
    ap.add_argument("--panel-config", default=str(HERE / "panel-config.json"))
    ap.add_argument("--out", default=str(HERE / "library"))
    args = ap.parse_args(argv)

    builder_digest = check_builder_unmodified()
    cfg_path = Path(args.panel_config).resolve()
    cfg = json.loads(cfg_path.read_text())
    if cfg.get("run_identity") != "floor":
        raise SystemExit("panel config must declare run_identity 'floor'")
    for side in ("candidate", "parent"):
        if cfg[side]["sha256"] != SUBJECT_SHA256:
            raise SystemExit("panel config %s.sha256 is not the champion" % side)

    sits = bol.harvest(Path(args.games), cfg_path, REPO)
    dropped = [s for s in sits if s["kind"] == "REAL_CORPUS"]
    sits = [s for s in sits if s["kind"] != "REAL_CORPUS"]
    for d in dropped:
        print("EXCLUDED (not the subject): %s from bot %s"
              % (d["kind"], d["provenance"]["bot_source_sha256"][:16]))
    repoint_provenance(sits)
    raw = len(sits)
    sits = bol.dedupe(sits)
    out_dir = Path(args.out)
    index = bol.write_library(sits, out_dir)

    index_path = out_dir / "index.json"
    index = json.loads(index_path.read_text())
    panel_cfg_sha = hashlib.sha256(cfg_path.read_bytes()).hexdigest()
    index["subject"] = {
        "name": "door1_champion_547fa706",
        "path": SUBJECT_PATH,
        "git_ref": SUBJECT_GIT_REF,
        "sha256": SUBJECT_SHA256,
        "run_identity": "floor",
        "judged_against": "itself (candidate bytes == parent bytes)",
    }
    index["subject_note"] = SUBJECT_NOTE
    index["panel_config_sha256"] = panel_cfg_sha
    index["builder_sha256"] = builder_digest
    index["excluded"] = [{
        "kind": d["kind"],
        "reason": ("produced by a different bot (%s), not the subject %s"
                   % (d["provenance"]["bot_source_sha256"], SUBJECT_SHA256)),
    } for d in dropped]
    assert index["library_sha256"] == library_sha256(index["situations"])
    index_path.write_text(json.dumps(index, indent=1, sort_keys=True) + "\n")

    ident = identity_record(sits, index, panel_cfg_sha)
    (out_dir.parent / "identity.json").write_text(
        json.dumps(ident, indent=1, sort_keys=True) + "\n")

    print("harvested %d subject episodes -> %d frozen situations "
          "(library_sha256 %s)"
          % (raw, index["situation_count"], index["library_sha256"]))
    print("mechanisms:", index["mechanism_histogram"])
    print("blocker:   ", index["blocker_state_histogram"])
    print("kind:      ", index["kind_histogram"])
    print("identity:   %d/%d cases gate-ready"
          % (ident["gate_ready_count"], ident["case_count"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
