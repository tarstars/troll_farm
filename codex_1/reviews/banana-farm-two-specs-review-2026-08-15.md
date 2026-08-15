# Banana-farm Spec A/B logical review — 2026-08-15

Task: `20260815-banana-farm-two-specs`  
Reviewer: `codex_1`  
Subject commit: `e916ec86`; base source SHA-256 `98628e98…`

## Verdict

**REVISION_REQUIRED. Do not freeze or implement either spec yet.** The one-predicate A/B entry
comparison is a good experimental shape, the latches prevent state reversal, and the readable
source citations sampled here match. The shared abort sensor does not measure the owner's abort
condition, crop ownership is underspecified, and the claimed nightly resolution is overstated.

## Blocking findings

### F1 — the abort sensor does not measure collection from our farm

The owner rule is: abort when the enemy collects more **from our farm** than we do. The proposed
sensor compares total banked-banana deltas since FARM entry.

Those are different quantities in both directions:

- Our specified farm loop HARVESTs and then PLANTs the renewable banana. Replanted harvest is
  collection from our farm but need not increase our bank at all. Thus `d_us` can stay zero while
  our farm is working as designed.
- The opponent can harvest and bank its own bananas. That increases `d_them` without collecting
  from our farm. "No training reason" is not "no scoring reason," and the specs themselves later
  admit this proxy is inexact.
- A cumulative bank lead also mixes pre-existing independent production with the farm exposure;
  W/K persistence cannot restore missing provenance.

Consequently GA+/GA− would prove only that the implementation follows this proxy, not that it
implements the owner's rule. Calling it a "sound proxy" contradicts the recorded
`NOT_REPAIRABLE` provenance finding. Either the owner must explicitly approve a different,
observable abort rule (and accept what it means), or the spec must define a provenance-bearing
sensor and prove it is observable. Do not silently substitute total-score deltas; that is a third
design with the same attribution problem.

### F2 — tracked-crop ownership lacks a transactional state contract

The spec says a table is "reconciled from observed plants" and that failed commands, collisions,
death, opponent removal, or replacement cannot invent progress. Observed plants carry no owner
field. A plant at a tracked cell after disappearance/replacement is not proof that it is our
generation. The spec needs an explicit pending-command/next-state transition table: what exact
pre-state, emitted command, carry delta, plant delta, and generation identity establishes each
owned generation; how ambiguity fails closed; and how reserve promotion avoids inheriting an
opponent replacement. Without it, GF and the abort interpretation can be satisfied by falsely
owned crops—the same provenance class that invalidated earlier Banana R2 rounds.

### F3 — farm payload semantics are incomplete

After HARVEST, the text says carry the banana to one conversion cell and PLANT, then return to
seed acquisition. It does not specify what happens when harvest power produces more than one
banana or the troll already carries multiple bananas. One PLANT consumes one unit; remaining
banana cargo conflicts with "return to seed acquisition," precedence banking, reserve policy,
and the claim that renewable seed is never dropped. Define the full post-harvest loop and its
termination for carry counts 1..capacity.

### F4 — the measurement claim is statistically too strong

At sigma 1.501 and 4 observations per arm, the stated standard error is about 1.06, but a
2-point difference is only 1.89 standard errors. It is not "cleanly resolved" at a conventional
two-sided 95% threshold (even the normal approximation needs about 2.08 points; a small-sample
t interval needs more). The sigma estimate also bundles sequential ladder drift. State the
uncertainty and decision rule explicitly; do not promise that one night resolves ~2 points.

## Owner-decision recommendations

- **A-1:** concur with second-troll materialization if "unconditional" means D89a-like earliest
  entry. A first-denial marker would introduce a second causal difference and make the A/B less
  clean. The document should say the pipeline phases overlap after entry; it is not strictly
  deny-then-farm.
- **B-1:** concur with no new turns-remaining floor. Measure late non-establishment rather than
  add an ungrounded constant.
- **A-2/B-2:** first valid comparison should be A versus B only after the shared sensor and
  ownership contracts pass. A winner-versus-resident night answers a different question and
  cannot identify the entry predicate effect.

## Non-blocking corrections and accepted structure

- The denial latch has no re-enable path as specified. In A, denial and farming intentionally
  overlap until enemy-third or abort; in B, enemy-third disables denial as FARM starts.
- `second_troll_ready` correctly prevents new farm actions before our second troll exists.
  Existing resident banana conversion remains an explicit exception, so avoid an unqualified
  whole-bot "no banana action" claim.
- Routing the starter into a farm-specific candidate generator is achievable without inserting
  a new cross-band score. Forced door clearing and the post-selection resolver remain outside
  that local score set and must be tested as such.
- The behavioral gates need population floors and exact denominators, not only existential
  statements such as "at least one cycle." Freeze those only after F1–F3 define what counts.

## Boundary

Review only. No implementation, panel, candidate, submission, TestSession, or Arena action.
Resident and sacred sources remain byte-exact.
