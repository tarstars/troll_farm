# B1 — platform-access check (task `20260811-s3-collector-v2`)

- Author: `claude_1`, on the VM
- Date (real UTC): 2026-08-11
- Plan: `docs/superpowers/plans/2026-08-11-s3-phase1-collector-v2.md` Part B, task B1
- Client under test: `data/scripts/collect_snapshot.py::PublicClient` at `origin/main`, imported
  unmodified; the frozen collector's own read path
- Credentials held during every run: **none.** No session cookie, no `Authorization` header, no
  cookie jar. This is asserted mechanically, not assumed — the runner inspects the outgoing
  request headers and the installed urllib opener and records them
  (`cookieless_assertion.outgoing_headers` = `["Content-type"]`, no global opener installed).

## Verdict

**Platform reads work cookieless. B1's stop rule does not trip; B4 may proceed without a
cookie being provisioned.**

All three services collector v2 needs answered anonymously, first try, from this VM:

| Service | Result |
|---|---|
| `Leaderboards/getFilteredPuzzleLeaderboard` | ok — 1000 users, 669,545 bytes |
| `gamesPlayersRanking/findLastBattlesByAgentId` | ok — 154 completed battles for agent `6479768` |
| `gameResult/findByGameId` (ids discovered live) | ok — 3/3, `replay_shape` valid, 601 frames each |

Evidence: `claude_1/collector-v2/b1-platform-access-2026-08-11.json`, produced by
`claude_1/collector-v2/b1_platform_access_check.py`.

## The second finding, which is not a cookie problem

Three game ids taken from this checkout's `data/raw/games/` cache returned HTTP **422**
`{"id":548,"message":"Game not found"}`. That is the frozen collector's hard-stop class, so it
needed explaining before B4 is designed around it. **`gameResult/findByGameId` does not resolve
arbitrary historical ids, and no credential is implicated.**

I did not stop at the first explanation that fit the numbers. Three measurements, each able to
falsify the one before:

1. **Age?** No. Sweep of 16 ids across the whole observed range
   (`b1-retention-sweep-2026-08-11.json`, runner `b1_retention_sweep.py`): `NOT_AGE_SHAPED`.
   The oldest id sampled (`891153730`) resolves while much newer ones fail, so there is no
   retention horizon in game-id order.
2. **A sharp cutoff among unlisted games?** No. Bisect plus neighbour verification
   (`b1-boundary-bisect-2026-08-11.json`, runner `b1_boundary_bisect.py`): `RAGGED`.
   Adjacent ids interleave — `895033310` fails, `895033321` resolves, `895033338` fails,
   `895033352` and `895033359` resolve, `895033379` fails. Each id gives the same answer across
   runs, so availability is a stable per-game property, not flakiness and not a horizon.
3. **Participant battle windows?** Consistent, 7/7.
   (`b1-visibility-hypothesis-2026-08-11.json`, runner `b1_visibility_hypothesis.py`.)
   Hypothesis: *a replay is anonymously readable iff at least one of its two participants still
   has that game in their `findLastBattlesByAgentId` window.* Tested on 3 available and 4
   unavailable games, participants read from the cached bodies, windows fetched live.
   **No counterexample in either direction.** The earlier "unlisted but resolving" cases were
   games whose *other* participant still listed them — the first sweep only consulted one
   agent's window.

**Label: `H_CONSISTENT`, not proven.** Agreement on 7 cases is not the platform's retention
rule; that rule is not observable from here. What is measured is that availability tracks
participant windows and does **not** track age. **Whether a session cookie would widen
historical access is UNTESTED** — I hold no cookie and cannot test it. Nothing here should be
read as "a cookie would not help"; it is "a cookie is not needed for anything B1 gates."

## Consequences for the rest of Part B

- **B4 fetches promptly or loses the game.** A game is retrievable only while a participant's
  window still holds it. Collector v2 must fetch on discovery, in the same run — a deferred or
  retried-tomorrow fetch is a permanent loss, not a delay. Any failure to fetch on the day is
  therefore a real error to surface, not a soft skip.
- **Already-collected games are not re-fetchable, which strengthens the archive rationale.**
  Of 8 ids sampled from this VM checkout's `data/raw/games/` (290 files, ids `892621271`–
  `895035298`), **5 no longer resolve**. The measurement is on this VM's cache, not on
  `project_host`'s 15,291-game corpus, which I cannot see from here — but the two are drawn
  from the same platform population, so the same expiry applies and the Part A upload is
  preserving something that cannot be recovered if lost. Stated as a fact about the upload's
  value only: Part A is the coordinator's, and the network gate is the owner's call.
- **B5's comparison tool needs the same-day framing.** Comparing id sets across a date range is
  fine, but a game the `project_host` cron caught and the VM missed cannot be back-filled later
  by re-fetch; the comparison reports a permanent gap, not a to-do.
- **No change to B1's own gate.** Cookieless is confirmed; I did not request, receive or use any
  credential.

## Honest deviations and limits

- The three follow-up measurements are beyond B1's literal text ("a short report — works
  cookieless / needs the cookie / needs anything else"). I ran them because the raw 422s fall
  under "needs anything else", and a report that had recorded them as an unexplained failure
  would have left B4 to guess. Total extra network cost: **50 requests** (sweep 17, bisect 17,
  visibility test 16 — 7 replay probes plus 9 distinct participant windows), all read-only and
  paced by `PublicClient`'s own 0.35 s interval.
- The first run of `b1_platform_access_check.py` printed `BLOCKED` on a coarse rule that
  required *every* replay probe — historical ones included — to succeed. The rule was wrong,
  not the data: B1 gates B4, and B4 only fetches games it has just discovered. The runner now
  reports `forward_path_verdict` separately from an informational `historical_refetch` count,
  and the committed JSON is from a re-run under the corrected rule. The historical 422s are
  unchanged and are recorded in that same file.
- All ids probed are public; no session, no Arena action, no write outside `claude_1/`.
- The single leaderboard agent used for battle-window sampling is `6479768` (rank 1 at run
  time). A different cohort could sample different windows; the visibility result does not
  depend on which agent, since participants are read per game.
