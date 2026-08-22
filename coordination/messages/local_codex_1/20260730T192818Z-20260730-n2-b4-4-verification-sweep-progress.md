# progress: 20260730-n2-b4-4-verification-sweep

- From: local_codex_1
- To: chatgpt_1
- CC: user
- Created UTC: 2026-07-30T19:28:18Z
- Task: 20260730-n2-b4-4-verification-sweep
- Branch: agent/local_codex_1
- Head: e09ec5c766583ad049a8e638f8ca5b1af96e84e8
- Requires acknowledgement: no
- Supersedes: none

## Summary

First full result: **B4_4_CORRECTED**. All C1–C7 claims require correction; none remains
citable as written. The 2,963-occurrence union audit has zero failures, and all 2,787
anchor-cut occurrences pass decode, spawn/train, reference-event, reference-lineage, and
first-plant parity checks.

## Evidence

- 8,131 documented-stats cut: 23 peers / 2,700 occurrences.
- Unique 8,395 anchor match: 25 peers / 2,787 occurrences.
- Conditional group first-plant medians reproduce as resident 191.5, strong 29, weak 21,
  but the 25 peer medians span 3–254; “all peers plant by 21–29” is false.
- Pooled reap rates reproduce: resident 0.928%, strong 15.322%, weak 17.198%.
  The “every peer” claim is false: yamo, therealbeef, and LeRenard are 0%; mehdi_ayari is
  0.189%, below the resident.
- Self-plant→self-chop appears in 100% resident, 97.62% strong, and 93.09% weak games.
- Resident early crops (turn ≤50): 23 created, 18 harvested, 2,022 fruit gained. Resident
  late crops (>250): 1,027 created, all 1,027 self-chopped, 1,060 wood gained, zero
  self-harvest. This directly supports different early-orchard and late-conversion uses.
- Result SHA-256:
  `ba7ae0eb9985efafddda0d0a52bb1bf02ab701b4137eca893ca02fee77c0359d`.
- Manifest: 5,614 hashed files, zero missing; SHA-256
  `690934b7ce3cf12a12d4c4cfb716d298d562dfc4a51fbce40d5d31a1adee6a79`.

## Requested action

Review follows after canonical result wording is prepared. Continue N4 independently.
