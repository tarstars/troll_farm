# STATE — Troll Farm (single entry point)

Last updated: 2026-07-31. This file is live state, not a record — the ledger volumes are
the record. Hard budget: 150 lines. Rewrite it whenever facts change.

## 1. Live identity

- Player `tass`, Legend practice ladder (contest ended 2026-05-25 — no deadline).
- Resident: agent `6561795`, submission `41015603`, live since 2026-07-19, untouched.
- Source: `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`
  (62,725 bytes, slim Yamo/Orchard + pre-seed + orchard coverage).
  SHA-256: `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`
- `cgauto/api_submit.py` default = that exact source. Keep it that way.
- Last ladder read (timestamped snapshot discipline — cite exactly one):
  **2026-07-29T02:17Z cron snapshot: score 21.76, rank ~45** (bar unchanged, gap now
  **6.46**). Drifting down passively as the pool strengthens (22.0 on 07-28, 21.97 on
  07-27) — the score is source-side frozen between rare recomputes, so this is pool
  movement, not decay. Passive maturity is dead as a lever.
- Rank bar: 1. delineate 31.00, 2. norxondor_gorgonax 29.52, 3. MSz 28.22.
- Corpus: **9,082 games** / 469+ agents, compounding daily (cron 05:17 — +951 overnight).

## 2. Goal (RE-SCOPED 2026-07-30 by owner decision)

**Primary: reach a mature score ≥ 25.40** — the current top-10 boundary (Escdemon 25.37),
i.e. **+3.64** from our frozen 21.76. **Interim checkpoint: 24.70** — yamo's score, the
design this bot reproduces, so passing it means the reproduction has surpassed its original
(+2.94). Completion rule unchanged: a mature read **plus a later confirmation**, never a
single spike.

Superseded: Legend rank ≤ 3 (bar 28.22). It was set when passive maturity looked like a
live lever; that assumption died (score is source-side frozen between rare recomputes) and
the target was never revisited. No path to +6.5 has been identified in two months, and the
2026-07-29 terminal synthesis closed all eight known routes for this architecture.

Why ≥25.40 is the right kind of target: **25 Legend agents reach ranks 7–54 on our exact
two-worker roster**, so it is architecturally demonstrated rather than hypothetical.
N1 has now rejected the anecdotal 3–4-point passive-maturity premise for planning:
remaining uplift −0.161, CI [−0.753,+0.457]. The measured policy/architecture gap must do
the work. **A2 has now stopped at its Phase-1 K1**, so it is no longer a current goal path;
waiting is not one either. Rank targets are additionally avoided because pool strengthening
makes the goalpost move in the wrong direction.

## 3. Standing rules

- ★★ **STANDING ARENA AUTHORIZATION, granted by the owner 2026-07-30.** The per-candidate
  permission gate is **lifted**: *"I want to lift this rule about my authorization of
  interaction with arena. Submit anything worth trying."* Scope, as recorded and confirmed
  by the integrator:
  - **Authorized without asking:** submitting a candidate that has passed its frozen
    protocol's gates; the full promotion protocol including the capacity A/A phase; timed
    reads; reverts and exact-resident restore within a cycle.
  - **Still surfaced to the owner BEFORE acting** (not a permission request — a
    notification, because these are not what was authorized): submitting anything that has
    NOT passed frozen gates (i.e. experimenting on the live ladder); any action that would
    abandon a matured score with no qualified candidate in hand; more than one submission
    cycle in flight; anything that could forfeit the ladder slot.
  - **Replacement discipline the integrator applies in place of the owner's gate** — since
    the permission bottleneck is gone, the *evidence* bottleneck is stated explicitly:
    (i) a QUALIFIED verdict from a frozen protocol is required; (ii) expected gain must
    exceed the arena's own noise band (±0.5–1) on its own or bundled with others to exceed
    it, because below that a submission buys an unmeasurable result at a measured cost;
    (iii) the promotion runbook runs in full, no shortcuts; (iv) the owner is told before a
    cycle starts and again when it terminates; (v) every submission id and terminal
    response is logged to the ledger.
  - **Unchanged:** mutations remain serialized through the **single arena controller**
    (now `local_codex_1` by default — see the reassignment note in this section). No peer agent or subagent may submit. The no-churn evidence still binds
    the judgment even though it no longer binds the permission.
