# Curriculum Level 4 transfer-clone result — 2026-07-19

## Verdict

Pass.  The frozen seed-83 clone from the accepted Level-3 checkpoint clears every prospective
functional gate on exact seeds 2,015,000--2,016,999.  This authorizes the already specified
four-million-decision PPO discovery run; it does not accept Level 4 or authorize live transfer.

| Metric | Zero-shot Level 3 | Level-4 clone | Frozen clone gate |
|---|---:|---:|---:|
| Overall success | 90.25% | 97.80% | 70% |
| Nontrivial success | 91.01% | 98.41% | 65% |
| Worst recipe success | 67.06% | 93.33% | 55% |
| Worst height success | 89.20% | 97.00% | 60% |
| Tracked crop created | 94.35% | 97.90% | 75% |
| Renewable harvest | 92.45% | 98.90% | 65% |
| Paired teacher median delay | 0 | 0 | <=45 turns |

The weakest recipe remains cheap planter at 93.33%; harvest producer rises from 70.36% zero-shot
to 96.84%.  The other six recipe families lie between 98.36% and 99.20%.  Thus the prescribed
online clone repaired the two composition deficits without eroding the fixed standard-chopper
behavior (98.42% before and after cloning on this bank).

The run consumed exactly 800,000 online teacher decisions from stream 6,600,000.  It completed in
539.88 wall seconds and 7,147.06 CPU-seconds, equal to 66.19% of the 20-logical-CPU host.  Teacher
generation completed 8,635/8,636 episodes; the one miss is a teacher timeout rather than label
corruption.  Every saved loss is finite.

## Reproducibility anchors

- checkpoint: `6ba4daa6a871103776d205046e11f9fc5a8381eba1807d93d515dec148c88259`;
- exact evaluation: `e8dbb939ec8806ee44972d11d025177ff8b5aef12c93642c8db50e807d3f3a8f`;
- complete training summary: `ea5fbc6c824cdd2850b8934bee85fa64191738c61980a7ab23f0b4162e1892da`;
- initial Level-3 checkpoint: `a0a0f4bd590175d45be4ec63a8394a47cbe475187d942906d4e01038a167b0df`;
- frozen protocol: `aef6cdd612d57423509f057b5aceaee669af43771b658cb369091b7befaa7418`.

## Next execution

Run PPO unchanged from stream 6,700,000 with model seed 83, the legal-only 0.10 teacher auxiliary,
Stage A at one million decisions, and final at four million.  Stop only if the prospective Stage-A
gate fails; otherwise decide discovery from the frozen final functional and strict action audits.
