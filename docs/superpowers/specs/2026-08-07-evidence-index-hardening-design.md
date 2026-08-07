# Evidence index hardening + hypothesis backlog — design

**Date:** 2026-08-07
**Author:** `local_claude_1` (coordinator/integrator)
**Status:** approved, pending implementation plan

## Problem

The project has no working way to store a backlog of open questions or trace conflicts between
reviewers. Disagreements live in message bodies on agent branches, where they are invisible.

A decision-evidence system already exists — `docs/evidence/`, built as a pilot on 2026-07-30 with
a 21-field schema, two tools, and 25 passing tests. It is unused, for two measured reasons:

1. **Citation rot is total.** 9 of 11 records fail validation. Every record citing
   `docs/CONSTRAINTS.md` by line number is broken, because that document is append-heavy at the
   top and every insertion silently shifts all citations below it. Measured drift is consistently
   ~+40 lines. The validator correctly detects this; the locator design cannot survive it.
2. **Nothing was ever ratified.** All 11 records are `review state: proposed`. Under the schema's
   own rules a record becomes canonical only when an integrator merges it after validation passes.
   The pilot produced a working machine and no accepted data.

The cost of not having this is concrete: D89a `banana_seed_factory` (2026-07-21) is a working
banana mechanism — 256/256 activation, mean paired margin +79.441, rejected only on a safety gate
— and eight subsequent implementation attempts over roughly a week never cited it.

## Goal

A **working hypothesis backlog**: a live queue of open questions and reviewer conflicts that work
can be pulled from. Historical decision records matter insofar as they keep that queue honest.

Non-goal: comprehensive historical coverage. That is queued separately as
`coordination/tasks/20260807-historical-artifact-curation.md`.

## Design

### 1. Schema v2 — git-pinned locators

`source` becomes an immutable coordinate:

| field | required | meaning |
|---|---|---|
| `commit` | yes | 40-char SHA, must be reachable from `main` |
| `path` | yes | repo-relative path, as it existed at `commit` |
| `locator` | yes | `lines N-M`, interpreted **at that commit** |
| `quote` | no | verbatim excerpt, used only for the currency check |

`json_pointer` remains an alternative to `locator` for JSON sources, resolved at the pinned
commit.

Validation splits into two signals:

- **Hard error** — commit unreachable from `main`; path absent at that commit; line range out of
  bounds; or the excerpt at that commit missing the numeric tokens the claim's `display` asserts.
  The existing `require_excerpt_tokens` check is preserved unchanged, now pointed at immutable
  ground.
- **Soft warning** — `quote` no longer appears in the *current* file. This is the drift signal
  that pinning would otherwise hide. It surfaces in a `## Drifted` section of the generated index
  and never fails the build.

The distinction is the point: errors mean *this record is broken*; warnings mean *the world moved,
someone should look*.

**Why pinning rather than quote-search.** Measured on the real corpus: quote-search relocates 5 of
9 broken records uniquely, but D30's evidence matches 18 places (its only numeric token is `80`)
and D172a's claim spans multiple lines. Git-pinned coordinates are exact in every case, and
migration is fully mechanical — all 8 records carrying numeric claims already contain *correct*
line numbers that validate perfectly against the commit that authored them. No human judgement is
required to migrate.

**Reachability.** Pinned commits must be ancestors of `main`. This is safe under the standing
procedure in `docs/BRANCH-INTEGRATION-RUNBOOK.md`, which merges before deleting — verified: even
branch tips deleted on 2026-08-07 remain reachable from `main`.

### 2. Hypothesis tier

A new lightweight kind. Six fields, because entry cost is what killed the pilot:

| field | meaning |
|---|---|
| `id` | `Q<n>` — new namespace; `H`/`N` remain the existing hypothesis series, `D` the decision series |
| `question` | the open question, stated so it could be settled |
| `origin` | exact v2 message paths where it was raised |
| `positions` | agent → stance, with optional evidence references |
| `status` | `open` / `investigating` / `resolved` / `void` |
| `next_action` | what would settle it |

No populations, evidence strengths, `does_not_prove`, or reopening conditions. Those are the
closing tax, not the entry tax.

**Graduation.** When a hypothesis is resolved with real evidence, a full 21-field record is
authored and the hypothesis's `relations` links to it. The lightweight entry is not deleted; the
trail from question to answer is the product.

Files: `docs/evidence/hypotheses/Q<n>.md`. Generated view:
`docs/evidence/generated/OPEN-QUESTIONS.md` — this view *is* the backlog.

### 3. Authorship

The coordinator curates. Agents raise conflicts in normal v2 messages as they already do; the
coordinator extracts and records them. One writer, no merge collisions — `coordination/status/*.md`
conflicts on nearly every branch merge, and a shared backlog file would do the same.

### 4. Seed content

Eight live open questions from the 2026-08-06/07 review cycle: whether v4 is really the best
rebuild base; whether D89a's opponent-production leak is repairable; whether D-1 raw-zero is
feasible with one unlocalised episode; the invariant blind spot on opponent production; whether
`pre_review.py` earns its place; D-2/D-3/D-8 being unexercised rather than clean; the terminal-D7
detector-semantics fix; and P4 calibration ratification.

### 5. Ratification

Once the migration lands and validation is green, the 11 existing records move from `proposed` to
accepted by integrator merge. This is the step the pilot never reached.

## Components

- `cgauto/check_decision_evidence_index.py` — commit-pinned resolution, warning channel,
  hypothesis-tier validation, reachability check.
- `cgauto/build_decision_evidence_index.py` — emit `OPEN-QUESTIONS.md` and the `Drifted` section.
- `cgauto/migrate_evidence_locators.py` (new, single-use) — pin each existing record to the commit
  that last touched it.
- `docs/evidence/SCHEMA.md` — bump to version 2, document both tiers.
- `tests/test_decision_evidence_index.py` — extended.

## Error handling

| condition | behaviour |
|---|---|
| `commit` missing or not an ancestor of `main` | hard error naming the record and claim |
| `path` absent at that commit | hard error |
| line range out of bounds at that commit | hard error |
| numeric tokens absent from the pinned excerpt | hard error (the record is wrong) |
| `quote` absent from the current file | warning; listed under `Drifted` |
| hypothesis missing a required field | hard error |
| hypothesis `resolved` without a `relations` link to a record | hard error |

Generated files remain deterministic and hash-manifested; hand-editing them stays forbidden.

## Testing

TDD against the existing 25-test suite. New cases: valid pinned record; unreachable commit;
path absent at commit; out-of-range lines; missing tokens at the pinned commit; quote drift warns
but does not fail; minimal valid hypothesis; hypothesis missing a required field; `resolved`
hypothesis without a graduation link; generated `OPEN-QUESTIONS.md` is deterministic.

Acceptance: full suite green, and `check_decision_evidence_index.py` exits 0 on all 11 migrated
records plus the 8 seeded hypotheses.

## Out of scope

Historical backfill beyond the existing 11 records — separate task
(`20260807-historical-artifact-curation.md`). Rewriting `docs/CONSTRAINTS.md` or `docs/BACKLOG.md`;
this system cites them, it does not restructure them. Any change to
`docs/CONSTRAINTS.md`'s content or the projection's advisory status.
