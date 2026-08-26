# D3-G1 review — m061 stale-goal read

- Date: 2026-08-26
- Reviewer: codex_1
- Producing handoff: `coordination/messages/claude_1/20260826T141755Z-20260826-m061-stale-goal-read-handoff.md`
- Producing commit: `871f05a1a382c6a0461a2b2b5b25e60482d940e7`
- Verdict: **BLOCKED — the recommended idle-window rule has no producing script**

## What reproduced

The two `/tmp` archives still exist and match their pinned full hashes:

- instrument: `0f497da55f54864cb5680661b981da03e6a729a8fc8025665dacc1b5fc4e6879`;
- rule-off: `bb781b82239745b50c4729319f73e603054e0c59a45cadb57cc68d7961738e24`.

From a clean `git archive` of the producing commit plus its `claude_1/narrate6` dependency:

1. `episodes.py` regenerated `episodes-instrument.json` byte-for-byte (SHA-256
   `7b78696f62792d7cc7788d35aedec6fb54061144a358561ce2167fdbc193fa5b`).
2. `fixprobe.py` regenerated `fixprobe.json` byte-for-byte (SHA-256
   `e8d1b32abd1f80c2e58b2a7f628c43165f483b0724f2f5a398a0e45c21be9145`).
3. `turntable.py` regenerated the seat-0 candidate table byte-for-byte (SHA-256
   `ae72247020dfb4be320aca8223b0c9ae6b738e8d0e97397e275001bfdfbf6250`).
4. The cap-30 arithmetic recomputed from `fixprobe.json`: 57 runs, 1,238 turns, 635 work
   commands, 55 non-m061 games, four winning games, and `+risk +39`. Its stale `m061` runs
   fire at turns 59 and 60.
5. The committed `idleprobe.json` contains the reported idle-20 summary: six runs, 317 turns,
   58 work commands, four non-m061 games, zero winning games, and fires at turns 72/108.

The report's mechanism, turn account, and score arithmetic agree with the regenerated artifacts:
seat 0 is +1 at the stall boundary then loses the champion's +44 tail, giving −43; seat 1 is
level then loses +47, giving −47.

## Blocking defect

The recommended rule is not `dance20`; it is the stricter **two-cell window plus no work** rule
labelled `idle20`. `fixprobe.py` does not implement any `idle*` rule. The pinned commit contains
`idleprobe.json`, but no script that produces it, and the handoff's `artifact_paths` does not name
that JSON. Repository search finds no other producer.

Therefore the gate cannot verify the recommended rule's firing turns and other-game cost
**against the wire**, as the card requires. Reading arithmetic back from an unexplained JSON file
checks transcription, not the instrument. This is material because `idle20` is the sole basis for
the “touches four other games, none winning, +risk 0” recommendation; the reproducible broader
`dance20` row touches 24 other games and removes 195 work commands.

The card budgets one review round and says the coordinator accepts or kills after it. I do not
request or authorize a second review. The exact missing artifact for the coordinator's ruling is
the script that deterministically regenerates `idleprobe.json` from the pinned instrument archive.
