# D32a deterministic field option A/B — recovery protocol (2026-07-20)

## Pre-result harness incident

The first D32 external call, baseline versus delineate, returned to the local process.  While
constructing the result row, the newly added trace collector raised `ModuleNotFoundError` because
`field_panel.py` was launched as a script without adding the repository root to `sys.path`.  The
process terminated before persisting a game ID, score, inventory, stdout stream, turn-one map, or
any result field.  No candidate/B call had started and no baseline outcome was observed.

The incomplete panel is preserved as
`data/panels/d32-pretrace-harness-failure-20260720.json`.  It contains the exact frozen manifest and
zero rows.  The unobserved call is excluded from inference but disclosed in the external-call
count.

## Sole correction and clean restart

The sole correction adds the already computed repository root to Python's import path before the
trace collector imports `render_turn_one`.  It does not change either Rust source, request body,
seed, opponent, call order, result field, integrity gate, or value threshold.  Focused tests and a
script-mode trace-import check must pass before restart.

D32a then performs a clean six-row panel under the original D32 protocol:

- exact source hashes remain
  `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` and
  `5138066175177a9b198c2c3f51deeef30d13d6207bee316227fae607662a6f82`;
- the bank remains SHA-256
  `58260acf1327c3b57c2de36fd3a7efc57480dda47bda1fda67be086f5e7eab2d`;
- order remains A then B for delineate, Escdemon, and laconic; and
- every integrity and value gate remains exactly as frozen in D32.

The complete operational disclosure is seven TestSession calls: one unobserved, unrecorded A call
from the failed harness plus six new D32a calls.  Only the six-row clean panel is analyzed.  A
second harness failure or any candidate/B observation before another defect stops the experiment;
there is no further restart authority.
