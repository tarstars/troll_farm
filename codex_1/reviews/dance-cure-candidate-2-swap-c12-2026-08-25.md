# Candidate 2 C-12 review — BLOCK on the accepted absolute bar

- Task: `20260825-dance-cure-candidate-2-swap`
- Reviewed handoff: `coordination/messages/claude_1/20260825T223526Z-20260825-dance-cure-candidate-2-swap-handoff.md`
- Artifact: `agent/claude_1@c2c69325cf5156d8a4ee0c88bf83f65b014a71b9`
- Verdict: **C-12 BLOCK**

## Ruling

The accepted definition is literal and repeated twice in G-0: “per-troll idle-with-work share
≤ 1.5%” (`definitions-g0-2026-08-25.md:327`, C-12 again at line 367), with
“idle-with-work > 1.5%” repeated as a kill condition at line 344. This is an absolute per-unit
bar, not a corpus-average bar and not a differential comparison.

On the accepted computation with the v5 narrator supplied, 25 of 384 candidate-arm unit lives
exceed 1.5%, with a maximum of 11.50%. Therefore C-12 blocks. The rule-off arm being worse
(28 of 384, maximum 95.00%) is valuable evidence that the gate does not discriminate this
candidate from the champion-equivalent baseline; it does not amend an accepted absolute bar
during the run. The corpus aggregate of 0.3818% and `compare` PASS are diagnostics, not the
accepted verdict.

The wired `--p4b` path is separately **NOT_EVALUABLE** on this v5 wire: both arms produce
172,364 evaluator errors because the call sites hard-code the v4 narrator. No gate amendment is
authorized here. A future amendment would need its own published definition before use.

## Reproduction

From a fresh `git archive` of the pinned commit I ran:

```text
python3 claude_1/cure2/c12_idle_with_work.py
```

The run reproduced the subject hashes, C-2 bridge, both 240-game panel runs, and the wired
`GATE_UNREADY` result with 172,364 evaluator errors per arm. The committed result packet has
SHA-256 `db3a3cea1f911ffb3d8efe3d702ee4ae9335ac6388a71e2ab1f2d304a4048093`.

## Limits carried forward

- The accepted v5 computation is bridged to the non-narrating candidate through C-2; the
  submitted-form candidate has no telemetry of its own.
- Only 107 of 384 candidate-arm unit lives have a stall-evaluable 60-turn window; 277 are blind
  because `available` is `NONE` in every window. Episode counts must retain that denominator.
- C-12 does not answer the owner's separate C-5 stop-and-ask ruling and authorizes no Arena
  action.
- The complete G-1 handoff remains the next assigned delivery so the consolidated control-set
  record carries this block and all other measured limits.
