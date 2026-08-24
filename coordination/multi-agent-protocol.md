# Multi-agent coordination protocol — Troll Farm

Adapted 2026-07-29 from `/home/tarstars/prj/icfpc2026/docs/two-agent-protocol.md`
(introduced there 2026-07-25). The topology, four-artifact scheme, lease/takeover rule,
path-ownership model, and message grammar are carried over unchanged in substance; the
contest-submission section is replaced by this project's Arena rules, and the
project-specific hazards in §7 are new.

There is no daemon, bus, or lock manager. The protocol is Markdown files at agreed paths,
with Git as transport and durability.

> **Transport invariant — unpushed means unsent.** A working-tree file, local commit,
> terminal output, or statement in chat is invisible to the other agents and has **no
> coordination effect**. A claim, progress update, blocker, handoff, acknowledgement,
> release, integration notice, or status change becomes real only after the commit
> containing it is pushed to `origin` and its remote SHA is fetchable. Never tell the user
> or another agent that repository communication was sent, published, pushed, or completed
> until that remote verification succeeds.

## 1. Topology and roles

Two writing agents must never share a Git worktree: one working tree, one branch, one
index — path ownership alone cannot make simultaneous staging and commits safe.

- one worktree and `agent/<id>` branch per writing agent;
- one designated **integrator**, who alone updates the integrated branch — **`main`**
  (corrected 2026-08-21: this line said `session-2026-07-01` and "no active `main`
  workflow" long after both stopped being true. `main` is the shared root of trust that
  `coordination/roster.json` and the frozen legacy baseline are read from, and
  `night_runner` fast-forwards it on every publish — `cgauto/night_runner.py:169`.
  `session-2026-07-01` has not moved since 2026-08-17);
- one designated **arena controller**, normally the integrator, who alone performs
  platform-side mutations (see §6).

**The roster of record is `coordination/roster.json` on `origin/main`, not this
paragraph.** §10.2 reads the coordinator from there, and a second list that drifts is
worse than no list. As of the owner transfer on 2026-08-24 it says:
**`local_claude_1`** — coordinator (integrator) and sole Arena controller;
**`claude_1`** — active contributor; **`codex_1`** — active contributor and standing
reviewer (a separate agent from `local_codex_1`); **`local_codex_1`** — contributor with
no integration or Arena authority; **`chatgpt_1`** — reachable reviewer through its
interactive session; **`chatgpt_2`** — unreachable. Historical messages and quarantines
remain authoritative. Current transfer brief:
`coordination/HANDOVER-2026-08-24-local_codex_1-to-local_claude_1.md`. Roles are defaults,
not capability limits; a task record says who owns a particular outcome, and the user may
reassign at any time.

Agent ids are lowercase `[a-z0-9_]+`. A newcomer claims an unused id, creates its own
status file and message directory, and follows these rules; no spec change is needed.
Onboarding brief: `coordination/peer-prompt.md`.

**A newcomer is not reachable until it has published the SHA-256 of the
`scripts/inbox_sweep.py` and `scripts/lint_outbox.py` it actually runs, matching `origin/main`.**
Self-onboarding is otherwise unsupervised, and it has already failed once: an agent ran an older
inbox tool that could not parse v2 front matter, saw **zero** messages for ten days, and reported
having no work — while the coordinator asserted the problem was fixed because that agent was
replying. Treat a reply as evidence of nothing. The digest is the evidence.

## 2. Units of work — task records

Task ids: `YYYYMMDD-<area>-<short-outcome>` (e.g. `20260729-d176-mining-window-audit`).
One file per task at `coordination/tasks/<task-id>.md`, from `templates/task.md`, owned by
its record owner. The assignee acknowledges by message, never by editing the record.

A task assignment or claim is effective only when the task record and/or claim message is
committed and pushed to a remote ref. A local file or local commit does not reserve work;
other agents cannot be expected to respect ownership they cannot fetch.

Do not start implementation until ownership and the write set are explicit **and remotely
published**. If two proposed tasks need the same file, split the ownership, serialize the
tasks, or give both changes to one owner.

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

**Task records** — §2, `templates/task.md`. A task record that exists only locally is not a
scheduled task.

**Agent status** — `coordination/status/<agent-id>.md`, a replaceable snapshot owned only
by that agent, from `templates/status.md`. Update when accepting or releasing a task,
before a long-running job, after the first reproducible result, when the write set or plan
changes, when blocked, when a handoff is ready, and after integration. Status is a
convenience snapshot; messages and commits are the durable history. A status update is not
visible or current for peers until its commit is pushed.

**Immutable messages** — each sender owns `coordination/messages/<sender>/`. Filename:

```text
YYYYMMDDTHHMMSSZ-<task-id>-<kind>.md
```

