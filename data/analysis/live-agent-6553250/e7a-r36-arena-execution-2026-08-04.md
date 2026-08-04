# E7a round-36 simplified Arena execution

Status: **EXACT SOURCE ACTIVE / INITIAL HEALTH CLEAN / SETTLING WITHOUT MUTATION**

## Qualification

Round 36 first passed the frozen 516-task development equality panel with zero differing tasks
and every gate green. Candidate:
`cgauto/submissions/candidate-agent6553250-e7a-r36-simplified.min.rs`, 55,799 bytes, SHA-256
`2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381`.

The pretrial resident was exact readable no-orchard `6593838` / `41089629`, complete at score
24.76 and rank 21/137 over 160 games, with clean identity and zero runtime signals.

## One-call execution

- Call time: 2026-08-04T14:56:50Z.
- Endpoint result: `TestSession/submit` HTTP 200.
- Submission id: `41090606`.
- New agent id: `6594200`.
- Submit log SHA-256: `13e3272082f4dd52310ec65ad91b725c8ceabb25f629af10f030241a8ded3185`.
- Retry count: zero.

Read-only recovery immediately after submission returned exactly 55,799 bytes at the frozen
candidate SHA. The ten initial queued battles all carried the new agent/submission identity.

## Initial health

At 2026-08-04T14:57:50Z:

- 11 finished games plus one pending;
- 7 wins, 0 ties, 4 losses;
- one catastrophic loss; negative-margin mass 375;
- identity clean and zero runtime signals;
- Arena-room endpoint: score 0/rank 136; filtered ladder: score 17.55/rank 102.

The score endpoints were visibly asynchronous during cold start and are not a strength verdict.
The exact source and runtime gates pass, so the owner-directed execution is complete. No restore,
retry, or further Arena mutation will occur while this source settles.

## Settled result

At 2026-08-04T16:25:25Z the Arena-room and filtered-ladder endpoints agree:

- score **22.81**, rank **32/137**;
- **160/160** finished games, zero pending;
- **93 wins, 2 ties, 65 losses**;
- mean margin **+8.925**;
- 21 catastrophic losses; negative-margin mass 6,381;
- clean identity and zero runtime signals.

Checkpoint:
`data/analysis/live-agent-6553250/r36-simplified-settled-checkpoint-2026-08-04.json`, SHA-256
`0f4765143c9a43be9dfe78fa031a63111eb5f4a29565007d1a110ad8772a189b`.

This is the requested settled observation. The Arena remains unchanged.
