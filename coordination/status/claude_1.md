# claude_1 Status

- Updated UTC: 2026-08-11T23:59:00Z
- State: all deliverables with reviewers; nothing unblocked on my side
- Role: contributor + **execution reviewer** on every artifact (coordinator, integrator, arena controller AND detector-semantics owner = `local_claude_1`; `chatgpt_1` = adversarial/committed-blob reviewer)
- Branch: agent/claude_1-banana-restoration-r2; canonical agent/claude_1
- **Read `claude_1/SESSION-FINDINGS-2026-08-07-to-11.md` before acting.** It carries the programme state, the measured findings, and the error patterns.

## Blocking state

- **The panel is `GATE_UNREADY`** and gates the programme. TRAIN referee repair **r4 delivered**, awaiting `chatgpt_1` acceptance + `local_claude_1` execution review (B1). r1/r2 `NOT ACCEPTED`; r3 dispatch-layer accepted only.
- **Parked behind acceptance:** P4 post-`C_T`, D-4 repair (Round 2, serialises — touches the parent), gate revision 3, D-9 calibration, all candidate verdicts. Do not restart without checking the ruling.
- Instrument `fuzz-panel/5` · corpus `c5-two-player-phase-merged-2026-08-11`. **Floor (parent vs itself) = 118/240. Candidate run (banana `eac2eb36` vs parent) = 121/240.** Different quantities; `run_identity` is now machine-checked.

## Delivered, with reviewers

TRAIN r4 (+ artifact-commit correction) · M2 score-hierarchy method packet rev 2 · I-30 rev 3 · bite-test audit revision · `oscillation-library-98628e98` (34 situations, correct subject) · oscillation attack answer.

## Owed when unparked

M1 Decision Packet implementation (spec frozen by `chatgpt_1` against `98628e98`; behind r4 acceptance) · M3b adjudication (needs M1 + valid M3a) · P4 re-do on c5 evidence · D-4 repair · gate revision 3 execution review. **With the owner:** the D89a label; whether to fund a fresh 512-row corpus for U4.

## Do not cite

The `+12.453/+76.508` D89a split (`UNRESOLVED`, TSVs never committed) · `oscillation-library/` as M3a (it is parent lineage `a8eb3b2b`) · D-9 as `INAPPLICABLE` or "196 false positives" (now `INSTRUMENT_UNSUPPORTED / GATE_UNREADY`) · D-6 as falsified (it is a `CONTRACT AUTHORITY: CONFLICT`) · any floor figure for the ~10 of 17 rules lacking a corpus witness.

## Transport

**Dual-format MANDATORY** (v2 front matter + legacy `- To:` bullets) — a peer was blind to v2 for ten days. **`ack_for` is inert unless `type: ack`** (I broke this 4x). **Gate publishes on `lint_outbox.py` EXIT STATUS**, not on grepping its output. `pytest` absent — use `python3 -m unittest`. Push before citing: *unpushed is unsent*, and a stale remote-tracking ref makes `git merge` a silent no-op. Never `git add -A` — agents share this tree.

## Standing constraints

Arena controller: **NO**. `rust/src/bin/yamo_orchard_live.rs` (`fff6669b`) byte-untouchable; `engine.rs` (`7c240abf`) is the authority, not any bot's self-restraint. `trace_detectors.py` is `local_claude_1`'s. No CI anywhere.
