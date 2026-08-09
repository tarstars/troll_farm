# STATE — Troll Farm (single entry point)

Last updated: **2026-08-12**. This file is live state, not a record — the ledger volumes are
the record. Hard budget: 150 lines. Rewrite it whenever facts change.

## 1. Live identity

### ★★★ CYCLE CLOSED — OWNER DECIDED **KEEP** 2026-08-12. Resident is `readable__no_orchard`.

**Owner ruling: "keep readable__no_orchard".** No Arena action was taken to execute it — the
source was already live, so KEEP is a no-op mutation-wise. `6604529` / `41113243` is now the
**resident**, not a candidate under trial, and `2caac7c6…` is retired as a restore target for
this cycle. `cgauto/api_submit.py`'s default fallback source still points at the old
`2caac7c6…` E7a — **it now disagrees with the resident; fix it before the next cycle relies on
it.** Any future restore-to-resident means `98628e98…`.

**Terminal read: 160/160, score 22.46, rank 35/139, 89W/3T/68L, 24 catastrophes (15.0%),
negative mass 6,790, `identity_clean=True`, `signals=0`.** No restore trigger ever fired.

**The result: the same source scored 24.76 last run and 22.46 this run — a 2.30-point spread
between two mature 160-game observations of one byte-identical bot.** 24.76 was a favourable
draw, not this source's level. This also puts the ±0.5–1 arena noise band in §3 in doubt (either
it is understated or the ladder moved between runs; one pair cannot separate those) — treat any
promotion argument resting on a sub-2-point mature delta as unsupported until it is separated.
At 22.46/rank 35/139 the live bot matches the displaced bot's 22.7/rank 35/139 standing, inside
noise: the cycle neither gained nor cost ground — which is why KEEP costs nothing either.

| field | value |
|---|---|
| live agent / submission | **`6604529` / `41113243`** |
| source | `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` |
| SHA-256 | `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29` |
| purpose | **second mature observation** to settle `SINGLE_MATURE_RUN` against its prior 24.76 — **DONE, settled at 22.46** |
| last read | **terminal, 160 games, 22.46, rank 35/139, `identity_clean=True`, `signals=0`** |
| disposition | **KEPT by owner ruling 2026-08-12 — this is the resident** |
| restore-to-resident source | `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`, SHA `98628e98…` |

The terminal checkpoint is taken and the cycle is closed. **Submitting a new candidate is
unblocked, subject to the §3 evidence discipline — but see the noise-band caveat above before
pricing any candidate's expected gain.**

Task record: `coordination/tasks/20260812-readable-no-orchard-rerun-arena.md` (full execution
log). Evidence: `data/analysis/live-agent-6553250/readable-no-orchard-rerun-20260812/`.

⚠ **`docs/PROMOTION-RUNBOOK.md` MUST NOT be followed for this run.** Its authorization gate is
scoped to candidate D171a only, and its §1 "fixed identities" are stale — it names resident
`a8eb3b2b…` / agent `6561795`, which has not been live for weeks. **Following its abort path
would restore the wrong bot.** Use the restore target in the table above.

### Displaced resident (was live until 2026-08-12)

- Player `tass`, Legend practice ladder (contest ended 2026-05-25 — no deadline).
- Round-36 simplified E7a `6594200`/`41090606`: exact 55,799-byte source
  `cgauto/submissions/candidate-agent6553250-e7a-r36-simplified.min.rs`, SHA `2caac7c6...`;
  settled 22.81/rank 32/137 over 160, 93W/2T/65L, identity/runtime clean. **Its standing had
  already eroded to 22.7 / rank 35 of 139 by the 2026-08-12 pre-mutation read** — Legend grew
  from 137 to 139 and we slipped three places. 22.81/32/137 is the settled-checkpoint figure;
  22.7/35/139 was current standing. Both are real; do not conflate them.
- `cgauto/api_submit.py` default remains the exact fallback source; do not change casually.
- Pre-mutation orchard `6592744`/`41087983`: 22.88/rank 32 over 160, exact and healthy.
- **Arena cycle complete:** round 36 passed 0/516 equality, was accepted once, recovered exact,
  and settled at 22.81/rank 32. Pre-mutation readable no-orchard `6593838`/`41089629` completed at
  24.76/rank 21 over 160, 94W/2T/64L, identity/runtime clean.
