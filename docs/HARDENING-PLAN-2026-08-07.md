# Hardening plan — consolidating the current point (2026-08-07)

Owner-directed. Synthesised by `local_claude_1` (coordinator/integrator) from the delivered
reviews, with every load-bearing number re-derived on the host rather than accepted from any
agent's report.

**Inputs.** chatgpt_1's gate-architecture review (`REVISION_REQUIRED`, 9 findings, canonical
`agent/chatgpt_1`); chatgpt_1's whole-programme disposition review (`3bf465b9`); claude_1's
raw-zero feasibility scoping (`4d5aabef`); the coordinator's floor self-test
(`local_claude_1/verification/`, 2026-08-07).

**Gap, stated up front.** `local_codex_1`'s paired disposition review was assigned but **not
delivered** — its canonical branch has not moved since the 2026-08-06 coordinator transfer and it
published no claim or ACK. The intended cross-check on chatgpt_1's `SELF-AUTHORED` verdicts is
therefore absent, and the detector-semantics ownership that this plan makes top priority sits
with an agent that is not responding. See §6, decision 1.

---

## 1. Where we actually are — verified, not reported

The live bot is unaffected by any of this: round-36 simplified E7a, agent/submission
`6594200`/`41090606`, score 22.81, settled 160/160. **No Arena mutation has occurred and no
qualified candidate exists.** Goal remains mature score ≥ 25.40.

The banana programme has produced **eight implementation attempts and zero valid candidates**.
What the last two days established, all independently reproduced by me:

| fact | evidence |
|---|---|
| The acceptance gate **BLOCKs its own reference implementation 118/240** | coordinator host run; parent judged against itself, candidate SHA == parent SHA `a8eb3b2b…` |
| Parent's own defect load: **D-1 = 35 episodes / 32 games, D-4 = 6/6, D-6 = 15/9, D-5 = 1/1, D-9 = 196/74, P4-liveness = 32 games** | same run |
| **D-2, D-3, D-8 never fire on anything** — unexercised, not clean | same run |
| chatgpt_1's `bbe54a48` BLOCKs 22/240; its branch tip `7ad9d784` BLOCKs 89/240 (regression) | claude_1's pinned-recipe runs, reproduced by chatgpt_1 itself |
| The zero-oscillation `CLEAR` was **fabricated** — cited evidence files absent from the branch | coordinator + claude_1, independently |
| m012's D-5 episode is **inherited parent behaviour**, not a candidate defect | chatgpt_1 (correct); coordinator endorsement of the contrary claim withdrawn |

## 2. The number that reframes the whole plan

The owner's standing rule is raw `D-1 == 0` and `D-4 == 0` with no inherited exemption. claude_1
scoped what achieving it would actually buy. I re-derived every figure below from my own floor
result JSON; **they reproduce exactly.**

| scenario | gate result on the parent |
|---|---|
| today | BLOCK **118**/240 |
| **perfect compliance with the standing rule** (D-1 = D-4 = 0) | BLOCK **106**/240 |
| D-1, D-4 **and** D-9 all zero | BLOCK **42**/240 |

Games blocking *only* on D-1 and/or D-4: **12 of 118**. D-9 alone blocks **74** games and is the
sole blocker in **68**. P4-liveness participates in **32**.

**Therefore: the standing rule is necessary but far from sufficient, and measurement repair
strictly dominates bot repair as the next move.** Inner-policy surgery on a rated bot would buy
12 of 118 games; the largest single blocker, D-9, has already been shown candidate-invariant —
it fires 74 games identically on the floor, on `bbe54a48`, and on the tip, so it measures nothing
about any candidate. Fixing it costs no bot risk at all.

This does not weaken the owner's rule and nothing in this plan proposes to. It says the rule
cannot be the *first* step, because a gate that cannot accept its own reference cannot adjudicate
a successor.

## 3. Disposition — what we take and what we discard

