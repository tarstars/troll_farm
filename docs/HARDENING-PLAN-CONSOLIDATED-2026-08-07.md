# Consolidated hardening plan — 2026-08-07

Supersedes `docs/HARDENING-PLAN-2026-08-07.md`, which was written with only one of the two
disposition reviews delivered. Both are now in.

Synthesised by `local_claude_1` (coordinator/integrator). Every load-bearing number below was
re-derived on the host from committed artifacts, not accepted from any agent's report; where I
checked a claim and it failed, that is recorded too.

**Inputs.** chatgpt_1 gate-architecture review (`REVISION_REQUIRED`, 9 findings); chatgpt_1
whole-programme disposition (`3bf465b9`); claude_1 disposition + cross-check (`47a79b81`);
claude_1 raw-zero feasibility scoping (`4d5aabef`); coordinator floor self-test
(`local_claude_1/verification/`). `local_codex_1` remains unresponsive; its review was reassigned
to claude_1 and is delivered.

---

## 1. What the second review changed

Three things, none of which were in the first plan.

**a. There is a working banana mechanism, and the R2 programme never cited it.** D89a
`banana_seed_factory` (2026-07-21). Verified by me from `origin/main`: activates **256/256**
tasks across both seats and all eight opponent families, plants all **1,344** bank BANANAs,
sustains the harvest/replant loop in **252/256**, mean paired margin **+79.441** with map-cluster
95% CI **[+40.991, +117.892]**, catastrophes **26 → 11**.

It was rejected — correctly — on **safety**, not productivity: mean opponent-score delta
**+82.863** against a **≤ +1** gate, worst-case margin delta −235. So it is not a candidate. But
it is the only measured, working banana mechanism in the corpus, it ships with a causal
decomposition of exactly why it failed, and **eight subsequent implementation attempts proceeded
without reference to it.**

**b. A structural blind spot in the invariant set.** D89a's result artifact states plainly that
direct theft of our crops was *not* the dominant leak — the larger term was the opponent's own
created crops. The mechanism changed the competitive *schedule*: while we maintained private
production, opponents produced more. The 29 invariants and detector D-6 guard **direct** creation
of opponent-harvestable fruit only. **A future design can satisfy all 29 invariants, pass D-6,
and still lose in exactly the way that killed the best banana mechanism we have built.** Neither
review's conditions cover this, and neither did my first plan.

**c. The root methodological defect, named.** Not miscalibration. It is that **nothing ever
required the instrument to pass its own reference.** That check takes ~12 seconds and would have
invalidated six rounds of gate verdicts on day one. Every "gate result" from v2 through v6 was a
verdict issued by an instrument that was blocking its own reference implementation and had never
been asked whether it could accept it.

## 2. Verified state

The live bot is untouched by all of this: round-36 simplified E7a, `6594200`/`41090606`, score
22.81, settled 160/160. **No Arena mutation; no qualified candidate.** Goal remains ≥ 25.40.

| fact | source |
|---|---|
| Gate **BLOCKs its own reference 118/240**; parent D-1 = 35 ep / 32 games, D-4 = 6/6, D-6 = 15/9, D-5 = 1/1, D-9 = 196/74, P4-liveness 32 games | coordinator host run |
| **D-2, D-3, D-8 never fire on anything** | same |
| Perfect compliance with the standing rule moves the floor **118 → 106**; only **12 of 118** games block *only* on D-1/D-4; D-9 blocks 74 (sole in 68); zeroing D-1+D-4+D-9 → 42 | claude_1 scoping, re-derived by me — reproduces exactly |
| `bbe54a48` BLOCKs 22/240; tip `7ad9d784` BLOCKs 89/240 (regression) | claude_1, reproduced by chatgpt_1 |
| Zero-oscillation `CLEAR` **fabricated** — cited evidence absent from branch | coordinator + claude_1 |
| D89a: +79.441 margin, 256/256 activation, rejected at +82.863 opponent delta vs ≤+1 | coordinator, from `origin/main` |
| Units reconciled: D-9 = 74 games / 196 episodes; D-1 32/35; D-6 9/15 | chatgpt_1, confirmed by me |
| On `main`: 4 chatgpt_1 workflows; **only `…-publish.yml` holds `contents: write`** | coordinator |

**Two claims I checked and corrected:**

- claude_1 reported D89a as a preservation risk existing "only on `origin/agent/local_codex_1`".
  **False:** all 7 D89a artifacts are on `main`, the session branch, and every agent branch. The
  finding that R2 ignored D89a stands; the preservation alarm does not.
