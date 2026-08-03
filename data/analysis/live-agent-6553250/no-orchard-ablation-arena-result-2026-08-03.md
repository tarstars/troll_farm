# No-orchard Arena ablation — terminal result

Date: 2026-08-03

Task: `20260803-owner-no-orchard-ablation-arena`

Arena controller: `local_codex_1`

## Result

The owner-directed no-orchard candidate was rejected, and the exact E7a bot was restored.

The candidate completed its full 160-game platform queue at score **23.27**, rank **34/137**.
Immediately before the experiment, the exact E7a resident read score **25.3**, rank **12/137**.
The observed change was therefore **−2.03 score and 22 rank places**, materially larger than the
project's usual ±0.5–1 live-ladder noise allowance. This experiment does not support removing the
secure-orchard layer.

## What changed

Candidate source:
`claude_1/no-orchard-arena/candidate-e7a-r28-no-orchard.rs`

- size: 56,200 bytes;
- SHA-256: `d1f32c358d0f7b6a49b988c1b4ad6958a2d8ed84a9e3492632087732aae7e02a`;
- parent behavior: simplified E7a round 28;
- ablation: the one branch that activates `SecureOrchardBot` was disabled, leaving the Yamo
  controller as a passthrough for the whole game.

This was intentionally behavior-changing. It was not presented as a gate-qualified promotion.
Independent controller checks reproduced the builder output byte-for-byte, compiled the optimized
program, passed empty-input handling and all ten semantic fixtures, and preserved the sacred
resident-policy source at SHA prefix `fff6669b`. In the frozen replay packet, 24 of 25 games stayed
exact; the intended game `897833045` first diverged at turn 79, directly after the orchard would
have activated.

## Platform execution

The candidate was submitted exactly once. `TestSession/submit` returned HTTP 200, submission
`41085842`; agent `6592097` then converged cleanly from 13 to 45, 74, 96, 125, and finally 160
finished games. There were no automatic retries, identity mismatches, fetch failures, or runtime
signals.

| Measurement | Exact E7a before trial | No-orchard terminal |
|---|---:|---:|
| Agent / submission | `6590141` / `41081503` | `6592097` / `41085842` |
| Finished games | 160 | 160 |
| Score | 25.26 platform checkpoint; 25.3 Arena room | 23.27 |
| Rank / field | 12/137 | 34/137 |
| W / T / L | 82 / 3 / 75 | 91 / 4 / 65 |
| Mean game margin | −29.30 | +10.56875 |
| Catastrophic losses | 35 (21.875%) | 16 (10.0%) |
| Negative-margin mass | 10,045 | 5,441 |
| Runtime signals | 0 | 0 |

The tail statistics look better without the orchard, while the platform score and rank are much
worse. These queues contain different opponent samples, so the tail difference is not a paired
causal estimate and must not be used to claim that the orchard itself creates every catastrophe.
The bounded conclusion is simpler: this live no-orchard ablation loses overall ladder value and
does not qualify for retention.

## Restore and current state

After recording the terminal source hash and verdict, the controller submitted the exact 62,820-
byte E7a source once. `TestSession/submit` returned HTTP 200 with submission `41086057` and agent
`6592131`. Platform source recovery matched SHA-256
`97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595` exactly.

The first health checkpoint contained 15 finished games plus one pending: score 18.57, rank
84/137, 10W/0T/5L, two catastrophes, negative-margin mass 468, zero runtime signals, and clean
identity. This is a cold-start placement read, not a strength comparison. Source and health gates
are satisfied, the restore is active and converging, and the serialized Arena mutation cycle is
closed.

## Decision

**Reject blanket orchard removal. Preserve the secure orchard and treat future work as a bounded
activation or coordination refinement, not global deletion.** The active platform source is again
exact E7a. Any new Arena mutation requires a distinct serialized task.

Primary machine-readable evidence:

- `no-orchard-ablation-pretrial-checkpoint-20260803T145723Z.json`;
- `no-orchard-ablation-terminal-checkpoint-20260803T154310Z.json`;
- `no-orchard-ablation-e7a-restore-initial-checkpoint-20260803T154916Z.json`.
