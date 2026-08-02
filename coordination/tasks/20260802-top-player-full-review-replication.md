# 20260802-top-player-full-review-replication

- Status: initial handoffs accepted — two-way cross-review released
- Record owner / integrator: local_codex_1
- Independent work owners: claude_1, chatgpt_1
- Created UTC: 2026-08-02T12:38:00Z
- Cross-review released UTC: 2026-08-02T13:47:00Z
- Branches: `agent/claude_1`, `agent/chatgpt_1-top-player-full-review`
- Area: identical independent full review of recent games from the current best bot

## Owner directive

Assign the same full review to the other agents. Both agents independently analyze the same
frozen package and produce the same deliverable: a ranked list of improvements that can be
checked immediately. This supersedes future work under the narrower Claude-only final-report
review; its completed handoff remains evidence.

## Frozen evidence

- current bot: exact agent/submission `6589709`/`41079653`, source SHA-256 `6f992a5a…`;
- shared package commit: `73718b3fdf9f2dc13359e17cb0ce002f95ea559e`;
- package paths:
  `data/analysis/live-agent-6553250/top-player-new-games-shared-2026-08-02.{manifest.json,sides.csv,direct-game.json,direct-trajectory.json}`;
- ranking rubric:
  `data/analysis/live-agent-6553250/top-player-new-games-ranking-rubric-2026-08-02.md`;
- constraints and live state: `docs/CONSTRAINTS.md`, `docs/STATE.md`, `docs/BACKLOG.md`.

Counts frozen by the package: 153 current-new open games, including one top-20 opponent,
73 rank-21–50 opponents, 52 rank-51–100 opponents and 27 rank-101+ opponents; 2,684 open
top20-source benchmark games; one exact direct game/trajectory (`897780884`); seven
sealed-tagged games excluded.

The integrated local report is not an input to the initial replication. Claude has already
reviewed it and cannot be blind; Claude must disclose that prior exposure. ChatGPT must not
read the local or Claude reports until its initial report is pushed. Neither agent reads the
other replication before both initial handoffs are published.

## Identical analysis mandate

Each agent independently:

1. verifies package hashes, cohort membership, identities, seats, durations and outcome
   accounting;
2. compares current behavior and temporal/resource/action profiles against opponent-rank
   bands and the top-20 benchmark, clearly separating direct from observational evidence;
3. performs the exact `897780884` postmortem from the committed replay/trajectory;
4. identifies and quantifies recurrent loss modes using only fields in the shared package;
5. checks every candidate against the nearest closed branch in `docs/CONSTRAINTS.md`;
6. returns a ranked list of immediately checkable improvements.

Every ranked idea must include exact game IDs/mechanism, affected `k/n`, association and
uncertainty, one smallest source seam, current-vs-projected value, an exact first
command/config/check, pass threshold, stop rule, closure distinction, confidence and rubric
score. Mark unsupported turn-level claims `UNAVAILABLE_FROM_PACKAGE`; do not infer them from
the local final report.

## Independent outputs

- Claude: `claude_1/top-player-full-review-replication-2026-08-02.md`.
- ChatGPT: `chatgpt_1/top-player-full-review-replication-2026-08-02.md`.
- Each agent owns only its report, status, and task-specific messages.

## Cross-review

After both initial handoffs are remotely visible, the integrator releases the reports for a
two-way cross-review:

- claude_1 reviews chatgpt_1;
- chatgpt_1 reviews claude_1.

Each review checks provenance, arithmetic, closure collisions, source seams, actual
runnability, thresholds and rank order. Do not begin cross-review early.

## Prohibitions

No raw-cache or host-only path access, sealed data, source/frozen-artifact/shared-doc edit,
analyzer implementation, build, simulation, candidate, TestSession, Arena/API/submission
action, cron change, or another agent's namespace. No report may call the one direct top-20
game broad evidence or convert margin/wins to Arena rating.

## Lease and acceptance

The 15-minute progress lease begins independently at each acknowledgement. A valid result
requires two pushed initial reports, two pushed cross-reviews, and integrator disposition.
Late or unavailable agents are recorded honestly; no local substitute counts as their work.

Initial handoffs were accepted at `2026-08-02T13:46:50Z`. Cross-review output paths and the
required reconciliation were released in
`coordination/messages/local_codex_1/20260802T134700Z-20260802-top-player-full-review-replication-release.md`.
