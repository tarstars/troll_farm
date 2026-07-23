# Opponent-crop dual value — controlled transfer execution, 2026-07-19

## Status

**Closed: candidate rejected at the frozen 60-game gate; exact resident restored.**  Execution followed
`opponent-crop-dual-value-controlled-transfer-protocol-2026-07-19.md`.  No threshold or source
change was made after the arena write.

## Preflight and fixed bracket

| Role | Bytes | SHA-256 |
|---|---:|---|
| Exact resident/fallback | 62,725 | `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` |
| Dual-value candidate | 64,536 | `083107f53e412be49fa06163f511a1453f7dc5447baed51ecda6d567785044cf` |

The candidate compiled standalone, its sidecar matched, and nine focused tests passed.  The first
saved-source preflight intentionally failed on a transcription error in the new documentation
(`...047f...`); comparison against the artifact sidecar exposed it before submission.  The notes
were corrected, and a second read-only recovery verified the live platform source as the exact
resident SHA ending `...047b884e55` at 62,725 bytes.

The mature baseline checkpoint for submission `41012593`, agent `6560289`, parsed all 160 finished
games with zero pending, zero runtime/validity signals, and clean identity:

| Games | Score | Rank | Catastrophic losses | Negative-margin mass |
|---:|---:|---:|---:|---:|
| 160 | 24.28 | 23/107 | 22 (13.75%) | 6,693 |

## Candidate landing

The explicit candidate path was submitted through `TestSession/submit` as submission `41012867`.
The first battle stream row identifies candidate agent `6560350`; it contained one finished and
two pending rows while the room snapshot still displayed the mature resident, which is expected
during landing.  `cgauto/api_submit.py` was used with an explicit path and was not modified.

## Checkpoints

| Read | Finished | Pending | Score | Rank | Catastrophic | Negative mass | Signals | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Landing | 1 | 2 | pending room refresh | pending | pending | pending | pending | monitor |
| Identity-clean landing | 14 | 1 | 14.89 | 105/107 | 2 (14.3%) | 957 | 0 | wait; cold start |
| Formal early gate | 63 | 1 | **16.51** | 98/107 | 8 (12.7%) | 2,362 | 0 | **reject** |

All 63 formal-checkpoint results parsed, agent `6560350` / submission `41012867` identity was
clean, and no runtime/validity signal appeared.  The deterministic evaluator returned `reject`
because score delta was -7.77 versus the fixed 24.28 bracket, far below the -1.50 early-rejection
boundary.  Tail behavior was not used to override the rating failure.

The exact resident recompiled and rehashed, then was explicitly restored as submission `41012883`,
agent `6560353`.  A read-only saved-source recovery immediately verified 62,725 bytes at SHA-256
`a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.
`cgauto/api_submit.py` remains unchanged and resident-defaulted.

This closes the exact 1:1 dual-value treatment.  Do not tune its multiplier, ETA, provenance, or
arena rule on the consumed 63 games.
