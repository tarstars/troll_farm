# Evaluation contract after the September 5 reset

This replaces the goal, selection gate and queue-order assumptions in the historical `CLAUDE.md`.
The owner's current request is a significant bot improvement toward **seventh place or better**.
The owner has authorized platform publication. Work is confined to this repository and
`/data/separate_troll_farm-working/`; the neighboring `../troll_farm` is read-only. The owner later
authorized bounded delegation through Claude to conserve primary-agent tokens. The installed
command is `/home/tarstars/bin/claude-proxy` (hyphen, not underscore). The primary agent retains
responsibility for reviewing changes, verification and platform publication; delegation does not
authorize writes to the neighboring project or unbounded platform experiments.

## Success, references and authority

Success is an observed top-seven rank in the highest platform division for the exact submitted
agent, with completed rollout, no pending games and a later confirming reading. A rating threshold
is not a substitute. `monitor_platform_agent.py` now requires 160 distinct exact-submission games,
100% cached and uncached progress, and qualifying observations spanning at least five minutes by
default. A missing observation or a change between qualifying/nonqualifying rank resets the window.
The game-count check retains the known rollout protocol; if the platform changes that protocol,
investigate and document it rather than silently weakening identity or completion checks.

V468 is the historical reference, not a mandatory opening or architectural ancestor. V543 was the
deployed artifact at the reset, not the demonstrated champion. The separately predeclared direct
restoration check now supports V439 (4/6 versus V543's 2/6 fresh real-agent wins), published once
as submission 41245746 / agent 6704418. It has now confirmed mature rank 28, rating 23.43,
with all 160 games complete; see V439-RESTORATION-MATURE-2026-09-05.md. This is not a top-seven
result. V564 is a promising dense-economy
comparison, not a certified improvement. Maintain exact source hashes and executable artifacts
for comparisons. Do not change `bot.rs`/`submission.rs` merely to designate an experimental policy.

Normal local tests and bounded unranked platform evaluation are within the task. Publication is
authorized but should follow competitive evidence and deployment checks, not the old +40 rule.
Publish one exact candidate at a time, capture its identity, and do useful offline work during
rollout. Never claim completion from a local panel or a transient placement reading.

## What each measurement can establish

Use highest-league rules for the active goal. Empty iron terrain is not a league
flag: official training costs depend on league, while the current Rust model's
parse/apply handling disagrees on artificial iron-free states. Such fixtures must
not silently define expected highest-league behavior. Movement tests must also
distinguish official goal normalization from the local direct-endpoint harness.
See `docs/REFEREE-LEAGUE-SCOPE-2026-09-07.md` for verified source details.

| Measurement | Appropriate use | Does not establish |
|---|---|---|
| Executable state fixture | Correct transactions, accounting, legal commands | Strategic strength |
| Historical 8-map / 12-family panel | Regressions and mechanisms on development data | Independent validation or named-agent fidelity |
| Fresh maps against existing proxies | Map generalization within that proxy population | Strength against unrelated real policies |
| Paired official games against fixed real agents | Competitive behavior in the tested blocks | A calibrated rating or full-field rank from a small sample |
| Mature exact-agent ladder result | Actual platform outcome | Reproducibility across arbitrary resubmissions |

Every competitive report must include wins, draws, losses, W+0.5D, own/opponent score, margin,
deployment failure count, and opponent-specific results. Preserve failed runs in the denominator;
an additional clean-game analysis may diagnose their effect but must not erase them. Use official
ranks for official-game outcomes (including ties and disqualifications), score ordering for valid
local referee games. Early score, training time, wood, plants, traffic and idle time diagnose why
a policy wins or loses; they are not universal acceptance conditions.

Pair policies on identical initial state, seat and adaptive opponent. Verify seed echo, normalized
initial input and actual opponent identity for platform pairs. Replay command streams cease to be
adaptive once a candidate changes the game and must not be called live opponent comparisons.
The September 5 pilot protocol is frozen separately in
`FIELD-CALIBRATION-PROTOCOL-2026-09-05.md`.

## Selection and experimental discipline

1. State a falsifiable mechanism, comparison policies, test budget and decision before running.
   Use behavioral tests for the mechanism; source-string checks only validate construction.
2. Treat familiar maps and policies as development data. Repeatedly inspecting them is allowed,
   but does not accumulate independent evidence. Count maps/seed blocks as well as games.
3. Before selecting a replacement, test across fresh maps and materially different adaptive
   opponents, including competitive opponents near the target and lower-ranked controls. Track
   paired outcome changes first; inspect margins without letting huge already-won games dominate.
4. Quantify uncertainty at the shared-map level, keeping both seats/opponents of one map together.
   A three-map pilot is descriptive, not a confident superiority test. A fixed opponent panel
   cannot quantify uncertainty over unseen opponent strategies by bootstrapping maps alone.
5. Keep a separate prospective confirmation set; do not tune a failed candidate on it and still
   call the next use a holdout. Freeze the larger sample and acceptance decision before opening it.
   Do not fit a rating conversion or threshold from two historical observations or a tiny pilot.
6. For a supported finalist, compile its exact standalone source, enforce the UTF-16 source limit,
   compare readable/exported command streams, and exercise startup plus complete protocol I/O.
   In-process decision timing alone does not cover deployment startup.
7. A failed experiment closes the tested implementation and schedule, not every implementation
   of its economic idea. Unexpected behavior requires a reproducer before a strategic conclusion.

The old `panel_gate.py` and its tests remain unchanged for historical reproducibility. Its PASS is
now a legacy score-curve verdict, **not a publication or strength gate**. Do not run another chain
of marker-substitution candidates merely because it is the first open historical queue item.
Prefer one reviewable active controller with deterministic standalone export when the next
substantial gameplay change is chosen; preserve the historical artifacts rather than deleting them.
