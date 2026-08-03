# STATE — Troll Farm (single entry point)

Last updated: 2026-08-03. This file is live state, not a record — the ledger volumes are
the record. Hard budget: 150 lines. Rewrite it whenever facts change.

## 1. Live identity

- Player `tass`, Legend practice ladder (contest ended 2026-05-25 — no deadline).
- Active resident: owner-directed E7a sector agent `6590141`, submission `41081503`.
  Mature checkpoint: 160/160 parsed, score 25.34, rank 11/131, 82W/3T/75L; exact identity
  and runtime health are clean, but 35 catastrophes make the result tail-heavy.
- Source: `cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs`
  (62,820 bytes, SHA-256 `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`).
- `cgauto/api_submit.py` default remains the exact fallback source; do not change casually.
- Latest exact stored read: **2026-08-02T18:55:03Z**, agent `6590141`; 160/160 games,
  score 25.26 at rank 11/131, one exact submission hash and zero runtime signals.
- Rank bar: 1. delineate 31.02, 2. norxondor_gorgonax 29.67, 3. MSz 28.26.
- Corpus: **10,470 games** / 513 agents, zero parse failures. The 2026-08-02 manual wide
  catch-up added 282; the 05:17 cron was healthy and the prior STATE count was stale.

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
  **Coordinator (integrator) = `local_codex_1` from 2026-07-30** (owner reassignment); arena controller follows the coordinator by protocol default unless the owner directs otherwise. `claude_1` is again an active contributor but not controller; `chatgpt_1` is a contributor. Handover: `coordination/HANDOVER-2026-07-30-claude_1-to-local_codex_1.md`. Hazards (§7) bind every agent: the dev copy
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
  DONE:** −1.44, CI crosses. **N5 CORRECTED/RE-REVIEW PENDING:** literal ETA keeps CI <20. **N6
  ACCEPTED/CLOSED_AT_DEVELOPMENT:** HIGH +0.559 fails direction/breadth. **E1 NARROWED:** only a
  terminal pairs are runtime-closed by N4. **E1 CLOSED:** N4 surface infeasible. **E2 DONE:** 0.335 hindsight move-turn/side-game. **E3 VOID:** tree order closed. **E4 DONE:** mother reverse −0.0855. **E5 DONE:** +0.106, seat 0 loses. **E6 VOID:** seed carry. **E7 DONE:** flip −12.174; hindsight +10.510; **E7a SECTOR LIVE:** `6590141`/`41081503`, mature 25.34/160 at rank 11. **E7a HALF-SIZE:** 31,407-byte tree-edge source transfer-rejected on catastrophes and negative mass; no Arena action. **S1 DONE:** full exact infeasible. **S2 BLOCKED:** no valued library or map representation. **S3 GATED:** distinct combination; specification/model/runtime unresolved. **H10a NARROWED:** 72 spatial +17 decision fields; peer-gated. **L1 PRIMITIVE-ONLY:** 199 exact games; hidden plan/beam unlabeled; peer-gated. **L2/L3 CLOSED:** N4 runtime close. **N7 DONE:** deploy already slim; sacred fixtures stay exact. **H4 DONE:** 0/17 strict deniable bills. **H7′ DONE:** contention ubiquitous, not strong-cohort. **H3′ SIGNAL:** DiD 0.606; pre-loss 0.510; **H3a PAUSED FOR OWNER PRIORITY.** **BANANA R2 ASSIGNED:** unbounded/ring publications implementation-invalid, not algorithm evidence; Claude retries stable-parent restoration. **H11 DONE:** umbrella decomposed. **B3.7 DONE:** orchard is conversion-by-design. **B3.10 CLOSED:** ceiling 4.84/game. **B3.11 RE-REVIEW PENDING.** **B3.12 DISPLACED:** 22.99 historical, 19.37 repeat. **B3.13 FAIL; B3.14 AUDIT; B3.15 DISPLACED; B3.16 FAIL; B3.17 UNRANKED.** **F1 RELEASED.**
- **E7a SINGLE DELETION QUALIFIED / NOT DEPLOYED:** owner superseded the 50% target. The
  62,278-byte source deletes the unreachable roster-above-two selector and matches 7,234
  public-live command lines, 516 development tasks, and 516 one-shot untouched tasks exactly.
  Its expected gain is zero, so the mature rank-11 Arena bot remains unchanged under no-churn.
- **Coordination:** `local_codex_1` integrates/controls Arena; `claude_1` is an active
  contributor without platform credentials; `chatgpt_1` is a contributor. Inbox: `python3 scripts/inbox_sweep.py --me local_codex_1 --fetch`.
- **Operations:** daily collection cron 05:17; B5.3 migration ripens ~2026-08-03; H12 weekly
  surveillance. Sole Arena leg: E7a sector `6590141`/`41081503`, read-only. The single-deletion
  source is untouched-qualified but not submitted because exact equality gives no rating gain.

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

Per-experiment obligations: ledger entry; CONSTRAINTS bullet for anything closed; §4 update here.
First session ending with the live volume over 100 KB freezes it and opens the next.