Kinds: `claim`, `progress`, `update`, `question`, `blocker`, `policy`, `stop`,
`takeover`, `handoff`, `ack`, `release`, `integrated`, `correction`. The enforced set is
`V2_KNOWN_KINDS` in `scripts/inbox_sweep.py`; `update` was in daily use and missing from
this list until 2026-08-21. Messages are immutable once
published; here **published means committed and pushed to `origin`**. A correction is a
new pushed `correction` message at a new immutable path whose `supersedes` array names the
exact superseded message path; the superseded message stays immutable and visible. Moving
or copying an old message between refs is not a new coordination event. All kinds except
`progress`, `update`, `ack`, `release` and `integrated` require an `ack` from the
recipient's own namespace (`correction` requires acknowledgement by default).

**The ack obligation falls on `to` recipients only** (ruling 2026-08-20, implemented as
`ack_obliged_to_me`; recorded here 2026-08-21, having lived only in a code docstring). A
`cc` recipient may acknowledge as a courtesy but never owes one, and on a `CARD:` or
`DEFERRED:` message a bystander's ack is actively forbidden — it would discharge another
agent's queue anchor. Address the parties who must act in `to`; everyone else is `cc`.

**Transport schema v2** (mandatory for newly created messages once announced; task
`20260805-coordination-transport-hardening`). Every new message starts with YAML front
matter declaring `schema_version: 2`; list fields are single-line JSON arrays parsed with
`json.loads` (no PyYAML):

```yaml
---
schema_version: 2
type: handoff
task_id: 20260805-example
from: claude_1
to: local_codex_1
cc: ["user"]
message_id: coordination/messages/claude_1/20260805T100000Z-20260805-example-handoff.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-05T10:00:00Z
---
```

`message_id` must equal the repository-relative path at which the body is read, and `from`
must equal the sender namespace in that path. `ack_for` and `supersedes` hold exact
repository-relative immutable message paths — never task ids or timestamps. A v2 `ack` has
a non-empty `ack_for` and covers exactly the listed paths, nothing else; an ACK may itself
set `requires_ack: true`, in which case the response targets that ACK's exact path.
Filename timestamps are human-readable ordering hints only.

## Owner-facing wording policy (owner directive, 2026-08-13)

Any text the owner is expected to read — messages with `user` in `to:`/`cc:`, session
summaries, reports, backlog/state presentations — follows these rules:

1. **Plain language.** Short sentences. Say what a thing IS before what it is called.
2. **No unexplained codes.** Every project abbreviation or codename (G6, H3a, D-9, σ,
   CBF, …) gets a plain-language explanation at first use: *"the watchdog-test job
   (G6)"*, *"the score-wobble number (σ, 'sigma')"*. A code the reader must look up is
   a defect, not shorthand.
3. **Numbers carry their meaning.** Not "σ = 1.501" alone, but "scores wobble by about
   ±1.5 points — one test run proves nothing."
4. **Describe, then name.** Prefer "the rule that no banana tricks happen before the
   second troll is trained" over "the D-9(a) constraint."
5. Inter-agent technical artifacts (task records, evidence files, code) keep full
   precision and exact identifiers — this policy governs the owner-facing layer, not
   the lab notebook. When one message serves both audiences, the owner-facing summary
   comes first, the technical detail after.

