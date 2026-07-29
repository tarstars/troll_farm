# STATE — Troll Farm (single entry point)

Last updated: 2026-07-29. This file is live state, not a record — the ledger volumes are
the record. Hard budget: 150 lines. Rewrite it whenever facts change.

## 1. Live identity

- Player `tass`, Legend practice ladder (contest ended 2026-05-25 — no deadline).
- Resident: agent `6561795`, submission `41015603`, live since 2026-07-19, untouched.
- Source: `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`
  (62,725 bytes, slim Yamo/Orchard + pre-seed + orchard coverage).
  SHA-256: `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`
- `cgauto/api_submit.py` default = that exact source. Keep it that way.
- Last ladder read (timestamped snapshot discipline — cite exactly one):
  **2026-07-28T13:59Z: rank 43/112 @ 22.0**, 203 battles, promotable=False. Score is
  source-side frozen between rare ladder recomputes (no recomputation since 07-23);
  passive maturity is dead as a lever.
- Rank bar: 1. delineate 31.00, 2. norxondor_gorgonax 29.52, 3. MSz 28.22.
- Corpus: 8,131+ games / 469 agents, compounding daily (cron 05:17).

## 2. Goal

Formally standing: Legend **rank ≤ 3** on a mature read + confirmation. **Post-terminal
reality (2026-07-29): this architecture cannot reach it** — closing the +6.25 gap
requires a new bot (H2 programme) or an owner re-scope. The resident holds the slot.

## 3. Standing rules

- **Arena writes require explicit user authorization per exact candidate. No
  exceptions.** (The 2026-07-28 D171a standing grant is consumed — D171a CLOSED, never
  triggered, does not carry over.) Promotion runs only via `docs/PROMOTION-RUNBOOK.md`
  (tooling verified 2026-07-28; baseline read taken).
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
  `claude_1` = integrator + arena controller. Hazards (§7) bind every agent: the dev copy
  `rust/src/bin/yamo_orchard_live.rs` stays byte-exact at SHA prefix `fff6669b`
  (library-visible to all experiments); no formatters over `rust/src/bin/` or `cgauto/`
  (locks record hashes); do not disturb `data/raw/games/` or the 05:17 cron.
- Repository pushed to GitHub 2026-07-29 (`origin/session-2026-07-01` current); remote
  message transport is live; full-history bundle on `medium_data`; 1,629 tracked bulk
  artifacts migrated to USB as committed symlinks (digest
  `docs/storage-migration-2026-07-29-tracked.sha256`).

## 4. Open thread

- **2026-07-29 TERMINAL SYNTHESIS: the improvement space for THIS architecture is
  closed.** Eight routes, each with a frozen protocol and verdict: learned selection
  (D172a — signal abundant, unlearnable from observables), closed-loop training (D170b),
  production/farming (D175a: −26.44, Δopponent +21.09 — third confirmation production is
  structurally negative), scaling+mining (D174a: `can_train` hard cap; FRUIT binds the
  real bill, not iron; mining −10.76), harvest capability (D173a/b), execution waste
  (comparative baseline: we waste LESS than the top cohorts on all six signatures),
  suppression efficiency (B4.6: fix class failed twice on this binary). Key structural
  facts: at equal roster we are at parity with strong two-worker peers (58.2/58.3); the
  whole deficit is scale-asymmetry survival; a worker prices at +2–4 rating (B4.3); we
  reap 0.93% vs every other two-worker agent's 15–17%. Full table: ledger vol 2 TERMINAL
  SYNTHESIS entry; reader's version: `docs/D-series-atlas.pdf` (27 pp).
- **Direction menu (post-terminal): `docs/rank-hypotheses-2026-07-29.md`** (claude_1),
  independently reviewed by chatgpt_1
  (`docs/reviews/2026-07-29-chatgpt_1-rank-hypotheses-critique.md`, integrated; H7
  premise falsified at `docs/mechanics.md:42-44` — no cross-player blocking exists).
  Working taxonomy: **audit-ready now** H5 (postmortem search), H3 (no-loop quartet:
  4 agents with our profile survive 2v3 at −1.8 vs our −37), H8 (worker-2 timing: top
  cohort trains turn 2, we turn 8); **preflight-gated** H1 (read-only joint upper bound
  only — the four-lever resident bundle is rejected), H4 (deniability census first),
  H6 (oracle-gap audit first), H7-rewritten (action contention, after H3); **owner
  programme decisions** H2 Architecture-2 (PRIMARY — five milestone gates in the
  review), H10 spatial-planes learner (sanctioned long shot); **near-closed** H11;
  **operations** H9 (capacity A/A only inside an authorized promotion), H12 (running).
- **Coordination roster**: `claude_1` (integrator, arena controller); `chatgpt_1`
  (reviewer — onboarded 2026-07-29 after correction; its critique is merged and its
  record reconciled through branch tip `3eaf880`; task
  `20260729-rank-hypotheses-critique` awaits **its** release; first right of claim
  offered on H5/H3/H8). Inbox: `python3 scripts/inbox_sweep.py --me claude_1 --fetch`;
  new agents get `coordination/peer-prompt.md`. The review's three findings are now
  CONSTRAINTS bullets (no cross-player blocking; families ≠ map classes; no multi-lever
  resident bundles) so they cannot be re-proposed.
- **Operations running**: collection cron 05:17 (`# troll-farm-wide-collect`); B5.3
  cold-file migration ripens ~2026-08-03; weekly surveillance cadence (H12) with
  explicit triggers.
- **Awaiting owner**: (a) dispatch of the audit-ready set (H5/H3/H8 — parallel,
  read-only, delegable to any agent); (b) the H2 Architecture-2 programme go/no-go.

## 5. Reading order & pointers

1. This file.
2. `docs/CONSTRAINTS.md` — check BEFORE proposing any experiment.
3. `docs/BACKLOG.md` — live priorities at the top; historical tiers below are the record.
4. `coordination/README.md` + inbox sweep — mandatory for any agent before writing.
5. Live ledger: `data/analysis/live-agent-6553250/legend-top3-experiment-cycle-vol2-2026-07-23.md`
   (vol 1 `...-2026-07-18.md` frozen at D166). Atlas: `docs/D-series-atlas.pdf`.
6. `AGENTS.md` (process), `docs/storage-policy.md`, `docs/mechanics.md`,
   `docs/archive/INDEX.md` (superseded docs).

Per-experiment obligations: ledger entry; CONSTRAINTS bullet for anything closed; §4
update here. First session ending with the live volume over 100 KB freezes it and opens
the next.
