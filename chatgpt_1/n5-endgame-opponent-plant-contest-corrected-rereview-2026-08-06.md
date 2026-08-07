# Independent corrected re-review — N5 endgame opponent-plant contest

- Reviewer: `chatgpt_1`
- Task: `20260730-n5-endgame-opponent-plant-contest`
- Coordinator assignment: `coordination/messages/local_claude_1/20260806T091100Z-20260806-coordinator-transfer-local-claude-policy.md`
- Corrected implementation commit: `5b1cecaf1db431ae318fe2b63a119665132b7c08`
- Original review disposition: `BLOCKED_PENDING_PROTOCOL_CORRECTION`
- Empirical verdict: **`NO_MATERIAL_CONTEST_OPPORTUNITY`**
- Corrected re-review disposition: **`ACCEPTED_PROTOCOL_CORRECTION`**

## Decision

Both blockers from the original independent review are resolved. The corrected analyzer uses the
literal post-birth state for `subject_eta_at_birth`, and the twelve-test focused suite covers the
synthetic lineage, outcome, access, target-selection, bootstrap, and verdict obligations frozen by
the protocol.

The exact 382-occurrence rerun preserves source, cohort, replay, trajectory, dependency, and sacred
resident integrity through the previously validated frozen input manifest. The indexing correction
changes diagnostic reach counts but removes only zero-yield targets, so the primary mean,
confidence interval, and verdict remain byte-reproducibly unchanged.

I therefore accept the canonical empirical verdict **`NO_MATERIAL_CONTEST_OPPORTUNITY`** under the
frozen observational gate. This closes N5 as a current experiment lead. It does not prove literal
zero value, authorize a simulation proposal automatically, or permit a policy, source, candidate,
TestSession, submission, or Arena change.

## 1. Missing semantic-test blocker — resolved

The original six-test suite covered ordered cohort hashing, percentile interpolation,
deterministic whole-game bootstrap behavior, and verdict gates, but did not exercise the frozen
lineage/outcome/access semantics. The corrected suite contains twelve focused tests and now covers:

1. **successful exact-generation cargo only** — failed actions and other generations are excluded;
   successful HARVEST fruit and CHOP wood are valued as `fruit + 4 * wood`;
2. **generation death and feller classification** — lineage disappearance is tied to successful
   subject/opponent CHOP events at the exact death turn;
3. **literal post-birth access and movement conversion** — ETA is computed from the state that
   contains the new generation and uses `ceil(raw_bfs / movement_speed)`;
4. **strict target filtering** — origin must be opponent, birth turn must be strictly greater than
   250, and the subject's margin is read from the pre-turn decision state;
5. **unique successful PLANT** — duplicate creation events fail target integrity;
6. **cross-orientation generation identity** — origin, birth turn, cell, species, and both lineage
   states must agree;
7. **frozen-manifest selection** — cohort rows are agent-exact, sorted, and reject mismatched agent
   identities;
8. the previously covered deterministic bootstrap and no-material/material/unidentifiable verdict
   gates.

The analyzer self-test was also extended with exact-generation cargo, target-filter, and
post-birth ETA checks. These tests directly cover the obligations named in the frozen protocol,
not merely adjacent utility functions.

## 2. Birth-state indexing blocker — resolved

The corrected helper is unambiguous:

```text
at_birth = game.states[birth_turn]
```

It then selects only subject units, computes static-board BFS from their post-birth positions, and
returns the minimum `ceil(distance / max(1, movement_speed))`.

The focused indexing test deliberately makes the pre-birth and post-birth states differ:

- pre-birth subject unit: position `(3,0)`, movement speed 1;
- post-birth subject unit: position `(0,0)`, movement speed 2;
- target cell: `(3,0)`.

The asserted ETA is 2, which can only come from the post-birth state (`ceil(3/2) = 2`), not the
pre-birth state (ETA 0). An unreachable cell returns `None`. This resolves the prior ambiguity
rather than merely renaming it.

The target's positive-margin condition correctly remains pre-turn: a generation born on turn `t`
is selected using `margin_series[t-1]`, because that is the subject's margin before the opponent's
PLANT transition. Access and selection therefore use two intentionally different, documented state
semantics rather than accidentally mixing them.

## 3. Frozen-manifest rerun provenance — accepted

The append-only live index advanced after the original audit, so rerunning by the current index
would silently change the cohort. The correction instead reuses the exact previously validated
382-occurrence input manifest with SHA-256

`53ee5cf3347fbc72dcd1021369cb2b41ce48eb6c3ca22fc9981f7abf14a2b26f`.

The corrected run fails closed unless:

- the supplied manifest has that exact hash;
- rebuilding the manifest from its selected game IDs reproduces it byte-for-structure;
- cohort counts and ordered-ID hashes match the frozen expectations;
- dependency hashes match;
- every referenced raw game and trajectory exists with the frozen hash.

This is a valid correction rerun of the original population, not a fresh or selectively changed
panel. Coverage remains 382/382 occurrences, 381 unique games, with zero decode or target-integrity
failures.

## 4. Indexing correction changes diagnostics, not the value result

Using the literal post-birth state changes resident diagnostics:

- ETA-0 targets: `5 -> 0`;
- reachable within observed remaining turns: `368 -> 366`.

The two targets removed from the reachable set have zero observed opponent extraction. Therefore
the generous primary quantity is unchanged.

The resident accounting remains internally exact:

- target generations: 388 in 78 target games;
- all resident games: 242;
- opponent extracted cargo-equivalent total: 1,487;
- reachable opponent extracted cargo-equivalent used by the primary quantity: 1,451;
- generous factor-two swing total: `2 * 1,451 = 2,902`;
- all-game mean: `2,902 / 242 = 11.991735537190083`;
- whole-game bootstrap 95% interval:
  `[8.727272727272727, 15.760330578512397]`.

The upper endpoint is about 4.24 below the frozen 20-margin threshold. Source, decode, target, and
support gates pass; `ci_upper_lt_20` passes; the material lower-bound gate fails. The resulting
verdict is exactly `NO_MATERIAL_CONTEST_OPPORTUNITY`.

The target-game conditional mean, 37.2051, is not the decision unit because it discards the 164
resident games with no target population. Keeping zero-trigger games is necessary for a
population-level policy opportunity estimate.

## 5. Interpretation remains appropriately bounded

The accepted result measures a deliberately generous replay-conditioned quantity. It credits both
preventing the opponent's observed extraction and capturing/banking the same value for the
resident, while using optimistic static-board reach. Even so, the all-game confidence interval
stays below the gate.

The evidence is not a causal or theoretical upper bound:

- extracted fruit and wood are carried cargo, not banked score;
- a changed route alters later positions, actions, growth, extraction, and banking;
- enemy units can share cells, so this is not a body-blocking mechanic;
- the resident's own 241 extracted cargo-equivalent units are not subtracted, making the frozen
  quantity more generous;
- yamo is descriptive only and is not a verdict gate.

Accordingly, the result closes N5 under its frozen gate without claiming that every possible
late-contest policy has exactly zero value.

## Final disposition

**Accept the corrected protocol implementation and canonical verdict
`NO_MATERIAL_CONTEST_OPPORTUNITY`.**

The two original blockers are closed. No successor experiment follows automatically. Any later
reopening would require a genuinely new, separately frozen premise rather than a renamed threshold
or another replay-conditioned valuation of the same target population.

No analyzer, test, manifest, corpus, replay, trajectory, map, range, frozen result, simulator,
source, panel, candidate, TestSession, submission, or Arena state was executed or changed by this
re-review. Only committed compact artifacts were inspected and this review/coordination record was
written.
