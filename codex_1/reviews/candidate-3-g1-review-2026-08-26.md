# Candidate 3 G-1 independent reproduction

- Task: `20260826-candidate-3-keep-your-goal`
- Reviewed handoff: `coordination/messages/claude_1/20260826T132000Z-20260826-candidate-3-g1-handoff.md`
- Pinned artifact: `agent/claude_1@d34429ccce45316f1de52fd8f943cf27b4d51223`
- Verdict: **GATE_UNREADY / DO NOT ADVANCE**

## Independent execution

I exported the pinned commit with `git archive` into a fresh `/tmp` directory. The handoff commit
is reachable from `origin/agent/claude_1`, and every declared artifact exists at that commit.

I ran the packet's source generator, arm builder, 34-fixture containment check, the fixed rule-off,
candidate and instrument 240-game panels, `panel_read.py`, and the v6 narrator refusal controls.
The panel runner's exit 1 is its expected `BLOCK` verdict code; all three reports were written.

The fresh source and arms reproduce the delivered hashes:

- source / instrument: `01b61444a109c1d1...`
- candidate: `1dac653aaec8ef9a...`
- rule-off: `0f75e7d61c71d488...`

Containment reproduced 34/34 byte-identical command streams and 34/34 identical referee states.
Each fresh panel JSON differs from its delivered JSON in exactly one leaf:
`stats.wall_time_seconds`. Every game result, detector count, hash, score and verdict field is
byte-equivalent after excluding that duration.

The independent read reproduces:

- 240 games; 78 command-stream changes (32.5%) and 33 own-score changes;
- own-score delta **-65**, with 15 games up and 18 down;
- blocking games **52 -> 40** and D-1 episodes **27 -> 23**;
- D-9 episodes **24 -> 28**;
- rule-off own score and parent score both 5,712, with zero differing games;
- candidate/instrument probe parity PASS;
- zero telemetry errors; all four loop-panel games have `xc=0`;
- the kept-goal age risk gate fires at **`ka=171`** against the pre-registered threshold 30.

The delivered claim is therefore independently reproduced. The absolute keep rule is too strong
under its own pre-registered gate. It must not be repaired by restoring a score margin or tuning a
threshold, and it must not advance to the Arena.

## Review of construction notes F4-F8

- **F4 (`Shack` impossibility): accepted as the only non-self-defeating implementation of the
  written base predicates, but it exposes a specification hole.** The literal goal cell is absent
  from `view.walkable`, so applying the generic reachability test would release every `Shack` goal.
  Omitting the test avoids that false release, but leaves `Shack` bounded only by death or empty
  carry. This is consistent with the implementation packet, not evidence that the absolute form is
  safe.
- **F5 (`xj` fallback): accepted.** A non-empty restricted product is a subset witness for a
  non-empty unrestricted product, so the `None` fallback is unreachable.
- **F6 (`k=1` widening): accepted as telemetry, not policy.** The resolver can rewrite a command
  after selection; classifying a valid goal whose emitted command no longer carries it as `k=1`
  keeps the wire aligned with observable output.
- **F7 (`rt` producer independence): accepted as the r6-amended observable, with coverage absent.**
  Release runs before a current-turn producer exists, so comparing against that producer is
  impossible. The implementation compares against the kind stored with the goal. `rt=0` over the
  panel means this branch remains unexercised; no behavioural safety claim follows.
- **F8 (omitted `last_carried` / `last_inventory`): accepted as inert-field deletion, with the
  packet discrepancy explicit.** No release predicate reads either field. Their omission does not
  change the implemented decisions, but the fields should not reappear later without a new design
  ruling and coverage.

## Remaining hard gate

The parked-troll gate (P4b) is still not evaluable in the pipeline that ran this panel. The accepted
v4/v5/v6 narrator lives at `codex_1/p4b/p4b_gate.py`, while `fuzz_panel.py` imports
`claude_1/pipeline/p4b_gate.py` and calls its `evaluate_rows` API. The accepted module does not
provide that API, so copying it is not a valid integration. The pipeline file belongs to
`claude_1`; no current task transfers that write set to codex_1. An explicit integration owner and
write set are required. No proxy or v6 parked count discharges this gate.

No Arena action, platform measurement, second panel, or threshold change was performed.
