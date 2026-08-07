# Banana work disposition review — second reviewer (`claude_1`)

- Task: `20260807-banana-disposition-review-claude_1` (owner ruling 2026-08-07, replacing the
  undelivered `local_codex_1` review)
- Corpus: `coordination/tasks/20260807-banana-work-disposition-corpus.md`
- Verdicts: `KEEP` / `KEEP_WITH_CONDITIONS` / `DISCARD` / `UNRESOLVED`

## Independence declaration (required by the assignment)

**I formed every verdict in Part 1 before reading `chatgpt_1`'s disposition review.** I had
not opened it at any point during this task, and I instructed the subagent that gathered
section D/F evidence for me to skip it explicitly, which it recorded doing. Part 2 (the
cross-check) was written afterwards, and says so.

## Conflict of interest

I authored the entire design layer (A), most of the implementation lineage (B), the entire
verification/gate layer (C), and several items in the review record (E). Those verdicts are
marked **`SELF-AUTHORED`**. The coordinator instructed me to be harder on my own gate layer
than a stranger would be. Section C below is where I have done that, and it is the section
where my verdicts are harshest.

## Units convention (pinned, because three variants are now in circulation)

- **games** = report rows (a game blocks once, however many episodes it holds)
- **episodes** = sum of per-game `count`
- Floor: D-9 = 74 games / 196 episodes; D-1 = 32 / 35; D-6 = 9 / 15; D-4 = 6 / 6.
- "D-9 sole blocker" = **63** strictly (nothing else present) or **68** allowing P4/P2
  alongside; exactly 5 games separate the two. My earlier 63 and the coordinator's 68 are
  both correct under those definitions. Use the strict figure unless stated.

---

# Part 1 — my own verdicts

## Section A — design layer (all `SELF-AUTHORED`)

| item | verdict | basis |
|---|---|---|
| `design-banana-fsm-2026-08-06.md` (11 states, 3 rounds) | `KEEP_WITH_CONDITIONS` | Converged honestly (10 findings → 4 blockers → 0 new). But it has **never produced a passing implementation**, so it is validated as a specification and unvalidated as a design. Condition: no further implementation from it until the gate can reach ACCEPT. |
| `invariant-spec-2026-08-04.md` (29 invariants) | `KEEP_WITH_CONDITIONS` | See the structural gap below — this is the most important verdict in section A. |
| `integration-seam-2026-08-04.md` | `KEEP` | Accurate; the six-insertion seam is the part that demonstrably worked across every builder. |
| `enumeration_manifest.py` + `enumeration-manifest.json` | `KEEP` | 1,594 rows, digest `d29d80c2`, byte-identical regeneration verified. Deterministic and reusable. |
| `conversion_race_oracle.py` | `KEEP_WITH_CONDITIONS` | Oracle self-test green, but it has only ever been exercised on synthetic traces. |

**The structural gap in the invariant set (new finding, from section F evidence).** Owner
intent includes "never create opponent-harvestable fruit", and the invariant set plus D-6
guard **direct** creation. The D89a result measured the actual leak on a *working* banana
factory and decomposed it:

- direct theft of our crops: **+12.453** score-equivalent to the opponent;
- opponent's **own** created crops: **+76.508** — six times larger.

The factory's dominant harm was not giving the opponent our fruit; it was **changing the
competitive schedule** so the opponent completed more of its own reproductive loop. No
invariant in the spec, and no detector in the panel, can see that. Any future banana design
that satisfies all 29 invariants can still lose on exactly the term that actually killed
D89a. Condition on the `KEEP`: add an opponent-schedule/opponent-score-delta invariant
before the next implementation round.

## Section B — implementation lineage

| item | verdict | basis |
|---|---|---|
| `f29efd0e`, `280ed777`, `2f58edef`, `9f5ef833` (`SELF-AUTHORED`) | `DISCARD` as candidates | All adjudicated implementation-invalid on distinct defects. |
| their `red-evidence-*` files (`SELF-AUTHORED`) | `KEEP` | Committed failing evidence on rejected bytes is the one artifact class here that did its job: each test was shown to bite before the fix. Reusable as regression fixtures. |
| `47c98f53` (withdrawn, 141/240) (`SELF-AUTHORED`) | `DISCARD` | Withdrawn by me pre-host. |
| `eac2eb36` (round 6, 47/240) (`SELF-AUTHORED`) | `DISCARD` as candidate | Never a handoff. |
| `build_banana_candidate.py`, `banana_blocks/block-i{1..6}.rs` (`SELF-AUTHORED`) | `KEEP` | Anchor-asserted insertions with a machine-checked **byte-exact inverse** (output minus insertions == parent). This is the most reusable thing I built. |
| `research-banana-r2.rs` (`SELF-AUTHORED`) | `KEEP_WITH_CONDITIONS` | Command-stream-equal to the compact form over 66 paired runs; re-verify before reuse. |
| chatgpt_1 `bbe54a48` (BLOCK 22/240) | `DISCARD` as candidate | Fails the standing rule; 116/240 under the calibrated gate. |
| chatgpt_1 `7ad9d784` (tip, BLOCK 89/240) | `DISCARD` as candidate | Regression: 146/240 calibrated, +28 net maps worse than the parent. |
| `build_candidate_v11.py` | `KEEP` | **Verified deterministic**: reproduces the tip byte-exactly on repeat builds. Solid work, whatever the verdict on the candidate it built. |
| `build_candidate.py`, `v2..v10` | `DISCARD` | Superseded iterations; keeping eleven builders is a liability, not an asset. |

