# Multi-agent coordination protocol — Troll Farm

Adapted 2026-07-29 from `/home/tarstars/prj/icfpc2026/docs/two-agent-protocol.md`
(introduced there 2026-07-25). The topology, four-artifact scheme, lease/takeover rule,
path-ownership model, and message grammar are carried over unchanged in substance; the
contest-submission section is replaced by this project's Arena rules, and the
project-specific hazards in §7 are new.

There is no daemon, bus, or lock manager. The protocol is Markdown files at agreed paths,
with Git as transport and durability.

## 1. Topology and roles

Two writing agents must never share a Git worktree: one working tree, one branch, one
index — path ownership alone cannot make simultaneous staging and commits safe.

- one worktree and `agent/<id>` branch per writing agent;
- one designated **integrator**, who alone updates the session branch
  (currently `session-2026-07-01`; this project has no active `main` workflow);
- one designated **arena controller**, normally the integrator, who alone performs
  platform-side mutations (see §6).

Current roster: **`claude_1`** — integrator and arena controller by default, being the
only agent present. Roles are defaults, not capability limits; a task record says who owns
that particular outcome, and the user may reassign at any time.

Agent ids are lowercase `[a-z0-9_]+`. A newcomer claims an unused id, creates its own
status file and message directory, and follows these rules; no spec change is needed.

## 2. Units of work — task records

Task ids: `YYYYMMDD-<area>-<short-outcome>` (e.g. `20260729-d176-mining-window-audit`).
One file per task at `coordination/tasks/<task-id>.md`, from `templates/task.md`, owned by
its record owner. The assignee acknowledges by message, never by editing the record.

Do not start implementation until ownership and the write set are explicit. If two
proposed tasks need the same file, split the ownership, serialize the tasks, or give both
changes to one owner.

Experiment work has a second, stricter layer that predates this protocol and outranks it:
a frozen experiment protocol under `data/analysis/live-agent-6553250/dNNN*-protocol-*.md`
plus its lock. A coordination task record schedules the work; the frozen protocol governs
what may be changed and what the gates are. Where they disagree, the frozen protocol wins.

## 3. Path ownership

- During an active task only its owner edits its exclusive write set.
- The **integrator** owns these shared hotspots unless a task transfers one explicitly:
  `AGENTS.md`, `docs/STATE.md`, `docs/CONSTRAINTS.md`, `docs/BACKLOG.md`,
  `docs/RUNBOOK.md`, `docs/storage-policy.md`, the ledger volumes under
  `data/analysis/live-agent-6553250/legend-top3-experiment-cycle-*.md`,
  `cgauto/api_submit.py`, `cgauto/submissions/`, `rust/Cargo.toml`, `.gitignore`,
  and this `coordination/` tree outside your own namespaces.
- Agent-private bookkeeping stays private: `claude_1/` belongs to `claude_1`; no agent
  rewrites another's area, status file, or message directory — not even to acknowledge.
  Acknowledgements are written from the acknowledging agent's own namespace.
- Frozen artifacts are immutable: experiment protocols, locks, result documents, digest
  manifests, and `cgauto/submissions/*`. A new attempt is a new file, never an overwrite.
- Merge name collisions: keep the target branch's filename, rename the incoming one with a
  `tarstars_` prefix.

## 4. Synchronization artifacts

**Task records** — §2, `templates/task.md`.

**Agent status** — `coordination/status/<agent-id>.md`, a replaceable snapshot owned only
by that agent, from `templates/status.md`. Update when accepting or releasing a task,
before a long-running job, after the first reproducible result, when the write set or plan
changes, when blocked, when a handoff is ready, and after integration. Status is a
convenience snapshot; messages and commits are the durable history.

**Immutable messages** — each sender owns `coordination/messages/<sender>/`. Filename:

```text
YYYYMMDDTHHMMSSZ-<task-id>-<kind>.md
```

Kinds: `claim`, `progress`, `question`, `blocker`, `policy`, `stop`, `takeover`,
`handoff`, `ack`, `release`, `integrated`. Messages are immutable once published; a
correction is a new message naming the superseded file. All kinds except `progress`,
`ack`, `release` and `integrated` require an `ack` from the recipient's own namespace.

**Handoffs** — a message using `templates/handoff.md`. A statement such as "done" without
an inspectable commit and validation evidence is not a handoff.

**Goals** — `coordination/goals/*.md`, integrator-owned: a time-boxed autonomous mission
brief the user activates by naming the file. Self-contained: it restates the liveness and
stop rules inline, lists explicit may/may-not authority, and states its end condition. The
window begins when the receiving agent accepts, not when the file was committed. Goal
files never authorize Arena writes.

## 5. Cadence and liveness

Event-triggered, not polled: **claim** before implementation → **progress** at the first
reproducible result or material design decision → **blocker/question** immediately if work
would otherwise diverge or stall → **handoff** after validation and push → **ack** before
the reviewer or integrator proceeds → **integrated/release**.

An active task has a **15-minute progress lease**. Concrete progress is new inspectable
evidence: a commit or diff, a test or experiment result, a narrowed failure, or a
previously announced long-running command with traceable output. Repeating an intention or
touching a timestamp does not renew the lease.

