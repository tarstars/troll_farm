# STATE — Troll Farm (single entry point)

Last updated: 2026-08-10 (doc diet; see docs/archive/STATE-2026-08-10-pre-diet.md for the
pre-diet text). This file is live state, not a record — the ledger volumes are the record.
Hard budget: 150 lines. Rewrite it whenever facts change.

## 1. Live identity

### ★★★ CYCLE CLOSED — OWNER DECIDED **KEEP** 2026-08-12. Resident is `readable__no_orchard`.

Owner ruled **KEEP** — `6604529`/`41113243` is the resident, restore target `98628e98…`.
Terminal read 160/160: **22.46, rank 35/139**, clean. The same bytes scored 24.76 the
prior run — a 2.30 spread; registry median 23.61. A sub-1.5-point mature delta is
unresolvable at one run per arm (difference SD 1.552, §3). Cycle closed; submitting a
new candidate is unblocked under §3.
Task record: `coordination/tasks/20260812-readable-no-orchard-rerun-arena.md` (its "08-12"
dates are the fabricated-clock session of 2026-08-09; trust `git log`).

| field | value |
|---|---|
| live agent / submission | **`6604529` / `41113243`** |
| source | `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` |
| SHA-256 | `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29` |
| purpose | **second mature observation** to settle `SINGLE_MATURE_RUN` against its prior 24.76 — **DONE, settled at 22.46** |
| last read | **terminal, 160 games, 22.46, rank 35/139, `identity_clean=True`, `signals=0`** |
| disposition | **KEPT by owner ruling 2026-08-12 — this is the resident** |
| restore-to-resident source | `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`, SHA `98628e98…` |

⚠ **`docs/PROMOTION-RUNBOOK.md` MUST NOT be followed for this run.** Its authorization gate is
scoped to candidate D171a only, and its §1 "fixed identities" are stale — it names resident
`a8eb3b2b…` / agent `6561795`, which has not been live for weeks. **Following its abort path
would restore the wrong bot.** Use the restore target in the table above.

- Displaced: `6594200`/`41090606` (`2caac7c6…`), settled 22.81/32/137, eroded 22.7/35/139.
- Corpus: 14,930 games / 582 agents / 279 names, 0 parse failures (verified 2026-08-12-labelled session).

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
- ★★ **OWNER 2026-08-12 (real date 2026-08-09): the noise-band gate is REMOVED.** The ladder
  is an information channel; submissions are the cheap instrument. QUALIFIED-verdict
  correctness bar stands; magnitude bar is gone; runbook in full; owner told before and
  after each cycle; every id and terminal response logged.
- ★ **σ = 1.098** (CI [0.707, 2.418]; 4 families / 10 deployments / 6 d.o.f.;
  `cgauto/arena_noise_band.py`). Difference SD at n=1 per arm = 1.552; SE 0.5 needs
  10 runs/arm (~40 h). Re-submission draws an independent sample (zero duplicate scores
  across 10 deployments). A mature 160-game read takes **~2 h**. Prefer interleaved
  A/B/A/B over blocked runs. Re-run the estimator after every new mature deployment.
  - **Unchanged:** mutations remain serialized through the **single arena controller**
    (now `local_claude_1` by owner reassignment — see the note in this section). No peer agent
    or subagent may submit. One cycle in flight at a time — that is a ladder-slot constraint,
    not an evidence one, so higher throughput means *shorter cycles*, never parallel ones.
- **B0.3 no-churn — SUBSTANTIALLY WEAKENED 2026-08-12, by measurement.** The rule read: "fresh
  reads sit 3–4 points below matured ones; every failed trial costs days of standing." The
  first clause holds. **The second does not, at current ladder rates:** the 2026-08-12 cycle
  went from submission to a settled 160-game read in **~2 hours** (21 games at +15 min, 127 at
  +1 h 35 m, 160 at +1 h 55 m). The "days" figure dates from the B0.1 regime when the score was
  source-side frozen and the resident drew 6 battles in 4 days. A mature observation is now
  cheap. What remains true: never *abandon* a run before it matures, since a half-matured read
  is the expensive kind of worthless.
- Sealed, do not open: maps `9,844,200–9,844,215`; the official-map holdout; the 11
  sealed D164 field games; D170's confirmation block `9,852,000–063` (unused, preserved).