**Ack requirement is kind-based first, field-based second (ruled 2026-08-12, coordinator,
after claude_1's finding):** the sweep's `ACK_REQUIRED_KINDS` (e.g. `policy`, `handoff`)
makes those kinds ack-required regardless of front matter — `requires_ack: false` on a
`policy` is inert and misleading; do not write it expecting an exemption. `requires_ack:
true` can only ADD an obligation to a kind that lacks one (e.g. a `progress`); it never
subtracts. Supersession does not discharge an ack, and retiring a message does not carry
its `ack_for` — re-issue discharges explicitly (both learned live, 2026-08-12).

A v2 `handoff` additionally carries `artifact_ref` (the sender's canonical branch,
`agent/<sender-id>`), `artifact_commit` (a full 40-hex object), and `artifact_paths` (a
single-line JSON array). **Canonical publication rule:** a v2 handoff is valid only when
`artifact_commit` is reachable from `refs/remotes/origin/<artifact_ref>`, every
`artifact_path` exists in that commit, and the handoff message itself is present on
canonical `refs/remotes/origin/agent/<sender-id>`. Publish artifacts first, then the
handoff message in a later commit on the same canonical branch. Remote task branches
remain inspectable evidence but cannot alone satisfy a v2 handoff.

Legacy messages (no `schema_version`, or < 2) remain readable indefinitely; the old
task-plus-timestamp ACK rule is fallback only for legacy messages and must never
acknowledge a v2 message. The 689 existing immutable message paths are never rewritten.

**Handoffs** — a message using `templates/handoff.md`. A statement such as "done" without
an inspectable commit and validation evidence is not a handoff. A handoff that has not been
pushed is not a handoff at all.

**Goals** — `coordination/goals/*.md`, integrator-owned: a time-boxed autonomous mission
brief the user activates by naming the file. Self-contained: it restates the liveness and
stop rules inline, lists explicit may/may-not authority, and states its end condition. The
window begins when the receiving agent accepts, not when the file was committed. Goal
files never authorize Arena writes by themselves — the standing authorization in `docs/STATE.md` §3 is the only source, and its conditions apply regardless of what a goal file says.

## 5. Cadence and liveness

Event-triggered, not polled: **claim (write → commit → push → verify)** before
implementation → **progress (commit → push → verify)** at the first reproducible result or
material design decision → **blocker/question (commit → push → verify)** immediately if
work would otherwise diverge or stall → **handoff** after validation and push → **ack**
after fetch and review → **integrated/release** after their commits are pushed.

The lifecycle label is not earned when a file is written or committed locally. It is earned
only when the corresponding remote commit is fetchable. Before telling the user that a task
is claimed, in progress, handed off, integrated, released, or done, verify the remote ref
and describe that exact repository state.

An active task has a **15-minute progress lease**. Concrete progress is new **remotely
inspectable** evidence: a pushed commit or fetchable diff, a pushed test or experiment
result, a narrowed failure recorded in a pushed message, or a previously announced
long-running command with traceable output whose phase marker has been pushed. Repeating an
intention, touching a timestamp, making a local commit, or leaving an unpushed phase marker
does not renew the lease.

*Project adaptation:* experiments here routinely run for hours. A long-running experiment
renews its lease through **phase markers** — `.superpowers/sdd/<exp>-phase-markers.md`
entries, or equivalent appended progress lines — which are exactly the "announced
long-running command with traceable output" the rule contemplates. Announce the job before
starting it, commit and push that announcement, and push markers as phases complete; a
silent or unpushed multi-hour run is a lease breach even if work is happening locally.

If an agent produces no remotely inspectable concrete progress for 15 minutes, the
integrator may instruct it to stop and may reassign or take over without further user
approval. Takeover procedure: fetch and inspect the peer's status, messages, branch and
announced job; publish a `stop` or `takeover` message naming the last observed remote
evidence; **never** clean or rewrite the stopped agent's worktree or commits; record the new
owner and write set; continue on a separate branch or a new artifact version so late work
cannot silently overwrite the takeover. The stopped agent ceases promptly, checkpoints if
possible, pushes the checkpoint, acks, releases, and does not resume without reassignment.
Direct user chat may duplicate an urgent notification, but it does not create repository
coordination state; the pushed repository message is authoritative.

### 5.1 Wake-driven operation (owner rule, 2026-08-21)

Since 2026-08-20 `claude_1` and `codex_1` are not sessions a human starts. They are woken
by `agent-launcher.service` (`scripts/agent_launcher.py`): every 180 s it fetches, computes
each agent's set with the agents' own sweep — never a second scanner — and launches only
when that set has GROWN. Guards: a 60-second debounce so one burst is one wake, one live
session per agent, a per-agent hourly cap, and `LAUNCHER-PAUSED` in the repo root which
stops all launches instantly. §5's event-triggered cadence above is what an agent does
once awake; this subsection is what may wake it.

**THE RULE (owner, 2026-08-21): an agent is woken only by mail from someone else.** The
**wake set** is exactly (a) messages it has not seen, sent by another agent, with this
agent in `to`; plus (b) ack-required obligations it owes to another agent. Three things
are excluded by construction, each because it caused a measured failure:

1. **Nothing an agent wrote itself may wake it.** Its own `DEFERRED:` cards remain in the
   queue as obligations — §10's "nothing owed to me AND nothing owed by me" is untouched —
   but an obligation is not news. An agent has read what it wrote.
2. **`cc`-only mail never wakes.** A cc recipient owes nothing (§4); waking it to read what
   it does not owe contradicts the same ruling. It reads the cc on its next real wake.
3. **A receipt that authorizes nothing never wakes** — an `ack` with `requires_ack: false`.
   A verdict, ruling or authorization CHANGES the recipient's queue and must therefore
   already carry `requires_ack: true` toward that party (the queue-changing rule below);
   published that way it wakes normally. Published as a bare receipt it waits for the next
   real wake, and receipt-for-a-receipt ping-pong terminates instead of sustaining itself.
4. **A `DEFERRED:` card wakes nobody — not even the peers it names in `to`.** Both live
   agents address their own cards to each other, and no peer can discharge another agent's
   card (§10: only a later message of the same agent naming it in `ack_for` does), so the
   obligation such a card appears to place on a peer is one the peer cannot act on. It
   stays fully visible as status. An assignment (`CARD:`) addressed to its assignee is a
   different shape and still wakes.

**The incident, measured 2026-08-21.** Between 12:39Z and 14:21Z `claude_1` woke eight
times and did the same nothing each time: read one peer receipt, re-measured a blocked
dependency byte-identically, and re-issued the same card. Every one of those wakes was
mail-triggered and therefore legal — **the mail was its own.** Three separately correct
rules composed into a loop: a blocked job must be a self-addressed ack-required card
(08-18); a card is discharged only by delivering it or by a replacement card (08-19);
self-addressed cards became visible to the sweep (repair `8c531096`, 08-21). So the
discharge of a card is another card, that card enters its author's own actionable set,
the set changed, and the launcher rang. While work is blocked that set has no fixed
point. The peer's courtesy acks were a second loop through `cc`. This is the
`docs/DISCOVERY-two-correct-doors-make-a-wall-2026-08-17.md` family: no rule here was
wrong and the composition was still a wall.

**One predicate, one code path.** The wake set is computed once, in
`inbox_sweep.actionable_set()`, and both consumers read it from there — the launcher and
`scripts/sentinel.py`, which shares the predicate by import. A sentinel that disagrees
with the sweep is worse than no sentinel.

**A standing card is left standing.** An agent must NOT re-issue an unchanged `DEFERRED:`
card merely because it woke. A card blocked on something outside the agent's control
carries a body line `UNBLOCK-SIGNAL:` naming the exact observable that must change (a
command and its exit status, a named written ruling), and is re-issued only when that
signal changes, when the work starts, or once per 24 h so the record shows it still owed.
This does not touch the owner's 08-18 law that **a deferral is a status, not a silence** —
the first deferral is still published the moment the decision is made. What is retired is
the re-declaration of an unchanged status.

**The 15-minute progress lease runs inside a session, not between wakes.** A wake-driven
agent that is asleep is not stalled and must not be taken over for it; its liveness is the
wake log plus its standing cards. The lease applies from the moment a session starts until
it ends, and to any agent that has announced a long-running job.

## 6. Arena authority (replaces the source protocol's contest-submission section)

Read-only platform work (leaderboard reads, replay collection) may be delegated to any
agent under the existing authorization rules in `docs/STATE.md` §3. **Mutations — any
submission, TestSession game, or anything that changes our ladder standing — are
serialized through the single arena controller**. Since
2026-07-30 the owner's per-candidate permission gate is **lifted** (standing authorization —
see `docs/STATE.md` §3), but the requirements it protected are not: a **QUALIFIED verdict
from a frozen protocol**, the full runbook, and owner notification before and after each
cycle. **The magnitude bar is GONE** — corrected 2026-08-21: this section went on
demanding "expected gain above the arena noise band" for nine days after the owner removed
exactly that bar (`docs/STATE.md` §3, recorded 2026-08-12 — the ladder is an information
channel and submissions are the cheap instrument). The correctness bar stands; the size
bar does not.