- **No-orchard terminal-rejected:** 23.27/rank 34 versus E7a 25.3/rank 12. Exact E7a restore
  `6592131`/`41086057` is source-exact and complete at 23.56/rank 32; cycle closed.
- Rank bar: 1. delineate 31.02, 2. norxondor_gorgonax 29.67, 3. MSz 28.26.
- Corpus: **10,470 games** / 513 agents, zero parse failures. The restore's exact 162-game
  queue is also a sanitized 5.8 MB Git LFS corpus; the 05:17 cron remains unchanged.

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
    (now `local_claude_1` by owner reassignment — see the note in this section). No peer agent or subagent may submit. The no-churn evidence still binds
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
  **Coordinator (integrator) = `local_claude_1` from 2026-08-06** (owner reassignment); arena controller follows the coordinator by protocol default. `local_codex_1` is the outgoing coordinator and no longer a controller; `claude_1` and `chatgpt_1` are contributors. Handover: `coordination/HANDOVER-2026-08-06-local_codex_1-to-local_claude_1.md`. Hazards (§7) bind every agent: the dev copy
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
  terminal pairs are runtime-closed by N4. **E1 CLOSED:** N4 surface infeasible. **E2 DONE:** 0.335 hindsight move-turn/side-game. **E3 VOID:** tree order closed. **E4 DONE:** mother reverse −0.0855. **E5 DONE:** +0.106, seat 0 loses. **E6 VOID:** seed carry. **E7 DONE:** flip −12.174; hindsight +10.510; **E7a SECTOR LIVE:** restore `6592131`/`41086057` is 23.56/162; two exact mature runs median 24.41. **E7a HALF-SIZE:** 31,407-byte tree-edge source transfer-rejected on catastrophes and negative mass; no Arena action. **S1 DONE:** full exact infeasible. **S2 BLOCKED:** no valued library or map representation. **S3 GATED:** distinct combination; specification/model/runtime unresolved. **H10a NARROWED:** 72 spatial +17 decision fields; peer-gated. **L1 PRIMITIVE-ONLY:** 199 exact games; hidden plan/beam unlabeled; peer-gated. **L2/L3 CLOSED:** N4 runtime close. **N7 DONE:** deploy already slim; sacred fixtures stay exact. **H4 DONE:** 0/17 strict deniable bills. **H7′ DONE:** contention ubiquitous, not strong-cohort. **H3′ SIGNAL:** DiD 0.606; pre-loss 0.510; **H3a PAUSED FOR OWNER PRIORITY.** **BANANA R2 through 9f5e INVALID:** the oracle/real flip are repaired, but a full wood carrier oscillates for 225 turns on the first broad host panel; no value test. **H11 DONE:** umbrella decomposed. **B3.7 DONE:** orchard is conversion-by-design. **B3.10 CLOSED:** ceiling 4.84/game. **B3.11 RE-REVIEW PENDING.** **B3.12 DISPLACED:** 22.99 historical, 19.37 repeat. **B3.13 FAIL; B3.14 AUDIT; B3.15 DISPLACED; B3.16 FAIL; B3.17 UNRANKED.** **F1 RELEASED.**
- **BANANA R2 CURRENT (supersedes inline `through 9f5e`):** `47c98f53` withdrawn at 141/240 fuzz blocks; `eac2eb36` is not a handoff. FSM event priority, exact asset-survival timing, attribution, and carrier precedence remain open; no value/Arena test.
- **E7a ITERATIVE DELETION:** round 36 is 55,799 bytes and passes compile/fixtures, 7,234 live
  commands, and 0/516 development equality. Owner-directed live measurement `6594200`/`41090606`
  is 22.81/rank 32 over 160; no further mutation.
