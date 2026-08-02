# 20260802-top-player-new-games-multiagent-analysis

- Status: takeover — three independent read-only tracks complete; final synthesis in progress
- Record owner / integrator: local_codex_1
- Work owner: local_codex_1 (lease takeover at 2026-08-02T11:33:00Z)
- Unavailable assignees: claude_1, chatgpt_1 (no acknowledgement or task progress after the
  corrected fetchable assignment)
- Created UTC: 2026-08-02T10:52:42Z
- Branch: `agent/local_codex_1`
- Area: read-only analysis of newly collected games against top players

## Owner directive

All present agents analyze the new games simultaneously, then cross-review one another.
The terminal result is a ranked list of ideas to improve the live bot that can be checked
immediately.

## Frozen cohort

Source snapshot: `20260802T092656Z-d61p-wide`, completed
2026-08-02T09:30:28.490Z; manifest SHA-256
`27f00b482266f9290903a529ea4119dc96d2bb7825fef53b2ce38cbcae2fcfe4`.

- New means acquisition status `fetched` in that immutable snapshot.
- Our bot means exact agent/submission `6589709`/`41079653`.
- Top players means snapshot-time Legend ranks 1–20, matching the collector's established
  `legend_top20` definition.
- Current-new cohort: 153 open fetched games of our exact bot; seven further fetched current
  games are sealed-tagged and excluded.
- Direct top-20 slice: exactly one open current-vs-top20 game, `897780884` versus rank-13
  Astrobytes. It supports an exact postmortem but cannot establish breadth or value alone.
- Benchmark cohort: 2,684 open games sourced from snapshot top-20 agents, including prior
  cache entries; only three of those games are newly fetched. Benchmark comparisons are
  observational context, never direct current-vs-top evidence.
- The seven sealed-confirmation-tagged games are excluded from every shared row and analysis.

`local_codex_1` publishes a compact, sanitized, hash-pinned shared corpus derived from the
snapshot so cloud agents need neither platform credentials nor the host raw cache. The
union contains 2,836 open games / 5,672 side rows.

## Parallel tracks

1. **local_codex_1 — quantitative matchup deltas.** Rank loss modes by frequency and
   score/margin association; compare top-20 with rank 21–50 and lower/current-field games;
   propose narrow policy edits.
2. **claude_1 — economy and tactical sequence audit.** Inspect resource flow, workforce,
   planting/harvest/chop/banking, denial, collisions and temporal phase differences; propose
   minimal mechanisms rather than broad rewrites.
3. **chatgpt_1 — adversarial synthesis and closure audit.** Independently generate candidate
   improvements from the shared evidence, test them against `docs/CONSTRAINTS.md`, and favor
   ideas with a cheap decisive discriminator.

## Required initial-report schema

Each agent returns a ranked list. Every idea must state:

- rank and short name;
- exact supporting game IDs and observed mechanism;
- affected-game coverage and score/margin association, with uncertainty stated;
- smallest plausible bot change and the exact source seam it would touch;
- an immediate executable check using only open data (exact replay, boundary test, or small
  unsealed panel), including command/config and pass/fail threshold;
- falsification/stop condition;
- matching closed-branch constraints and why the idea is distinct;
- confidence and expected value band, explicitly separating measurement from projection.

## Cross-review matrix

After all three initial reports are remotely published:

- local_codex_1 reviews claude_1;
- claude_1 reviews chatgpt_1;
- chatgpt_1 reviews local_codex_1.

Each review checks evidence provenance, arithmetic, constraint collisions, test immediacy,
and rank ordering. The integrator publishes a final consensus/dissent ranking only after all
reviews or an explicit lease-based blocker.

### Lease-takeover substitution

The external ring was not entered because neither external assignee acknowledged or
published an initial report. After the 15-minute lease elapsed, the integrator formally
took over their unstarted write sets. Three isolated read-only tracks had completed in
parallel: quantitative matchup, economy/action-flow, and exact direct-game postmortem.
Their completed ring is economy→matchup, matchup→direct, direct→economy. The final report
must distinguish these completed reviews from the two missing external handoffs.

## Exclusive write sets

- local_codex_1: this task, shared corpus/manifest under
  `data/analysis/live-agent-6553250/top-player-new-games-*`,
  `local_codex_1/top-player-new-games-*`, own messages/status, and final integration docs.
- claude_1: `claude_1/top-player-new-games-*`, own messages/status only.
- chatgpt_1: `chatgpt_1/top-player-new-games-*`, own messages/status only.

All raw/snapshot/processed inputs are read-only. No agent edits bot source, frozen artifacts,
the live ledger, shared docs, or another agent's namespace during initial analysis/review.

## Prohibitions

No sealed-data read, simulation on reserved ranges, source edit, formatter, candidate build,
TestSession, submission, cron change, raw-cache mutation, or Arena mutation. An improvement
idea is not authorization to implement or deploy it.

## Acceptance

Three independent read-only track reports, three cross-reviews, a compact shared corpus
with deterministic hashes, and one integrated ranked list with immediately runnable
checks. The final report must record the lease takeover and must not imply that the two
unavailable external assignees contributed. Claims, takeover, reviews and integration must
be pushed and remotely verified under the protocol.
