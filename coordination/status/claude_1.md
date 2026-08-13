# claude_1 Status

- Updated UTC: 2026-08-12T20:52:00Z (REAL clock, `date -u` — see the stamp-drift correction below)
- State: **inbox clean, sweep exit 0, 0 unacknowledged, 0 delivery errors.** Three `policy` messages processed this cycle: the two quarantine adjudications (`20260812T193500Z` superseded by `20260812T193800Z`) and the **bounded arena lease `20260812T201400Z`, ACCEPTED and not yet started**. Acks at `5c753f9f`, `26afe667`, `85045fed`.
- **ARENA LEASE COMPLETE 2026-08-13T06:43Z — all five steps delivered, authority reverted to `local_claude_1`.** Final handoff `20260813T064318Z`, artifact `a890dfa9`, published `cdbc5800`. **Pooled within-source SD = 1.501** score points, 95% CI [1.049, 2.634], 4 families / 14 mature observations / 10 d.o.f. — up 37% from 1.098, and the CI's lower bound now sits *above* the old point estimate. Campaign family n=6: [19.77, 22.46, 23.39, 23.73, 24.76, 24.90], range 5.13 (2–3× every other family). **`docs/STATE.md` §3's ±0.5–1.0 band does not survive**; a ≥+1.0 gate needs 5 runs per arm, not 3. Run 4 = `41129543` / agent `6614096`, owner-authorized in session. **Re-deployment noise and ladder drift are confounded and no analysis of these six observations separates them** — the runs are sequential, never contemporaneous, spanning 08-04→08-13 while the field grew 139→147.
- **The stale arena-room row is the story of this campaign.** `6604529 / field 140 / 22.46` appeared **six times** across two days, including on three consecutive *complete* 160/160 reads of run 4. **A gate on `matching_finished == 160` alone would have recorded 22.46 — another deployment's score — as run 4's terminal observation, with 0 pending, 0 unexpected rows and 0 fetch failures.** Gate on `identity_clean` AND the process exit status; `field total 140` is the reliable tell. Related repair `a9abae5f`: `submission_history.py` validated `filtered_ladder.agent_id` but never `arena.agent_id`, then read score/rank/field from that unchecked block — silent corruption with `identity_faults: 0` and maturity `terminal`. Two tests, both verified to fail first. `codex_1` reviews; I authored it.
- **Read the label, then read the content — the content wins.** I escalated a semantics question about run 2 that did not need to exist: `run2-checkpoint-initial.json` was a complete 160/160 clean terminal observation (23.73) sitting in the same directory the whole time. I had filtered on the `*-terminal` filename role and never opened it. Maturity is keyed on `matching_finished`/`matching_pending`/`identity_clean`, never on a role string.
- **`publish_outbox.sh` fetched only `origin/$BRANCH` until 2026-08-13** — so publishing could never surface inbound mail, and a policy addressed to me sat unread for 8h28m while I executed the task it governed. Fixed on trunk (`git fetch origin`, all refs), synced here at `5596941d`. **Binding: any Arena mutation requires a full `--fetch` sweep with its exit examined within ~10 minutes of the call.** Publishing is not freshness.
- (Superseded) **ARENA LEASE HELD (bounded, reverts on final handoff)**: σ campaign steps 1–5, serialized. Preconditions verified independently — cookie sha `09164093…` mode 600, gitignored + untracked; submission blob = `98628e98…` in three-way agreement with the `--expected-sha256` and the committed sidecar; run-3 interim is the 118-game read (arena 23.61, filtered 23.73, rank 31/147). **Step 2 (run-4 submit, the fourth and LAST budgeted mutation) is held for an explicit owner go** — irreversible, single call, ambiguity → STOP with no retry. Execution-environment gap named to the coordinator: the cookie is in the ~1300-commit-stale `/home/tarstars/prj/troll_farm`, the tooling is at `f7069d16`, and `troll_farm-plan` is detached at `21bd338d`.
- **`scripts/publish_outbox.sh` — the wrapper the coordinator calls binding — was ABSENT from `agent/claude_1`.** `scripts/` was stale against `main` by nine files; synced at `7ec39b4c`, and every message this cycle published through the wrapper with the lint armed. Second silent drift of this directory while the publish gate was defined as one of its scripts. **Verify the gate exists before trusting it; nothing on screen announces its absence.**
- **`requires_ack: false` does not exempt a `policy` message.** `policy` is in `ACK_REQUIRED_KINDS` (`scripts/inbox_sweep.py:78`) and the set is applied after the field (`:289`), so both adjudications declared `requires_ack: false` and both were correctly reported ack-required. Raised with the coordinator; needs a ruling.
- **250 messages remain `new (unseen)` and the watermark was deliberately NOT advanced** — protocol forbids blanket timestamp-marking a backlog before a pushed legacy-backlog audit. That audit remains the outstanding transport work.
- **Filename stamps ≠ real time.** Messages named `20260813T*` have real commit dates of 08-09; the M3a repair, the transport review and bite-test r2 are all ancestors of the current tip despite later-looking names. Trust `git log`, never the filename.
- (Prior cycle) **G2 delivered and accepted** (substance ACCEPTED by `codex_1`; the `task_id` provenance revision is published at `6fbacca4` and awaits the coordinator's integration, at which point G2 closes). **G6 started: all four D-7 branches pinned, 4 of 19.** Collector-v2 tasks both in `review`, all findings ACCEPTED.
- **G6 state (2026-08-13, D-8 group done, artifact `bb43f9ff`, progress `cee125d4`)**: mutation **33 caught / 31 survived of 64**, `caught_by_expected` **33/33**, control green; ledger `impl_validity` **20 PINNED, 4 PARTIAL, 8 UNPINNED, 15 NO_FIXTURE** (was 16/5/8/18). **8 of 19.** Remaining: D-5 ×3, D-6 ×3, D-1 ×2, D-4 ×2, D-3 ×1 — heaviest first, D-5 and D-6 next. D-9 (b)/(c)/(d) parked for the **c5 instrument ruling, assigned to me after G6**.
  - **D-8 (b) `plant kind == BANANA` is an EQUIVALENT MUTANT — D8-M8 can never be killed.** `detect_d8` reaches that guard only inside `c in alive_per_turn[t]`, and `own_banana_history` builds that set from the *same* `state(t)` filtering `kind == "BANANA"`, so the guard is true whenever evaluated. Proven by construction (a DIAG banana turning to WOOD leaves the alive set the same turn) and by differential (**0 of 416 probe-corpus traces differ**). **Left counted in the totals and the row left at `NO_FIXTURE` on purpose** — excluding it would improve my own kill rate, so the disposition is referred to the coordinator, not taken by me.
  - Discipline that paid: my first D-8 (f) fixture sat on a tie and so killed two mutants at once — one boundary carrying two claims. Rebuilt at a 2-turn margin so each branch stands on its own. D8-M7 was an unplanned catch; `owner_test_classes` extended and reported rather than left as an unexplained gap.
- **Owner plain-language policy in force (`20260813T191500Z`, acked `4b011941`)**: anything the owner reads opens with a sentence a non-specialist can follow, spells out what a thing IS before its code name, and gives numbers meaning. Technical artifacts keep full precision; the plain summary goes in the message that carries them.
- **THREE OF MY OWN GUARDS FAILED TODAY — read before publishing anything.** (1) **Message stamps ran up to +42 min ahead** of the clock because I incremented them by narrative instead of reading `date -u`; my drift put a coordinator reply *before* the message it answered. (2) **I published an invalid `correction` with an empty `supersedes`** — the identical defect that quarantined `20260807T113000Z`. (3) **I broke the publish gate**: `lint …; echo "LINT=$?"; git add … && commit && push` chains off `echo`, which always succeeds, so the gate ran and gated nothing. Worse, once pushed the message becomes *published* and default lint **skips it** — exit 0, defect invisible. Use `lint … || exit 1`, and `--all` after publishing. Retiring a message also **retires every ack it discharged**: carry `ack_for` forward when superseding.
- **`project_host`'s cron fires 02:17 UTC, not 05:17** (crontab `17 5` on Europe/Moscow) and skipped Aug 11-12. My unit comment and reports are corrected: 05:47 is right, but by luck not by the stated reasoning.
- **First unattended collector run** (2026-08-12 05:47): 6,295 candidates, 6,295 held, **0 fetched, 0 dropped**, exit 0 — verified as coverage not blindness (max held id `898583715` > max live-window id `898550181`). **Cut-over caution: with the platform quiet AND the reference cron intermittent, the seven-day criterion measures neither collector.**
- **Three measured facts to carry:** replay availability tracks participant battle windows, not age; the bucket grant blocks deletion but NOT overwriting (append-only is enforced by `If-None-Match: *` in our code); *missing from a day's manifests* (352) is a different question from *absent from S3* (**0**).
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
