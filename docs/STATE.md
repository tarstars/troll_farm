# STATE — Troll Farm (single entry point)

Last updated: 2026-08-10 (doc diet; see docs/archive/STATE-2026-08-10-pre-diet.md for the
pre-diet text). This file is live state, not a record — the ledger volumes are the record.
Hard budget: 150 lines. Rewrite it whenever facts change.

## 1. Live identity

### ★★★ OWNER RULED **KEEP** 2026-08-19 — the resident is **CURE C** (`cure-c-quiet`).

M-1 paired night 2026-08-18/19 (ledger `local_claude_1/cure-c-night-2026-08-18.md`):
cure C won **all five pairs** vs the prior resident `98628e98…` — +1.3, +0.2, +0.4,
+0.6, +2.6, **mean +1.02** (clears the 1.0 floor; planning winner bar 1.86 not met;
M-1's prescribed extension was superseded by the owner's KEEP, which is the owner's
call to make). Honesty: empirical pair SD 0.976 vs planning 2.123; pair-5 ladder-event
caveat on record. **m082 seat 1 (12→1) is the permanently accepted named cost.**
Prior resident era (98628e98, KEEP 2026-08-12, six reads 19.77–24.90): archived in
this file's git history and the night ledger.

| field | value |
|---|---|
| live submission | **`41159334`** (submitted 2026-08-19T04:04Z on the KEEP; agent id pending first read — night agents for these bytes: 6631618/6632611/6633433/6634457/6634986) |
| source | `cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs` (75,844 B) |
| SHA-256 | `ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1` |
| purpose | resident; cure C = mid-game fallback for chopless trolls (one hunk, six lines, over `98628e98…`) |
| last read | A5 night window: **24.4, rank 24/162, 160 games** (2026-08-19T00:58Z); night windows 25.2/23.0/23.2/22.9/24.4 |
| disposition | **resident — owner KEEP ruling 2026-08-19 on the night's numbers** |
| restore-to-resident source | `cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs`, SHA `ad3bfefe…` |

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
- ★ **σ = 1.501** (CI [1.049, 2.634]; 4 families / 14 mature observations / 10 d.o.f.;
  `cgauto/arena_noise_band.py`). **Supersedes the earlier 1.098** (6 d.o.f.) after the
  2026-08-13 four-run same-source campaign; the CI's lower bound now sits *above* the old point
  estimate, so the previous figure was optimistic, not merely imprecise. Difference SD at n=1
  per arm = **2.123**; SE 1.0 needs **5** runs/arm, SE 0.5 needs **19** (~76 h), SE 0.3 needs
  **51**. A mature 160-game read takes **~2 h**.
  - **What this number is** (wording required by `codex_1`'s review, 2026-08-13): `1.501`
    estimates **combined operational variability for sequential same-source deployments in the
    observed campaign**. Pure re-submission variance and ladder drift are **not separately
    identifiable** from these data, and **no inequality between them is established** — drift can
    increase *or* decrease within-family dispersion depending on its direction, timing and
    covariance with deployment order. An earlier draft of mine called `1.501` an upper bound on
    re-submission variance; **that claim is withdrawn** — it assumed an additive, independent
    drift term that this design cannot establish.
  - **The runs-per-arm figures are a planning approximation, not a guarantee.** They are exact
    under independent, stationary observations with variance `1.501²`. Persistent or
    autocorrelated drift can prevent the nominal `1/√n` improvement. **Interleaved A/B/A/B is
    required** to distribute drift across arms — with sequential blocks the arithmetic does not
    hold. Re-run the estimator after every new mature deployment.
  - Evidence: campaign family `e7a-readable-no-orchard-code-cost`, n=6 on byte-identical
    `98628e98…` — [19.77, 22.46, 23.39, 23.73, 24.76, 24.90], range 5.13, which is 2–3× every
    other family (1.70–1.77). Task record `20260810-arena-noise-band-measurement`; independently
    reproduced by `codex_1` to `SD 1.5010773908540938`.
  - **Read scores only from an agent-validated block.** The room serves a persistent
    stale row — agent 6604529 / field 140 / score 22.46 — that camouflages as a plausible
    value (it nearly entered the registry twice); the registry now faults any checkpoint
    whose arena block names a foreign agent.
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
- **Needs the owner:** G6 go-ahead only. (B7, B9, e7a all ruled 2026-08-11; the readable
  format is pinned rustfmt per `docs/readable-format.md`.)
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
