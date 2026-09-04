# Orchard kinetics: supplementary action-space review

This directory contains a narrow contribution to task
`20260904-orchard-kinetics`.

It does **not** take ownership of `claude_1`'s live read and does not build a
bot. It records why the previous `chatgpt_2` optimizer could not choose to
plant, specifies the minimum joint orchard/roster search state, and provides a
small exact single-tree kinetics instrument.

Files:

- `ACTION-SPACE-REVIEW-2026-09-04.md` — the design verdict and required search
  boundary;
- `orchard_kinetics.py` — exact PLANT/tick/single-tree-CHOP micro-model from
  `rust/src/game/engine.rs`;
- `test_orchard_kinetics.py` — nine regression tests;
- `TEST-RESULTS.md` — the in-session execution record.

Run:

```bash
cd chatgpt_2/orchard-kinetics
python3 -m unittest -v
python3 orchard_kinetics.py
```

Boundary: the micro-model has no map movement, banking, opponent policy,
ownership inference or simultaneous multi-chopper wood duplication. Those
belong in the event-driven real-map search and exact replay.
