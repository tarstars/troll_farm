#!/usr/bin/env python3
"""Build the CORRECT-SUBJECT oscillation situation library.

This is a thin driver over the ACCEPTED method in
``claude_1/banana-restoration-r2/build_oscillation_library.py``.  The method was
reviewed and accepted; only the *data* it was pointed at was wrong.  Nothing in
the harvest, the classifier, the dedupe key, the freezing discipline or the
integrity hashing is reimplemented here -- every one of those is imported from
that module and called unmodified.

What this driver changes, and why -- three things, all provenance, none method:

1.  **The subject.**  ``panel-config.json`` in this directory points BOTH
    ``candidate.source`` and ``parent.source`` at
    ``cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs``
    (``git show origin/main:<path>``, SHA-256
    ``98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29``) --
    the M3a subject ``readable__no_orchard``.  The earlier library was harvested
    from the PARENT ``candidate-agent6553250-preseed-orchard-coverage-slim.min.rs``
    (``a8eb3b2b...``), a different program.

2.  **The provenance note.**  ``build_oscillation_library.harvest`` writes a
    fixed note saying "the arena parent judged against itself".  That sentence
    is true of the parent-lineage library and FALSE here.  It is replaced, per
    situation, with a note naming the subject and its git ref.  The bot source
    is recorded as its ``origin/main`` git ref rather than the scratch absolute
    path the panel was handed, so the record is reproducible from the repo.

3.  **The real-corpus record is excluded.**  ``harvest`` appends the Elost
    same-tree deadlock as a PARTIAL ``REAL_CORPUS`` situation.  Its committed
    result file names its own bot as
    ``candidate-agent6585739-owner-tent-banker-commitment-slim.min.rs``
    (``f26e3781...``) -- a THIRD program, neither the subject nor the parent.
    A library whose declared subject is ``98628e98`` may not contain a
    situation produced by a different bot.  It is dropped here, not deleted
    from the repo: it remains in the parent-lineage tree, correctly labelled.

Scope, unchanged from the accepted method: **M3a freezes situations only.**  No
best action, preferred action, recommendation, verdict, fix or remedy is
recorded anywhere, and ``test_oscillation_library.py`` enforces that by walking
every key and every string of every frozen file against forbidden lists.

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

SUBJECT_PATH = "cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs"
SUBJECT_GIT_REF = "origin/main:" + SUBJECT_PATH
SUBJECT_SHA256 = ("98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85"
                  "d41fbc29")
PARENT_SHA256 = ("a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b"
                 "884e55")

SUBJECT_NOTE = (
    "SUBJECT-CORRECT library. Every situation here was harvested from the M3a "
    "subject `readable__no_orchard` = %s (git ref %s, sha256 %s), judged "
    "against ITSELF at run_identity `floor` -- candidate bytes == parent "
    "bytes, machine-checked by fuzz_panel._check_run_identity. It is NOT the "
    "parent lineage: the sibling tree `oscillation-library/` was harvested "
    "from `candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` "
    "(sha256 %s), a different program, and must never be cited as M3a."
    % (SUBJECT_PATH, SUBJECT_GIT_REF, SUBJECT_SHA256, PARENT_SHA256))

HARVEST_NOTE = (
    "candidate and parent are the SAME source -- the M3a SUBJECT "
    "`readable__no_orchard` (%s, sha256 %s) judged against itself. This is the "
    "panel FLOOR for the subject, not a candidate regression, and not the "
    "parent lineage `a8eb3b2b...`." % (SUBJECT_GIT_REF, SUBJECT_SHA256))


def repoint_provenance(sits):
    """Rewrite the three provenance strings that name the wrong lineage.

    Touches provenance ONLY.  No classification, window, world state, command
    line, detector count or dedupe input is altered, so the harvested data is
    exactly what the accepted method produced.
    """
    for s in sits:
        prov = s["provenance"]
        if prov.get("bot_source_sha256") != SUBJECT_SHA256:
            raise SystemExit(
                "refusing to build: a harvested situation carries "
                "bot_source_sha256 %r, not the subject %r"
                % (prov.get("bot_source_sha256"), SUBJECT_SHA256))
        prov["bot_source"] = SUBJECT_PATH
        prov["bot_source_git_ref"] = SUBJECT_GIT_REF
        prov["subject"] = "readable__no_orchard"
        prov["note"] = HARVEST_NOTE
    return sits


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--games", required=True)
    ap.add_argument("--panel-config", default=str(HERE / "panel-config.json"))
    ap.add_argument("--out", default=str(HERE / "library"))
    args = ap.parse_args(argv)

    cfg_path = Path(args.panel_config).resolve()
    cfg = json.loads(cfg_path.read_text())
    if cfg.get("run_identity") != "floor":
        raise SystemExit("panel config must declare run_identity 'floor'")
    for side in ("candidate", "parent"):
        if cfg[side]["sha256"] != SUBJECT_SHA256:
            raise SystemExit("panel config %s.sha256 is not the subject" % side)

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

    # Re-write the index with the subject declaration added.  library_sha256 is
    # computed over the (id, content_sha256) pairs only, so an added index
    # field cannot mask an added, removed or altered situation.
    index_path = out_dir / "index.json"
    index = json.loads(index_path.read_text())
    index["subject"] = {
        "name": "readable__no_orchard",
        "path": SUBJECT_PATH,
        "git_ref": SUBJECT_GIT_REF,
        "sha256": SUBJECT_SHA256,
        "run_identity": "floor",
        "judged_against": "itself (candidate bytes == parent bytes)",
    }
    index["subject_note"] = SUBJECT_NOTE
    index["panel_config_sha256"] = hashlib.sha256(
        cfg_path.read_bytes()).hexdigest()
    index["excluded"] = [{
        "kind": d["kind"],
        "reason": ("produced by a different bot (%s), not the subject %s"
                   % (d["provenance"]["bot_source_sha256"], SUBJECT_SHA256)),
    } for d in dropped]
    assert index["library_sha256"] == library_sha256(index["situations"])
    index_path.write_text(json.dumps(index, indent=1, sort_keys=True) + "\n")

    print("harvested %d subject episodes -> %d frozen situations "
          "(library_sha256 %s)"
          % (raw, index["situation_count"], index["library_sha256"]))
    print("mechanisms:", index["mechanism_histogram"])
    print("blocker:   ", index["blocker_state_histogram"])
    print("kind:      ", index["kind_histogram"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
