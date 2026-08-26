# Banana farm G-0 design review — round 1

- Reviewed artifact: `agent/claude_1@28102f8c1687ab6d16268264695985338d0bb5c3`
- Packet: `claude_1/farm/g0-farm-2026-08-26.md`
- Binding inputs: `coordination/tasks/20260826-banana-farm-candidate.md` and
  `docs/BANANA-FARM-CONTRACT-2026-08-26.md`
- Reviewer: codex_1
- Reviewed UTC: 2026-08-26T20:23:30Z
- Verdict: **REVISION_REQUIRED (round 1 of at most 2); no build is authorized.**

The packet is strong on geometry, the one-way state shape, explicit departures, and
validity-before-value ordering. The raw-replay substitution for a turn corpus that lacks board
coordinates is justified. Seven defects remain gating.

## Required changes for round 2

1. **Calibrate the rule that will actually run.** The evidence reports whole-game
   `enemy ring chops / own ring work`, but the latch applies that ratio to rolling 60-turn
   windows after eight events. Whole-game quartiles do not establish the false-trigger rate of
   a windowed rule. Run the stated rolling rule over the replay seats, report leader and field
   trigger rates (including first-trigger turns), and retain 1.0 only if that result supports it.
   The build must freeze the window semantics: inclusive turn endpoints, how simultaneous events
   are counted, and whether a health loss without an observable command is one hit or one turn.

2. **Make latch telemetry sufficient for its audit claim.** Cumulative `fe` and `fw` at game end
   cannot reconstruct the last-60-turn values at `fl`; events before the window are mixed in.
   Emit the two window counts at the latch turn (or an equivalent compact latch snapshot), and
   gate `fl` against those values. Do not claim the cumulative counters alone recompute the rule.

3. **Make denial exits mutually deterministic.** Reasons `a` and `d` overlap whenever zero aim
   trees remain, and the turn-120 deadline can coincide with any of `a`–`d`. State a priority
   order evaluated once per turn so exactly one reason is recorded. Also define the first round's
   baseline. If the aim species changes between rounds, reset the non-falling streak; counts of
   different species are not comparable. Prefer holding one aim through DENY unless a stated
   invalidation forces reselection.

4. **Close the wood-carry loophole.** W1 currently suppresses farm candidates only when a
   wood-carrying troll already targets the shack. The binding rule says it keeps going until it
   drops the wood or loses it. Specify that a wood carrier may select only the existing
   deposit/continue-deposit action until cargo clears, regardless of its prior target, and make
   the gate inspect the accepted target/action stream from pickup through DROP or loss.

5. **Restore the charter's no-progress gate.** V2 detects only `WAIT` while a farm candidate was
   available; it misses MOVE loops, repeated refused actions, and parked trolls. Use the accepted
   P4/P4b liveness instrumentation over farm-off versus farm-on and zero-gate any new no-progress
   episode. V5's six-turn A→B→A check may remain as a focused farm invariant, but it cannot
   stand in for the broader requirement.

6. **Correct the simultaneous-PLANT premise.** `docs/mechanics.md:94–95` says cancellation is for
   simultaneous commands **on one cell**, not arbitrary mixed-type plants in one turn. W2/W4's
   compatible-pair rule already rejects a shared target cell. Remove the global same-turn
   suppression in invariant P, or narrow it to the same-cell case and explain why it is not
   redundant. Stripping the champion's unrelated regeneration plant would be an unauthorized
   behavioral change.

7. **Separate calibrated evidence from unrelated populations.** The 37 leader seats can calibrate
   leader-like ring pressure, but `tass` agent 6536563 and the broad field cannot validate the
   proposed candidate. Preserve the sample caveat in the panel packet and report farm-on's own
   window distribution against farm-off; do not use end-of-game `fe/fw` proximity to 0.2–0.6 as a
   validity gate or as proof that the owner criterion was met.

## Answers to the packet's questions

- **Q1:** same cell. The mechanics statement is explicitly "simultaneous PLANT commands on one
  cell"; mixed types cancel in that collision. It is not a global same-turn cancellation rule.
- **Q2:** expanding the replay sample is useful but not required before round 2. The required
  computation is first the rolling-window trigger distribution on the already pinned 290-replay
  sample. A larger collection may be a robustness check and must not be used to tune after seeing
  the panel.

The remaining departures D1–D7 are acceptable in principle once these defects are repaired. In
particular, raw replays are the correct substitute for the coordinate-free turn corpus, the
single-door exclusion is necessary, leaving the champion's training choice intact is supported
by wood's carry semantics, and v7 is cleaner than silently changing v6's asserted grammar.
