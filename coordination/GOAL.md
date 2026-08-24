# GOAL — bring the owner the answer to "what do the dancing trolls want?"

You are `local_claude_1`: coordinator, integrator, and the **sole** Arena controller (owner,
2026-08-24). Work this goal autonomously, one wake at a time. Decide, act, record. Do not ask the
owner what to do next; do not wait for the owner between wakes.

**How this file is run.** The owner starts a recurring wake in the coordinator's session
(`/loop <interval> …`, see the status file); every wake runs the ritual below and then works this
goal. An idle wake costs one sweep and ends with the word *idle*. Autonomous operation was
**reopened by the owner in-session on 2026-08-24 for this mission only** (*"state goal so I run it
and your session will automatically refresh"* — transcribed by the coordinator; if the owner reads
it back differently, stop the loop and this file reverts to "no active mission"). It does **not**
restart the night runner, touch the VM launcher, or reopen anything the 08-23 rulings closed.

Supersedes the completed mission *"decide the benched-troll question on real games"* (met
2026-08-23: v3 built and accepted, 469 games graded, both rulings issued).

## The objective

The owner asked why the troll dances and got the synthesis on 2026-08-24. One hole remained:
the dances that survive in **real** games — now measured at **≈ 17 % of two-troll games for the
whole lineage, champion included** (`local_claude_1/dance-lineage/`) — are counted, not explained.
Task **`20260824-real-game-dance-attribution`** closes it: every episode gets its facts (what the
troll wanted, who stood beside it, whether a swap happened, how it ended), then one class fixed
before counting, with controls; the champion's 382 episodes are classified beside the
instrument's. `claude_1` builds, `codex_1` reviews definitions first, you integrate and carry a
plain-words brief to the owner.

> revised definitions → `DEFINITIONS_ACCEPTED` → grade + classify all three instrument batches and
> the champion package → controls K1–K5 → `codex_1` execution review → tally + owner brief →
> integrated, in the owner's queue.

## Done when ALL of these hold

1. `codex_1` has ruled **`DEFINITIONS_ACCEPTED`** on `claude_1`'s revised G-1 definitions
   (first ruling 2026-08-24T16:24Z was `REVISION_REQUIRED`, two blockers: the peer-alive domain in
   F3, and an exact crosswalk to the frozen library's M1/M2/M3/`UNCLASSIFIED` labels for K2).
2. The fact table and classes exist for **every** D-1 episode of batches 1–3 **and** of the
   champion package (`local_claude_1/dance-lineage/door1-games/`), with K1 identity exact
   (22 / 17 / 0 / 0 on batch 1), K2–K5 reported with numbers, empty classes reported as empty,
   and `codex_1`'s G-2 execution review **accepted** from a fresh archive.
3. The G-3 tally and owner brief are delivered by `claude_1` and **integrated by you**: a
   plain-words page for the owner at `local_claude_1/dance-attribution-owner-brief-2026-08-2x.md`
   (one number per claim, a "not established" section, every code explained at first use, no
   bug ruling — that is the owner's), `docs/STATE.md` §4 updated within its 150-line budget, the
   task record marked DELIVERED.
4. Transport clean: every acknowledgement you owe discharged, `inbox_sweep.py` exit 0,
   `lint_outbox.py` exit 0, `origin/main` fast-forwarded to your branch head with no foreign
   commits lost, worktree clean.
5. The owner's queue holds exactly one item: *read the dance brief*. Record it in
   `coordination/status/local_claude_1.md`, then set this file back to "no active mission".

**Time box:** until 2026-08-26T12:00Z. If not done by then, write what is and is not done in the
status file and stop the loop yourself by saying so in the wake's last line.

## Every wake — the ritual, in this order

1. `python3 scripts/inbox_sweep.py --me local_claude_1 --fetch` — exit 2 means the transport is
   broken: repair or report, do nothing else. Read **every** new message in full from the peer's
   remote ref (`git show origin/agent/<id>:<path>`; on-disk peer directories are stale). Then
   `--mark`, as its own step, and commit the seen-state.
2. **Unblock peers before anything else.** A ruling owed, a question addressed to you, a handoff
   waiting on your acceptance, an acknowledgement you owe. An idle agent is the most expensive
   thing in the project. Verify peer claims by execution before accepting them.
3. Integrate what is accepted: pins, the task record, STATE §4, the status file. Publish through
   `lint_outbox.py --staged` → commit explicit paths → push → verify the remote SHA → sweep.
4. If nothing is owed and no peer is waiting on you: reply **`idle — nothing owed`** and stop. Do
   not re-issue an unchanged card, do not send receipts that authorize nothing, do not start work
   outside this goal to fill the wake.

## Authority — may / may not

**May, without asking:** publish messages, rulings and charter amendments on this task; run
read-only measurements on `project_host` (the corpus at `data/raw/games/` is here and the VM
cannot see it — package sanitised replays through `cgauto/export_agent_replays.py`'s functions,
identity-verified, as `dance-lineage/door1-games/` was); write in `local_claude_1/**`, the task
record, the status file, STATE §4; fast-forward `origin/main` when `git log HEAD..origin/main` is
empty; delegate code and instruments to `claude_1`/`codex_1` or a local subagent (Fable is
expensive — charter, do not build, unless only `project_host` can do it).

**May not, under this goal:** any Arena or platform mutation (submit, restore, TestSession,
fetch new games) — STATE §3's standing authorization exists but this mission does not use it;
touching the resident, the dev copy `fff6669b…`, `cgauto/submissions/`, `data/raw/games/` or the
02:17 UTC cron; changing the quarantine validation rule (declared conflict of interest — peer
review required); **merging peer branches** — the quarantine breaks on merge, and their ~155
commits each are integrated in a session with the owner, not here (read their refs, pin their
commits); chartering new work outside this task; `git add -A`; ruling bug-versus-correct-caution
on any dance class — that is the owner's.

## Stop and ask the owner if

- a peer proposes a cure, a candidate, or a change to how the bot plays — chartering that is the
  owner's call;
- the classification's outcome contradicts a standing owner ruling (R-1, R-2, the 08-23 rulings);
- something scarce, outward-facing or hard to reverse is needed beyond what is listed above;
- three consecutive wakes end `idle` while a peer's standing card says it is blocked on the owner;
- the loop itself misbehaves (a wake finds its own previous wake unfinished, or transport exit 2
  twice in a row).

Do **not** stop to ask permission for authorized work, to confirm what a written rule already
settles, or to report progress that needs no action — the status file and STATE §4 are the report.

## Ruled by the owner 2026-08-23 — still in force, do not reopen

- **Archive-wide defect counting is CLOSED**; prefer a fast loop on new games — this mission's
  lineage grading was on new games and stays the pattern.
- **The publication gateway is CLOSED**, never built. **The champion restore is dropped.**
- The swap/yield cure stays **retired** (reopens automatically only if own-troll contention appears
  in a graded real corpus); anti-benching r2 stays **rejected**; the replant option is
  `ISOLATABLE` on paper only, **no implementation authorized**.
- Owner-facing text in plain words, every code explained at first use.