**`docs/PROMOTION-RUNBOOK.md` is not the runbook to follow as it stands.** Its
authorization gate is scoped to one retired candidate and its "fixed identities" name a
resident that has not been live for weeks, so its abort path would restore the wrong bot
(warning carried in `docs/STATE.md` §1). Use the restore target recorded there.

**No peer agent or subagent may submit** — serialization through the single controller,
currently `local_claude_1`, is the point. The controller may execute a block through a
**deterministic service it configures** (`night-runner.service`), which is not a peer
agent: it submits only the arms named in a pre-registered plan, verifies each file's
SHA-256 before the swap, never retries an ambiguous submission, and HALTs fail-closed on
any anomaly. What it computes at the end of a block is arithmetic; KEEP/REVERT is the
owner's, never the runner's.

No agent submits merely because a candidate qualifies. Before any submission: confirm the
exact artifact and its SHA-256, confirm only one controller is active, take the pre-trial
baseline read, and preserve the returned submission id and terminal response. Never
automatically retry an ambiguous submission. Announce to all agents when a submission
starts and again when it terminates. **No-churn, restated on measurement (2026-08-21):** a
failed trial no longer costs "days of standing" — a mature 160-game read takes about two
hours (`docs/STATE.md` §3) and the ladder has been swapped every two hours for several
nights without loss. What churn still costs is the **slot**: while a block runs, no other
candidate can be measured, so queue order is the scarce resource, not standing.

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
- **The collection cron** fires daily at **02:17 UTC** and writes to `data/raw/games/`.
  (Corrected 2026-08-21. Every document said 05:17 UTC, including this one: the crontab
  reads `17 5` and `project_host` runs Europe/Moscow, so the job fires three hours earlier
  than every runbook claimed — measured 2026-08-12, `coordination/coordd-shadow-runbook.md`.)
  Do not symlink, move, or lock that directory; do not leave the USB volume required for a
  run that touches it.
- **Bulk writes** require `python3 cgauto/check_external_storage.py --required-free-gib N`
  first; never replace a missing external symlink with a real directory.

## 8. Conflict and failure rules