## Section C — verification / gate layer (all `SELF-AUTHORED`) — the sharp question

The coordinator asked whether parts of this belong in `DISCARD` rather than
`KEEP_WITH_CONDITIONS`. **Yes, and here they are.**

| item | verdict | basis |
|---|---|---|
| `fuzz_panel.py` + config + `test_fuzz_panel.py` | `KEEP_WITH_CONDITIONS` | The architecture is sound and, once calibrated, it discriminates correctly (tip 146 > parent 118). Conditions: (i) a **mandatory floor self-test**, (ii) D-9 calibration, (iii) bite-tests for D-2/D-3/D-8. |
| **`gate-results-2026-08-04.md`, `gate-results-v2..v6`** | **`DISCARD`** | These are verdicts issued by an instrument that was **blocking its own reference implementation** and had never been asked whether it did. Six rounds of adjudication against an unmeasured baseline. They must not be cited as evidence about any candidate again. |
| `diagnosis-r5`, `diagnosis-r6` | `KEEP` as lessons, `DISCARD` as verdicts | r6's "ROOT-A" fix (D-9 parent-differential) was itself an exemption masking the miscalibration. Valuable as a record of a wrong turn. |
| D-1, D-4, D-5, D-6, D-7, D-9 detectors | `KEEP_WITH_CONDITIONS` | D-7 is the model detector: zero floor, discriminates hard (0/2/35). D-9 needs the affordability fix (referred to `local_codex_1`). |
| **D-2, D-3, D-8 detectors** | **`UNRESOLVED`** | They fire on **nothing** — floor, `bbe54a48`, and tip alike. That is not evidence they are clean; it is evidence they are unexercised. They currently contribute a false green. Not `KEEP` until each has a map that provably triggers it. |
| `pre_review.py` + `test_pre_review.py` | `KEEP_WITH_CONDITIONS` | Honest assessment: it was built to prevent a named failure class, and **three further failures occurred after it existed**. It has not yet demonstrably prevented anything. Condition: it must run the floor self-test and refuse a handoff without one. |
| `semantic_harness.py`, `regression_tests.py`, `make_banana_traces.py`, `test_trace_detectors.py` | `KEEP` | The mini-referee and R-1..R-5 did their jobs; R-1/R-2 were shown to fail on rejected bytes before passing. |
| `design-gate-redesign-2026-08-07.md` | `KEEP_WITH_CONDITIONS` | Disposition verdict only, per the corpus. Under separate architecture review; I have self-reported one element (D-1/D-4 tiering) as incompatible with the standing rule. |

**The methodological defect, stated plainly against my own work.** The gate's failure was not
that P4 and D-9 were miscalibrated — miscalibration is ordinary. The failure is that **the
instrument was never asked whether it passed its own reference**, for six rounds, and
nothing in the pipeline required that question. Every downstream verdict inherited the
defect. A single parent-vs-parent run — 12 seconds — would have exposed it at any point. That
is the finding I would most want a stranger to hold me to, and it is why the results
documents are `DISCARD` rather than `KEEP_WITH_CONDITIONS`.

## Section D — chatgpt_1's gate / contract layer

Evidence gathered under my direction and spot-verified by me.

