# Primary fresh-trace review — not an unexplained bank leak

Worker exec35259 terminal03:39:16 exit0. Reported15pass/1fail, no panel or runtime
certification. Primary independently reproduced the no-iron failure on the exact
current generated test source with ONLY per-turn logging added to run-local
primary-trace.rs. The source/control copies and primary-trace.log are preserved;
no bot source was changed by primary. Compile required copying the relative
control include into the same run directory; first missing-include failure kept.

Current emitted actions establish why the bank does not accumulate LEMON:
- t65 DROP banks the last harvested wild LEMON; t66 PICK LEMON, t67 PLANT at(2,3).
- t68 emits CHOP0 once, then repeated WAIT; t100 HARVEST, t101 DROP => one LEMON.
- Opponent chops that planted tree from t94. t105 PICK, t106 PLANT at samecell.
- t144 PICK, t145 PLANT again. Each recovered lemon funds the next destroyed tree.
- PLUM stays3 through t180. Both units PICK PLUM at181 then PLANT at182, after
  the acquisition target has failed; this is not a t74 unexplained inventory leak.

Therefore the requested next 'bank leak' investigation is superseded. The current
planting loop invests one seed into a slow/dry repeatedly contested site and
returns only one fruit before destruction. The bank accounting alone cannot fix
that investment. Inspect why a growing planted target still permits CHOP68 too,
but do not attribute every emitted PICK to a higher wrapper: it is a plan step.
Earlier trace-no-iron.log/trace-layers.log were made before final fixes and must
not be treated as a trace of the final source. Current trace is authoritative.

One concrete controller change remains meaningful: choose planting sites by real
time to grow and bank enough needed fruit, including travel and contest exposure,
instead of immediate planting at the current feasible cell. This is not a general
ban on dry plots or near-bank planting. Corrected iron fixture24vs40 is negative
synthetic profit evidence; all remaining strength claims need actual evaluation.
No production changes or new platform calls.