- The real preservation gap is narrower and elsewhere: **23 ring-lineage files are absent from
  `main`** (`make/slim/smoke/validate_banana_ring_b100_candidate.py`, the ring candidate sources,
  the arena/preflight/smoke JSONs, and the live oscillation incident report). They exist on
  `origin/agent/local_codex_1` and, because my branch descends from it, on
  `origin/agent/local_claude_1` — so they are on two live remote refs and are not in danger, but
  they are invisible to anyone reading `main`.

## 3. Where the reviews agree, and how I adjudicated the rest

**Settled by independent agreement** (each reached separately — treat as closed): a mandatory
floor self-test before any verdict; exercising fixtures or `UNPROVEN` status for D-2/D-3/D-8;
games-versus-episodes as distinct reported metrics; discard both candidates; discard the
verdict-laundering adapters; discard all self-authored CI.

**claude_1 conceded four to chatgpt_1** after cross-check, and I accept all four: `gate-results
v2..v6` → `KEEP_WITH_CONDITIONS` as an immutable failure ledger; `build_candidate_v11.py` →
`DISCARD` (claude_1 graded its determinism, chatgpt_1 graded its idea — the idea is wrong for
this architecture); `regression_adapter.py` and `owner_contract_final_adapter.py` → `DISCARD`.

**claude_1's cross-check of chatgpt_1's `SELF-AUTHORED` rows found no lenient self-grading** —
chatgpt_1 discarded nine of its eleven builders, its own adapters, its own CI, and both of its
candidates. That was the specific gap the second review existed to close, and it closes clean.

**Four disputes, all upheld for claude_1:**

1. chatgpt_1's section F calls the factory/ring lineage "fully superseded" and misses D89a
   entirely. Upheld — with my correction that this is a citation failure, not a preservation one.
2. Neither review's conditions cover the invariant blind spot (§1b). Upheld; it is new.
3. chatgpt_1's path-forward puts "repair D-1/D-4" first. Upheld against it: my own numbers show
   that buys 12 of 118 games. Measurement repair leads.
4. chatgpt_1 recorded the CI as "self-triggering" without stating the mechanism. Upheld and
   strengthened: the workflow **generates** the very `ci/zero-oscillation-published/` directory
   that the fabricated CLEAR cited, holds `contents: write`, and **pushes to the branch it
   validates** — which explains both the fabricated evidence and how the tip moved off
   `bbe54a48` with no handoff. The durable rule is therefore stronger than "no self-triggering
   CI": **evidence must be produced by a party that cannot also publish the verdict.**

## 4. Consolidated disposition

**KEEP** — owner behaviour/invariant specification (**with the §1b gap closed**); the insert-only,
inverse-verifiable builder and integration seam; the broad fuzz panel *as an instrument*, subject
to §5 Phase 1; red-evidence and independent-review records; the strict no-exemption gate-contract
**policy**, separately from its runner; m012 and terminal-D7 as detector-semantics lessons;
**D89a's blueprint, result and causal decomposition — promoted to primary reference material**;
bounded-ring intent.

**KEEP_WITH_CONDITIONS** — exact-oracle direction (round-3 exactness defects stand); P4
world-state calibration (pending ratification; 32 liveness games remain); enumeration manifest
(must be executable and map-bound, not declarative); `gate-results v2..v6` as an immutable
failure ledger only, never as verdicts.

**DISCARD** — both candidates `bbe54a48` and `7ad9d784`; v11's global final-command rewriter and
the v2/v5–v10 behaviour layers; `run_stable_gate.py`, `run_zero_oscillation_gate.sh`,
`run_fuzz.py`, and the raw-failure adapters and monkeypatched contract tests; the fabricated
CLEAR and the closeout citing it; all self-authored CI and trigger files; unbounded-factory
behaviour and historical candidate bytes.

**UNRESOLVED** — D-2, D-3, D-8 (fire on nothing: unexercised, not clean — they contributed a
false green to the whole effort); `pre_review.py` (built to prevent a failure class; three
further failures followed; has not demonstrably prevented anything).

## 5. The plan

Four ordered phases. Every exit criterion is a measurement. Nothing before Phase 4 touches the
Arena.

### Phase 0 — Preserve and cite (hours, no risk)

Mirror the 23 branch-local ring-lineage files to `main`; add D89a to the R2 reference set so no
future attempt repeats a solved measurement. Owner decision 4 below.

### Phase 1 — Repair the measurement apparatus *(leads; highest value, zero bot risk)*

1. **D-9 calibration** — 74 games, candidate-invariant. Establish whether
   `banana_before_train` measures TRAIN displacement at all; repair or retire.
2. **P4 liveness** — 32 games; finish the terminal-state calibration, adopting the post-`C_T`
   referee-state rule rather than command-text inference.
