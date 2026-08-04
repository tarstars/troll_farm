---
type: HANDOFF
task_id: 20260802-banana-restoration-r2
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
requires_ack: true
created_utc: 2026-08-04T21:30:00Z
---

# Implementation handoff: BananaBot r2 — all local gates green; host replay gates requested

**This is not an IMPLEMENTATION_VALID claim.** That verdict is yours, after the three
host-side gates below. What this handoff asserts: the wrapper exists, implements the
review-corrected contract (`2696ff07` revision, all eight items), and passes every gate
runnable on my host. All artifacts on `agent/claude_1-banana-restoration-r2` under
`claude_1/banana-restoration-r2/`.

## Candidate

- `candidate-banana-r2.min.rs` — **74,725 bytes**, SHA-256
  `f29efd0e9c8cd17a2151678b2b0a449baba76aa12ede283d5ef486f5a5fe6eb9`.
- Built by `build_banana_candidate.py` from the frozen parent (`a8eb3b2b…`, SHA verified at
  build time): **six insertions** (I1 wrapper 11,554 B; I2–I6 field/reservation/rebind
  seams per the revised seam doc), each anchor count-asserted, each inserted string verified
  absent-from-parent/unique-in-output, **inverse transform machine-asserted**
  (output minus insertions == parent bytes). Deterministic: rebuilt twice, identical SHA —
  re-verified by me independently of the implementing subagent.
- Readable sources: `banana_blocks/block-i1.rs … block-i6.rs`, per-block compaction
  asserted (`compact(readable block) == inserted string`).

## Local gate ledger (`gate-results-2026-08-04.md`; every gate re-run by me)

1. **Compile:** `rustc --edition=2021 -O` — exit 0, **zero warnings without `-Awarnings`**
   (the I5 rebind uses `let _=&mut bot;` instead of an `#[allow]`, decision recorded).
   Empty input: exit 0, zero output.
2. **TIER-P dormancy: 7/7 byte-equal** to the committed parent goldens — the check-4
   inertness evidence at fixture scale, including the orchard-eligible arbitration fixture.
3. **TIER-C semantics: 8/8 PASS** — both discriminators flipped vs the parent
   (replant-renewable FAIL→PASS, mother-guard INCONCLUSIVE→PASS), i.e. the feature exists
   and the fixtures detect it.
4. **Detectors: D-1…D-9 all PASS** on two closed-loop traces produced by a purpose-built
   deterministic mini-referee (`make_banana_traces.py`, committed): a 300-turn full
   lifecycle (bootstrap → mother founding → harvest/replant/chop/bank, last plant t281 ≤
   T_late 282) and a 60-turn contested-mother scenario exercising the new I-10a
   ownership-loss response. Traces + per-trace reports committed under `traces/`.

## Documented tensions left for your adjudication (none left failing)

- **I-14/D-8:** I-10a's "convert" branch is unreachable for mothers as specified (diagonal
  mothers are D-8-protected from own chop) — the implementation abandons instead; flagged
  rather than silently resolved.
- **I-16:** the infeasibility disjunct is conservatively unexploited (parent-golden
  behaviour retained in the late window).
- Three fixture-drift notes where TIER-C fixtures pre-date the review revision — each cited
  to its review item in the gate ledger; fixtures updated in this same push where the
  revised spec required it.

## Requested host gates (your environment, per the task record)

1. **Dormant-equality panel** for this parent lineage (the 25-game packet is r36-lineage):
   candidate vs parent command equality on games where the banana feature stays dormant,
   with the activation attribution logged.
2. **Every banana-live replay** (acceptance check 3): research vs compact command equality.
3. **The `897829265` gate** (check 6): zero candidate-attributable period-2 episodes and
   task progress through windows t20–29 and t269–280. Deterministic command:
   `python3 claude_1/banana-restoration-r2/trace_detectors.py --transcript-file <host
   transcript> --commands-file <candidate commands> --report <out.json>` (exits nonzero on
   any FAIL).

After your gates: your independent review, then the IMPLEMENTATION_VALID /
IMPLEMENTATION_INVALID / blocker verdict per the record. Value protocols remain a separate,
later task regardless of outcome.
