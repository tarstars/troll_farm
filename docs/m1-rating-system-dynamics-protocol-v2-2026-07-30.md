# M1 rating-system dynamics — frozen audit protocol v2

Frozen UTC: 2026-07-30T18:35:30Z  
Owner: `local_codex_1`  
Reviewer: `chatgpt_1`  
Task: `20260730-m1-rating-system-dynamics`  
Supersedes: `docs/m1-rating-system-dynamics-protocol-2026-07-30.md`

This immutable v2 incorporates v1 except where replaced below. It corrects a source-time
assumption before analyzer implementation and adds the game-associated platform score
field discovered during source inspection. No result was inspected and no model was fit
before this correction.

## Question and verdicts

Can the stored Legend evidence recover how ladder score responds to wins and losses? If
yes, how many additional net wins correspond to a +1 score move near resident agent
`6561795`? Return exactly one verdict:

- `RECOVERED`: the observable rule and wins-per-+1 estimate pass all gates;
- `DESCRIPTIVE_ONLY`: useful response evidence exists but the rule is not recovered;
- `UNIDENTIFIABLE`: the stored evidence cannot price a score point.

The audit must distinguish a per-game rule, a batched recomputation, and an empirical
association between outcomes and platform-reported scores.

## Frozen inputs

Read these seven complete `troll-farm-d61p-snapshot-v1` directories, and no later snapshot:

1. `20260721T105508Z-d61p`
2. `20260727T130712Z-d61p`
3. `20260728T050038Z-d61p`
4. `20260728T050038Z-d61p-wide21to50`
5. `20260728T110709Z-d61p-wide`
6. `20260729T021701Z-d61p-wide`
7. `20260730T021701Z-d61p-wide`

The two `20260728T050038Z` directories share the exact leaderboard response SHA-256
`fc3698a3b92af042c626c2410e3d0c8deba9aa1431dfbbd20bd7ac22a0adeea9`.
The narrow collection completed at `05:01:01Z`; the wide extension completed at
`07:06:35Z`. Therefore they are one leaderboard observation but distinct battle-list
observation times. Coalesce the leaderboard rows only. Preserve per-request
`requested_at_utc` for battle exposure and never assign the wide lists to 05:00.

A snapshot is admissible only when its manifest is complete with the required schema.
Verify the manifest-recorded SHA-256 for every consumed leaderboard, battle-list,
`requests.json`, and `games.json`. Raw game reads are restricted to `cache_file` paths
explicitly indexed by an admitted `games.json`; verify raw bytes against that row's
`response_sha256`. All inputs remain read-only.

## Two evidence panels

### A. Leaderboard recomputation panel

Parse exact integer `agentId`, `score`, `creationTime`, `updateTime`, and rank. Coalesce
identical leaderboard hashes. Construct consecutive exact-agent intervals and record score
delta and update-time behavior. This panel diagnoses the frequency and magnitude of score
recomputations; it does not by itself assign games to an interval.

### B. Game-associated score panel

For every indexed raw game, parse integer `gameId`, terminal `ranks`, and each
`agents[]` entry's exact `agentId` and floating `score`. Terminal ranks define win/loss/tie;
raw resource `scores` do not. Retain an agent-game observation only when:

- the agent is named as a `sources[].agent_id` for that game in at least one admitted
  `games.json`, proving the game came from that agent's sampled battle list;
- player identity and game-associated agent identity agree;
- all duplicate copies of the game have byte-identical response hashes.

Sort each source agent's observations by integer game ID for deterministic sequence
diagnostics. Game ID ordering is not a timestamp and cannot by itself prove exposure
completeness.

Partition each agent sequence into maximal constant-score epochs at tolerance `1e-12`.
For every adjacent epoch pair, evaluate both conventions:

- `prior-epoch outcomes -> next score` (game score behaves like a pre-game/current rating);
- `next-epoch outcomes -> next score` (game score behaves like a post-game/recomputed
  rating).

Do not choose the better convention solely by fit. It must also be consistent with
leaderboard `updateTime` transitions and repeated raw games across collection dates.

## Exposure completeness and censoring

For every source-agent battle-list observation, record its request time, length, minimum
and maximum game ID, additions, drops, and overlap with the prior observation. A score-epoch
transition is outcome-complete only when all of the following hold:

- the epoch's games appear in a source-agent battle list, not merely through an opponent;
- every game decodes and hashes correctly;
- the epoch is bracketed by observed scores on both sides;
- overlapping battle-list observations do not reveal a later missing game inside the
  bracket;
- the epoch is not truncated at the beginning or end of the union sequence;
- no source request failed.

List growth, overlap, and game-ID continuity are diagnostics. They cannot convert an
unbracketed recent window into lifetime-complete exposure.

## Identification ladder

Classify support before model interpretation:

- **FULL:** at least 30 outcome-complete score transitions across at least 10 agents; at
  least 80% of all internal score transitions are outcome-complete; both positive and
  negative score changes and both wins and losses occur; the score-field convention is
  independently resolved; and the selected rule passes validation.
- **PARTIAL:** FULL fails, but at least 20 outcome-complete score transitions across at
  least 8 agents contain both wins and losses, with no source-integrity failure.
- **UNIDENTIFIABLE:** fewer observations than PARTIAL, no outcome variation, unresolved
  score-field semantics, or any source-integrity/identity failure.

An attractive fit never upgrades support.

## Candidate rules and validation

Fit only outcome-complete internal transitions under a resolved score convention. Candidate
families, ordered from least to most elaborate:

1. affine response to wins, losses, and ties;
2. net-win response (`wins - losses`) with an intercept;
3. Elo-like logistic expected result using agent and opponent game-associated scores, with
   bounded deterministic grids for scale and K;
4. recomputed aggregate win-rate transforms only if a stable cumulative denominator is
   actually observed.

No polynomial, agent-specific curve, or outcome-selected subset may be added. Use
leave-one-agent-out validation with at least eight agents; otherwise deterministic
leave-one-transition-out and label it weaker. Report MAE, median absolute error, bias,
maximum absolute error, zero-change baseline MAE, and residuals by agent/transition.

A rule is recovered only when support is FULL and validation MAE is at most `0.05` and at
least 50% below the zero-change baseline; median absolute error is at most `0.02`; no agent
with at least three held transitions has absolute mean residual above `0.10`; win and loss
signs are coherent; and the same parameters explain positive and negative changes.

## Wins-per-+1

Only a recovered rule earns a point estimate. Evaluate its local finite difference at
score 21.76 against the empirical opponent-score distribution for agent `6561795`, holding
loss/tie mix at the resident's observed mix. Bootstrap agents 1,000 times with seed
`20260730`. PARTIAL support may earn only a clearly labeled descriptive range if finite
and stable under leave-one-agent-out deletion. UNIDENTIFIABLE support earns no number.

## Required diagnostics and consequence

Report source hashes, coalesced leaderboard instants, battle request times, list
growth/overlap/censoring, raw-game coverage, duplicate consistency, score epochs,
leaderboard-to-game score consistency, convention evidence, transition support, outcome
balance, all candidate metrics, resident coverage, and sensitivity excluding the long
July 21→27 interval. If not recovered, state the minimum additional collection required.

This read-only audit cannot qualify a bot or authorize an experiment, Arena read,
TestSession, or submission. Negative and unidentifiable verdicts are successful completion.
