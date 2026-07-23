# Lab-notes reorganization — design

Date: 2026-07-23
Status: approved design, pending implementation plan

## Problem

The laboratory notes have accreted across three eras (Bronze→Gold, Gold→Legend, Legend) into
~604 KB of markdown in `docs/` (28 files, only ~5 live) plus 2.4 MB of PDF/HTML snapshots, a
292 KB / 4,125-line master journal whose critical "Knowledge retained" section sits mid-file,
and a 227 KB Gold-era ledger. Staleness is managed by chained "superseded, see X" banners, some
of which are themselves stale (README named resident `6557204`; actual is `6561795`). A session
today reads ~330 KB (journal + handoff + AGENTS.md) to answer two questions: *what is true now*
and *is this proposal already closed*.

## Decisions (user-approved 2026-07-23)

1. **Optimization target:** session startup cost — minimize what must be read to resume work
   and to legality-check a proposed experiment.
2. **History handling:** immutable, relocate only. No historical note is rewritten or deleted;
   bulk reduction comes from moving superseded files unchanged and adding a small distilled
   top layer of *new* text.
3. **Approach:** layered knowledge head (STATE + CONSTRAINTS) + era archive + ledger volumes.
4. **Old bulk:** Gold-era ledger and PDF/HTML snapshots archive **in git** (no external
   migration of docs).

Out of scope: the per-experiment reproducibility layer
(`data/analysis/live-agent-6553250/dNNN-*` protocol/result/lock files, 2,230 entries) is
untouched; `docs/plays/` stays (live input of `sim/validate_replay.py`); no storage-policy
migration is part of this work.

## Target layout

```
docs/
  STATE.md                       NEW  live head, hard budget ≤150 lines
  CONSTRAINTS.md                 NEW  check-before-propose knowledge base
  mechanics.md                        live reference (referee-verified mechanics)
  statement.md                        live reference (puzzle statement)
  storage-policy.md                   active policy
  storage-migration-2026-07-23.sha256 active manifest
  plays/                              live workflow data (replay validator input)
  superpowers/                        specs/plans (this doc lives here)
  archive/
    INDEX.md                     NEW  one line per file: old path → new path, era, what it
                                      was, what superseded it
    bronze-to-gold/                   27 items (list below)
    legend/                           8 files (list below)
data/analysis/live-agent-6553250/
  legend-top3-experiment-cycle-2026-07-18.md       VOLUME 1 — frozen (one appended freeze
                                                   note; no other edit, ever)
  legend-top3-experiment-cycle-vol2-2026-07-23.md  NEW — live ledger, D167+
```

## File disposition

**`docs/archive/bronze-to-gold/`** (Bronze/Silver/Gold eras, content ≤2026-07-12):
`ROADMAP.md`, `arena-queue.md`, `BOSS5-FINDINGS.md`, `boss5-game-analysis.md`,
`player-loss-analysis.md`, `motion-findings.md`, `refactor-goal.md`, `pressure-aware-farm.md`,
`map-value-ownership.md`, `session-handoff-total-map-value-ownership.md`, `conclusions.md`,
`session-handoff-2026-07-11.md`, `strategic-rethink-2026-07-11.md`,
`discussion-2026-07-11-ceiling-and-expressiveness.md`, `silver-experiment-log.md`,
`statement_bronze.md`, `statement_bronze_full.md`, `best-bot-v1.4.5.pdf`,
`best-bot-v1.4.5.html`, `best-bot-v1.4.5.rs`, `v1.4.1-algorithm.pdf`, `v1.4.1-algorithm.html`,
`v1.4.1-nostarve-readable.rs`, `bot-architecture.html`, `troll-farm-bot.pdf`,
`troll_farm_dom_dump.html`, `troll_farm_play.html`, plus `cgauto/HANDOFF.md` (moved in from
`cgauto/`).

**`docs/archive/legend/`** (2026-07-13..22, superseded by STATE/CONSTRAINTS/vol 1):
`session-handoff-2026-07-16.md`, `hierarchical-controller-roadmap-2026-07-17.md`,
`improvement-roadmap-2026-07-16.md`, `alternative-approaches-roadmap-2026-07-16.md`,
`residual-search-iteration-2026-07-16.md`, `portfolio-geometry-prospective-gate-2026-07-16.md`,
`portfolio-motion-followup-2026-07-16.md`, `portfolio-prospective-gate-2026-07-16.md`.

All moves are `git mv` (byte-identical, rename-detected). Filenames never change.

## STATE.md contract

Rewritten in place whenever facts change; it is live state, not a record — the ledger is the
record. Hard budget: 150 lines. Sections:

1. **Live identity** — resident agent/submission IDs, source artifact + SHA-256, submit-helper
   default, last ladder read (rank/score/date).
