# Provenance of the recovered three-troll artifact

- Correct agent identity: `chatgpt_2`.
- Original mistaken namespace: `chatgpt_1/three-troll-optimized-start/`.
- Cause: two simultaneously running sessions were both labeled `chatgpt_1`.
- Owner correction: the session that produced this artifact is `chatgpt_2`; the original
  opening-solver-review / DP-oracle / Rust-anytime-planner session remains `chatgpt_1`.
- Rescue ref: `rescue/chatgpt1-three-troll-optimized-start-2026-09-03`.
- Rescue commit: `8da821a28db9658062bfb772e2e63b6f47f4868d`.
- Rescue subtree: `chatgpt_1/three-troll-optimized-start/`.
- Corrected publication path: `chatgpt_2/three-troll-optimized-start/`.

The rescue tree contained 47 files: 19 root blobs plus 28 files under `results/`. The corrected
publication preserves all 47 historical files. Generated Rust sources, SHA-256 sidecars, raw logs
and JSON are reused byte for byte. `README.md` and `RESULTS.md` add the identity correction and the
later selector ruling; this provenance page is new.

The scientific verdict is unchanged: `DEAD_AS_BOT`. Candidate smoke was 19/24 and control smoke was
15/24 against a 24/24 requirement. The later instrument audit also retired paired win-rate
difference in favor of paired score-margin difference with a 95% interval.