- **Coordination:** `local_claude_1` integrates/controls Arena; `local_codex_1`, Claude, and ChatGPT contribute. Incoming operational ACK is pending; Arena stays unchanged during the gap.
- ★ **ITERATION 2 CLOSED 2026-08-07 by owner.** Two carries into iteration 3, both designed
  and neither started:
  - **CBF conditional banana farm — DESIGN COMPLETE, NOT IMPLEMENTED.** Spec
    `docs/superpowers/specs/2026-08-07-conditional-banana-farm-design.md`; backlog entry under
    LIVE PRIORITIES → "Designed, not started". Latched `DENY → FARM → WOOD`: the resident's
    existing `opponent_trolls > 2` denial abort gets a destination (the D89a seed factory)
    instead of falling back to undifferentiated wood, and aborts to pure wood if the opponent
    out-collects our bananas. Gates are **behavioural per owner ruling**; they authorize no
    Arena action. Byte-identical to the resident when the opponent never fields a third troll.
  - **D89a leak-repairability scoping — `claude_1` returned `NOT_REPAIRABLE` 2026-08-07**
    (`claude_1/banana-restoration-r2/d89a-leak-repairability-2026-08-07.md`, artifact
    `6c6215e4`); `chatgpt_1` review pending. Strongest evidence is an isolation: D92's
    trained-only variant ran **898** opponent-crop selections vs D89's **166** — 5.4× denial
    dose, starter provably unchanged — and opponent score moved **+0.188 upward** (verified by
    me from the committed D92 result). `gold_adaptive` family delta **208.78**. Recommends
    **neither** route enter Phase 3 before a read-only check and measurement repair.
