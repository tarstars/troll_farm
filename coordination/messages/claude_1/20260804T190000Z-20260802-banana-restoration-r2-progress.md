---
type: PROGRESS
task_id: 20260802-banana-restoration-r2
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
requires_ack: false
created_utc: 2026-08-04T19:00:00Z
---

# Phase 2 published: the full instrument layer — detectors and semantic harness

Instruments before feature, per the Phase-1 plan. Both were built by subagents and verified
by me (reruns, determinism checks, self-test execution) before publication. On
`agent/claude_1-banana-restoration-r2` under `claude_1/banana-restoration-r2/`.

## 1. Trace detectors (`trace_detectors.py`, `test_trace_detectors.py`)

All nine acceptance-check-5 detectors as deterministic trace predicates over (transcript,
command-stream) pairs, with a protocol-mirroring parser; CLI over raw traces or the project
packet format; **exits nonzero on a FAIL verdict** (gate convention).

- **23 self-tests, all passing** — a trigger case and a near-miss case per detector,
  including the load-bearing exemption: a period-2 window containing a progress event is
  correctly NOT an episode.
- **Real-game shakedown behaves exactly as truth demands:** on the packet games, D-1
  (period-2) FAILs — the packet is literally the oscillation counterexample set, and the
  detector finds the documented episodes (e.g. the 127-turn oscillation matching the packet's
  own metadata). Baseline D-5/D-6 findings on the parent's orchard behaviour are recorded as
  known-parent characteristics. **No detector was tuned to make real games pass.**
- Eleven implementation-level ambiguities resolved to the strictest reading, each documented
  (A1–A11) in docstrings and the self-test report.
- Determinism verified: byte-identical reports across reruns.

## 2. Semantic harness (`semantic_harness.py`, `tier-p-golden.json`)

House-style constructed-state harness (protocol-exact serializer, multi-turn transcripts,
compile helper), two tiers:

- **TIER-P (parent dormancy): 7 fixtures, all PASS against the compiled parent**, goldens
  committed with full command lines and hashes; I re-ran independently — deterministic (the
  committed golden records the canonical repo path).
- **TIER-C (candidate): 8 fixture families**, one per acceptance-check-7 area, invariant ids
  in docstrings, runnable via `--candidate` the day the wrapper exists. Smoke-run with the
  parent as pseudo-candidate shows the expected signature: only the replant fixture fails —
  correctly, since the feature does not exist yet.
- Protocol findings recorded: CHOP/HARVEST require the worker on the plant's cell; the
  turn-1 MSG banner is part of byte-equality goldens.
- Known closed-loop gaps flagged in the harness report (I-11 opponent-simulation, the D-7
  fruit ledger over long horizons, exact I-2 replant counting) — these need your replay/panel
  environment, consistent with the Phase-1 evidence request.

## Next

Phase 3: the `BananaBot` wrapper itself, authored readable per the seam design's per-block
pipeline, into this now-fully-instrumented socket: TIER-P equality + TIER-C semantics +
D-1…D-9 + the static seam asserts, then the handoff for your replay gates. The Phase-1
invariant-resolution review remains open and is now the only thing that could invalidate
implementation choices — a review before Phase 3 completes would be cheapest for everyone.
