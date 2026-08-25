# Session findings, 2026-08-07 → 2026-08-11 (`claude_1` / fable)

Context-flush digest. Successor to `SESSION-FINDINGS-2026-08-03-to-05.md`. Everything here is
either MEASURED by me or cited to the artifact that measures it. Read §6 first if you are short
of time — the error patterns cost more than the findings gained.

---

## 1. Programme state at flush

- **The panel is `GATE_UNREADY`.** TRAIN referee repair r4 delivered, awaiting `chatgpt_1`
  acceptance (owns it) and `local_claude_1` execution review (blocker B1). r1 and r2 were
  `NOT ACCEPTED`; r3 was `DISPATCH_LAYER_ACCEPTED — PANEL_REVISION_REQUIRED`.
- **Parked behind panel acceptance:** P4 post-`C_T`, D-4 repair, gate revision 3, D-9
  calibration, and every candidate verdict. Do not restart these without checking the ruling.
- **Instrument:** `fuzz-panel/5` · corpus `c5-two-player-phase-merged-2026-08-11`.
  **Floor (parent vs itself) = 118/240. Candidate run (banana `eac2eb36` vs parent) = 121/240.**
  These are different quantities — see §6.2.
- Coordinator/integrator/arena controller: **`local_claude_1`** (since 2026-08-06). **Detector
  semantics also `local_claude_1`** (since 2026-08-08, taken from an unresponsive `local_codex_1`).
- Review pairing is **capability-matched**: `claude_1` = execution reviewer (can run suites),
  `chatgpt_1` = adversarial/committed-blob reviewer (could not clone the repo). This is not a
  hierarchy — `chatgpt_1` found the TQ-2 authorization hole and the r2/r3/r4 blockers by reading.

## 2. The finding that reordered the programme

**The acceptance gate blocked its own reference implementation.** Parent judged against itself
= BLOCK 118/240. Consequences, all measured:

- **Perfect compliance with the owner's strict rule (raw `D-1 == 0`, `D-4 == 0`) moves the floor
  only 118 → 106.** Just 12 of 118 games block solely on D-1/D-4.
- **Measurement repair therefore precedes bot repair** — the ordering the owner adopted.
- Six rounds of prior gate verdicts were issued against an unmeasured baseline. A single
  parent-vs-parent run costs ~12 seconds and would have exposed it on day one.

## 3. Instrument defects found (all real, all measured)

1. **The referee silently discarded `TRAIN` — and `MINE`.** `grep -c TRAIN fuzz_panel.py`
   returned 0. Worst consequence: on `m040` both seats the bot re-emitted a discarded TRAIN for
   83–91% of the game, and **those two games scored among the panel's cleanest** (D-1..D-9 all
   zero). A candidate could be *rewarded* for provoking a state that displaces real work while
   remaining invisible. The exhaustive-dispatcher fix immediately found the second verb.
2. **D-9 is `INSTRUMENT_UNSUPPORTED / GATE_UNREADY`.** Its unpaired `banana_before_train` proxy
   fired 196 episodes / 74 games on the floor while all three paired clauses fired zero — because
   `p_train` is never set, so the paired block never executes. Both committed D-9 tests call
   `detect_d9(tr)` with **one argument**, so the paired clauses are uncovered on *both* axes.
   (My earlier `INAPPLICABLE` and the "196 false positives" framing are **withdrawn**.)
3. **`founding_safety_oracle` is called by zero detectors.** Design finding F4 records it as
   replacing arrival-order; `detect_d6` still uses arrival-order.
4. **D-6 is a `CONTRACT AUTHORITY: CONFLICT`, not a falsification.** The standing invariant spec
   and a later retrospective design disagree and **no ratified supersession exists**. My original
   "enforces a retired predicate" claim was stronger than the evidence.
5. **The bite-test suite pins about a third of its behaviour**: mutation kill rate **21/64
   (32.8%)**, reproducible from `claude_1/banana-restoration-r2/bitetest-audit/run_mutations.py`.
   **22 of 47 detector branches have NO FIXTURE at all** — that number matters more than the rate.
6. **The shipped bot and the sacred source have diverged and are cited interchangeably.**
   Shipped `readable__no_orchard` = `98628e98…`; sacred `yamo_orchard_live.rs` = `fff6669b…`;
   parent = `a8eb3b2b…`. Engine authority = `rust/src/game/engine.rs` = `7c240abf…`.

## 4. Substantive findings worth keeping

**Oscillation (subject `98628e98`).** Three mechanisms with one common cause:
- **M1** corridor block — a stationary peer occupies the only route and the resolver invents a
  retreat;
- **M2** stationary occupation is invisible to planning — **`compatible` returns `true`
  unconditionally when either target is `Target::None`** (`yamo_orchard_live.rs:1330-1331`);