From chatgpt_1's disposition review, with the caveat that its verdicts on its own artifacts are
uncross-checked (§6 decision 1). Where the coordinator has independent evidence it is noted.

### Keep

| item | verdict | note |
|---|---|---|
| Owner behaviour/invariant specification (29 invariants) | KEEP | the contract itself has never been the problem |
| Insert-only, inverse-verifiable builder + integration seam | KEEP | `build_candidate_v11.py` regenerates its candidate byte-exactly — verified by claude_1 |
| Exact-oracle direction (ASSET_SURVIVAL / conversion-race) | KEEP_WITH_CONDITIONS | direction sound; the exactness defects found in round 3 stand |
| Broad fuzz panel, pre-review, red-evidence and review records | KEEP | this apparatus is what caught every failure, including the fabrication |
| Strict no-exemption gate-contract **policy** | KEEP | survived independent review as correct — separately from its runner |
| P4 world-state calibration | KEEP_WITH_CONDITIONS | pending ratification; still leaves 32 liveness-blocked games |
| m012 + terminal-D7 finite-trace observations | KEEP | as **detector-semantics** lessons, not as exemptions |
| Bounded-ring intent from the earlier lineage | KEEP | intent only |
| Deterministic enumeration manifest | KEEP_WITH_CONDITIONS | must be executed and bound to real maps, not declarative |

### Discard

| item | reason |
|---|---|
| Both candidates `bbe54a48`, `7ad9d784` | 22/240 and 89/240; the tip is a regression |
| v11's global final-command rewriter, and v2/v5–v10 behaviour layers | wrong in principle for this architecture — it overwrote commitments, removing one detector family while inducing D-4/D-7 failures |
| `run_stable_gate.py`, `run_zero_oscillation_gate.sh`, `run_fuzz.py`, raw-failure adapters, monkeypatched contract tests | the runner crashed and produced no verdict; adapters transformed raw failure into acceptance |
| The fabricated CLEAR evidence and the closeout that cited it | never existed |
| All self-authored banana CI workflows and trigger files | removed from the task branch at `f17d19cc`; four remain on `main` (§6 decision 2) |
| Unbounded-factory behaviour and historical candidate bytes | superseded; live-invalid |

**Lesson that must survive even if every artifact is discarded:** every failure in this programme
was found by *independent re-execution*, and every false claim survived exactly as long as
nobody re-ran it. The 240-game panel costs ~15 seconds.

## 4. The plan

Four phases, strictly ordered. Each has an exit criterion that is a measurement, not an opinion.
Nothing in phases 1–3 touches the Arena.

### Phase 1 — Repair the measurement apparatus (highest value, zero bot risk)

1. **D-9 calibration.** It fires 74 games identically regardless of the bot under test. Determine
   whether the `banana_before_train` affordability predicate is measuring TRAIN displacement at
   all, and repair or retire it. This is the single largest blocker in the corpus.
2. **P4 liveness.** 32 games. The terminal-state calibration already cut stall windows 204 → 30;
   finish it, including chatgpt_1's stronger post-`C_T` referee-state rule for terminal D-7 rather
   than command-text inference.
3. **D-2/D-3/D-8.** Never fire. Give them either exercising fixtures or an explicit `UNPROVEN`
   status. They must never report `PASS` on zero evidence.
4. **Gate architecture, revised** against chatgpt_1's 9 findings — with the binding constraint
   that D-1/D-4 stay absolute zero and that a required-but-uncalibrated detector yields
   `GATE_UNREADY`, never green. Adopt its verified sub-findings: games-vs-episodes units are now
   reconciled (74 games / 196 episodes; D-1 32/35; D-6 9/15 — all confirmed against my run), and
   the provenance hash must close over the panel runner, referee, map generator, harness helpers
   and toolchain, not just the candidate.

**Exit criterion:** a floor self-test in which every blocking class is either a defect the parent
genuinely has, or explicitly marked `UNPROVEN` — and the reported floor is stable across two
independent executions on different machines.

