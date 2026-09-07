# Forward-model foundation for joint-action planning

The next substantial hypothesis is that joint short-horizon action evaluation can resolve
worker interference and compare growth/harvest/chop/banking sequences more effectively than
the experimental controller's fixed priority stack. This document authorizes a bounded local
foundation, not a new ladder submission or a presumption that search is stronger.

V439 already selects compatible immediate action pairs in its Yamo core; the proposed new
capability is evaluation of action sequences, not rediscovering pairwise assignment. Preserve
V439 as the measured stronger reference. Do not pick a weaker ancestor just because its smaller
source is easier to combine with this module, or override a stateful controller without reconciling
the transaction/goal state it committed for its originally generated command.

Extract the existing read-only neighboring Java-parity substrate into an independently
exportable local module, preserving its parse-time eligibility, simultaneous movement and
action-phase ordering. Keep source provenance/hashes. Do not substitute the simpler historical
`engine.step`, which does not enforce equivalent parsing eligibility. Generated maps and hidden
SHA1PRNG state must not ship in a bot that cannot observe that state.

Initial model domain: both players supply explicit reachable MOVE endpoints (including staying
in place). Non-direct MOVE commands require hidden random tie-breaking and are rejected before
state mutation, not silently modeled with an invented seed. Named fruit commands are supported;
numeric fruit aliases are out of domain because the extracted helper's string handling is not
general. This restriction is appropriate for a planner that generates its own command grammar,
not a claim of a universal platform emulator. Keep physical player ordering and raw unit IDs;
a future relative-seat bot adapter must explicitly handle simultaneous training-ID allocation.

First verification:

1. Executable fixtures for MOVE chains/swaps/collisions and same-turn train egress; train/PICK/
   DROP ordering and shared stock; growth and bank-only scoring; simultaneous HARVEST/CHOP/PLANT.
2. Differential checks against the frozen full neighboring parity referee on generated states,
   both players, all supported action types and sequences. Compare full state and legality,
   not just final scores. Test rejection before mutation for unsupported movement/fruit syntax.
3. Replay-derived state checks where commands are in the supported domain. Account explicitly
   for physical player order, plant creation order and hidden early-termination state. A model
   extracted from the local referee needs independent official evidence; local A/A alone is
   not platform validation.
4. Deterministic standalone export size and throughput measurements. Whole candidate must stay
   below 100,000 UTF-16 units; shipping simulation without decision changes is not a bot improvement.

Only after correctness checks should a bounded planner be integrated and compared with exact
frozen policies. Any competitive screen gets a new prospective protocol. The V439 restoration
rollout continues untouched, with useful offline work instead of an additional platform collector.