- **M3** scorer cycle — **`endgame_candidates` (~1290-1302)** prices only the door a unit stands
  on but all doors one step away, a ~25% valuation discontinuity for the same plan. **This
  localises D1-B for the first time** (it was `UNRESOLVED — not localised` for a week).
- **Common cause (`chatgpt_1`'s framing, better than my three-mechanism list): the
  planner/executor contract is broken** — target-only compatibility followed by an invisible
  one-turn detour with no typed feedback or target invalidation. One defect, three surfaces.
- **Blocker finding, holds on the correct subject:** IDLE 20 ≥62 turns / 2 <62; **WORKING 0 ≥62
  / 8 <62**. No working blocker reaches the terminal threshold. So **the mover invariant alone
  would convert oscillations into stalls** — 20/20 terminal blockers never move — and must be
  paired with an idle-yield rule.
- Prior attempts constrain the space: **D171a** (hard forbid) manufactured oscillation in 72
  clean tasks; **D176a** cut the ≥10-turn rate 8.50%→2.88% **by fragmenting long runs into short
  ones** (5–9 bucket 213→825) and left the worst run at **247 turns**. Fragmentation is a win
  under a rate gate and a **regression** under raw-zero.

**D89a — a working banana implementation that was never Arena-tested.** 256/256 activation,
1,344 bank BANANAs planted, sustained loop 252/256, **mean paired margin +79.441, CI
[+40.991, +117.892]**, catastrophes 26→11. Rejected on four *safety* gates, not productivity —
and not marginally: **mean opponent-score delta +82.863 against a ≤ +1 gate** (`gold_adaptive`
+208.78). Verdict history: `NOT_REPAIRABLE` → `UNRESOLVED` → `NOT_REPAIRABLE`; **the label is
with the owner**, and `chatgpt_1` holds `UNRESOLVED, strongly leaning`. Key evidence: the U4
pre-treatment snapshot **does not exist in the repo**, and the perfect-hindsight oracle's own 95%
UCB is **+8.002** against a ≤ +1 gate. **Preservation risk: the whole D89a/ring lineage exists
only on `origin/agent/local_codex_1`, whose author is inactive.**
⚠ The `+12.453 / +76.508` theft-vs-schedule split is **`UNRESOLVED`** — the provenance TSVs were
never committed. Do not cite it; it propagated into the CBF spec and BACKLOG before being caught.

**Score hierarchy (subject `98628e98`).** 10 crossings — **zero of them arithmetic**. The owner's
point 6 asked whether *sums of sub-scores* cross intention boundaries; on the real artefact none
do. Classification: 1 temporal, 2 state/position, 1 unit-scale, 3 admission, 2 arbitration,
1 duplicate, plus 3 dead-code. Structure is **two-tier: banded and sound above 6_000, entirely
unbanded below**, where three intentions share `(0, 2400]` on scales differing by 10⁴.
**Largest crossing X1 is temporal:** conversion priced ≤187.5 on turn 250 and 7_000 on turn 251
— ×37–×961 at a magic number. **No arithmetic bounds check would find it** (six of the ten are
invisible to bounds checking). Also: chop max is **1500/2400, not 3000/3900** (the `.max(1)` is
dead), and the band is **not caller-set** (one literal call site each).
**`GLOBAL_AX_STATUS = UNRESOLVED`** — "zero arithmetic" covers only the ten *known* findings.

## 5. Method assets that survived review

- `claude_1/pipeline/fuzz_panel.py` — exhaustive dispatcher (unknown verb ⇒ `GATE_UNREADY /
  unsupported_command`, exit 2), engine-authoritative TRAIN with every rule cited to `engine.rs`,
  **`run_identity` machine-check** (a config claiming `floor` with candidate ≠ parent is
  *rejected*, naming both digests), row retention, version fail-closed.
- `claude_1/banana-restoration-r2/score_hierarchy_check.py` + ledger — typed findings, generated
  counts byte-compared against the report, fails on a reachability-asserting ledger.
- `i30_*` — conservation identity `D_OPP = D_DIRECT + (D_SCHEDULE − D_TRAIN)`; **input gate that
  rejects a discarded-command trace** (the exact class the broken referee produced); `owner_frozen`
  is a pinned blob on a ref, not a self-declared string; aggregate stays `GATE_UNREADY`, no PASS.
- `oscillation-library-98628e98/` (34 situations, correct subject) and `oscillation-library/`
  (33, **parent lineage `a8eb3b2b` — labelled, must not be cited as M3a**).
- `bitetest-audit/` — committed mutation runner, manifest, raw results, RED probe transcript.

## 6. My error patterns — the most valuable part of this session

### 6.1 Right finding, wrong reason (≥3×)
"Conditional activation uses no CHOP" (false — 13.1 chop candidates/task in 255/256); endorsing
D-9 `INAPPLICABLE` (the panel *can* reach TRAIN — 2/240); "the manifest audits the wrong program"
(it read the right file and reasoned wrongly about it). **I reach for the structural explanation
because it is the one I have been finding, and stop checking once the arithmetic agrees.**

### 6.2 A figure changing meaning at a boundary (5×)
games vs episodes (74/196, 32/35); sole-blocker 63 (strict) vs 68 (P4/P2 allowed); a "32 games"
that was a **D-1 column**; **floor vs candidate run** (119 vs 123 — I published a candidate run
as the floor); M3a extracted from the **wrong bot entirely**. **Always name the config, the
subject identity, and the instrument version beside any number.**

### 6.3 Scratch-only evidence (2×)
The r3 floor evidence and the 64-mutant runner both lived in `/tmp` and were unreproducible.
Both invalidated real conclusions. **Commit the runner, manifest and raw results.**

### 6.4 `ack_for` inert on non-`ack` messages (4×)
Put in a `handoff` once and a `correction` twice more. Silent every time: the sender believes an
obligation is discharged, the receiver's tooling correctly says it is not. **Mechanical rule now:
an ack is a message whose `type` is `ack` and whose body is only acknowledgement.** A lint rule
erroring on this has been requested.

### 6.5 A publish gate that did not gate
`lint_outbox.py | grep -E "^errors" && git commit && git push` — **`grep` succeeds when it finds
the word "errors"**, so a failing lint passed the `&&` chain, and did. **Gate on exit status.**

### 6.6 Other, each once
Acked messages I had not read (twice, the second one message after promising not to). Published a
handoff pinning a commit that did not contain two of its own artifacts — committed locally,
**never pushed**; *unpushed is unsent*. Reported an inert mutant in a kill rate (a mutant that
could not fail).

### 6.7 The generalisations worth carrying
- **A mechanism that cannot fail is not a check.** D-9's clause never runs; D-6's predicate is
  retired; my I-30 tie-break was reproducible but not identifiable; one mutant was inert.
- **Bite-tests measure detector-vs-spec; the floor measures detector-vs-parent; neither measures
  detector-vs-truth.** Independent oracles are a third requirement (`chatgpt_1`, GAR-3: *"a
  fixture built from the same predicate faithfully tests the wrong predicate"*).
- **Reviewing for a failure mode does not immunise you against it.** I filed the
  shipped-vs-sacred divergence as its own disposition, then made that exact error four days later.
- **A caveat that does not constrain the verdict it qualifies is decoration.** I scoped "0 of 60
  measured, 0 of 240 inferred" correctly and then endorsed a conclusion resting on the stronger claim.
- **Re-derive, never repeat**, any figure crossing a document boundary.
- **Read a prose figure to the end of its own paragraph** before citing it (D92's "898 selections"
  is qualified nine lines later as "too late or too low-leverage").

## 7. Transport / protocol state

- **Dual-format is MANDATORY** (v2 front matter *and* legacy `- To:` bullets). `chatgpt_1`'s
  committed sweep parses only legacy bullets and was **blind to every v2 message for ten days**.
- **Run `python3 scripts/lint_outbox.py --me claude_1 --fetch` before every publish, and gate on
  its exit status.** `pytest` is NOT installed anywhere — use `python3 -m unittest`.
- Quarantine is enforced on **1 of 55 refs**; my canonical branch carries neither
  `quarantine.json` nor `legacy-baseline.json`, so my sweep ignores quarantine entirely. Five
  sweep versions are live — check which one you are running.
- **The coordinator is resolved from an unvalidated env var `TROLL_FARM_COORDINATOR`** — the
  authorization system's notion of who the authority is, is untrusted input. Reported, unfixed.
- Six `chatgpt_1` messages are quarantined (adjudicated 2026-08-07); two of mine were
  re-published validly and quarantine requested.
- Standing: I am **not** the arena controller. `rust/src/bin/yamo_orchard_live.rs` is
  byte-untouchable. No CI anywhere. Artifacts must be merged to canonical **and pushed** before
  the message citing them.

## 8. Open queue at flush

**With reviewers:** TRAIN r4 (+ artifact-commit correction), M2 method packet rev 2, I-30 rev 3,
bite-test audit revision, `oscillation-library-98628e98`, oscillation attack answer.
**Owed by me when unparked:** M1 Decision Packet implementation (spec frozen by `chatgpt_1`
against `98628e98`; behind r4 acceptance), M3b independent adjudication (needs M1 + a valid M3a),
P4 post-`C_T` re-do on c5 evidence, D-4 repair (Round 2, serialises — touches the parent),
gate revision 3 execution review.
**With the owner:** the D89a label; whether to commission a fresh 512-row corpus for U4.
