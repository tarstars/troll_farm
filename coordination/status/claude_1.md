# claude_1 Status

- Updated UTC: 2026-08-12T06:10:00Z
- State: inbox clean (sweep exit 0, 0 unacknowledged, 0 delivery errors). **Collector v2 ran unattended for the first time and every review item is closed.** `20260811-s3-collector-v2` and `20260811-collector-v2-dedupe` both in `review`; all four review findings (exit-code gate, codec independence, ordering guard, plus the coordinator's cross-review) repaired and ACCEPTED by `codex_1`.
- **First unattended run, 2026-08-12 05:47 UTC**: candidates **6,295**, already held **6,295**, fetched **0**, dropped **0**, exit 0, 49.5 s. No pack, no upload, cursor unchanged at 603 — exactly what binding design point 6 specifies.
- **`fetched=0` was VERIFIED as coverage, not blindness** (the check that matters): max held id in S3 `898583715` is **higher** than the max id visible in live participant windows `898550181`; 0 candidates above our max, 0 unheld. The platform is not producing games beyond our corpus. **Consequence for cut-over: while the platform is quiet, the spec's seven-day criterion is satisfiable by a collector that does nothing** — do not start the clock until at least one day shows genuine inflow.
- **Three measured facts to carry:** replay availability tracks participant battle windows, not age; the bucket grant blocks deletion but NOT overwriting, so append-only is enforced by `If-None-Match: *` in our own code; and *missing from a day's manifests* (352 on 2026-08-11, the cut-over criterion) is a different question from *absent from S3* (**0**). Never quote the first as the second.
- **VM disk**: 64%, 6.9 GB free. `~/.cache/uv` had reached 5.0 GB because `mutation_runner.py` spawns a `uvx` environment per mutant; `uv cache clean` reclaimed it. Runner NOT changed to reuse one environment — that tooling is under review and both tasks' evidence rests on it; proposed as a sequenced follow-up. `codex_1`'s `/tmp` dirs untouched.
- **Ruled 2026-08-12 by the coordinator**: M3a portability repair adopted as written; **M3b substrate = base-panel golden bundle v2**, with the c5 46-episode diagnostic library a separate versioned dataset, never a silent substitute. Genuinely open and unowned: the I-30 trust root and the M2 method packet.
- Role: contributor + **execution reviewer** on every artifact. Coordinator/integrator/arena controller AND detector-semantics owner = `local_claude_1`. **`chatgpt_1` and `chatgpt_2` are unreachable** (owner ruling 2026-08-12). `codex_1` is a NEW agent (canonical `agent/codex_1`, onboarded 2026-08-09) and is **not** `local_codex_1`, which is dormant since 2026-08-06.
- Branch: agent/claude_1-banana-restoration-r2; canonical agent/claude_1 at `7366e1cf`. Tooling `inbox_sweep.py` `be8251c4…`, `lint_outbox.py` `f3c47b70…` (synced from `main` twice this cycle — `main` moved under me).
- **Read `claude_1/SESSION-FINDINGS-2026-08-07-to-11.md` before acting.** It carries the programme state, the measured findings, and the error patterns. It predates the 08-12 unblock below.

## Blocking state

- **The TRAIN/referee blocker is CLEARED.** r4 accepted by `chatgpt_1` for the c5 execution layer; B1 closed by `local_claude_1` through independent execution in a second checkout (7/7 artifact digests, `engine.rs` `7c240abf` untouched, panel 163 OK, pre-review 24 OK, mutation 16/16 caught, and floor packets **row-level `IDENTICAL`** to committed `evidence-r4/` — agreement on *which* games block, not just the total). The r4 panel is merged to `main`: `main:claude_1/pipeline/fuzz_panel.py` = `d8900abf31dd030d…`, 33 TRAIN references. `main` was pre-r4 until 08-12, so anything measured from `main` before then used the broken referee.
- **This does NOT authorize verdicts.** `chatgpt_1` holds I-30 at `GATE_UNREADY / MEASURED_UNTHRESHOLDED` and states plainly: **no detector branch is authorized for candidate acceptance, and no I-30 PASS, FAIL, threshold or candidate verdict is accepted.** Do not read the r4 acceptance as a gate opening.
- Instrument `fuzz-panel/5` · corpus `c5-two-player-phase-merged-2026-08-11`. **Floor (parent vs itself) = 118/240. Candidate run (banana `eac2eb36` vs parent) = 121/240.** Different quantities; `run_identity` is machine-checked. `118/240` is quotable **only** with r4's binding restriction attached: TRAIN is witnessed in 2 games (1 spawn each), and 10 of 17 repaired rules have no corpus witness — those are pinned by unit tests, the two-oracle differential and the mutation drive, never by the floor.

## Reviewers — resolved, and degraded on purpose

`chatgpt_1` held every review slot below and is unreachable. `codex_1` claimed
`20260807-gate-architecture-review` and the M3a idle-blocker replication, and declined the rest.
`local_claude_1` ruled (`20260812T211000Z`, superseding `20260812T204000Z`): **three of the four
reviews had already been delivered before `chatgpt_1` went dark**, so the vacancy is the *re-review
of my repairs*, not of my current work — I am not blocked.

Standing terms of that ruling, all still in force:

- **I do not review my own repairs.** Not negotiable, and it is why I am not the check on anything
  below that I author.
- Anything `local_claude_1` reviews alone is labelled **`SINGLE_REVIEWER_DEGRADED`**; it is the
  coordinator, so it adds a second look, not a second opinion.
- **Nothing closes as fully `ACCEPTED` under a single reviewer without the owner's sign-off.**
- Every `chatgpt_1` disposition is **`RECORDED / UNREPLICATED`** until reproduced by execution here
  — they rest on self-run Actions jobs by the reviewing agent, the same evidence class as the
  quarantined 2026-08-06 fabrication.
- `local_claude_1` **cannot** review `20260807-transport-quarantine-and-outbox-lint` (it authored
  it), so that task still needs a second reviewer; I am one of the two required and the other slot
  is unfilled.

Worth remembering: I once treated a reassignment table as a settled allocation. It was an *offer* —
a reassignment is not complete until the receiving agent claims it, and the decline was already
published when I wrote. **Re-sweep between reading an allocation and acting on it.**

## Open dispositions requiring my revision work

- **M3a correct-subject** — **REPAIRED AND DELIVERED** 2026-08-13, handoff `20260813T003000Z`, artifact `ae701fc4`. Each panel config now carries `source_git = {commit, path}` on an immutable 40-hex commit; the replay materialises the blob and re-checks it against the config's own `sha256` before compiling; corpus skips are evaluated before compilation; no absolute host path remains in either config's data fields. `fuzz_panel.py` untouched (`d8900abf…` is the accepted referee digest). Verified against a control that failed first: with the scratch directory masked, pre-repair reproduces `chatgpt_1`'s `PanelError` verbatim and repaired gives 94 tests OK / **34 of 34 byte-for-byte**. New `TestSourcesArePortable` (6 tests, default suite, no `rustc`) makes a recurrence a failure now. **Still open and not mine:** the M3b substrate selection — the c5 46-episode diagnostic library and the golden v2 record (34 exact D-1 episodes / 32 source games) are different populations and neither may silently replace the other.
- **Bite-test audit r2** — **blockers 1, 2, 4, 5 CLOSED; blocker 3 open.** Handoffs `20260813T030000Z`, `20260813T054000Z`, `20260813T081000Z`; latest artifact `3e5ade1b`.
  - **4** `run_mutations.py` exit status describes the experiment: `1` control not green, `2` incomplete, `0` only when whole; `--only` needs `--partial`. Accepted.
  - **5** 47-branch tallies derived from `branch_ledger.json`; `render_branch_ledger.py --check` compares audit prose to data both ways. Accepted. **The contract-authority tally was never derivable from the table** — now an explicit field.
  - **1** `LIVE` → **`PROBE_SENSITIVE`** with the limit inline everywhere: *changes probe output on generated traces; does NOT establish legal-game reachability.* Results schema bumped to `detector-mutation-results/3`; derived artifacts regenerated, not edited. Measurement unchanged and verified: 64 counted, 21 caught, 43 survived, 30 probe-sensitive survivors.
  - **2** No contention label. `max(speed, 1)` replaced by the engine's own `d <= speed` — **`engine.rs::next_cell` has no floor**, so at speed 0 the authority returns `current`. Three D-3 rows carry `NO_WITNESSED_POPULATION (720 referee games, 3 corpora)`. **Binding wording: zero observed episodes is a statement about this corpus, NOT "the predicate cannot fire."** No D-3 branch is probe-covered.
  - **3** — **substantially unblocked 2026-08-10, not closed.** The owner's strict rule (*no banana manipulation before training the second troll*, threshold 0) **dissolves** D-9 (a)'s affordability question rather than answering it: there is no affordable delay to price when the permitted count is zero. Row (a) is the operative rule, no longer a retired proxy. **I pinned it** (handoff `20260810T111000Z`, artifact `80c3dd63`): it was `UNPINNED` with D9-M1/M2/M3 surviving — a strict rule policed by a detector nobody had shown could tell right from wrong — and three negative tests, each verified to kill its own mutant before being written, take D-9 to **4/4 CAUGHT, 0 survivors**. Overall 21→24 caught; tally 11→12 `PINNED`. **Paired branches (b) `train_late`, (c) `train_missing`, (d) `train_stats_differ` still carry the stale pre-c5 `INSTRUMENT_UNSUPPORTED` label and are NOT addressed** — the rule says nothing about non-banana TRAIN displacement.
- **I-30 rev 3** — **blocker 2 REPAIRED**, handoff `20260813T050000Z`, artifact `7e5c9874`. Owner-freeze chronology is decided by Git ancestry between the decision's commit and an immutable `observation_anchor`; an anchored authority refuses to fall back to timestamps, so an unanchored production run cannot reach `verified`. Demonstrated: the pre-repair analyzer verifies a bound frozen AFTER the observation with **zero reasons**. 105 existing tests still pass + 8 new (all 8 fail pre-repair). **Blocker 1 still open** — `ExecutionValidity` still validates a self-declaration: `referee_sha256` checked for presence only, `verb_manifest_sha256` self-consistent by construction, command counts caller-supplied. Design proposed; awaiting a ruling on whether the verb manifest is *derived from the dispatcher* or *bound to a committed registry of reviewed referee digests*.
- **M2 rev 2** — accepted, nothing owed. **Fast-verification-executor requirements** — **PARKED** by the coordinator: its author is unreachable and nobody inherits an unowned spec. `coordination/tasks/20260811-fast-verification-executor-design.md` is `PROPOSED / BLOCKED ON REQUIREMENTS REVIEW`, owner unassigned.
- **`20260807-transport-quarantine-and-outbox-lint`** — my execution review delivered 2026-08-13, handoff `20260813T012000Z`, artifact `afb6903a`: **`REVISION_REQUIRED`**. Accepted: the 41-message delta is exact, all 41 carry an explicit `ack_for` (verified from raw blobs, not via the tool under review), 92 tests pass, zero regressions. Blocking: `parse_json_list` is unguarded in `collect_my_acks`, so a malformed `ack_for` in the sweeping agent's **own** namespace crashes the sweep with an uncaught `JSONDecodeError` — exiting `1`, which collides with the documented "healthy but unacknowledged" status — and published messages are immutable, so it cannot be repaired without quarantine. No test reaches the changed branch.

## Owed, now unparked by r4

M1 Decision Packet implementation (spec frozen against `98628e98`) · M3b adjudication (needs M1 + valid M3a) · P4 re-do on c5 evidence · D-4 repair · gate revision 3 execution review. **With the owner:** the D89a label; whether to fund a fresh 512-row corpus for U4.

## Do not cite

**My idle-blocker claims are `UNREPLICATED / UNRESOLVED`** (`codex_1`, `20260809T190604Z`, accepted
by me in full). The terminal population of **20 episodes** on subject `98628e98` IS independently
reproduced and may be cited. **Claims 1 (all 20 have an `IDLE` blocker) and 2 (no working-blocker
episode reaches 62 turns) are not** — the base panel carries no per-turn states, so they are
unresolvable from any evidence outside my own library. **The merged repair plan's mover-only
rationale rests on claim 2 and must carry that label wherever cited.** Repair proposed and awaiting
the coordinator's sequencing: commit raw `98628e98` transcripts as a non-library artifact. The
lesson is mine — committing my extraction is not committing the evidence it came from.

The `+12.453/+76.508` D89a split (`UNRESOLVED`, TSVs never committed) · `oscillation-library/` as M3a (it is parent lineage `a8eb3b2b`) · D-9 as `INAPPLICABLE` or "196 false positives" (now `INSTRUMENT_UNSUPPORTED / GATE_UNREADY`) · D-6 as falsified (it is a `CONTRACT AUTHORITY: CONFLICT`) · any floor figure for the ~10 of 17 rules lacking a corpus witness.

## Transport

**Dual-format MANDATORY** (v2 front matter + legacy `- To:` bullets) — a peer was blind to v2 for ten days. **Gate publishes on `lint_outbox.py` EXIT STATUS**, not on grepping its output. Push before citing: *unpushed is unsent*, and a stale remote-tracking ref makes `git merge` a silent no-op. Never `git add -A` — agents share this tree.

**`ack_for` is no longer inert on non-`ack` kinds** (changed 2026-08-12, `f9fc1810`). It used to count only on `type: ack` — I broke that 4x — and now any kind may discharge by naming exact paths. `ack` must still carry a non-empty `ack_for`. **Prefer a separate `ack` anyway:** a busy handoff acking four questions in its front matter is easy for a reader to miss.

**`pytest` is absent from the host but the transport suite requires it** — `tests/test_inbox_sweep.py` does `import pytest`, so `python3 -m unittest` cannot run it. Use `uvx pytest tests/…` (92 pass). The old "use `python3 -m unittest`" guidance holds only for suites that do not import pytest.

**Tooling: `inbox_sweep.py` `be8251c4…`, `lint_outbox.py` `f3c47b70…`, both matching `main`.** `lint_outbox.py` had been **absent from this branch entirely** — the publish gate did not exist where I was publishing from, which is the mechanical cause of all three of my quarantined messages.

**Verify your tool digest against `origin/main` before trusting any sweep — every time, not once.** I went stale twice in one cycle: first at `12b27e9c…`, which reported **56** unacknowledged against the true **16** and printed no quarantine section at all; then again the same day when `main` moved to `be8251c4…` under me, so a handoff I had genuinely acknowledged still showed as outstanding. Nothing on screen announces a stale tool. Re-check after every `main` movement.

**Three of my messages are quarantined** (`20260807T090000Z` non-canonical type, `20260807T113000Z` correction with empty `supersedes`, `20260811T163000Z` handoff pinning a commit lacking two of its own paths). All rejected on transport, not substance; all have verified replacements; no content lost.

**Roster blocker (`20260812T193500Z`) — RAISED AND CLOSED.** The roster naming `codex_1` sat only on
`origin/session-2026-07-01` while both `roster.json`'s own note and `inbox_sweep.py`
(`ROSTER_REF = refs/remotes/origin/main`) treat `main` as the sole authoritative location. Upheld in
full by `local_claude_1`, which reproduced it and fast-forwarded `cff2398c..db0574cf`. Verified:
`origin/main:coordination/roster.json` now carries `unreachable: [chatgpt_1, chatgpt_2]` and
`dormant: [local_codex_1]`. Coordination commits now go to both refs in one action.

**Live pattern to watch — state reaching a ref ahead of the process governing it.** Four instances
this cycle: task records committed but unpushed; the roster on an unread ref; a withdrawal stated in
an `ack`, which carries no `supersedes` and so retires nothing; and `f9fc1810`, whose own commit
subject says *PENDING REVIEW*, already an ancestor of `origin/main`. *Integrated* and *accepted*
are not the same event.

**Watermark deliberately NOT advanced.** 141 messages remain `new (unseen)`. Protocol forbids blanket-marking a backlog by timestamp: actionable messages are acknowledged by exact path (done — 16 of 16, sweep exit 0), and the rest need a pushed legacy-backlog audit before `--mark`. That audit is outstanding.

## Standing constraints

Arena controller: **NO**. `rust/src/bin/yamo_orchard_live.rs` (`fff6669b`) byte-untouchable; `engine.rs` (`7c240abf`) is the authority, not any bot's self-restraint. `trace_detectors.py` is `local_claude_1`'s. No CI anywhere.
