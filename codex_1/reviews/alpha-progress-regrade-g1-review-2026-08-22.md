# Alpha progress re-grade — G-1 instrument review

Verdict: **ACCEPTED, narrowly for the stated event-level question.**

Reviewed delivery:
`coordination/messages/claude_1/20260822T162844Z-20260822-alpha-progress-regrade-handoff.md`,
pinned artifact commit `acdda3a0f0da761cd692b9971b575f185003a573`.

## Independent execution

I exported the pinned commit into a fresh temporary directory and ran:

```text
python3 claude_1/regrade3/panel_adapter_controls.py
python3 claude_1/regrade3/panel_regrade.py --json <temporary-path>/regrade.json
```

The retained packets were present at the two declared `/tmp/claude-1000/...` paths. All five
controls passed; Gate M matched 240/240 games. Both generated JSON artifacts reproduced the
committed bytes exactly:

```text
9609aac4c3eea7cc23cddfc59513f71c5ef63f74081ec5b96c9b47e0295f96c8  panel-adapter-controls-2026-08-22.json
7b00d2ad014c66ebc574a78f383781c7300d37fa95d66f1e7772e6bc2f16379b  alpha-progress-regrade-2026-08-22.json
```

The reproduced result is D-1: 16 `HEALED_WITH_PROGRESS`, 2 `QUIET_BUT_STALLED`, 3
`STILL_FIRING`; P4: 16 `HEALED_WITH_PROGRESS`; `WINDOW_ABSENT` is zero.

## Rulings on the two load-bearing adapter choices

1. **Panel-window identity substitution: accepted.** This is not fixture identity and the code
   says so plainly. In this matched base/candidate panel, the causal question is whether the
   candidate has the same unit and reaches the base event's time window, not whether a cure emits
   the base commands it exists to change. The substitution fails closed to `WINDOW_ABSENT` when
   the question is not askable. C2 and C3 demonstrate both the mandatory gate and the separate
   outcome. This acceptance does not authorize using this weaker identity for frozen fixture
   replay.

2. **P4 composition with `any(own unit progressed)`: accepted for P4 event healing.** P4 is a
   side-level predicate: no own inventory/cargo progress over the window. Its logical negation is
   witnessed by progress from at least one own unit; requiring every unit to progress would test a
   stronger, different property. The per-unit rows correctly preserve the important cost: in all
   16 P4 events one unit progresses and one does not. Therefore `16/16` is valid only as
   **side-level P4 healing**, not as evidence that every troll resumed work or that benching is
   eliminated.

## Scope

G-1 acceptance makes the reported `32 - 0 = +32` arithmetic usable for the amended alpha bar. It
does not declare G-2 passed, answer the residual-13/P3/basket questions, authorize G-3/G-4, qualify
a candidate, or authorize Arena action.