- Substrate rule (D158/D161): controllers use the exact Yamo/Orchard resident fallback
  natively or first prove same-panel dominance. D40/q6 is dead as a substrate.
- External play bursts ≤ 12 games; stop on HTTP 422 or degenerate results.
- Bulk writes: preflight `python3 cgauto/check_external_storage.py --required-free-gib N`
  (`AGENTS.md`, `docs/storage-policy.md`). YT root:
  `//home/delivery_ml/research/tarstars/troll_farm`.
- **Coordination is migrating to a control plane** — spec
  `docs/superpowers/specs/2026-08-10-coordination-control-plane-design.md` (approved
  2026-08-10; no CI this iteration). Until P2 switches authority, the existing protocol
  `coordination/multi-agent-protocol.md` remains in force. Coordinator/integrator/Arena
  controller = `local_claude_1` (owner reassignment 2026-08-06). §7 hazards bind everyone:
  byte-sacred `fff6669b` dev copy, no formatters over hash-locked sources, `data/raw/games/`
  and the 05:17 cron untouchable.
- **History rewrite: DECLINED by owner 2026-07-30, closed.** Measured gain was 12.9 MB
  (39 MB → ~26 MB) against invalidating all ~380 published commit hashes, four of which are
  cited directly in experiment records. `git gc --aggressive` already reclaimed 14 MB for
  free. The full-history bundle stays on `medium_data` as a backup. Do not reopen.
- Repository pushed to GitHub 2026-07-29 (`origin/session-2026-07-01` current); remote
  message transport is live; full-history bundle on `medium_data`; 1,629 tracked bulk
  artifacts migrated to USB as committed symlinks (digest
  `docs/storage-migration-2026-07-29-tracked.sha256`).

## 4. Open thread

- **Transport CLEAN 2026-08-10** — delivery errors 0, quarantine errors 0, quarantined 10
  for all three active agents; the half-done self-quarantine was found unpushed and landed
  (`4de33b8c`, trunk `8c01c6ad`).
- **Control-plane migration is the live programme.** Spec approved; plan
  `docs/superpowers/plans/2026-08-10-coordination-control-plane.md` (P0+P1). P2/P3 follow
  shadow-mode verification.
- **Iteration-3 carries (designed, unstarted):** CBF conditional banana farm
  (`docs/superpowers/specs/2026-08-07-conditional-banana-farm-design.md`; note the strict
  no-banana-before-second-troll rule and D-9(a) UNPINNED status) and D89a
  leak-repairability follow-up (claude_1 returned NOT_REPAIRABLE; review pending).
- **P0 tooling-integrity task** `20260810-guards-that-cannot-fail` (G1–G6; G6 owner-gated).
- **σ task** `20260810-arena-noise-band-measurement` — unowned; Q2–Q4 open; blocked
  ordering cannot separate our variance from ladder drift, only interleaved A/B/A/B can.
- **Needs the owner:** B9 (325 tracked files under
  gitignored `data/raw/`), e7a 375-vs-586 canonical formatting definition, G6 go-ahead.
- History: 2026-07-29 terminal synthesis closed all eight resident levers; A2 stopped at
  Phase-1 K1; N1 closed passive maturity; the full pre-diet record is
  `docs/archive/STATE-2026-08-10-pre-diet.md` and the ledger volumes.

## 5. Reading order & pointers

1. This file.
2. `docs/CONSTRAINTS.md` — check BEFORE proposing any experiment.
3. `docs/BACKLOG.md` — live priorities at the top; historical tiers below are the record.
4. `coordination/README.md` + inbox sweep — mandatory until P2; see the control-plane spec.
5. Live ledger: `data/analysis/live-agent-6553250/legend-top3-experiment-cycle-vol4-2026-08-04.md`; prior volumes frozen. Atlas: `docs/D-series-atlas.pdf`.
6. `AGENTS.md` (process), `docs/storage-policy.md`, `docs/mechanics.md`,
   `docs/archive/INDEX.md` (superseded docs).

Per-experiment obligations: ledger entry; CONSTRAINTS bullet for anything closed; §4 update here.
First session ending with the live volume over 100 KB freezes it and opens the next.
