# Code block index (generated — do not edit)

Generated from `blocks.json` over 318 bot sources. Rebuild with `build_block_index.py`; the curated layer is `blocks.json`.

## Blocks

| Block | Class | Present in | Partial | Measured cost | Live value |
|---|---|---:|---:|---|---|
| **Secure apple orchard** (`secure-apple-orchard`) | feature | 117 | 2 | 15,013 B | -2.03 score / -22 ranks when ablated (agent 6592097, 160 games) |
| **Shack door unblocking** (`door-unblocking`) | feature | 117 | 0 | 5,991 B | unmeasured; disabling changed 0 of 7,234 commands on the frozen packet |
| **Training deadline fallback** (`training-deadline-fallback`) | feature | 119 | 0 | — | — |
| **Opening policy configuration record** (`opening-policy-record`) | configuration | 103 | 0 | 580 B | — |
| **Persistent regeneration commitments** (`persistent-regeneration`) | feature | 118 | 0 | — | — |
| **Endgame idle harvest** (`idle-harvest`) | feature | 118 | 0 | — | — |
| **Contested-tree risk penalty** (`opponent-eta-penalty`) | feature | 91 | 0 | 1,341 B | — |
| **Preferred-only opening mode** (`preferred-only-opening`) | configuration | 93 | 0 | 1,254 B | — |
| **Movement-first tie-break mode** (`movement-first-tie-mode`) | configuration | 94 | 0 | 234 B | — |
| **Idle-starter activation gate** (`idle-starter-gate`) | configuration | 81 | 0 | 403 B | — |
| **Focus species selection** (`focus-species-selection`) | shared-infrastructure | 142 | 0 | — | — |
| **Self-reproducing banana orchard** (`banana-orchard`) | feature | 6 | 0 | — | — |

## What each block does

### Secure apple orchard — `secure-apple-orchard`

Plants an apple 'mother' tree in a spot the opponent cannot cheaply reach, then camps one worker there harvesting its fruit for the rest of the game, reserving that worker and protecting the tree from the main policy.

- class: feature
- anchors: `SecureOrchardBot`, `OrchardPhase`
- source cost bytes: 15013
- source cost percent: 23.898
- activation rate: 1 of 25 packet games; 11 of 160 ladder games showed camp signature
- live value: -2.03 score / -22 ranks when ablated (agent 6592097, 160 games)
- evidence: `claude_1/orchard-code-cost/orchard-code-cost-report.md`
- evidence: `claude_1/no-orchard-arena/no-orchard-ablation-postmortem-2026-08-03.md`

### Shack door unblocking — `door-unblocking`

When the home shack has exactly one walkable doorway, detects a worker blocking it and issues forced moves to clear the way for a carrier heading to the bank.

- class: feature
- anchors: `force_unique_door_clear`
- source cost bytes: 5991
- source cost percent: 9.537
- coverage: entered 7,234 times (every turn); 1.17% of regions; action paths planned_egress/forced_move/carries_committed_fruit have ZERO entries
- live value: unmeasured; disabling changed 0 of 7,234 commands on the frozen packet
- evidence: `claude_1/door-unblocking-cost/door-unblocking-cost-report.md`

### Training deadline fallback — `training-deadline-fallback`

If the second worker has not been trained by a deadline turn, abandons the preferred build and trains the strongest currently affordable one instead.

- class: feature
- anchors: `enforce_training_deadline`, `strongest_affordable`
- coverage: guard runs 35,529 times; strongest_affordable / training_affordable / fallback_second_troll all 0% covered
- evidence: `claude_1/e7a-incremental-simplification/r36-coverage-analysis-2026-08-04.md`

### Opening policy configuration record — `opening-policy-record`

Seven-field tuning record (train horizon, carry/chop preferences and caps, extra-ETA allowance, hard train turn) selecting the second worker's stats.

- class: configuration
- anchors: `YamoOpeningPolicy`
- source cost bytes: 580
- note: single-valued in the resident lineage; inlined and deleted by simplification rounds 15-22 with no behavior change
- evidence: `claude_1/e7a-incremental-simplification/r22-contract-2026-08-03.md`

### Persistent regeneration commitments — `persistent-regeneration`

Remembers which worker committed to replanting which fruit species and keeps that commitment across turns instead of re-deciding each turn.

- class: feature
- anchors: `regeneration_commitments`

### Endgame idle harvest — `idle-harvest`

In the endgame, when every candidate action is a WAIT, harvests ripe fruit instead of idling.

- class: feature
- anchors: `idle_harvest_candidates`

### Contested-tree risk penalty — `opponent-eta-penalty`

Discounts chop targets an opponent can reach first, by estimated damage they could do before we arrive.

- class: feature
- anchors: `opponent_eta_penalty`
- source cost bytes: 1341
- note: penalty fixed to zero in the resident lineage, making the whole calculation unreachable; deleted by simplification round 11
- evidence: `local_codex_1/e7a-iterative-logical-deletion/candidate-r11-remove-zero-opponent-risk-manifest.json`

### Preferred-only opening mode — `preferred-only-opening`

Alternative opening mode that refuses any second-worker build not meeting the preferred carry/chop minimums.

- class: configuration
- anchors: `require_preferred`
- source cost bytes: 1254
- note: fixed false in the resident lineage; deleted by simplification round 12

### Movement-first tie-break mode — `movement-first-tie-mode`

Alternative opening tie-break preferring movement speed over chop power.

- class: configuration
- anchors: `prefer_movement_ties`
- source cost bytes: 234
- note: fixed false in the resident lineage; deleted by simplification round 13

### Idle-starter activation gate — `idle-starter-gate`

Optional requirement that the starting worker be idle before the orchard may activate.

- class: configuration
- anchors: `require_idle_starter`
- source cost bytes: 403
- note: permanently disabled in the resident lineage; deleted by simplification round 2

### Focus species selection — `focus-species-selection`

Chooses which fruit species to cut based on aggregate walking distance from the shack to each species' trees.

- class: shared-infrastructure
- anchors: `focus_type`
- note: load-bearing; the semantic-fixture harness probes this function

### Self-reproducing banana orchard — `banana-orchard`

Banana-based production loop: early planted bananas reproduce, late ripe fruit converts to wood, harvested fruit is banked.

- class: feature
- anchors: `banana_factory_commands`
- note: architectural study measured +162.3 own score on a development panel; live publications 2026-08-02 were implementation-invalid. Anchor corrected 2026-08-04: the first attempt used PlantKind::Banana, which is the species enum present in every bot, so 291 artifacts resolved 'partial' — a worked example of why anchors must discriminate the implementation, not the domain vocabulary.
- evidence: `docs/CONSTRAINTS.md`