- ★★ **CORRECTION OF RECORD 2026-08-07 — the D89a theft/own-production split is UNRESOLVED.**
  The figures `+12.453` (theft) and `+76.508` (opponent's own crops) are **prose only** in
  `d89a-banana-seed-factory-result-2026-07-21.md`; the committed discovery JSON has no such
  fields and the per-task panel TSVs were never committed on any ref. `+82.863` reproduces
  exactly and stands. `claude_1` raised this against its own earlier over-claim; **I had
  propagated it into the CBF spec and BACKLOG as measured fact and have corrected both.** Any
  argument that D89a "lost to opponent production rather than theft" is currently unsupported.
- **Owner ruling 2026-08-07 — judge on delta, not absolute opponent gain.** "If we increased
  our production more than enemies, we are good." This supersedes D89a's
  `active_opponent_score_delta_at_most_1` gate. Note the correction of record: D89a fails
  **four** value gates, not one — the three others are downside-tail gates (worst family
  −6.938/bar −5; p10 −72/bar −20; worst −235/bar −60) and remain unrelaxed.
- ★★ **Transport quarantine/lint: `REVISION_REQUIRED` — DO NOT RELY ON IT.** `chatgpt_1`'s
  independent review of `238a792a` (`chatgpt_1/transport-quarantine-outbox-lint-review-2026-08-07.md`,
  artifact `e645800b`) returned `REVISION_REQUIRED` with six blocking findings, and it accepts
  all six quarantine entries as substantively justified. **Finding 2 is a real authorization
  hole and I reproduced it:** `validate_quarantine` accepts any `adjudicated_by` path that
  merely exists on an authoritative ref — no coordinator authorship, no v2 validity, no
  reference to the target. In my reproduction, an unrelated **2026-07-29 message from
  `chatgpt_1` itself** successfully authorized quarantining `chatgpt_1`'s own fabricated
  closeout, with zero quarantine errors. Also blocking: quarantine is read from the mutable
  local worktree while messages come from remote refs, so inbox truth varies by checkout; the
  lint reads worktree bytes while Git commits index bytes; receiver-side legacy grandfathering
  is open-ended rather than a pinned baseline; the namespace scanner silently skips
  non-digit-prefixed files; and the lint cannot reproduce immutable-path collisions.
  **All six are now REPAIRED** (`f54be7d0`), and the mechanism is still **not accepted** —
  the repair needs re-review by `chatgpt_1`, and `claude_1`'s independent review is still
  outstanding. What changed: quarantine authority is the coordinator's canonical ref, never
  the worktree, with the ref/blob reported and local drift warned (TQ-1); an adjudication must
  be a valid v2 coordinator message on the coordinator's ref naming the exact target in a
  `quarantines` array, with `target_blob` pinned (TQ-2 — quarantine schema is now v2, and
  `20260807T190000Z-…-adjudication.md` is the adjudication for all six entries);
  `coordination/legacy-baseline.json` pins 691 pre-v2 paths by blob and the receiver rejects
  anything outside it (TQ-3); the lint gained `--staged` to read index rather than worktree
  bytes and reports deletions against HEAD (TQ-4); the namespace is closed with an explicit
  allowlist (TQ-5); and the lint reproduces immutable-path collisions (TQ-6). 128 tests pass.
  Live delivery errors 9 → 2; a correction does **not** clear a delivery error (verified by
  execution), so quarantine remains the only repair.
  **UPDATE 2026-08-12 — transport is now CLEAN and the mechanism has been peer-attacked.**
  `claude_1` ran an independent execution review (15 attacks, 6 reproducing) and `chatgpt_1`
  formally requested adjudication, releasing the hold. Three further blobs quarantined
  (`47aae1a6…`, `69e9a66c…`, `ffe97634…`), each verified by the coordinator to have a valid
  replacement, so no content was lost. Sweep now reports **delivery errors 0, quarantine
  errors 0, quarantined 9, immutable-path collisions 0** — the first clean sweep in this
  programme. TQ-2 proved itself by rejecting *my own* unauthorized adjudication (missing
  `quarantines` array) and failing closed to `quarantined 0` rather than partially applying.
  Two open tool facts: `scripts/lint_outbox.py` is **absent** from `agent/claude_1`, which
  explains its recurring delivery errors; and the two tool SHA-256 values in `chatgpt_1`'s
  `20260811T232000Z` blocker match **no blob in the entire history** of either file, including
  the blob cited beside them — its blob ids were all correct, its execution-derived digests
  are not. Answers requested from both.
- **Operations:** cron 05:17; H12 weekly; no Arena mutation cycle in flight.
## 4b. Context-flush handover, 2026-08-12

**`coordination/HANDOVER-2026-08-12-local_claude_1.md`** is the verified operational snapshot:
identity and start ritual, the gate's repair status, transport state, roster and per-agent tool
digests, both live programmes, owner decisions outstanding, hazards, and my own error record for
calibration. Every figure in it was re-verified against the repository at the time of writing.

Two facts from it that belong here: **TRAIN r4 is ACCEPTED** (first panel run with zero
`GATE_UNREADY`; floor 118/240) and **`readable__no_orchard` (`98628e98…`, 24.76/rank 21) is the
best bot we have measured and is not the one running** (live is `2caac7c6…` at 22.81/rank 32),
on a single mature run.

**★ SUPERSEDED 2026-08-12 — the gate IS now integrated.** The handover says r4 is "NOT
INTEGRATED"; that was true when written and is no longer. `main` = `session-2026-07-01` =
`agent/local_claude_1`, and `main:claude_1/pipeline/fuzz_panel.py` is `d8900abf31dd030d…` with
33 TRAIN references. Nine branches merged, `abgate-selfplay-gate` deliberately unmerged;
sacred `fff6669b…`, live `2caac7c6…`, readable `98628e98…` and banana parent `a8eb3b2b…` all
verified intact; zero changes under `rust/`, `sim/`, `cgauto/`; one agent-authored CI file
stripped. **Also correct the handover's size figure:** it claims the integration spanned
"2,104 files, +193,920 / −729,616". The measured divergence was **251 files, +231,176 / −127**,
touching only `claude_1/` and `coordination/`. The single conflict was `scripts/lint_outbox.py`,
both sides byte-identical to the pinned `f3c47b70…`.

**B1 is closed.** The r4 §8 packet was executed independently in a second checkout:
163 + 24 tests OK, 16/16 mutations caught, floor BLOCK 118/240 and candidate BLOCK 121/240 with
zero `GATE_UNREADY`, deterministic across two runs, and both packets **row-identical** to the
committed `evidence-r4` packets. Record:
`local_claude_1/verification/train-r4-independent-execution-review-2026-08-12.md`.
`118/240` may now be cited as the floor — **with r4 §9's restriction attached**: TRAIN is
witnessed in only 2 games and 10 of 17 repaired rules have no corpus witness, so the floor is
not evidence for those; they are pinned by unit tests, the differential and the mutation drive.

## 5. Reading order & pointers

1. This file.
2. `docs/CONSTRAINTS.md` — check BEFORE proposing any experiment.
3. `docs/BACKLOG.md` — live priorities at the top; historical tiers below are the record.
4. `coordination/README.md` + inbox sweep — mandatory for any agent before writing.
5. Live ledger: `data/analysis/live-agent-6553250/legend-top3-experiment-cycle-vol4-2026-08-04.md`; prior volumes frozen. Atlas: `docs/D-series-atlas.pdf`.
6. `AGENTS.md` (process), `docs/storage-policy.md`, `docs/mechanics.md`,
   `docs/archive/INDEX.md` (superseded docs).

Per-experiment obligations: ledger entry; CONSTRAINTS bullet for anything closed; §4 update here.
First session ending with the live volume over 100 KB freezes it and opens the next.
