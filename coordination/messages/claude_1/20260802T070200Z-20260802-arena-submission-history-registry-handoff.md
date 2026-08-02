# Handoff: 20260802-arena-submission-history-registry

- From: claude_1
- To: local_codex_1
- CC: chatgpt_1, user
- Created UTC: 2026-08-02T07:02:00Z
- Task: 20260802-arena-submission-history-registry
- Branch: agent/claude_1
- Handoff commit: 845e83da114444fc7b7313d8ef2118fb35a31198
- Base commit: dd14d808bf7dfafdf8cee2cfa88540faf8cfecce
- Requires acknowledgement: yes
- Platform mutation performed: **no** — read-only repository inspection only

## Outcome

The canonical Arena submission history exists and is queryable. 9 source families, 17
deployment records, 35 observations, 5 explicit unresolved items, built deterministically
from an explicit input manifest.

The registry contradicts the 2026-08-02 selection. Source-level, all history, unfiltered:

| source family | mature runs | median | worst | best | latest | dispositions |
|---|---:|---:|---:|---:|---:|---|
| `opponent-crop-b100-e6-slim` | 1 | 24.89 | 24.89 | 24.89 | 24.89 | rejected |
| `preseed-orchard-coverage-slim` | 4 | 24.19 | 23.05 | 24.77 | 23.05 | retained/restored/displaced |
| `owner-far-denial-no-return-d3-slim` | 1 | 22.99 | 22.99 | 22.99 | 19.37 | **active** |

A `preflight` on the far-denial source now prints the preseed resident's four mature runs
(24.1/142, 24.77/160, 24.28/160, 23.05/171, plus the excluded 24.4) directly under
far-denial's single 22.99, with `SINGLE_MATURE_RUN` and `LATEST_BELOW_MEDIAN` warnings and
the line "a single high historical run is NOT such a reason". That is the incident, encoded
as a test.

## Diff scope

- `cgauto/submission_history.py` — new; build/validate/query. No existing `cgauto/` file was
  touched and no formatter was run (protocol §7).
- `data/analysis/arena-submission-history-inputs.json` — new; the curated input manifest.
- `data/analysis/arena-submission-history.json` — new; the generated projection.
- `data/analysis/arena-submission-history-provenance-2026-08-02.md` — new; coverage report.
- `docs/arena-submission-history-schema-2026-08-02.md` — new; schema and query note.
- `tests/test_submission_history.py` — new; 38 tests.
- `coordination/messages/claude_1/…`, `coordination/status/claude_1.md`,
  `claude_1/inbox-watermark.txt` — my own namespaces.

Not touched: `docs/STATE.md`, `docs/BACKLOG.md`, `docs/CONSTRAINTS.md`, the ledger volumes,
`cgauto/api_submit.py`, `cgauto/submissions/*`, the task record. Suggested text for STATE
and BACKLOG is at the end of this message for you to apply or discard.

## Validation

- `python3 cgauto/submission_history.py build --check` — OK, byte-identical to a fresh build.
- `python3 cgauto/submission_history.py validate` — OK, 35 observations validate cleanly.
- 38/38 tests pass. **Caveat, stated plainly:** this machine has no `uv`, no `pytest` and no
  `pip`, so `uv run pytest tests/test_submission_history.py` **was not run**. The suite was
  executed with a minimal harness supplying `pytest.fixture`, `pytest.raises`, `capsys` and
  `tmp_path`. The tests are ordinary pytest tests needing no adaptation, but they have not
  been observed under pytest itself. Please run the canonical command once when you review.
- `sha256sum rust/src/bin/yamo_orchard_live.rs` — `fff6669b0bc0b15b…`, unchanged.
- `git status --short` — clean.

## Measurements

Every number in the registry is a **historical live-ladder** measurement transcribed from an
immutable checkpoint or execution report. There are no local simulations and no projections.
The one derived quantity is the per-source median across repeated deployments; it is labelled
as such and never presented as a platform reading.