*Project adaptation:* experiments here routinely run for hours. A long-running experiment
renews its lease through **phase markers** — `.superpowers/sdd/<exp>-phase-markers.md`
entries, or equivalent appended progress lines — which are exactly the "announced
long-running command with traceable output" the rule contemplates. Announce the job before
starting it and write markers as phases complete; a silent multi-hour run is a lease
breach even if work is happening.

If an agent produces no concrete progress for 15 minutes, the integrator may instruct it
to stop and may reassign or take over without further user approval. Takeover procedure:
inspect the peer's status, messages, branch and announced job; publish a `stop` or
`takeover` message naming the last observed evidence; **never** clean or rewrite the
stopped agent's worktree or commits; record the new owner and write set; continue on a
separate branch or a new artifact version so late work cannot silently overwrite the
takeover. The stopped agent ceases promptly, checkpoints if possible, acks, releases, and
does not resume without reassignment. Direct user chat may duplicate an urgent
notification, but the repository message is authoritative.

## 6. Arena authority (replaces the source protocol's contest-submission section)

Read-only platform work (leaderboard reads, replay collection) may be delegated to any
agent under the existing authorization rules in `docs/STATE.md` §3. **Mutations — any
submission, TestSession game, or anything that changes our ladder standing — are
serialized through the single arena controller and require explicit user authorization for
the exact candidate**, per `docs/PROMOTION-RUNBOOK.md` and backlog item B4.1.

No agent submits merely because a candidate qualifies. Before any submission: confirm the
exact artifact and its SHA-256, confirm only one controller is active, take the pre-trial
baseline read, and preserve the returned submission id and terminal response. Never
automatically retry an ambiguous submission. Announce to all agents when a submission
starts and again when it terminates. The no-churn rule stands: a failed trial costs days
of standing.

## 7. Project-specific hazards (new; violating these breaks other agents' work)

- **The resident dev copy is byte-sacred.** `rust/src/bin/yamo_orchard_live.rs` must stay
  at SHA-256 prefix `fff6669b`; it is library-visible as `troll_farm::resident_policy`, so
  *any* working-tree diff silently contaminates every concurrently running experiment.
  Experiments that must modify it use the compile-then-restore flow: apply the fix, build
  the panel binary, restore byte-exact immediately, verify the SHA, and preserve the change
  as a patch under `data/analysis/live-agent-6553250/`.
- **Experiment locks record file hashes.** Never run `cargo fmt`, a formatter, or an
  editor's format-on-save across `rust/src/bin/` or `cgauto/`: a semantically-null
  reformat breaks hash verification for every lock that references the file. This has
  already happened once (2026-07-29, 11 files, reverted).
- **Sealed data.** Maps `9,844,200–9,844,215`, the official-map holdout, the 11 sealed
  confirmation games, and any range a frozen protocol reserves must not be read or opened
  by any agent without that protocol authorizing it.
- **The collection cron** runs daily at 05:17 and writes to `data/raw/games/`. Do not
  symlink, move, or lock that directory; do not leave the USB volume required for a run
  that touches it.
- **Bulk writes** require `python3 cgauto/check_external_storage.py --required-free-gib N`
  first; never replace a missing external symlink with a real directory.

## 8. Conflict and failure rules

**Never stage another worker's files.** With concurrent work in the same tree, `git add
-A`/`-u` is forbidden — name explicit paths. (Violated 2026-07-29: an integrator `add -A`
swept a running audit's in-progress script into an unrelated commit; content survived but
the provenance is wrong in history.)

Overlapping claims → integrator picks one owner. Unexpected peer edits inside your write
set → stop, publish a `blocker`, let the integrator reconcile. A dirty shared worktree →
do not operate on it; split into separate worktrees. Stale progress → the §5 procedure.
Failed experiment → preserve the evidence, release the task, never hide a negative result
(this project's ledger is built from negative results). Platform ambiguity → freeze new
mutations until reconciled. Secret exposure → stop, notify the user, never re-propagate.

## 9. Definition of done

Deliverables exist at recorded paths; acceptance checks and their exact commands are
recorded; local, projected and live measurements are distinguished; hashes are preserved;
the handoff commit is pushed **and acknowledged**; integration is completed or explicitly
deferred; claims and status are released; any external mutation has a recorded terminal
result. For experiments, additionally: a ledger entry, a `docs/CONSTRAINTS.md` bullet for
anything closed, and a `docs/STATE.md` update.

The user remains the authority for priorities, role changes, and Arena authorization.

## 10. Transport

Canonical transport is Git refs: publish by committing to your `agent/<id>` branch and
pushing to `origin`; receive with `git fetch origin` and read peer refs, since a message
may exist only on its sender's branch.

The remote transport went live on 2026-07-29 (`session-2026-07-01` pushed through
`2ebb5c6`): remote agents can clone, branch as `agent/<id>`, and their messages become
fetchable. `scripts/inbox_sweep.py --fetch` sweeps remote refs, local refs, and the
working tree alike. Note that a message existing only on its sender's unpushed branch is
invisible to peers — pushing is part of sending.