2. **Goal** — Legend rank ≤3, mature read + confirmation; moving rank-3 bar noted.
3. **Standing rules** — arena writes need explicit user authorization; fresh-vs-mature scoring
   artifact (never churn submissions); sealed resources (maps 9,844,200–215, official-map
   holdout, 11 sealed field games); substrate rule (exact-resident anchoring per D158/D161);
   throttle/burst limits.
4. **Open thread** — current hypothesis and next experiment (at adoption: D167
   acquisition-path recovery → trajectory-conditioned semantic successor-job value), plus the
   top 1–3 queued hypotheses. Replaces vol 1's frozen "Provisional next-hypothesis queue".
5. **Reading order & pointers** — CONSTRAINTS.md, current ledger volume, AGENTS.md,
   storage-policy.md, archive/INDEX.md; one line noting that pre-2026-07-23 doc references
   resolve via `docs/archive/`.
6. **Last-updated stamp.**

## CONSTRAINTS.md contract

Freshly written distillation (new text; vol 1 keeps its original "Knowledge retained" section
byte-intact). Purpose: a proposal is checked against one section before any protocol is
frozen. Entry format: one bullet = claim + decisive number + evidence pointer (`D161`,
`Phase 10`, or an archive path). Target ≤ ~150 bullets / ~30 KB by deduplicating to one bullet
per closed *class* (the dNNN result files keep per-experiment detail).

Classes:
(a) workforce & scaling; (b) imitation & offline value learning; (c) substrate/evaluation
validity (dead proxies, pairing limits, retired zoos); (d) denial & opponent-crop;
(e) renewal & farm grammars; (f) wrappers, residuals, online-search latency;
(g) arena measurement & platform behavior; (h) meta-lessons (execution-class-only transfer,
no tuning on consumed blocks, isolation discipline).

Maintenance: append-only. A constraint is never deleted; if overturned, the old bullet is
marked `[overturned by dNNN]` and the new entry appended.

Seeding sources (coverage-audited during implementation):
1. vol 1 "Knowledge retained between cycles" (lines 2226–2506);
2. closure verdicts in vol 1 entries D29–D166 and the "Current iteration" rolling summary;
3. Phase 1–21 closures in `session-handoff-2026-07-16.md` and vol 1;
4. Gold-era standing lessons still binding (measurement deltas-only policy, fresh-vs-mature
   artifact, execution-class transfer record) from `arena-queue.md` and the 07-11 docs.

## Ledger volumes

- Vol 1 gets exactly one appended entry: `## 2026-07-23: volume frozen at D166 — continue in
  legend-top3-experiment-cycle-vol2-2026-07-23.md; distilled state → docs/STATE.md, closed
  branches → docs/CONSTRAINTS.md`. No other edit, ever.
- Vol 2 opens with a ~10-line header: objective pointer to vol 1, entry obligations, size cap.
  Entry style continues unchanged from vol 1.
- Per-experiment obligations: ledger entry (as today) + CONSTRAINTS bullet for anything
  closed + STATE.md open-thread update.
- Freeze trigger: the first session that ends with the live volume over 100 KB freezes it the
  same way and opens the next; STATE.md always names the live volume.

## Companion edits

- `README.md`: fix the stale state banner to point at `docs/STATE.md` (live doc, editable).
- `AGENTS.md`: reading order becomes STATE → CONSTRAINTS (before proposing) → current volume
  tail; storage sections unchanged.
- Functional path strings in code updated: `cgauto/make_bot_pdf.py` default output →
  `outputs/troll-farm-bot.pdf` (external root, keeps docs/ clean);
  `cgauto/portfolio_geometry_prospective_gate.py`, `cgauto/portfolio_prospective_gate.py`,
  `cgauto/portfolio_motion_followup.py` `protocol_document` strings → archive paths;
  `cgauto/ramp.py` docstring reference → archive path.
- Rust/Python doc-comments referencing moved files are left alone (filenames are stable;
  archive/INDEX.md maps old → new).
- Claude memory (`MEMORY.md` + `legend-era-state.md`) repointed after implementation.

## Verification

1. Every move appears as a 100% rename in `git diff --cached -M100% --stat` (byte-identical).
2. Coverage audit: every "Knowledge retained" bullet and every D29–D166 / Phase 1–21 closure
   maps to a CONSTRAINTS bullet — checked off one by one during implementation.
3. Post-conditions: `docs/` root ≤ 10 entries; resume+legality read
   (STATE + CONSTRAINTS + AGENTS + vol 2) ≤ 50 KB (vs ~330 KB before).
4. `rg` finds every archived filename under `docs/archive/`; archive/INDEX.md lists all 36
   moved files (27 bronze-to-gold from docs/ + 1 from cgauto/ + 8 legend) with old paths.
5. Python and Rust suites pass (only string-constant edits touch code).
