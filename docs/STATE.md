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
two-worker roster**, so it is architecturally demonstrated rather than hypothetical; and
H13's maturity finding (3–4 points) means it may be reachable **without any code change at
all** — which N1 is designed to settle. **Consequence: H2 Architecture-2 is demoted from
"required by the goal" to optional upside.** Rank-based targets are additionally avoided
because the pool strengthens under us (22.0 → 21.76 with no code change), which makes a
rank goalpost move in the wrong direction.

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

- ★★★ **2026-07-29 (H5): the resident is a reproduction of yamo's #3-Legend published
  bot** (`docs/reference/yann-moisan-postmortem-2026-05-26.txt`, restored) — so "this
  architecture's ceiling" must be read against the fact that this architecture placed 3rd.
  **yamo currently ranks 15 @ 24.70 while we rank 45 @ 21.76 at the same 2-troll roster:
  a 2.94-point, non-architectural gap** to our own source design, 45% of the gap to the
  bar. This is H13 and it is the strongest cheap lead available.
- **2026-07-29 TERMINAL SYNTHESIS: the improvement space for THIS architecture is
  closed** *(scope note: closed for the eight tested LEVERS; H13's fidelity question is
  outside that scope and untested)*. Eight routes, each with a frozen protocol and verdict: learned selection
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
  **Iteration 2 backlog formed 2026-07-29** (`docs/BACKLOG.md` LIVE PRIORITIES): leads with
  **N1 maturity-curve measurement** — if the fresh-vs-mature effect is the documented 3–4
  points, the true code gap to the bar is ~2.5–3.5 rather than 6.46, which re-baselines
  every downstream decision including whether to build at all. Then N2 (retire/verify B4.4's
  twice-corrected figures), N3 (renewable-base feasibility — the gate on H2), N4 (H6
  residual as a value audit), N5 (missing endgame opponent-plant contest), N6 (unswept
  denial weight), N7 (dead-accretion removal plan).
  Working taxonomy: **all iteration-1 P0 audits CLOSED 2026-07-29** (H3, H5, H8, H13; H1 too).
  **D176a CLOSED-AT-MECHANISM 2026-07-29 — no experiment now in flight.** The fix largely
  worked (incidence 8.50%→2.88%, below yamo's 2.9% reference; zero de-novo; all six value
  gates pass) but is worth only **+0.045 overall**, so the oscillation line closes
  permanently. Two mechanism sub-gates were mis-specified by me and the errors are recorded
  as gate-design rules in CONSTRAINTS. **Next: iteration-2 P0 — N1 maturity measurement.** **H13 DONE** — the 2.94 gap
  to yamo is most plausibly maturity not code (≤1 pt attributable), but we oscillate at
  6.4× yamo's rate; four accretions are structurally dead. **H5 DONE** (b)+(c) — confirms the model, corrects H6's
  lookahead premise, and revealed that the resident reproduces yamo's #3-Legend design
  while ranking 2.94 below it;
  **H8 CLOSED** (B) forced — trains on the first legal turn in 219/220 games, premise was
  a stale census, timing worth +1.31 n.s.; **H3 CLOSED** (C) — the quartet's edge does not
  survive controls and inverts at 2v4+, B4.4 corrected on four counts, residual
  contact-coverage lead gated into P1; **H1 CLOSED** (C) — the economy package cannot pay even at its
  upper bound (−21.33 rating, 0/220 positive; worker 4 never affordable because credited
  resources are a finite windfall, not a renewable stream); **preflight-gated** H4
  (deniability census first),
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
- ★★ **2026-07-30 OWNER DECISION: A2 Architecture-2 programme AUTHORIZED** —
  `docs/A2-programme-charter-2026-07-30.md`. Integrator recommendation of record was to hold
  pending N1/N3; the owner elected to build, and N3's renewable-base question is folded into
  **Phase 0a** rather than used as a pre-gate. Five preregistered milestone gates (adopted
  from chatgpt_1's review) plus five kill rules including a 6-session budget circuit-breaker.
  Phase 0 runs two parallel workstreams: **0a renewable-base feasibility** (K1: no renewable
  base → stop the programme) and **0b referee/evaluation parity harness**. The resident is
  untouched throughout; Phase 5 (arena) needs a NEW explicit authorization per candidate.
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
