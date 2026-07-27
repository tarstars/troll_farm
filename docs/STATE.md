# STATE — Troll Farm (single entry point)

Last updated: 2026-07-27. This file is live state, not a record — the ledger volumes are the
record. Hard budget: 150 lines. Rewrite it whenever facts change.

## 1. Live identity

- Player `tass`, Legend practice ladder (contest ended 2026-05-25 — no deadline).
- Resident: agent `6561795`, submission `41015603`.
- Source: `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`
  (62,725 bytes, slim Yamo/Orchard + pre-seed + orchard coverage).
  SHA-256: `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`
- `cgauto/api_submit.py` default = that exact source. Keep it that way.
- Last ladder read: rank 43/110 @ 21.97, 203 listed battles (2026-07-27 ~13:07 UTC, passive
  D61p snapshot). Score is bit-identical to 2026-07-23 — CodinGame's own updateTime shows no
  recomputation since 2026-07-23T02:45Z, so fresh-agent scores freeze between rare ladder
  recomputes; passive maturity recovery is slower than previously assumed.
- Rank bar (2026-07-27): 1. delineate 31.00, 2. norxondor_gorgonax 29.52, 3. MSz 28.22.

## 2. Goal

Legend **rank ≤ 3** on a mature read plus a later confirmation (journal vol 1 "Completion
rule"). Rank-3 bar was 28.11 at Phase 21 — a moving reference, not a frozen target.

## 3. Standing rules

- Arena writes require explicit user authorization. No exceptions.
- Never churn submissions: fresh submissions read 3–4 points below matured ones (proven by
  failed same-code A/A on 2026-07-16). Restores/candidates burn standing.
- Sealed, do not open: maps `9,844,200–9,844,215`; the official-map holdout; the 11 sealed
  field games from the D164 snapshot.
- Substrate rule (D158/D161): every controller uses exact Yamo/Orchard resident
  fallback natively, or first proves same-panel dominance over it. D40/q6 is dead as a
  competition substrate.
- External play bursts ≤ 12 games; stop on HTTP 422 or degenerate results.
- Bulk writes: preflight `python3 cgauto/check_external_storage.py --required-free-gib <N>`
  (see `AGENTS.md` + `docs/storage-policy.md`). YT root:
  `//home/delivery_ml/research/tarstars/troll_farm`.

## 4. Open thread

- **D167 DONE 2026-07-27: BANK_SEED frozen-eligible** (135/135 local, 71.4% top-5 field,
  gates clean; OPPONENT_DERIVED closed; top agents pre-carry seeds through suppression
  22/49 vs resident 0/1,024). **Next experiment — D168**: bounded BANK_SEED successor
  option as a causal test — exact resident KEEP, arm at the P→S transition (weigh a
  pre-carry variant), gates: prefix/fallback parity, activation breadth (both seats, ≥6
  families), mean value + own-score protection, tail safety. Kill: value < +2 or negative
  worst family → close hand-written successor controllers; branch moves to rollout-valued
  semantic actions inside B2.1.
- Queue after D167 (reorder only from written evidence):
  1. If D167 closes: family-robust closed-loop objective on the resident substrate — the
     explicitly skipped D109 question (see vol 1, D157 audit).
  2. Standing: let the resident mature undisturbed; no arena writes without authorization.
- Full prioritized backlog with gates and kill rules: `docs/BACKLOG.md` (2026-07-27).
  Pending ops: data-cleanup plan `docs/superpowers/plans/2026-07-24-data-footprint-cleanup.md`
  is approved but unexecuted.

## 5. Reading order & pointers

1. This file.
2. `docs/CONSTRAINTS.md` — check BEFORE proposing any experiment.
3. Live ledger: `data/analysis/live-agent-6553250/legend-top3-experiment-cycle-vol2-2026-07-23.md`
   (frozen history: `...-2026-07-18.md` = vol 1, 292 KB, includes Phases 1–21 + D1–D166).
4. `AGENTS.md` (process), `docs/storage-policy.md` (storage/YT), `docs/mechanics.md` (game).
5. Superseded docs: `docs/archive/INDEX.md`. Pre-2026-07-23 doc references resolve via
   `docs/archive/`.

Per-experiment obligations: ledger entry in the live volume; a `docs/CONSTRAINTS.md` bullet
for anything closed; update §4 of this file. First session ending with the live volume over
100 KB freezes it (one appended note) and opens the next.
