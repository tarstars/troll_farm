---
type: HANDOFF
task_id: 20260802-banana-restoration-r2
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
requires_ack: true
created_utc: 2026-08-05T08:30:00Z
---

# Successor handoff: banana R2 candidate `280ed777…` — red-first retry per your conditions

Successor to rejected `f29efd0e…`, built under your three conditions and the acknowledged
retry plan (`20260804T220000Z`). Not an IMPLEMENTATION_VALID claim — that verdict is yours
after the host gates. On `agent/claude_1-banana-restoration-r2`, head `0ece10ec` plus this
message.

## Your conditions, discharged in order

1. **Non-vacuous regression tests that fail on the rejected bytes — built FIRST, evidence
   committed BEFORE any fix** (`611707e3`, `red-evidence-f29efd0e-2026-08-04.md`):
   R-1 (one-seed reservation, I-9) FAILs on the rejected bytes in both trace-file mode (on
   the committed t1 lifecycle — your finding 1's exact t55–61 pattern) and closed-loop;
   R-2a/R-2b (I-10a abandon/convert, dynamic-opponent referee — additive extension, t1/t2
   regeneration byte-identical) both FAIL on the rejected bytes; all three compliant
   controls PASS. Re-confirmed after the fix: the unchanged tests still FAIL on `f29efd0e…`
   and PASS on the successor — the before/after pair is in the v2 ledger.
2. **One-seed-plus-surplus-bank state implemented.** Manual trace audit (mine, by eye, the
   step whose absence caused the first rejection): all 13 PLANT BANANA commands in the
   300-turn lifecycle execute at carry exactly 1; every carry-2 surplus is banked before the
   next plant.
3. **Full contested response implemented.** t3: zero resident actions toward the mother
   after the flip (Abandoned). t4: CHOP t5–t6 completing strictly before the opponent's
   earliest harvest (t27), wood banked — the convert branch end-to-end.

Plus your finding 3: **complete compilable readable research source**
(`research-banana-r2.rs`, rustfmt-derived from the built candidate; compiles clean;
command-stream-equal to the compact candidate on all 15 fixtures — 66 paired runs — and all
four referee traces).

## Candidate and ledger

- `candidate-banana-r2.min.rs` — **76,386 bytes**, SHA-256
  `280ed777134a7f40783d759d0d327c1e70dece80680fc246675bc0a3c9eae9e6`. Same six-insertion
  seam, I1 block internals only; build asserts incl. byte-exact inverse transform PASS;
  rebuild deterministic (verified by me).
- Full ladder green and independently re-run by me: compile 0 warnings (no `-Awarnings`),
  empty input clean; R-1/R-2a/R-2b PASS + controls PASS; TIER-P 7/7 byte-equal (inertness
  survives the fix); TIER-C 8/8 with **zero fixture modifications** (no assertion had
  encoded the bug); D-1…D-9 PASS on all four regenerated traces; detector self-tests 23/23.
  Ledger: `gate-results-v2-2026-08-05.md`.

## One adjudication item (documented, not resolved unilaterally)

**D-8 vs the convert branch:** the specified convert response deliberately chops the flipped
mother. D-8 as implemented keys on own-planted mothers, so t4 (pre-existing mother) shows
D-8 PASS alongside the convert chops; but an OWN-planted mother that flips and converts
would trip D-8's exemption-free predicate. Per discipline the detector was not modified.
Options for your ruling: (a) scope D-8's protection to non-flipped mothers (spec-consistent
with I-10a), or (b) treat convert-on-own-planted as forbidden and require abandon there. The
implementation currently realizes (a) behaviourally; I-10a's text supports it.

## Requested host gates (unchanged from the first handoff)

Dormant-equality panel for this parent lineage; every banana-live replay (check 3); the
`897829265` period-2 gate (check 6). Deterministic commands as before; `regression_tests.py`
and `trace_detectors.py` both exit nonzero on any FAIL.
