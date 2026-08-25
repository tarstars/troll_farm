---
schema_version: 2
type: handoff
task_id: 20260825-dance-cure-candidate-1-hold
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260825T093800Z-20260825-dance-cure-candidate-1-hold-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: abeda52a6f42d6f34e57e5268c9a7188732b98f3
artifact_paths: ["claude_1/cure1/g1-report-2026-08-25.md", "claude_1/cure1/cure1-hold-v4.rs", "claude_1/cure1/arm-manifest.json", "claude_1/cure1/arm-instrument.rs", "claude_1/cure1/arm-candidate.rs", "claude_1/cure1/arm-ruleoff.rs", "claude_1/cure1/make_cure1_source.py", "claude_1/cure1/build_arms.py", "claude_1/cure1/alpha_parity.py", "claude_1/cure1/panel_parity.py", "claude_1/cure1/panel_costs.py", "claude_1/cure1/arm_equivalence.py", "claude_1/cure1/d4_attribution.py", "claude_1/cure1/diagnostic_w1.py", "claude_1/cure1/make_control_probe.py", "claude_1/cure1/run_controls.py", "claude_1/cure1/poison_arm.py", "claude_1/cure1/results/alpha-parity-ruleoff.json", "claude_1/cure1/results/panel-parity-ruleoff.json", "claude_1/cure1/results/panel-parity-instrument.json", "claude_1/cure1/results/arm-equivalence.json", "claude_1/cure1/results/panel-named-costs.json", "claude_1/cure1/results/d4-attribution.json", "claude_1/cure1/results/resolver-controls.json", "claude_1/cure1/results/poison-arm.json", "claude_1/narrate4/narrate4.py", "claude_1/narrate4/controls.py", "claude_1/narrate4/results/v4-decode-controls.json"]
created_utc: 2026-08-25T09:38:00Z
---

- To: codex_1
- CC: local_claude_1, user, chatgpt_1
- Task: 20260825-dance-cure-candidate-1-hold
- Requires acknowledgement: yes — this is G-1 for your execution review; re-run it from a fresh archive

# G-1 HANDOFF — built, gated, **and I am handing you a MIXED result, not a green one**

Read `claude_1/cure1/g1-report-2026-08-25.md` whole; everything below is in it with the numbers.

## The arms — one source, one line

`make_cure1_source.py` generates `cure1-hold-v4.rs` from the base `547fa706` by anchored
replacements that each must match exactly once, and it refuses to run unless the v3 instrument's
own base and this base carry a byte-identical `select` block (that is what licenses transplanting
the `MSG` hunk verbatim). `build_arms.py` then makes three arms by rewriting **one line** and
refuses unless exactly one line differs; each is compiled before its hash is recorded.

| arm | flags | sha256 |
| --- | --- | --- |
| `arm-instrument.rs` | HOLD=true NARRATE=true | `5e1e5b27322587eaa57a2f4c8974def5cf015b88c1f04372cd65a4c7df2a9b38` |
| `arm-candidate.rs` | HOLD=true NARRATE=false | `7651b69847aa5a70…` (full in `arm-manifest.json`) |
| `arm-ruleoff.rs` | HOLD=false NARRATE=true | `b1b565b85fddf16d…` |

The resolver is the construction ruling's two-phase hold-seeded fixed point, not the charter's
superseded single pass. Your definition 5 is honoured literally: the static `MoisanBot` entry
points are untouched and off the path; the new stateful entry point takes `&mut blocked_turns`, the
rule flag and the branch map, and is called from `YamoBot::commands`.

## What is green

- **α parity, fixtures:** 34/34 byte-identical without `MSG` **and** 34/34 identical next referee
  state — both halves of your definition 4, second half included.
- **α parity, the 240-game panel:** **240/240** byte-identical without `MSG`, 0 telemetry errors
  over 48,000 turns, and on every rule-off turn `pz=1`, `sp=0`, no `H`, no nonzero `b`.
- **Candidate arm == instrument arm in play:** 240/240 games. Without this the instrument's branch
  counts would describe a bot nobody proposes to submit.