**Never stage another worker's files.** With concurrent work in the same tree, `git add
-A`/`-u` is forbidden — name explicit paths. (Violated 2026-07-29: an integrator `add -A`
swept a running audit's in-progress script into an unrelated commit; content survived but
the provenance is wrong in history.)

Only **remotely visible** claims participate in conflict resolution. Overlapping pushed
claims → integrator picks one owner. An agent cannot complain that a peer violated an
ownership claim that never left its local branch. Unexpected peer edits inside your write
set → stop, publish and push a `blocker`, let the integrator reconcile. A dirty shared
worktree → do not operate on it; split into separate worktrees. Stale progress → the §5
procedure. Failed experiment → preserve and push the evidence, release the task, never hide
a negative result (this project's ledger is built from negative results). Platform
ambiguity → freeze new mutations until reconciled. Secret exposure → stop, notify the user,
never re-propagate.

## 9. Definition of done

Deliverables exist at recorded paths; acceptance checks and their exact commands are
recorded; local, projected and live measurements are distinguished; hashes are preserved;
the handoff commit is pushed **and acknowledged**; integration is completed or explicitly
deferred; claims and status are released; any external mutation has a recorded terminal
result. For experiments, additionally: a ledger entry, a `docs/CONSTRAINTS.md` bullet for
anything closed, and a `docs/STATE.md` update.

No unpushed file, local commit, local test result, chat statement, or local status update can
satisfy the definition of done.

The user remains the authority for priorities, role changes, and Arena authorization.

## 10. Transport — the golden rule: unpushed = unsent

Canonical transport is **remote Git refs**, not the working tree and not local Git history.
Coordination state has four distinct levels:

1. **working-tree edit** — private and invisible;
2. **local commit** — durable only for its author, still invisible to remote agents;
3. **pushed agent-branch commit** — published and available for claims, progress, review,
   handoff, acknowledgement, and takeover decisions;
4. **integrated session-branch commit** — canonical shared state.

Every coordination event must follow this order:

```text
write artifact → commit explicit paths → push agent branch → verify remote SHA is fetchable → announce
```

Skipping the push or verification means the event did not happen for coordination purposes.
If a push fails, the claim is not active, the progress lease is not renewed, the handoff is
not delivered, and the acknowledgement/release/integration is not published. Chat may warn
the user about the transport failure, but agents must continue to treat the last fetchable
remote state as truth.

Publish by committing to your `agent/<id>` branch and pushing to `origin`. Receive by
running `git fetch origin` (or `scripts/inbox_sweep.py --fetch`) and reading peer refs. A
receiver must fetch before concluding that a peer has not claimed, progressed, handed off,
or released a task. A sender must verify the remote commit before saying that it has sent,
pushed, published, or completed anything.

The remote transport went live on 2026-07-29 (`session-2026-07-01` pushed through
`2ebb5c6`): remote agents can clone, branch as `agent/<id>`, and their messages become
fetchable. Since the 2026-08-05 transport hardening, `scripts/inbox_sweep.py` counts
**only `refs/remotes/origin/**`** as authoritative for cross-agent delivery and
acknowledgement; local branches and the working tree appear only behind
`--include-local`, labeled diagnostic/unpublished, and never change counts or exit
status.

**Inbox sweep exit semantics:** exit 0 — healthy inbox, nothing unacknowledged; exit 1 —
healthy inbox with unacknowledged ack-required messages in the current selection; exit 2 —
transport/schema/delivery error (failed `--fetch` prints Git stderr and labels the inbox
`STALE / NOT AUTHORITATIVE`; an immutable path with different bytes on two remote refs is
an immutable-path collision; a malformed or incomplete addressed v2 message appears under
`delivery errors`; a malformed or unresolvable `coordination/quarantine.json` appears under
`quarantine errors` — see §10.2). Repeatable `--task <exact-task-id>` and
`--sender <exact-agent-id>` filters affect display and `--mark` only, never
parsing/validation.

**Seen state:** newness is exact-path membership in agent-owned
`<agent-id>/inbox-seen.json` (deterministic, atomically written by `--mark`), not a
timestamp watermark. Marking a message seen does not acknowledge it. On the first run
without a seen-state file, the legacy `<agent-id>/inbox-watermark.txt` is read once as a
migration hint (existing messages at or before it count as seen); the legacy file is never
rewritten or deleted.

### 10.0 Dual-format addressing is mandatory (2026-08-11)

**Every message must carry BOTH the v2 front matter AND a legacy block**, until every agent has
published the SHA-256 of the `scripts/inbox_sweep.py` it actually runs and it matches
`origin/main`:

```markdown
- To: <recipients>
- CC: <cc>
- Task: <task-id>
- Requires acknowledgement: yes
```

Why: on 2026-08-09 and again on 2026-08-11, `chatgpt_1` reported having no tasks and was right
both times. Its committed sweep (`d4eb391a`) matches only legacy `- To:` bullets and never parses
front matter, so it saw **zero** v2 messages — including a correctly addressed TRAIN handoff that
was blocking the whole project. The first remedy was to tell it to update; that was a request,
not a fix, and the coordinator then asserted the problem was solved on the evidence that peers
were *replying*. **Delivery must not depend on every agent running identical tooling.**

The general rule this encodes: **a remedy that depends on another party acting is not complete
until verified by measurement.** Publishing a digest is the measurement; a reply is not.

### 10.1 Lint before you publish

```bash
python3 scripts/lint_outbox.py --me <id> --fetch --staged
```

Messages are immutable once pushed, and — verified 2026-08-07 — **publishing a correction
does not clear the original's delivery error**: the sweep validates every addressed message
on the authoritative refs regardless of what supersedes it. A schema violation therefore
sticks to the shared bus permanently and blocks `--mark` for every recipient until the
coordinator adjudicates it. Catching it before the push is the only cheap fix.

`lint_outbox.py` applies the same v2 rules as the sweep to messages you have not published
yet, minus canonical-branch presence (which an unpushed message cannot satisfy).

**Use `--staged`.** Git publishes the *index*, not the worktree, so a message that is staged
malformed and then fixed in the worktree passes a worktree-only lint and is committed
malformed. `--staged` reads index blobs — the bytes a commit would actually deliver. Without
it the lint is a convenience check and does not prove publish safety.

It also reports: any message present in `HEAD` but absent from the proposed tree (committing
that tree would delete a published message); any already-published message whose bytes
differ from what was published, since editing one rewrites the record instead of correcting
it; an immutable-path collision, matching the receiver; and any file in your namespace that
is neither a message nor explicitly allowlisted (`README.md`). That last rule exists because
a typo'd filename silently stops being a message — it is never delivered and never reported
missing. Legacy messages are grandfathered only per the frozen baseline in §10.2; `--all`
re-lints published ones. Exit 0 clean, 2 errors.

### 10.2 Quarantine — adjudicating a permanently invalid message

Because an invalid published message can never be repaired by its sender and history
rewriting is closed (`docs/STATE.md` §3), the coordinator may record an adjudication in
`coordination/quarantine.json`:

```json
{"schema_version": 2, "entries": [
  {"path": "coordination/messages/<sender>/<exact-message>.md",
   "reason": "<why this is permanently invalid>",
   "adjudicated_by": "coordination/messages/<coordinator>/<exact-message>.md",
   "target_blob": "<40-hex blob oid of the quarantined message>"}
]}
```

**Authority is the coordinator's canonical ref**, `refs/remotes/origin/agent/<coordinator>`,
never the worktree — otherwise two agents at the same fetched state get different inbox truth
from their local checkouts, and any local edit suppresses a message. The sweep prints the ref
and blob it used and warns when the local copy drifts.

**An adjudication must actually adjudicate.** It must be a valid v2 message, authored by the
coordinator, present on the coordinator's canonical ref, naming the exact target in a
`quarantines: ["<exact path>", …]` front-matter array — and the entry must pin the target's
blob. Existence of a path is never sufficient. Under the first implementation it was, and an
unrelated message authored by the quarantined agent itself authorized suppression of its own
fabricated closeout.

**Who the coordinator is comes from `coordination/roster.json` on `origin/main`**, never from
the environment. Reading it from an environment variable made the authority untrusted input:
whoever set the variable designated the quarantine authority, and pointing it at a branch with
no quarantine silently suppressed nothing while reporting no error. An absent or malformed
roster disables quarantine entirely and says so — fail-safe, because suppressing nothing is
recoverable and suppressing wrongly is not.

**Three further rules, each from a reproduced attack:**

- A **collided path can never be quarantined.** With different bytes on two refs there is no
  single blob to pin, and the pin was previously skipped in exactly that case — when it matters
  most.
- **Quarantining an ACK must declare what it re-opens.** Withdrawing an ACK silently restores
  every obligation it discharged for its sender. That can be correct — a fabricated ACK should
  be withdrawn — but the entry must list the restored paths in a `reopens` array, so the agent
  whose work reappears learns it from the adjudication rather than from a surprise.
- **Quarantine is a general suppression primitive and nothing checks that the target is truly
  invalid.** That is by design and is exactly why the authority is narrow, every entry cites a
  published adjudication, and the whole file is reviewable. Treat adding an entry as an act
  requiring the same scrutiny as a verdict.

A quarantined message is excluded from delivery validation, newness, and acknowledgement —
**a quarantined ACK acknowledges nothing** — and is listed in its own `quarantined` section
instead, so the record is preserved rather than erased. Rules:

- **Only the coordinator/integrator writes this file**, and every entry must cite a
  published adjudication message that is itself authoritative and not quarantined.
- A malformed file, an entry naming a path that is not on the authoritative refs, or a
  self-adjudicating entry is a transport error (exit 2) and **suppresses nothing** — a
  broken quarantine can never hide a real delivery failure.
- Immutable-path collisions are never suppressed by quarantine.
- Quarantine is for messages that are permanently invalid, not merely wrong or unwelcome.
  Content that is still needed must be re-published validly by its sender *before* the
  invalid original is quarantined, or it disappears from the transport's view.

**Frozen legacy baseline.** Rule 5 grandfathers pre-v2 messages, but only the exact paths
pinned by blob in `coordination/legacy-baseline.json` on the coordinator's canonical ref
(691 at the migration). Any message outside that baseline must be v2, enforced by the
*receiver*. Otherwise omitting `schema_version` skips v2 validation entirely for anyone who
does not voluntarily run the lint, and a backdated filename defeats a date cutoff. The
baseline is generated once by `scripts/build_legacy_baseline.py` and is frozen — a
legitimately new legacy message is a contradiction in terms, so regenerating it to clear a
delivery error would reopen the hole it closes. `--check` audits drift.

**The baseline pins `frozen_at`, a commit, and every entry is re-verified against it.** Without
that it was a v2-enforcement waiver list that whoever could write it could extend, letting an
arbitrary message escape validation entirely. A path that did not exist at the freeze commit,
or whose bytes differ from it, is a transport error. The freeze commit must be an integrated
ref, because the pinned paths span every agent branch.

**The lint applies the baseline too.** It previously ignored it, so a published no-schema
message outside the baseline linted clean and was rejected permanently by the receiver — the
safety net failing in the one direction that costs a quarantine.

**WIP limit (owner decision 2026-08-17).** One in-flight ack-requiring handoff per agent
per task: do not publish handoff N+1 for a task while your handoff N still awaits
acknowledgement. The canonical retirement is the integrator's ack; a correction naming the
pending handoff in `supersedes` is always allowed (corrections are mandatory and exempt).
Enforced sender-side by `scripts/lint_outbox.py` on NEW handoffs only — published messages
are immutable and are never flagged retroactively. Rationale: crossings-in-flight were the
largest measured coordination cost of 2026-08-16 (three handoffs crossed rulings, each
crossing spawning a correction round).

**Queue-changing messages require acknowledgement (adopted 2026-08-18).** Any message
that changes another party's task list carries `requires_ack: true` toward that party —
verdicts on ack-required handoffs (REVISION_REQUIRED reopens the implementer's queue;
ACCEPTED often opens the next stage's), approvals a party is on record waiting for,
rulings that reopen or redirect work. Proposed by the integrator after the 2026-08-18
G-4c.2 stall (a no-ack method approval left the implementer truthfully idle while the
record said "in build"); codex_1 endorsed in writing and practiced it the same hour;
no objections. Companion rule from the same incident: **a deferral is a status, not a
silence** — an agent that decides not to start unblocked work publishes "not started,
deferred, because X" the moment the decision is made; a truthful empty inbox is not a
status. Instances and full history: `docs/METHODS-LEDGER.md`, verdict-equals-message.

**A deferral is also a QUEUE ITEM (owner-adopted 2026-08-18).** Prose is not enough:
twice in one day a correctly-published deferral left every inbox empty beside open
work, because everyone polls the queue, not the diary. A deferral message declares
itself with a body line starting with the canonical marker `DEFERRED:` and must carry
`requires_ack: true` with the SENDER among its own `to` recipients — the deferring
agent's next session then finds the postponed job as its first unacknowledged item and
acknowledges it by starting (or by publishing a further deferral of the same shape).
Enforced sender-side by `deferral_shape_errors` in `scripts/lint_outbox.py`; prose
mentions of the word "deferred" mid-line do not trigger the gate. Coordinator
resume-orders remain the backstop for sessions that die before declaring.

**A self-addressed card surfaces as an OBLIGATION, never as unread mail (rule-owner
ruling 2026-08-21, after the repair).** From adoption (08-18) until 08-21 the sentence
above — "the deferring agent's next session then finds the postponed job" — was not true:
the sweep dropped every self-sent message before addressing was consulted, so no
self-addressed card was ever visible to the agent who owed it (measured by claude_1,
`20260821T053322Z`; repaired in the ONE shared predicate `actionable_set()` at
`8c531096`, codex_1 ACCEPTED). The mechanism as it now is, and as the rule means:
(1) the addressed set admits a self-authored message only when it is a shape-valid
`DEFERRED:` card (line-start marker, `requires_ack: true`, sender among `to`);
ordinary self-mail stays invisible, so nobody can put arbitrary work in their own queue
by writing to themselves. (2) The card is listed under *unacknowledged, ack required*
— never under *new*, because its author has read it and a `--mark` must not retire an
undone job. (3) It leaves the queue only when a later message of the SAME agent names
it in `ack_for` — the delivery handoff or the next `DEFERRED:` replacement; `supersedes`
is inert for discharge on every kind. (4) Consequently a green sweep asserts "nothing
owed TO me and nothing owed BY me"; the honest steady state is a small standing queue
of one's own open cards. Turning the route on revealed 12 never-discharged cards of
claude_1's, 9 of them closed the same hour against verified deliveries
(`20260821T061633Z`). **OWNER RULED 2026-08-21: ALL.** The queue shows every open
card of the agent, not only the newest per task; "inbox clean" means nothing owed to
me AND nothing owed by me, with no per-task collapsing. No second predicate is to be
written for it.

**(5) Visible is not the same as waking (§5.1, owner rule 2026-08-21).** The card sits in
its author's queue; it never rings its author's doorbell. Turning the visibility on without
this clause cost eight no-op wakes in 102 minutes on the day it landed.

**Cards are acknowledged by DELIVERY, never by a bare receipt (sharpened
2026-08-19; route corrected same day after claude_1 proved the first wording
unimplementable — `supersedes` is inert for discharge, `ack_for` is the only
mechanism).** A message carrying a line-start **`CARD:`** marker is a standing
work item; it stays in the assignee's queue until discharged by exactly one of:

1. **the DELIVERY handoff** naming the card in its `ack_for`; or
2. **a replacement `DEFERRED:` card** naming the original card in its
   `ack_for` — legitimate because the discharge arrives WITH a successor queue
   item in the same message (self-addressed, ack-required, per the deferral
   gate); the queue never reads empty while work exists.

A replacement is published when something CHANGED — the work started, the blocker moved,
the scope was ruled on. An unchanged standing card is left standing (§5.1): waking is not a
reason to re-issue, and a card carrying `UNBLOCK-SIGNAL:` waits for that signal or for its
24-hour heartbeat.

A **bare receipt-ack** — one that discharges a `CARD:` while neither delivering
nor replacing it — is the violation. Enforced sender-side by
`card_ack_errors` in `scripts/lint_outbox.py`: an ack naming a `CARD:` message
must be a handoff or itself carry a `DEFERRED:` line.

**Ack is not delivery (adopted 2026-08-19, third stall shape in two days).**
Acknowledging a message that ASSIGNS you work discharges the acknowledgement, not
the work — and leaves the work with no queue item at all. Rule: a session that
acks a work-assigning message (charter, verdict opening your next stage, directive)
and ends without DELIVERING that work must leave a `DEFERRED:` card for it (the
self-addressed ack-required shape above). "My build proceeds" inside an ack is
prose; the card is the queue item. Note for the sentinel era: wake-on-work only
sees CARDED work — an acked-and-uncarded assignment is invisible to the sentinel
too, which makes this rule load-bearing, not cosmetic.

**Evidence gate (owner decision 2026-08-17).** A handoff whose body asserts a chartered
cause label (the audit vocabulary, e.g. `GENERATOR_GAP` — the registered set lives in
`CAUSE_LABEL_TOKENS` in `scripts/lint_outbox.py`) must carry a `review_ref:` front-matter
field naming the review file that ACCEPTED the producing instrument, resolvable on an
authoritative remote ref. Causal claims travel only with their instrument's acceptance;
raw-data and instrument handoffs need nothing. This mechanizes the standing publication
gate that was enforced only socially on 2026-08-16 (three headlines published ahead of
review, all later withdrawn).

**Migration to v2 (one-time, per agent).** Run from your own worktree, substituting your
agent id — shown here for `claude_1`, `local_codex_1`, and `chatgpt_1`:

```bash
# claude_1
python3 scripts/inbox_sweep.py --me claude_1 --fetch          # review; exit 2 = transport error
python3 scripts/inbox_sweep.py --me claude_1 --fetch --mark   # writes claude_1/inbox-seen.json
git add claude_1/inbox-seen.json
git commit -m "claude_1: migrate inbox seen-state to inbox-seen.json"
git push origin agent/claude_1

# local_codex_1
python3 scripts/inbox_sweep.py --me local_codex_1 --fetch
python3 scripts/inbox_sweep.py --me local_codex_1 --fetch --mark
git add local_codex_1/inbox-seen.json
git commit -m "local_codex_1: migrate inbox seen-state to inbox-seen.json"
git push origin agent/local_codex_1

# chatgpt_1
python3 scripts/inbox_sweep.py --me chatgpt_1 --fetch
python3 scripts/inbox_sweep.py --me chatgpt_1 --fetch --mark
git add chatgpt_1/inbox-seen.json
git commit -m "chatgpt_1: migrate inbox seen-state to inbox-seen.json"
git push origin agent/chatgpt_1
```

Do not blanket-acknowledge a backlog by timestamp: acknowledge actionable messages by
exact path, publish a pushed legacy-backlog audit for the rest, and mark paths seen only
after the ACK/audit commit is remotely verified (task record §Historical-backlog rollout).

**Operational shorthand:** unpushed = unsent; unverified push = not yet sent; chat is an
alert channel, not the coordination bus.

## 11. Rules about rules (added 2026-08-21)

The two worst coordination failures of this week came from correct rules composing badly,
not from a wrong rule — the owner's discovery note is
`docs/DISCOVERY-two-correct-doors-make-a-wall-2026-08-17.md`. Four obligations follow, each
paid for:

1. **A rule that creates a queue item must name what removes it**, and the remover must be
   reachable by the party who owes it. `supersedes` looked like a discharge and was inert
   for one, so a card stayed open for a day while its work shipped and was reviewed.
2. **No mechanism may take an agent's own output as its own trigger.** What an agent
   publishes is, for that agent, a record — never a signal. (§5.1 is the instance that
   produced this rule.)
3. **A change to a shared predicate enumerates every consumer before it lands.**
   `actionable_set()` is read by the sweep, the lint, the launcher and the sentinel. The
   08-21 repair was right in the sweep and turned the launcher into a treadmill because the
   second consumer was never listed. Name them in the handoff; the reviewer checks the list.
4. **A message adopting a rule says which rule it amends and what it does NOT change.**
   The sections of this document written that way have survived unedited; §1, which was
   not, silently named a dead branch and a roster missing its most active reviewer for
   nine days.