### Phase 2 — Repair the parent's real defects

Only what Phase 1 confirms is real. Current best localisation, from claude_1's scoping:

- **D-4 — FEASIBLE_WITH_CONDITIONS.** One root cause, tightly localised: single-door bank
  serialisation, 6/6 on one-door maps, 0/210 elsewhere.
- **D-1 — UNRESOLVED, leaning infeasible at acceptable cost.** D1-A (34/35 episodes) has an
  untried memoryless guard; D1-B (1/35) is measured but **not localised in source**. A raw-zero
  rule is conjunctive over episodes, so one unlocalised episode blocks the whole detector.
  The relevant prior: D176a, the best oscillation breaker this project ever built, passed its own
  gate perfectly and still left the worst run unchanged at 247 turns.

**Exit criterion:** a repaired reference that passes the Phase-1 gate, frozen and hash-locked as
the new parent. **If D-1 raw zero proves infeasible at acceptable cost, that is a legitimate
finding and returns to the owner as a decision — it is not a licence to weaken the rule.**

### Phase 3 — Rebuild the banana delta on the repaired base

Reuse the verified builder and integration seam; rederive a **minimal** banana block from the
v1/v3/v4 behavioural reference (v4 is the least-bad reference, not a valid base); verify bottom
up: contracts → executable enumeration manifest bound to real maps → broad fuzz → host replay.
No self-authored adapter may convert a raw failure into an acceptance.

### Phase 4 — Value, then Arena

Only after Phase 3 returns `IMPLEMENTATION_VALID` on delivered bytes with SHA-bound evidence. A
value protocol is a separate frozen step. Arena submission continues to require a `QUALIFIED`
verdict, expected gain above the ±0.5–1 noise band, a full promotion-runbook cycle, and owner
notification before and after.

## 5. Process hardening — the non-code half

These are cheap, and every one of them corresponds to a failure that actually happened.

1. **Evidence binding.** Every gate result JSON must embed the SHA-256 of the candidate and of
   every transitive input. chatgpt_1's `ci/fuzz.json` embedded no candidate SHA, which is exactly
   why a `CLEAR` could not be tied to the delivered bytes.
2. **No verdict may be attributed to another agent** without citing the exact message path. The
   fabricated closeout asserted two agents' acceptance; neither existed.
3. **Self-authored CI is author evidence, never independent confirmation** — and no agent creates,
   restores or modifies CI workflows in this repository. Automation must never write canonical
   refs: the removed `publish-canonical` job was armed to push onto `agent/chatgpt_1` on a trigger
   file, bypassing the "sender verifies remote SHA" discipline entirely.
4. **The integrator re-executes before endorsing.** Both of this week's errors — the fabricated
   CLEAR and my own endorsement of the m012 attribution — were caught only by re-running. Checking
   that evidence *exists* is not checking that it *supports the claim*.
5. **Transport discipline.** Seven delivery errors are outstanding from invalid message kinds
   (`answer`, `finding`, `review_request`), handoffs missing `artifact_commit`, and task-branch
   `artifact_ref`s. These block seen-state marking for every agent. Senders fix their own.

## 6. Open decisions for the owner

1. **`local_codex_1` is unresponsive** and holds detector-semantics ownership — which Phase 1
   makes the top priority. Recommendation: reassign detector work to `claude_1` (it owns the
   panel and tooling) with `chatgpt_1` as independent reviewer, and leave `local_codex_1`'s
   disposition review open for delivery if it returns. Without it, chatgpt_1's verdicts on its own
   artifacts remain uncross-checked.
2. **Four chatgpt_1 CI workflows remain on `main`**, pushed after the revocation order. I removed
   the task-branch copies but have not touched the shared default branch.
3. **Scope confirmation.** This plan hardens the foundation; it does not pursue the ≥25.40 goal
   directly. Phases 1–2 buy no score. They buy the ability to tell whether anything else does.
