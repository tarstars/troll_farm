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

- Arena writes require explicit user authorization. No exceptions. **STANDING
  AUTHORIZATION 2026-07-28: if D171a returns QUALIFIED (all frozen local gates pass),
  execute promotion protocol B4.1 without further ask** — capacity A/A → candidate
  submission → +20/+35/+50-min reads → frozen bands (≥+0.5 keep / ≤−0.5 or inconclusive
  → revert) → exact-resident restore on any failure. Scope: this one candidate only.
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

- **D167→D168 DONE: hand-written successor controllers CLOSED** (BANK_SEED
  frozen-eligible but both scripted options failed value; motif survives only as a
  rollout-valued option). **D169 DONE 2026-07-27: PASS.** Unified resident-native option
  envelope (OPT_RETURN + D163's 3 resource options, incl. B3.1-trigger arming) on the
  full 1,024-task panel: **+10.671 mean, CI [+9.420, +11.922], 65% improved, 0
  regressions, tails better than control.** Every option is negative always-on; all
  value is per-game selection. Clears every frozen gate — no D169b needed.
- 🛑 **2026-07-28 (final): D170b CLOSED-AT-PHASE-2 — the Tier-2 closed-loop program is
  CLOSED per its frozen kill rule.** Mechanics fully valid (repair verified, 8/8 fits
  trained, all 13 arms live); all four objectives converged to always-KEEP (0/8 admitted;
  P(invoke) ≤3.3%; sampled-invoke value −1.0..−2.3 fit-side). Adjudicated: the +10.7
  envelope's positive contexts are unlearnable by on-policy terminal-reward training at
  any sane budget (~200 samples/arm vs SD≈26 noise); objective choice is irrelevant in
  this regime (the D109 question's answer). Veto panel and sealed confirmation block
  remain untouched. **OWNER DECISION 2026-07-28: (b) HOLD.** Maintenance mode ACTIVE and
  set up: daily collection cron installed (05:17, `# troll-farm-wide-collect`; corpus
  8,131 and compounding); B3.2/B3.3 audits DONE (motion clean at 4× scale; field rates
  stable except D164's motif population rate corrected 72%→49.7%, gate unaffected).
  **Best open maintenance lead: B3.4** — same-two-cell oscillation (18/194 games, worst
  131 turns frozen carry, 2.8× catastrophe-enriched; execution-class). Housekeeping
  B5.1/B5.3 open. No Tier-2 successor authorized; the dense-counterfactual-credit design
  stays on the shelf pending any future (a) decision; goal re-scoping remains open.
  D170a's CLOSED-AT-PHASE-1 was implementation invalidation (repaired in D170b); both
  records frozen.
- **2026-07-28 (latest): D172a CLOSED-AT-SELECTION — Tier-2 learning route closed with a
  definitive mechanism.** Signal abundant (40.4% of states ≥+2) yet unlearnable from
  observables (held +0.14..+0.26 vs +1.5 gate; exact labels, both classes). The owner's
  reopening is consumed with a clean scientific answer; see CONSTRAINTS ★FINAL bullet.
  Only untried observation class: spatial planes on the official substrate (reopening =
  new owner decision against the recorded evidence). **Project posture: maintenance mode
  + the execution-class pipeline. In flight: D173a harvest-before-chop** (the richest
  vein found: 9.62 pts/game net lost to a missing HARVEST action class; QUALIFIED would
  stop at the arena gate needing a NEW owner authorization).
- **2026-07-28: D169 PASS adjudicated by Fable; STOP marker cleared. D170 protocol
  FROZEN and delegable**:
  `data/analysis/live-agent-6553250/d170a-family-robust-option-policy-protocol-2026-07-28.md`
  — the resurrected D158 four-objective comparison (pooled / capped / own-score-protected
  / group-DRO+protection) on the valid resident-native substrate, closed-loop over the
  D169 vocabulary, budget-1 activation, paired-control reward. Fresh ranges declared
  (train 9,850,000–255; selection 9,851,000–127 as 8 blocks LOBO; sealed confirmation
  9,852,000–063). Gates: admission ≥ +1.5 LOBO / worst family ≥ −1 / own ≥ −0.5;
  veto-only consumed panel ≥ +1.0; confirmation ≥ +2.0 CI>0; deployability int8 ≤100 kB
  p95 ≤20 ms. Kill: no admission → program closes. Post-confirmation: 🛑 STOP for user
  arena authorization. Cheap sessions execute per `docs/RUNBOOK.md`; fillers B3.2/B5.1
  remain available.
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
