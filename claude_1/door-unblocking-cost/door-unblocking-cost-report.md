# What does the door-unblocking feature cost, and what does it do?

**Answer: it costs 5,991 bytes — 9.5 % of the 62,820-byte program — and across 25 real
ladder games (7,234 turns) it never changed a single command.**

## The feature

When the bot's home shack has exactly one walkable doorway, a worker standing in that doorway
can block a teammate carrying goods to the bank. The door-unblocking routine detects that
situation each turn and, if needed, issues forced moves to clear the doorway.

## Why it was measured

The round-36 coverage panel found `force_unique_door_clear` had the largest cold block in the
program: 341 code regions, 337 of which never executed (1.2 % covered). Coverage alone proves
nothing — cold code is not dead code — so this audit measures the feature directly, using the
same two-stage method as the accepted orchard code-cost audit and the same frozen baseline, so
the two feature costs are directly comparable.

## Artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Frozen live baseline (read-only) | 62,820 | `97bfe71e…` |
| Activation-disabled reference | 62,749 | see manifest |
| Physically stripped | 56,829 | see manifest |

Reference = baseline with the single guarded call removed, so the routine never runs.
Stripped = reference minus the implementation: `force_unique_door_clear` (4,803 B) and the
four helpers used only by it — `planned_egress` (540), `unique_shack_door` (207),
`forced_move` (156), `carries_committed_fruit` (146) — plus the `door_unblocking` switch
field, its initializer and the factory assignment. `compatible` and `move_command` are shared
with other policy and were retained.

## Results

1. **Source cost: 5,991 bytes = 9.537 % of the program** (6.0 % of the platform's
   100,000-character allowance).
2. **Safety gate — stripped vs reference: 25/25 games, 7,234/7,234 command lines identical.**
   The physical deletion introduces nothing beyond disabling the feature.
3. **Behavioral effect — reference vs the live baseline: 25/25 games, 7,234/7,234 lines
   identical.** Disabling the feature entirely changed **no command anywhere in the panel**.
   (Contrast the orchard, whose disablement changed one of the 25 games.)
4. Both variants compile under the standard optimized gate, exit cleanly on empty input, and
   pass all ten behavioral fixtures exactly.

## Mechanism — why it does nothing

Coverage on the same panel shows the routine is entered **7,234 times, once every turn**, but:

| Function | Entries | Coverage |
|---|---:|---:|
| `force_unique_door_clear` | 7,234 | 1.17 % |
| `planned_egress` | **0** | 0 % |
| `forced_move` | **0** | 0 % |
| `carries_committed_fruit` | **0** | 0 % |

Every turn the routine runs its guard prologue and returns. The parts that actually *do*
something — computing an escape route and emitting forced moves — never executed once. So the
feature is not merely rare like the orchard; on this evidence its action paths are unreached,
and the 25/25 command-identical result is exactly what that predicts.

## Honest limits

- The 25 games are the frozen liveness-counterexample packet, selected for period-2
  oscillation rather than sampled uniformly. "Never fires here" is not "never fires".
- The decisive test is the integrator's 516-task development panel: if the stripped variant is
  exactly equal there too, the feature is inert across a far broader map/opponent design and
  9.5 % of the source budget is being spent on nothing.
- Until such a panel runs, this is **not** a qualified candidate and nothing here justifies an
  arena submission. The no-churn rule and the standing evidence bar are unchanged.

## Recommendation

Ask the integrator to run one paired 516-task development panel of the stripped variant against
the exact baseline. That single run decides between two useful outcomes: either the feature is
genuinely inert and its 5,991 bytes are recoverable, or the panel finds the situation it
handles and we learn what triggers it — which would be the more interesting result, since the
routine's action paths have never been observed executing.