## Design decisions worth your review

1. **Source families are keyed by exact SHA-256**, not by name or lineage. Three deployments
   of the far-denial hash (41070584, 41071034, 41079354) are one family.
2. **Runs, not reads.** Each deployment collapses to its largest-sample mature observation
   before aggregating, so 41012256's four checkpoints are one run, not four.
3. **Ranking is by median then worst, never by maximum**, and the dispositions column is on
   the table — otherwise `opponent-crop-b100-e6-slim` would top `best` at 24.89 despite
   having been rejected by its own protocol against a matched control.
4. **Maturity is derived, with two rules no manifest entry can bypass:** a faulted
   observation is `invalid`, and a public-leaderboard read can never be mature-class.

## Known failures and assumptions

**The acceptance-4 discrepancy, unchanged from `20260802T065200Z`.** The task requires the
fixture to show "far-denial mature repeats 22.99/160 and **19.37/160**". The 22.99/160 half
is fully backed. The 19.37 half is **not backed at that quality**: it is an unauthenticated
public-leaderboard read at about T0+40 min with no game count, no catastrophe count and no
identity audit, and "/160" appears nowhere in the repository. I implemented the
evidence-faithful reading — score 19.37, `games_finished: null`, `provisional` — and the
fixture asserts far-denial's *latest* is 19.37 at unknown sample while its *mature* one is
22.99/160. The warning against selecting on the 22.99 maximum fires either way. If you want
the literal criterion, it needs a real 160-game submission-scoped audit of `6589510`, which
only you can produce; the fixture change is one line afterwards.

**One maturity override exists** — the 24.4 pre-reset room read, whose sample size was never
recorded. It is flagged `manifest_override` and excluded from every aggregate.

**Timestamp error of mine, already corrected** in `20260802T065800Z`: the message
`20260802T072000Z-…-evidence-transcription.md` is filename-dated ~23 minutes ahead of the
host clock. It does not affect the registry (pinned by content hash), but **do not advance
an inbox watermark to that value.**

**Coverage boundary.** Nothing before 2026-07-16 is transcribed; five unresolved items are
listed explicitly in the manifest and printed by every `preflight`.

## The finding I most want you to act on

The **live leg has nine games of submission-scoped evidence.** Agent 6589510 / submission
41079354 has only the initial health checkpoint; everything after it is public-leaderboard
data with no game count. Its source family has a single mature run. The registry therefore
cannot say whether the restore is performing at 22.99 or at 19.37, and it will not pretend
to. A submission-scoped maturity audit, added to the manifest, would close the largest gap
in the registry and it concerns the bot that is playing right now.

Two secondary findings in the coverage report: the highest score in the whole registry
(24.89/160) belongs to a **rejected** source, and the funding-first agent went **down** from
16.97 at 11 games to 16.37 at 265 — against the standing assumption that fresh reads sit
3–4 points below matured ones.

## Integration notes

1. `data/analysis/arena-submission-history.json` is generated. If a merge conflicts on it,
   take either side and re-run `build`; `build --check` then proves the result.
2. Nothing here imports from or modifies existing `cgauto` modules, so ordering against
   other branches does not matter.
3. Suggested `docs/BACKLOG.md` / `docs/STATE.md` line, yours to edit or drop:
   *"Arena submission history registry DONE — `cgauto/submission_history.py` plus
   `data/analysis/arena-submission-history.json`; run `preflight <source>` before any
   candidate selection. All-history source-level medians: preseed 24.19 over 4 mature runs,
   far-denial 22.99 over 1."*

## Requested action

Review and integrate this exact commit. Run `uv run pytest tests/test_submission_history.py`
once under the real virtualenv and tell me if anything differs from the 38/38 I observed.
Rule on the acceptance-4 discrepancy. No Arena action is requested or implied by any part of
this work.
