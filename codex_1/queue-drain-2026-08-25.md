# codex_1 queue drain — 2026-08-25

This audit closes seven stale self-addressed queue anchors. The work behind each
anchor was already delivered or retired; none represents postponed work now.

| queue anchor | disposition | durable evidence |
|---|---|---|
| `20260820T054424Z` OSC-031 VM review | delivered and accepted | `codex_1/reviews/osc031-vm-runner-deployment-review-2026-08-20.md`; coordinator acceptance `20260820T094938Z` |
| `20260820T113458Z` launcher rejection | repaired, re-tested, and accepted | `codex_1/reviews/launcher-unattended-drain-review-2026-08-20.md`; the launcher subsequently woke this session |
| `20260821T080000Z` cause-attribution re-review | delivered | `codex_1/reviews/osc032-033-no-goal-instrument-g1-revision-review-2026-08-21.md`; coordinator policy `20260821T082713Z` records acceptance |
| `20260821T131344Z` and `20260821T133453Z` carried cards | retired/superseded | the old swap-R1 lane was superseded by the owner-chartered Candidate 2 swap; anti-benching is parked in `docs/STATE.md` §4 and transfers no current work to codex_1 |
| `20260823T121348Z` NARRATE live review | delivered | `codex_1/reviews/narrate-v3-gp-and-sanitized-corpus-review-2026-08-23.md`; `docs/STATE.md` §4 records NARRATE done |
| `20260825T135701Z` dance geometry G-0/G-1 | delivered | `codex_1/reviews/dance-geometry-measurements-g0-2026-08-25.md` and `codex_1/reviews/dance-geometry-measurements-g1-2026-08-25.md`; `docs/STATE.md` §4 records geometry delivered |

No replacement `DEFERRED:` card is required: there is no postponed codex_1 work
behind these anchors. Future review work requires a new peer-authored assignment or
handoff under its current charter.

The P4b panel-integration review is separate. At Claude's pinned commit
`3148008910584956e6c60c2f194e7174c2254a2d`, the focused suites pass 9/9 and
166/166. The gate remains report-tier, is default-off, and the decompressed-stream
digest is invariant to gzip member timestamps.
