# Auto-refresh of the subject library after an owner KEEP — DESIGN ONLY, NOT DEPLOYED

Card `20260821-champion-subject-library` deliverable 3. **Nothing in this file is installed.**
No unit, timer, cron entry or `night_runner.py` line is changed by this card; deployment goes
through the VM deploy-card route after `codex_1`'s review, exactly as the OSC-031 runner did.

## What it is for

The rule the owner approved on 2026-08-21 is that a recorded episode belongs to the bot that
produced it, so a library outlives its subject by exactly zero champions. The failure this hook
prevents is the one we just lived through: a KEEP lands, the champion changes, and the fixtures
keep being cited for weeks until someone measures that 23 of 34 of them are a different game.

## Trigger — the KEEP, not the night

`night_runner.py` never rules KEEP/REVERT; it publishes the morning sheet and the owner rules
(`cgauto/night_runner.py`, `verdict_block`: *"KEEP/REVERT is the OWNER'S ruling, never the
runner's"*). So the hook must not fire on a session boundary. It fires on the **recorded
consequence** of a KEEP, which is a single observable fact: the champion of record changes.

    champion_of_record := the `sha256` the integrator records when the owner rules KEEP

Concretely: a `coordination/champion-of-record.json` written by the integrator at KEEP time,
holding `{sha256, source_path, source_commit, ruled_utc, ruling_message_id}`. The hook compares
that digest against `oscillation-library-<prefix>/library/index.json:subject.sha256`. Equal →
nothing to do, exit 0, no log noise. Different → refresh. That file does not exist yet; creating
it is part of the deploy card, and until it does the hook is a no-op by construction rather than
a guess about which branch is champion.

## What it runs

Three commands, all of which exist and are exercised by this card:

1. `python3 <libdir>/run_panel.py --workdir <scratch>`
   — the champion floor panel, sources materialised from their `source_git` pin and
   re-checked against the digest before compiling.
2. `python3 <libdir>/build_subject_library.py --games <scratch>/games/games.jsonl.gz`
   — the accepted builder, called unmodified, digest-checked before it will run at all;
   writes `library/` + `identity.json`.
3. `python3 <libdir>/build_pages.py`
   — the accepted viewer generator, with this tree's pinned situation count.

Then, gating publication:

4. `python3 -m unittest test_champion_library` (with `OSC_LIB_REPLAY=1`) — 24 tests, and
5. `python3 verify_identity.py` — every case must reproduce on its own subject.

**Fail closed.** If 4 or 5 fails, nothing is published and the hook HALTs the same way
`night_runner.halt` does: write the reason to the ledger, publish it, and stop. A library that
cannot replay its own episodes is worse than a stale one, because it looks current.

## Where the output lands

A NEW directory per champion, `claude_1/banana-restoration-r2/oscillation-library-<sha8>/`,
never an overwrite of an existing one. The old tree stays, with its README marking whose bot it
belongs to — the same treatment the `oscillation-library/` parent-lineage tree got. Viewer pages
land beside it in `<libdir>/viewer/`, so a link in an owner note keeps working for as long as the
commit that contains it.

`git` publication reuses `night_runner.git_publish` (union-merge ledger, rebase-abort,
fail-closed HALT), on the runner's own branch, with the paths enumerated explicitly.

## Cost on the VM

Measured on this host (4 cores, 15 GB; the panel config declares `processes: 8`), warm bot cache:

| step | wall clock |
|---|---|
| floor panel, 240 games × 200 turns | **10 s** (14 s on the first run of the session) |
| harvest + identity | < 1 s |
| viewer pages (21) | < 1 s |
| suite with `OSC_LIB_REPLAY=1` | ~5 s |
| **total** | **≈ 20 s warm; ≈ 60–90 s cold, dominated by one `rustc` build** |

This is small enough that it can run inline on the KEEP path rather than as a queued job, and
small enough that a re-run to check a suspicion is free. Disk: `library/` 21 JSON files ≈ 1.1 MB,
viewer 1.8 MB, games dump 545 KB in scratch (not published).

## What it must NOT do

- **Not delete the previous library.** Never the only copy of an artifact (`AGENTS.md`).
- **Not re-rule anything.** The mechanism carry-over table is regenerated, and it may only say
  "no exhibit", never "fixed".
- **Not touch the resident, the Arena, or any candidate.** It reads a champion and writes a
  record.
- **Not fire on its own schedule.** No timer. If the champion has not changed, it does nothing.

## Open question for the reviewer

The trigger file `coordination/champion-of-record.json` is a new integrator obligation at KEEP
time. The alternative — deriving the champion from the latest KEEP ruling message — means the
hook parses prose, and I would rather it read one machine field than infer a ruling. Whether
that obligation is acceptable is `local_claude_1`'s call as integrator, and the deploy card
should not be written until they say.
