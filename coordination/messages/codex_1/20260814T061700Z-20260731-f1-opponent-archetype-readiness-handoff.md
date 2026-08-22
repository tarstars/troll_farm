---
schema_version: 2
type: handoff
task_id: 20260731-f1-opponent-archetype-readiness
from: codex_1
to: ["local_claude_1", "claude_1"]
cc: ["user"]
message_id: coordination/messages/codex_1/20260814T061700Z-20260731-f1-opponent-archetype-readiness-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: 9bc243d123272673e7b3a6705d193c8c73dc2481
artifact_paths: ["codex_1/f1_opponent_archetype_readiness.py", "codex_1/tests/test_f1_opponent_archetype_readiness.py", "codex_1/results/f1-opponent-archetype-readiness-2026-08-14.json", "codex_1/results/f1-opponent-archetype-readiness-2026-08-14.md"]
created_utc: 2026-08-14T06:17:00Z
---

# Handoff: early proxy-family signal is present by turn 40

In plain terms for the owner: the legal public game history contains a strong, repeatable signal
about which of the eight local proxy opponents is playing. The result is
**`EARLY_PROXY_SIGNAL`**. This does **not** show that reacting to the label improves score, does
not identify arbitrary ladder opponents, and authorizes no bot change or Arena action.

The exact frozen 2,048-game source was restored from the verified cold archive (250 MiB) and
matched SHA-256 `9b7281fb…6f4`. All 128 map roots were held out as whole blocks across five folds.
At the primary turn-40 checkpoint, the standardized multinomial linear model achieved:

- macro-F1 `0.922` (map-root bootstrap 95% interval `[0.906, 0.937]`);
- top-2 accuracy `0.986`;
- minimum family recall `0.855`, with all eight recalls above the required `0.25` and `0.50`;
- seat macro-F1 `0.919 / 0.925`;
- static-map control macro-F1 `0.028` and within-seed permutation p99 `0.153`;
- byte-identical features and predictions after deleting commands, opponent labels/names, seed,
  terminal scores/length, and arm metadata;
- portable scorer/schema size 15,107 bytes, identical predictions to the fitted pipelines, and
  worst-fold single-example scorer p95 `0.012 ms`.

The centroid corroboration is `0.775`; current-state-only linear is `0.864`, so cumulative legal
transitions add real signal rather than merely reading a roster marker. Turn 10 already reaches
`0.800`, and turn 80 reaches `0.944`; no horizon was selected after seeing results.

Runtime boundary stated explicitly: the offline Python audit path takes roughly `2.6 ms` p95 to
rebuild 40 transitions from a stored trajectory. That is not the maintained-feature scorer gate;
a live extractor updates transition totals as states arrive. This is not an end-to-end Rust
deployment benchmark.

Validation: six new tests pass after being observed failing before implementation; exact source
hash/task coverage, 1,000 permutations per horizon, 2,000 map bootstraps, every frozen gate, and
the sacred resident hash `fff6669b…` all pass.

Per the frozen proposal, the only allowed follow-up is a separately reviewed action-target audit
that names a non-closed intervention and eventually compares family-conditioned, identical
unconditioned, and unchanged arms. A classifier result alone authorizes nothing downstream.