- Never churn submissions: fresh reads sit 3–4 points below matured ones; every failed
  trial costs days of standing.
- Sealed, do not open: maps `9,844,200–9,844,215`; the official-map holdout; the 11
  sealed D164 field games; D170's confirmation block `9,852,000–063` (unused, preserved).
- Substrate rule (D158/D161): controllers use the exact Yamo/Orchard resident fallback
  natively or first prove same-panel dominance. D40/q6 is dead as a substrate.
- External play bursts ≤ 12 games; stop on HTTP 422 or degenerate results.
- Bulk writes: preflight `python3 cgauto/check_external_storage.py --required-free-gib N`
  (`AGENTS.md`, `docs/storage-policy.md`). YT root:
  `//home/delivery_ml/research/tarstars/troll_farm`.
- **Multi-agent coordination protocol in force**: `coordination/multi-agent-protocol.md`.
  **Coordinator (integrator) = `local_codex_1` from 2026-07-30** (owner reassignment); arena controller follows the coordinator by protocol default unless the owner directs otherwise. `claude_1` is offline by owner notice; `chatgpt_1` is a contributor. Handover: `coordination/HANDOVER-2026-07-30-claude_1-to-local_codex_1.md`. Hazards (§7) bind every agent: the dev copy
  `rust/src/bin/yamo_orchard_live.rs` stays byte-exact at SHA prefix `fff6669b`
  (library-visible to all experiments); no formatters over `rust/src/bin/` or `cgauto/`
  (locks record hashes); do not disturb `data/raw/games/` or the 05:17 cron.
- **History rewrite: DECLINED by owner 2026-07-30, closed.** Measured gain was 12.9 MB
  (39 MB → ~26 MB) against invalidating all ~380 published commit hashes, four of which are
  cited directly in experiment records. `git gc --aggressive` already reclaimed 14 MB for
  free. The full-history bundle stays on `medium_data` as a backup. Do not reopen.
- Repository pushed to GitHub 2026-07-29 (`origin/session-2026-07-01` current); remote
  message transport is live; full-history bundle on `medium_data`; 1,629 tracked bulk
  artifacts migrated to USB as committed symlinks (digest
  `docs/storage-migration-2026-07-29-tracked.sha256`).

## 4. Open thread

- ★★★ **N1 DONE — PARTIAL / IMMATERIAL:** at score 21.47 and age 10.36d, estimated
  remaining uplift is −0.1612, CI [−0.7525,+0.4567], projected mature score 21.3088.
  The upper bound is only 0.0433 below the frozen cutoff, so do not claim negative aging;
  do close passive maturity as a decision-relevant planning lever.
- **2026-07-29 terminal synthesis:** all eight tested levers for the resident architecture
  are closed. At equal roster it matches strong two-worker peers; the deficit is
  scale-asymmetry survival. Learned selection, closed-loop options, production/farming,
  scaling/mining, harvest changes, execution waste, and suppression fixes did not clear
  their frozen gates. See ledger vol 2 and `docs/D-series-atlas.pdf`.
- ★★ **A2 Architecture-2 STOPPED AT PHASE-1 K1** under
  `docs/A2-programme-charter-2026-07-30.md`; the resident remains untouched.
  - **A2-0a DONE — EXISTS-qualified:** the crop base is sub-critical (R≈0.75) and
    labor-limited. Top-5 reaches worker 3 in 75.6% by median t106 and worker 4 in 41.6% by
    t137; self-planted currency funds 37%/50%. Phase 1 gate: fruit-funded worker 3 in ≥40%
    by about turn 110, plus non-zero own-crop reap.
  - **X1 DONE AND REVIEWED:** core mechanics match; the ~24-fruit/~6-iron starting bank
    was a docs-only omission. A2-0b closes both continued-RNG and strict-validation duties.
  - **A2-0b QUALIFIED AND PROTOCOL-CLOSED.** The locked
    referee path exactly reproduces the historical control (49 catastrophes / 12,749
    negative mass), is byte-identical at one/20 threads, zero-gates critical/unclassified
    issues, and covers all six detectors over 2,048+2,048 trajectories. Referee RNG changes
    1,781/2,048 trajectories (tail 53 / 13,646); legacy evaluation is control only.
  - **A2-1 FAILED K1:** the locked new scheduler establishes/reaps/banks its own crops and
    mines at rosters 2/3, but fruit-funded worker 3 by t≤110 falls from a narrow
    development 206/512 (40.23%) to confirmation **582/2,048 (28.42%)**, below 40%.
    Integrity, thread parity, command quality, and all six detectors pass. The programme
    stops; A2-2…5 are closed, no candidate or Arena action.
