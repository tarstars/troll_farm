---
type: HANDOFF
task_id: 20260804-door-unblocking-cost
from: claude_1
to: local_codex_1
cc: user, chatgpt_1
created_utc: 2026-08-04T11:00:00Z
requires_ack: true
---

# Door-unblocking costs 9.5 % of the source and changed zero commands; plus a block-index proposal

Two owner-directed items, both on branch `agent/claude_1-door-unblocking-cost`. No Arena or
TestSession action; no sealed range opened; the frozen baseline was read-only throughout.

## 1. Door-unblocking feature cost (owner-directed follow-up to the coverage panel)

Same two-stage method and same frozen 62,820-byte baseline as your accepted orchard
code-cost audit, so the two feature costs are directly comparable.

- Activation-disabled reference: 62,749 bytes — the single guarded call removed.
- Physically stripped: 56,829 bytes — `force_unique_door_clear` (4,803 B) plus the four
  helpers exclusive to it, `planned_egress` (540), `unique_shack_door` (207), `forced_move`
  (156), `carries_committed_fruit` (146), plus the `door_unblocking` switch field,
  initializer and factory assignment. `compatible` and `move_command` are shared and
  retained.
- **Cost: 5,991 bytes = 9.537 % of the program** (6.0 % of the 100k allowance).

Gates: both variants compile under the standard optimized gate and exit cleanly on empty
input; both pass the ten fixtures exactly; **stripped vs reference 25/25 games, 7,234/7,234
lines identical** (safety gate).

**The result that matters: reference vs the live baseline is also 25/25, 7,234/7,234
identical.** Disabling the feature entirely changed no command anywhere in the packet —
unlike the orchard, whose disablement changed one game. Coverage explains why: the routine is
entered 7,234 times (every turn) but its action paths — `planned_egress`, `forced_move`,
`carries_committed_fruit` — have **zero** entries. It runs its guard prologue and returns,
always.

Not qualified, and I am not proposing a submission. **One request:** a single paired 516-task
development panel of the stripped variant against the exact baseline. Either it is exactly
equal — and 9.5 % of the source budget is provably doing nothing — or the panel finds the
situation the routine handles, which is the more interesting outcome since its action paths
have never been observed executing at all.

## 2. Code-block index — owner idea, working prototype for your disposition

The owner proposed indexing code blocks (what they are, where they live, which bot versions
contain them) to make navigation, optimisation and bot re-assembly tractable. There are
**318 bot sources** in the tree, so I think the need is real. Prototype in
`claude_1/block-index/`:

- `blocks.json` — curated layer: purpose, class, locating anchors, and measured
  cost/coverage/live value with citations. 12 blocks seeded from work already qualified
  (orchard, door-unblocking, training-deadline fallback, the opening-policy record, the
  zero-penalty risk calculation, and the config switches consumed by rounds 2–13).
- `build_block_index.py` — derived layer: resolves presence across every artifact by anchor
  matching and emits `block-index.json` plus a generated `BLOCK-INDEX.md`.

Design point I would ask you to keep if you adopt it: **presence is derived, never
hand-written.** My round-28 "terminal" inventory rotted within a day precisely because it was
hand-written; a regenerable index cannot. The `partial` state is deliberately reported and is
already useful — it flagged two harness runners that reference `SecureOrchardBot` without
implementing it, and it caught a bad anchor of mine (`PlantKind::Banana` matches the species
enum in every bot, not the banana implementation; corrected to `banana_factory_commands`,
which resolves 6 artifacts instead of a spurious 291).

Proposed disposition: if you want this beyond my namespace, it should become an
integrator-owned task with a real task record — the natural home is alongside the submission
registry, and the natural next step is seeding entries from the ledger for blocks measured
before my time. I have deliberately not written outside `claude_1/`.
