#!/usr/bin/env python3
"""Mutation drive for the B4 collector service (task `20260811-s3-collector-v2`).

The collector runs unattended at 05:47 with nobody watching, so its failure modes are the
quiet ones: a cursor that advances past games it never uploaded, an unconditional PUT that
clobbers a day, a lost game reported as a clean run. Each mutant below is one of those.

Mechanics and exit-status semantics live in `mutation_runner.py`
(0 all caught · 1 control not green · 2 survivors · 3 incomplete).

Usage: python3 claude_1/collector-v2/run_b4_mutations.py --out <results.json>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mutation_runner import run_drive  # noqa: E402

HERE = Path(__file__).resolve().parent
TARGET = HERE / "collector.py"
TESTS = HERE / "tests"

MUTANTS = [
    ("C1-cursor-written-non-atomically",
     "writes the cursor in place, so a crash mid-write leaves a torn file (finding F8)",
     '    os.replace(temporary, path)',
     '    path.write_text(data); os.unlink(temporary)'),
    ("C2-no-directory-fsync",
     "skips the directory fsync, so the rename itself can be lost on power failure",
     '    directory = os.open(path.parent, os.O_RDONLY)',
     '    directory = os.open(os.devnull, os.O_RDONLY)'),
    ("C3-cursor-advances-after-failed-upload",
     "records games as seen even when nothing was uploaded, so a failed day is never retried",
     '        if upload.get("uploaded") or args.dry_run or not pack.game_ids:',
     '        if True:'),
    ("C3b-upload-failure-is-not-an-error",
     "reports exit 0 after a failed upload, so a lost day looks like a clean run",
     '                log("upload.failed", code=error.code, status=error.status)\n                exit_code = 2',
     '                log("upload.failed", code=error.code, status=error.status)'),
    ("C4-unconditional-put",
     "drops If-None-Match, so a re-run silently overwrites the day's object",
     '            put_pack = s3.put_object(pack_key, pack.pack_bytes,\n                                     content_type="application/gzip", if_none_match=True)',
     '            put_pack = s3.put_object(pack_key, pack.pack_bytes,\n                                     content_type="application/gzip", if_none_match=False)'),
    ("C5-rerun-never-escalates",
     "treats a collision as fatal instead of moving to the next rerun key",
     '                log("upload.collision", key=pack_key, rerun=rerun)\n                continue',
     '                raise'),
    ("C6-unbounded-rerun-search",
     "keeps inventing rerun keys forever rather than refusing to guess",
     '    for rerun in range(0, MAX_RERUN + 1):',
     '    for rerun in range(0, 10_000):'),
    ("C7-422-not-permanent",
     "does not distinguish a permanently gone replay from a transient failure",
     '"permanent": error.code == 422,',
     '"permanent": False,'),
    ("C8-incomplete-day-looks-clean",
     "returns 0 when some games failed to fetch, hiding an incomplete day",
     '        if exit_code == 0 and fetch_failures and not permanent:',
     '        if False:'),
    ("C9-upload-never-verified",
     "trusts the upload instead of downloading and re-hashing it",
     '                if not all(verification.values()):',
     '                if False and not all(verification.values()):'),
    ("C10-invalid-replay-staged",
     "stages a replay whose shape did not validate, corrupting the day's pack",
     '            if not valid:\n                raise ValueError(f"replay shape invalid: {error}")',
     '            valid = True'),
    ("C11-cursor-trim-silent",
     "trims the seen set without reporting how many ids were dropped",
     '            dropped = len(ordered) - self.capacity',
     '            dropped = 0'),
    ("C13-prune-before-verification",
     "prunes staging on any upload, so a failed verification destroys the only local copy",
     '        if args.prune_staging and upload.get("uploaded") and verification and \\\n                all(verification.values()):',
     '        if args.prune_staging:'),
    # --- dedupe path (task 20260811-collector-v2-dedupe) ---
    ("D1-known-ids-ignored",
     "discovers candidates but does not subtract what S3 already holds",
     '        wanted = [gid for gid in cursor.unseen(candidates) if gid not in known]',
     '        wanted = cursor.unseen(candidates)'),
    ("D2-dedupe-after-the-cap",
     "applies the budget before removing held games, so the budget is spent on re-fetches",
     '        already_held = [gid for gid in candidates if gid in known]',
     '        candidates = candidates[:args.max_games] if args.max_games else candidates\n        already_held = [gid for gid in candidates if gid in known]'),
    ("D3-newest-first",
     "keeps the newest un-held candidates, leaving the ones nearest to expiry behind",
     '            wanted = wanted[:args.max_games]',
     '            wanted = wanted[-args.max_games:]'),
    ("D4-empty-known-set-tolerated",
     "treats an empty manifest listing as 'we hold nothing' and re-fetches everything",
     '    if not keys:\n        raise KnownIdsUnavailable(',
     '    if False:\n        raise KnownIdsUnavailable('),
    ("D5-unreadable-manifest-skipped",
     "skips a manifest it cannot read, silently under-counting what is held",
     '            raise KnownIdsUnavailable(f"could not read {key}: {type(error).__name__}: {error}")',
     '            continue'),
    ("D6-known-ids-failure-is-generic",
     "reports a missing known-id set as an ordinary crash, losing the distinct signal",
     '        exit_code = 4',
     '        exit_code = 1'),
    # D7 originally mutated an early-exit branch for the empty-remainder case. It survived,
    # and the cause was redundancy rather than a weak test: the ordinary path already fetches,
    # packs and uploads nothing when the remainder is empty, so the early exit only duplicated
    # it (and recorded the run twice). The branch was deleted; what remains worth pinning is
    # the explicit marker that tells a reader "zero" from "broken".
    ("D7-no-explicit-zero-marker",
     "drops the fetched=0 line, so a nothing-new run is indistinguishable from a broken one",
     '            log("fetch", fetched=0, reason="every discovered game is already in S3")',
     '            pass'),
    ("D8-daily-manifests-not-counted",
     "builds the known set from the backfill only, so its own prior runs are re-fetched",
     "                 or Path(row['key']).name.startswith('daily-'))]".replace("'", '"'),
     '                 )]'),
    ("C12-no-end-marker-on-error",
     "skips the exit marker on the failure path, so a crashed run looks truncated-but-quiet",
     '    log("end", exit=exit_code, seconds=run["seconds"])',
     '    if exit_code == 0:\n        log("end", exit=exit_code, seconds=run["seconds"])'),
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="B4 mutation drive")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    return run_drive(drive="b4-collector-mutations", target=TARGET, tests=TESTS,
                     mutants=MUTANTS, out=Path(args.out))


if __name__ == "__main__":
    sys.exit(main())