- **Your six controls:** #1 gives exactly `H(b=1), H(b=2), R(b=0), H(b=1)`; #2a improving detour is
  `L0`; #3 no-detour is `W0` and #3b self-target is `W0`; #4 free primary `P0`; #5 non-MOVE `N0`;
  #6 rule-off cannot emit `H` or nonzero `b` — resolver-level in `results/resolver-controls.json`
  and corroborated across the whole panel.
- **My contention control:** with one unseeded pass, u9 (resolved first, higher id) is granted u5's
  square while u5 holds on it — the hazard, reproduced. The fixed point does not. Printed side by
  side.
- **v4 decode controls: 38/38 fired**, including mutual refusal against the **live** v3 decoder in
  both directions, and malformed / missing / duplicated `r` and `b`.
- **Behaviour:** D-1 episodes **27 → 1**; regressive-detour turns **1,290 → 618**; blocking games
  **43 → 41**; P4 violations 16 → 15 with no game worse; 6 healed blocks.

## What is NOT green — four things, and I am not rounding any of them off

1. **Your control #2b, the equal-distance detour, is NOT CONSTRUCTIBLE.** On a 4-connected grid
   adjacent BFS distances differ by exactly one, and a free orthogonal neighbour of a reachable cell
   is reachable, so the Manhattan fallback cannot apply to one side alone. `toward_goal[detour] ==
   d_cur` cannot happen and the predicate's `<=` is exactly `<`. Reported as not constructible, not
   as a pass. You may want the definition to say so.
2. **P3 is not clean.** `m004 seat 0`, orchard-eligible: at turn 7 the candidate emits
   `WAIT;MOVE 2 7 2` where the base emits `MOVE 0 5 2;MOVE 2 7 2`. Dormancy inertness fails on that
   game, while D-1 on it goes 2 → 0. The charter's clause is "P3 clean". It is not.
3. **D-4 grows 10 → 102**, and it is the rule's own turns: every episode is exactly 3 turns long and
   96 of 102 contain exactly two holds by the episode's unit. **`W = 1` is worse (132)**, so the
   window size is not the lever. D-4 reads standing still inside a wood-committed interval as
   abandoning the return.
4. **The charter's poison arm is NOT caught by the P4 gate.** `W = 255` parks a troll for **194
   consecutive turns** (2,689 hold turns over the panel) and P4 stays at the base's 16, while the
   poison arm blocks on **40** games against the base's 43 — it looks *better* than the candidate on
   every headline number. `fuzz_panel.progress_turns` is game-level (own inventory OR any own unit's
   cargo), so a parked troll beside a working teammate cannot trip it. Consequence I want you to
   rule on explicitly: **no green from the P4 clause licenses this candidate either**, including the
   16 → 15 above.

**Forecast, not a result:** the candidate's idle-with-work share on the panel (`H`+`W`) is 2.28 %
against the base's 0.73 % — and that 0.73 % reproduces the 0.72 % baseline the G-2 kill rule cites.
G-2's kill line is 1.5 %.

**The charter's "35" belongs to `candidate-door1-p1p2` (`5e1f4df4`), not to this base.** The champion
blocks 43 on this corpus; I re-ran the matched floor and reproduced local_claude_1's 2026-08-20
figure exactly. Both numbers are in `results/panel-named-costs.json` under `charter_bar_note`.

## What I am asking you for

A G-1 execution verdict re-run from a fresh archive, and specifically a ruling on (2), (3) and (4).
My own recommendation, stated so you can disagree with it on the record: **this should not go to
G-2 as built** — the safety net that was supposed to catch its failure mode does not work, and the
panel already forecasts the G-2 kill rule firing.

## Scope

No Arena action, submission, fetch, TestSession or sealed-data access. Nothing outside
`claude_1/cure1/**` and `claude_1/narrate4/**` was written. `rust/src/bin/yamo_orchard_live.rs`
untouched at `fff6669b…`. The W=1 arm and both poison arms are named for what they are and are
excluded from `arm-manifest.json`; none of them is a candidate.

Deferrals: none.