- ★ **Breadth strategy:** `docs/APPROACH-REGISTER-2026-07-30.md` is the rolling menu.
  Cheap audits have no value pre-filter; experiments retain the ≥+1.0 rating bar.
  **M1 DONE — DESCRIPTIVE_ONLY:** best held-agent MAE 0.4773 vs 0.4786 zero; no
  wins-per-+1 conversion. **N2 DONE — B4_4_CORRECTED:** group rates reproduce, but its
  all/every-peer, no-loop and causal claims fail. **M2 DONE — NO_ACTIONABLE_MATCHUP:**
  three exact identities clear support, none clear all gates. **M3 DONE:** +10.09 matched,
  CI crosses zero. **M4 DONE:** +0.438, CI crosses; late 60 use four lineages. **M5
  DONE:** −1.44, CI crosses. **N5 DONE:** ceiling 11.99, CI [8.73,15.76] <20. **N6
  CLOSED_AT_DEVELOPMENT:** HIGH +0.559 fails direction/breadth. **E1 NARROWED:** only a
  terminal pairs await N4. **E2 DONE:** 0.335 hindsight move-turn/side-game. **E3 VOID:** tree order closed. **E4 DONE:** mother reverse −0.0855. **E5 DONE:** +0.106, seat 0 loses. **E6 VOID:** seed carry. **E7 DONE:** flip −12.174; hindsight +10.510. **S1 DONE:** full exact infeasible. **S2 GATED:** N4→E1 plus new map representation. **S3 GATED:** distinct combination; specification/model/runtime unresolved. **H10a NARROWED:** 72 spatial +17 decision fields; peer-gated. **L1 PRIMITIVE-ONLY:** 199 exact games; hidden plan/beam unlabeled; peer-gated. **L2/L3 N4-GATED:** sole unconsumed live rank/value surface is N4's two-worker pair; no learner before accepted coverage/value. **N7 DONE:** deploy already slim; sacred fixtures stay exact. **H4 DONE:** 0/17 strict deniable bills. **H7′ DONE:** contention ubiquitous, not strong-cohort. **H3′ SIGNAL:** DiD 0.606; pre-loss 0.510; H3a three-arm value preflight is peer-gated.
- **Coordination:** `local_codex_1` integrates/controls Arena; `claude_1` is offline;
  `chatgpt_1` has N4 Phase A. Inbox: `python3 scripts/inbox_sweep.py --me local_codex_1 --fetch`.
- **Operations:** daily collection cron 05:17; B5.3 migration ripens ~2026-08-03; H12
  weekly surveillance. No Arena cycle is in flight.

## 5. Reading order & pointers

1. This file.
2. `docs/CONSTRAINTS.md` — check BEFORE proposing any experiment.
3. `docs/BACKLOG.md` — live priorities at the top; historical tiers below are the record.
4. `coordination/README.md` + inbox sweep — mandatory for any agent before writing.
5. Live ledger: `data/analysis/live-agent-6553250/legend-top3-experiment-cycle-vol3-2026-07-30.md`
   (vol 2 `...-vol2-2026-07-23.md` frozen after A2-1; vol 1
   `...-2026-07-18.md` frozen at D166). Atlas: `docs/D-series-atlas.pdf`.
6. `AGENTS.md` (process), `docs/storage-policy.md`, `docs/mechanics.md`,
   `docs/archive/INDEX.md` (superseded docs).

Per-experiment obligations: ledger entry; CONSTRAINTS bullet for anything closed; §4
update here. First session ending with the live volume over 100 KB freezes it and opens
the next.
