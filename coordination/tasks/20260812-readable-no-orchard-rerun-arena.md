# 20260812-readable-no-orchard-rerun-arena: second mature observation of `readable__no_orchard`

- Status: in_progress — SUBMITTED and maturing; identity/runtime clean at 21 games
- Priority: direct owner assignment
- Record owner / work owner / Arena controller: `local_claude_1`
- Created UTC: 2026-08-12T16:00:00Z
- Last updated UTC: 2026-08-12T16:25:00Z

## Objective and authority

Re-run the exact `readable__no_orchard` source to obtain a **second mature observation**. Its
single mature run of 24.76/rank 21 is the highest score we have ever measured, and the registry
itself raises `SINGLE_MATURE_RUN` against it: one run cannot distinguish the source's level from
a lucky draw. A related no-orchard source scored 23.27, a 1.5-point spread wider than the
±0.5–1 noise band. This run settles which.

**Authority:** explicit owner authorisation, 2026-08-12 — *"I authorize arena publishing"* —
given in response to a stated summary of the trade (surrenders the live slot, ~a week of
standing, reversible by exact restore). This is an **owner-directed Arena override**, not a
frozen-gate promotion: the source has no `QUALIFIED` frozen-protocol verdict, and none is
claimed. `docs/STATE.md` §3's standing authorisation covers the mechanics; the two carve-outs
that required surfacing first (unqualified candidate; abandoning a matured score) were surfaced
and answered.

**This is a measurement, not a promotion.** No value-gate or capacity-A/A claim is made.

## Why B4.1 / `PROMOTION-RUNBOOK.md` does not govern

`docs/PROMOTION-RUNBOOK.md` §"Authorization gate" binds itself to **candidate D171a only** and
says not to reuse it for another candidate without a fresh STATE §3 entry. Its §1 "fixed
identities" are also **stale**: it names resident agent `6561795` / submission `41015603` /
source `a8eb3b2b…`, none of which is live. Its 20/35/50-minute band protocol answers a
different question (short-window candidate-vs-control transfer) than the one asked here (a
mature 160-game level). **Mechanics reused; decision protocol not.** Restoring the source named
in that runbook would be an error — the correct restore target is recorded below.

Governing precedent is `coordination/tasks/20260804-readable-no-orchard-arena.md`, the prior
submission of this same artifact.

## Exact candidate

| field | value |
|---|---|
| path | `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` |
| size | 75,634 bytes, 1,475 lines (within the 100,000-char gate) |
| SHA-256 | `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29` |
| prior identity | agent `6593838` / submission `41089629`, `displaced_superseded` |
| prior mature result | **24.76 / rank 21**, 160 games, 94W/2T/64L, identity + runtime clean |

Hash verified against the working copy immediately before publication.

## Pre-mutation baseline, measured 2026-08-12

Read-only platform recovery: live source recovered exact at
`2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381`, 55,799 bytes — matches the
registry's `active` record. Platform state is what our record says it is.

```text
ARENA-ROOM: tass rank 35/139 Legend score 22.7 | promotable=False | agentId=6594200
battles listed: 200
top 3: delineate 30.42 | norxondor_gorgonax 29.94 | MSz 28.34
```

**Correction of record:** we have been quoting the live bot as **22.81 / rank 32 / 137**. That
was its settled 160-game checkpoint. As of this read it is **22.7 at rank 35 of 139** — Legend
grew by two and we slipped three places. The 22.81 figure is a settled-checkpoint number and
remains valid as such; the *current standing* is rank 35/139. Both belong in the record and
should not be conflated.

## Restore target — READ THIS BEFORE ANY ABORT

Restore is to the **current live source**, not the one named in the promotion runbook:

```text
cgauto/submissions/candidate-agent6553250-e7a-r36-simplified.min.rs
SHA-256 2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381
agent 6594200 / submission 41090606 (registry disposition: active)
```

## Serialized execution

1. Commit, push and remotely verify this task record and the pre-mutation baseline **before**
   any mutation.
2. Submit the exact candidate with `cgauto/api_submit_once.py --expected-sha256 98628e98…`
   **exactly once**. Preserve the complete response and the returned submission id.
3. **Do not retry an ambiguous response.** The tool reports `ambiguous` explicitly; on ambiguity
   stop and read platform state before any further call.
4. Discover the new agent id, recover the live source against `98628e98…`, record the identity.
5. Initial health checkpoint once enough games have finished to detect compile/runtime/identity
   damage. Do **not** reject on a cold-start score — cold reads sit below matured ones.
6. Let it mature to ~160 games; take the terminal submission-scoped checkpoint and compare with
   the prior 24.76.
7. Restore only on unambiguous source/identity/runtime failure, never on weak performance.
8. Publish the result, reconcile STATE/ledger/registry/status, notify owner and peers.

## Acceptance

This task delivers an **observation**, not a verdict on whether to keep the bot. Outcomes:

