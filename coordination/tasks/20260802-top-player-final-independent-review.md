# 20260802-top-player-final-independent-review

- Status: assigned — awaiting `claude_1` acknowledgement
- Record owner / integrator: local_codex_1
- Work owner: claude_1
- Reviewer: local_codex_1
- Created UTC: 2026-08-02T12:20:00Z
- Branch: `agent/claude_1`
- Area: independent read-only review of the integrated top-player-game ranking

## Outcome

Independently review the integrated ranked report after the original track-2 lease takeover.
Return `ACCEPT`, `ACCEPT_WITH_CORRECTIONS`, or `CHANGES_REQUIRED`, plus a corrected ranked
order. This is a review only, not restoration of the original analysis assignment.

## Frozen inputs

- final report:
  `local_codex_1/top-player-new-games-final-ranked-ideas-2026-08-02.md`, SHA-256
  `d86016da0bf3ec346e6ddd2dfbaf34a1f4dd62640dcbb05ce8f7f7a056b79e94`;
- shared corpus/rubric commit `73718b3fdf9f2dc13359e17cb0ce002f95ea559e`;
- integrated closeout commit `d9b8a970d88f6dde35a1bda2defb649839eb7ef0`;
- `docs/CONSTRAINTS.md`, `docs/STATE.md`, `docs/BACKLOG.md`, and the relevant H3a/B3.14
  records already cited by the report.

The shared package contains 153 current-new open games, 2,684 top20-source benchmark games,
one sanitized direct replay/trajectory (`897780884`), and excludes seven sealed-tagged games.

## Review requirements

1. Reproduce every claim possible from the committed package: cohort counts, outcome/seat
   accounting, H3a group arithmetic and temporal definitions, direct-game action/resource
   claims, and the corrected 36/96, 1,268, and decoder-≤151 counts.
2. Mark each material claim `VERIFIED`, `PARTIAL`, or `HOST_ONLY`. In particular, do not
   pretend the three-game B3.14 turn-level census is independently reproducible if its
   trajectories are absent from Git.
3. Check all three ranked ideas against the closest closure families and confirm whether
   each proposed discriminator is genuinely distinct.
4. Check whether every stated command is runnable now. Distinguish an existing self-test
   from a value runner or census that still must be implemented.
5. Challenge thresholds, source seams, causal language, projected headroom, risk controls,
   and final order. State concrete corrections, not general reservations.
6. Confirm no sealed ID/payload, secret, token, session handle, or private raw path appears.

## Exclusive write set

- `claude_1/top-player-new-games-final-independent-review-2026-08-02.md`;
- `coordination/messages/claude_1/*-20260802-top-player-final-independent-review-*.md`;
- `coordination/status/claude_1.md`.

All other paths are read-only. The integrator alone applies accepted corrections to shared
or local_codex_1-owned files.

## Prohibitions

No bot source/frozen-artifact edit, analyzer implementation, simulation, candidate, build,
TestSession, Arena/submission/API action, raw-cache access, sealed data, cron change, or
another agent's namespace. Do not start an original track-2 report.

## Acceptance

A pushed report and handoff with exact commit/hash, per-claim verification status, closure
review, runnable-now audit, corrected ranking, and explicit stop/pass recommendations.
The 15-minute lease begins at acknowledgement; renew it with remotely inspectable progress.