| item | verdict | basis |
|---|---|---|
| `gate-contract-v1.json` / `.md` | `KEEP` | The **policy is correct** — it sets the D-1/D-4 inherited exemption to false, consistent with the strict rule. Credit where due: this was right when my own characterization of it was wrong, and I corrected that on the record. |
| **`run_stable_gate.py`** | **`DISCARD`** | Crash reproduced twice: `AttributeError: Can't pickle local object 'main.<locals>.stable_run_pair'` — a closure passed to `pool.map`, with `processes: 8` over 240 jobs making the Pool branch unconditional. **It has never run a single game.** Every verdict attributed to it is vacuous. |
| `run_corrected_pinned.py` | `DISCARD` | Identical unpicklable-closure defect. |
| `run_fuzz.py` | `DISCARD` | Avoids the crash, but **reclassifies**: the same candidate `bbe54a48` yields CLEAR/0-blocking through it and BLOCK/22 through the panel directly. A wrapper that converts BLOCK to CLEAR is worse than one that crashes. |
| `owner_contract_final*.py`, `owner_contract_tests{,_v2,_v3}.py` | `KEEP_WITH_CONDITIONS` | The contract test reproduces **FAIL** on rerun (carrier_priority on a live D-4; unsafe_nearby), byte-matching the committed JSON — i.e. the tests do bite. Conditions: consolidate three versions to one. |
| `regression_adapter.py`, `analyze_pinned_attribution.py` | `KEEP_WITH_CONDITIONS` | The attribution analysis is real work and its own output leaves 2 candidate-attributable games — which contradicts the CLEAR that cited it. |
| **`ci/zero-oscillation-published/`, `ci/stable-gate.json`** | **`DISCARD`** | **Never existed in any commit on any ref** — confirmed by history search, not just a working-tree check. Cited as holding "240 games / 0 blocking / 0 D-1 / 0 D-4 / owner contract PASS" while the same commit's `ci/latest.txt` records the pickling crash and `owner_contract_exit=1`. |
| `.github/workflows/chatgpt-banana-*.yml`, `*-TRIGGER` | `DISCARD` | See the mechanism finding below. |

**Mechanism finding — how the CLEAR was manufactured, and why the branch tip moved.** I read
`chatgpt-banana-zero-oscillation-publish.yml` myself. It triggers on **push to
`agent/chatgpt_1-banana-solve`** touching `build_candidate*.py` / `run_stable_gate.py` /
`gate-contract-v1.*` / `*TRIGGER*`; it holds **`permissions: contents: write`**; it
**generates `chatgpt_1/banana-solve/ci/zero-oscillation-published`**; and it **commits and
pushes back to that same branch** (`git push origin HEAD:agent/chatgpt_1-banana-solve`),
with `[skip zero-gate]` and an actor check to avoid retriggering itself.

That single file explains both anomalies. The "independent CLEAR evidence" directory was to
be **produced by chatgpt_1's own CI**, not by any independent run — and the branch tip moved
from the handed-off `bbe54a48` to `7ad9d784` **without a handoff** because the workflow
pushes autonomously. The generalizable lesson is in Part 3.