- Second mature read within ~±0.5 of 24.76 → the level is corroborated; `readable__no_orchard`
  becomes our best-evidenced bot and the goal reframes against the 24.70 interim checkpoint.
- Second mature read near 23.3 → 24.76 was a favourable draw; stop treating it as our ceiling
  and correct the register.
- Anything else → report the spread honestly; two observations 1.5 apart establish variance,
  not a level.

The keep/restore decision after a clean mature read is the **owner's**, not this task's.

## Write set and exclusions

- `coordination/tasks/20260812-readable-no-orchard-rerun-arena.md`, own status/messages;
- `data/analysis/live-agent-6553250/readable-no-orchard-rerun-20260812/`;
- `docs/STATE.md` §1 live identity, ledger, submission-history registry once identity is
  unambiguous.

Excluded: all bot sources except read-only access to the exact candidate; the protected
`rust/src/bin/yamo_orchard_live.rs` (`fff6669b…`); raw games; the 05:17 cron; sealed map ranges;
external storage.

## Execution log

| UTC | action | result |
|---|---|---|
| 2026-08-12T16:00Z | read-only preflight, `recover_live_source.py` | live recovered exact `2caac7c6…`, 55,799 B |
| 2026-08-12T16:00Z | baseline `cg_rank.py --top 3` | `rank 35/139 score 22.7 agentId=6594200`; battles listed 200 |
| 2026-08-12T16:05Z | pre-mutation record committed and pushed (`cfab35bc`) | no mutation made |
| 2026-08-12T16:10Z | **`api_submit_once.py` — ONE mutation call** | `accepted=true ambiguous=false http=200` **submission_id 41113243** |
| 2026-08-12T16:12Z | `recover_live_source.py --expected-sha256 98628e98…` | **exact match**, 75,634 B — platform holds our source |
| 2026-08-12T16:14Z | agent-id discovery via `findLastBattlesByTestSessionHandle` | **agent 6604529 / submission 41113243** |
| 2026-08-12T16:25Z | initial health checkpoint | `games=21 score=18.63 rank=83/139 catastrophic=3 (14.3%) negative_mass=605` **signals=0 identity_clean=True** |
| 2026-08-12T15:55Z¹ | progress checkpoint, 127 games | `score=22.46 rank=36/139 catastrophic=19 (15.0%) negative_mass=5045` **signals=0 identity_clean=True** |
| 2026-08-12T16:07Z¹ | **terminal checkpoint, 160/160 finished, 0 pending** | `score=22.46 rank=35/139 89W/3T/68L mean_margin −1.75 catastrophic=24 (15.0%) negative_mass=6790` **signals=0 identity_clean=True**; `checkpoint-terminal.json` |

¹ The checkpoint packets' own `observed_at` reads `2026-08-09T…Z` (host clock); the surrounding
log uses the coordination-branch date convention, which runs three days ahead of the host. Both
are recorded as written — do not silently reconcile them. Elapsed submit → terminal is ~1 h 55 m
on a single monotonic clock.

## New live identity

| field | value |
|---|---|
| agent | `6604529` |
| submission | `41113243` |
| source | `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` |
| SHA-256 | `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29` |
| displaced | agent `6594200` / submission `41090606` (`2caac7c6…`) |

## Status of the observation

**COMPLETE — second mature observation obtained. `SINGLE_MATURE_RUN` is settled, and it settles
against the level, not for it.**

| observation | agent / submission | games | score | rank |
|---|---|---|---|---|
| first mature run | `6593838` / `41089629` | 160 | **24.76** | 21 |
| second mature run (this) | `6604529` / `41113243` | 160 | **22.46** | 35/139 |

Same source, SHA `98628e98…`, byte-identical, both runs identity-clean with zero runtime signals.
**Spread across two mature observations of one source: 2.30 points.**

Against the task's frozen decision rules: not within ±0.5 of 24.76 (not corroborated), and not
"near 23.3" either — it lands 0.81 *below* the related no-orchard ablation's 23.27. So the third
rule applies: report the spread honestly. **24.76 was a favourable draw and must stop being
treated as this source's level, let alone as our ceiling.**

The consequence is bigger than this candidate. The replacement discipline in `docs/STATE.md` §3
prices the arena's own noise band at **±0.5–1**. Two mature 160-game reads of an identical source
differ by **2.30**. Either that band is badly understated, or the ladder moved under us between
the runs — this single pair cannot separate those. Until it is separated, no promotion decision
resting on a sub-2-point mature delta is safe, which is most of them.

Standing context, for the keep/restore decision: the displaced bot (`6594200`, E7a r36 simplified)
settled at 22.81/rank 32/137 and had eroded to 22.7/rank 35/139 at the pre-mutation read. At
22.46/rank 35/139 the live bot is at **the same standing, inside noise** — this cycle neither
gained nor cost material ground.

No restore trigger fired at any point: source exact on the platform, identity clean, zero runtime
signals throughout. **The keep/restore decision is the owner's.**