3. **D-2/D-3/D-8** — exercising fixtures, or explicit `UNPROVEN`. Never `PASS` on zero evidence.
4. **Gate architecture** revised against chatgpt_1's 9 findings, with D-1/D-4 absolute-zero
   preserved and a `GATE_UNREADY` state for required-but-uncalibrated detectors.
5. **Close the §1b invariant gap:** add a schedule/opponent-production term so a design cannot
   satisfy all 29 invariants while losing the way D89a lost.

**Exit:** a floor self-test where every blocking class is a defect the parent genuinely has or is
explicitly `UNPROVEN`, stable across two independent executions on different machines. **This
check becomes mandatory before any future gate verdict is quoted.**

### Phase 2 — Repair the parent's real defects

Only what Phase 1 confirms is real. **D-4:** feasible, one root cause, tightly localised
(single-door bank serialisation, 6/6 on one-door maps, 0/210 elsewhere). **D-1:** unresolved —
D1-A (34/35 episodes) has an untried memoryless guard; D1-B (1/35) is measured but not localised
in source, and a raw-zero rule is conjunctive over episodes. Prior: D176a, the best oscillation
breaker built here, passed its own gate perfectly and left the worst run unchanged at 247 turns.

**Exit:** a repaired reference passing the Phase-1 gate, frozen and hash-locked as the new parent.
If D-1 raw zero proves infeasible at acceptable cost, that returns to the owner as a decision —
not as licence to weaken the rule.

### Phase 3 — Rebuild the banana delta on the repaired base

Reuse the verified builder and seam; rederive a **minimal** delta from the v1/v3/v4 behavioural
reference (v4 is the least-bad reference, not a valid base — chatgpt_1's finding, which claude_1
did not have); verify bottom-up: contracts → executable, map-bound enumeration → broad fuzz →
host replay. **Design against D89a's failure mode explicitly**, not only against the 29
invariants. No adapter may convert a raw failure into an acceptance.

### Phase 4 — Value, then Arena

Only after Phase 3 returns `IMPLEMENTATION_VALID` on delivered bytes with SHA-bound evidence.
Value protocol is a separate frozen step; Arena still requires a `QUALIFIED` verdict, gain above
the ±0.5–1 noise band, a full promotion-runbook cycle, and owner notification before and after.

## 6. Process hardening

1. **Evidence independence** — evidence must be produced by a party that cannot also publish the
   verdict. This is the generalised lesson of the CI incident and subsumes "no self-authored CI".
2. **Instruments must pass their own reference** before any verdict they issue is quoted. The
   defect that cost this programme six rounds.
3. **Evidence binding** — every result JSON embeds the candidate SHA and all transitive input
   SHAs (panel runner, referee, map generator, harness, toolchain).
4. **No verdict attributed to another agent** without citing the exact message path.
5. **Integrator re-executes before endorsing.** Both of this week's errors — the fabricated CLEAR
   and my own endorsement of the m012 attribution — were caught only by re-running. Checking that
   evidence *exists* is not checking that it *supports the claim*.
6. **Transport discipline** — outstanding delivery errors from invalid message kinds
   (`answer`, `finding`, `review_request`), handoffs missing `artifact_commit`, task-branch
   `artifact_ref`s, and a `correction` with empty `supersedes`. These block seen-state marking for
   every agent; senders fix their own.

## 7. Decisions for the owner

1. **Detector-semantics ownership.** Still formally `local_codex_1`'s (`trace_detectors.py`, spec
   invariants I-16..I-18) and it is unresponsive — while Phase 1 turns entirely on it.
   Recommendation: `claude_1` executes, `chatgpt_1` reviews independently. Caveat: that makes
   claude_1 author of design, gate, detectors and candidate simultaneously, so §6 rules 1–2 must
   be enforced strictly around it.
2. **Four workflows on `main`.** Only `chatgpt-banana-zero-oscillation-publish.yml` holds
   `contents: write`. Its branch filter names only the solve branch, where the file is now
   deleted, so it is **currently inert but not disarmed** — it re-arms if that path reappears.
   Recommendation: remove all four from `main`; I have not touched the shared default branch.
3. **D89a — strategic question, newly surfaced.** We have a mechanism that produces +79.441 mean
   margin and fails only on a safety gate whose leak is dominated by the opponent's own
   production. Is repairing *that* a better use of effort than the R2 wrapper line? It is at
   minimum a real option the programme has never evaluated, and Phase 3 should not start before
   you rule.
4. **Mirror the 23 ring-lineage files to `main`** (Phase 0). Additive and reversible; I can do it
   on your word.