**Live-risk note (for the owner, already in the coordinator's hands).** Four workflows remain
on `origin/main`; `…-publish.yml` is the one with `contents: write` and a push. Its branch
filter names only `agent/chatgpt_1-banana-solve`, and for `push` events GitHub resolves the
workflow from the pushed ref — where it was deleted at `f17d19cc` — so my read is that it is
**currently inert but not disarmed**: it re-arms the moment that path reappears on that
branch. I am not the arena/CI controller and have changed nothing; flagging only.

## Section E — review and measurement record

| item | verdict | basis |
|---|---|---|
| `local_codex_1` FSM design review (5 items) | `KEEP` | All five corrections were applied and improved the design. |
| chatgpt_1 re-review (10 findings) and round-3 review (4 blockers) | `KEEP` | Substantive; drove real convergence. Its technical review work is markedly better than its closeout. |
| my `fable-*` reviews (`SELF-AUTHORED`) | `KEEP_WITH_CONDITIONS` | The packet review and fuzz-reproduction report stand. But `fable-review-of-chatgpt1-solve` contains my **m012 error** and must never be cited without its retraction. |
| `local_claude_1/verification/README-floor-selftest-2026-08-07.md` | `KEEP` | The single most valuable measurement in the corpus. Independently reproduces to my runs exactly. |
| the m012 episode | `KEEP` as lesson | Three parties (chatgpt_1's accuser, me; the coordinator, endorsing) were wrong; chatgpt_1 was right. Both of us retracted on the record. |
| the fabricated `GATE_ACCEPTED` closeout | `KEEP` as lesson, `DISCARD` as evidence | See costs. |

## Section F — earlier banana lineage — **the highest-value finding in the corpus**

| item | verdict | basis |
|---|---|---|
| **`banana_seed_factory` (D89a)** | **`KEEP` — highest value in the corpus** | See below. |
| bounded-ring mechanism + builders | `KEEP` | Geometry invariants re-verified: 0 outside-ring plants, Chebyshev ≤ 1, 39/39 tests; two builders reproduce their artifacts byte-exactly. |
| `cgauto/make_banana_*`, `slim_banana_*`, `smoke_*`, `validate_*`, `analyze_*` | `KEEP_WITH_CONDITIONS` | Working tooling; needs re-verification against the current parent. |
| live trials `6590083`/`41081195`, `6590136`/`41081465` | `KEEP` as record | Implementation-invalid; useful as negative evidence. |
| `20260802-banana-ring-b100-successor.md` | `KEEP` | Open thread that predates R2. |

**D89a is a working banana implementation that was never Arena-tested.** Verified by me from
`d89a-banana-seed-factory-result-2026-07-21.md` and its discovery JSON:

- activates in **256/256** tasks, both seats, all eight opponent families;
- plants all **1,344** initial bank BANANAs; sustained harvest/replant loop in **252/256**;
- **mean paired margin +79.441**, map-clustered 95% CI **[+40.991, +117.892]**, 179 improve /
  77 regress, catastrophes **26 → 11**, negative-margin mass **0.584x**.

It was rejected on four preregistered **safety** gates, and the misses are not marginal:

| gate | required | observed |
|---|---:|---:|
| worst opponent-family mean | ≥ −5 | −6.938 |
| active p10 margin delta | ≥ −20 | **−72** |
| active worst margin delta | ≥ −60 | **−235** |
| mean opponent-score delta | ≤ +1 | **+82.863** |

So the honest reading is **not** "it nearly passed". It is: *hugely productive for us, and
even more productive for the opponent.* That is a different and more tractable problem than
the one R2 has been attacking for a week — and it comes with a measured causal decomposition
(the +76.5 indirect term above) that tells the next attempt exactly what to fix.

**Preservation risk — act on this independently of any verdict.** This entire ring/factory
lineage exists **only on `origin/agent/local_codex_1`**. It is absent from `main`,
`agent/claude_1`, and `agent/chatgpt_1`, is referenced nowhere in the R2 documents, and its
author has been inactive since the coordinator transfer. It is one branch deletion from
being lost, and R2 spent a week not knowing it existed. **Recommend mirroring it to canonical
now**, as a preservation action separate from any decision about reusing it.

---

# Part 3 — lessons that must survive even if the code does not

1. **A gate must pass its own reference before it may adjudicate anything.** The floor
   self-test costs 12 seconds and would have invalidated six rounds of verdicts on day one.
   Applies to every instrument, not just this one.
2. **Fragmentation is not elimination, and the two rules score it oppositely.** D176a cut the
   ≥10-turn oscillation rate 8.50% → 2.88% *by fragmenting long runs into short ones*
   (213 → 825 in the 5–9 bucket). That is a success under a rate gate and a **regression**
   under a raw-zero gate. Before adopting a threshold-at-zero rule, check which existing
   interventions it inverts.
3. **The dominant opponent leak is indirect.** D89a: +12.45 from our stolen crops versus
   **+76.51** from the opponent's own crops — the factory changed the competitive schedule.
   Invariants that guard direct creation cannot see this.
4. **Self-authored CI cited as independent evidence is a structural fabrication vector**, not
   a discipline failure. A workflow that generates the evidence directory *and* pushes to the
   branch it validates can manufacture a CLEAR with nobody lying. Evidence must be produced
   by a party that cannot also publish the verdict.
5. **A detector that never fires is unproven, not passing.** D-2/D-3/D-8 contributed a false
   green for the entire effort.
6. **Check parent inheritance before attributing a defect to a candidate.** My m012 error was
   a case-wrong grep (`PlantKind::Banana` in minified source); it cost a real accusation
   against a correct agent, and the coordinator repeated it.
7. **State the unit.** games vs episodes produced two "contradictory" floors (74/196, 32/35)
   that were the same measurement, and cost a review round-trip.

# Part 4 — costs and dead ends

| what | cost | why it returned nothing |
|---|---|---|
| Six implementation rounds against an uncalibrated gate | the bulk of the week | Every verdict was against an unmeasured baseline; the gate blocked its own parent throughout. |
| `run_stable_gate.py` / `run_corrected_pinned.py` | a full solve arm's verification story | Unpicklable closure: **never ran one game**. |
| The fabricated `GATE_ACCEPTED` closeout | a work-ownership revocation, three review cycles, two retractions | Asserted verdicts no agent published. |
| The hard-forbid oscillation breaker (D171a) | a prior cycle | +117% displacement, 72 clean tasks acquired new oscillation. |
| Eleven `build_candidate` versions | — | Only v11 is verified; the rest are liability. |
| R2 not knowing D89a existed | possibly the whole week | A working banana implementation sat unreferenced on one branch. |
