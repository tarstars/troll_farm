# Candidate 1 hold — G-0 design review (2026-08-25)

Verdict: **REVISION_REQUIRED** before code.

The narrow intervention is appropriate: only the resolver changes, an improving or lateral
detour remains available, and `W = 2` bounds consecutive holds before production behaviour gets
one regressive attempt. The rule targets the observed forward/back geometry without importing the
retired swap rule. The three-arm plan is also the right parity shape.

Four transition details must be frozen first. They are small, but leaving them implicit makes two
implementations with different play both conform to the card.

There is also one blocking safety defect found by the builder after the first ruling was drafted:
the current cell of a projected mover is omitted from initial `reserved`. If that mover later
holds, an earlier-processed mover may already have claimed the holder's cell. Merely inserting the
cell when `H` is selected is too late. **The rule must not be built until the construction ruling
defines a two-phase reservation plan or an equivalently proved scheme under which every prospective
holder's current cell is protected before any landing is granted.** The rule-off arm must retain
the base's legal swap semantics, so globally adding all occupied cells to `reserved` is not an
acceptable shortcut.

1. **A missing detour is `W`, not `H`.** `H` is justified only when a detour exists and its
   distance is strictly worse than `d_cur`. If no legal detour exists, preserve today's forced
   `WAIT`, report branch `W`, and reset `blocked_turns[id]` to zero. There is no backward step to
   cure in that branch; counting it as a hold changes internal state and falsely attributes a
   pre-existing wait to the new rule.
2. **Make the counter a consecutive-H counter.** Increment it only on `H`. Set it to zero on every
   other resolved branch: `P`, `L`, `R`, `W`, and `N`. The card currently resets on a free landing
   or a non-MOVE command but says nothing about a lateral/improving detour; that permits an old H
   count to survive an intervening `L` and shorten a later hold sequence. The exact cycle under a
   persistent regressive block must be `H(b=1), H(b=2), R(b=0)`, repeating.
3. **Define telemetry state timing.** `b` is the post-decision consecutive-H count: 1 or 2 on `H`,
   zero on `P/L/R/W/N`. Exactly one `r` and one `b` are emitted for every live own unit, in the
   existing ascending-id v3 unit record. A selected self-targeting MOVE, which the resolver turns
   into WAIT before the mover loop, is `W`, not `N`; `N` means the selected gameplay command was
   not MOVE. Rule-off may emit `P/L/R/W/N` but never `H`, and its `b` is always zero.
4. **State the parity comparison literally.** For every turn, strip the single `MSG` token from
   rule-off output and require the remaining ordered gameplay-token vector to equal the champion's
   vector exactly. Also require identical next referee state. Candidate output must equal the
   instrument arm after stripping `MSG`. This is stronger and less ambiguous than
   “byte-identical in play,” while allowing the declared telemetry difference.

Answers to the builder's remaining implementation questions:

- Keep the existing static `MoisanBot` resolver entry points untouched. Add a stateful entry point
  used from `YamoBot::commands`, passing `&mut self.blocked_turns`, the compile-time rule flag, and
  a branch-output map. This makes ownership explicit and leaves an exact base path available.
- Before resolution, clear counters for every live own id absent from `command_by_id`; those are
  the selected non-MOVE commands. Clear stale ids no longer in the live own roster as hygiene.
- A selected MOVE whose projected landing equals its current cell is resolved `W0`, as specified
  above; it is not an H and carries no old counter.
- Compute `d_cur` with exactly the detour key's BFS-or-Manhattan fallback.

The distance predicate itself is accepted with one precision: use the resolver's existing
`toward_goal` map and the same Manhattan fallback for both `unit.cell` and the chosen detour.
`detour_distance <= current_distance` is `L`; strict `>` is eligible for `H`. The primary landing
may span movement speed while the detour is one cell, but the comparison asks only whether the
fallback loses distance, so no separate horizon normalization is needed.

Required red/green controls before G-0 can close:

- persistent regressive block: `H1,H2,R0,H1`;
- improving and equal-distance detours after one prior H: both `L0`, proving stale state clears;
- no-neighbour branch after one prior H: `W0` and gameplay-equivalent to base;
- free primary and non-MOVE after one prior H: `P0` and `N0`;
- v3 rejects v4, v4 rejects v3, and a malformed/missing/duplicate `r` or `b` is rejected;
- rule-off cannot produce `H` or nonzero `b`.

Once the card or an ack-required construction ruling adopts these four definitions, the design is
ready to build without another conceptual review. No code, panel, candidate, or Arena action was
performed in G-0.
