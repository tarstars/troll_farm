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
- one designated **integrator**, who alone updates the session branch
  (currently `session-2026-07-01`; this project has no active `main` workflow);
- one designated **arena controller**, normally the integrator, who alone performs
  platform-side mutations (see §6).

Current roster (owner reassignment 2026-08-06): **`local_claude_1`** — **coordinator
(integrator)** and arena controller by the "normally the integrator" default. **`local_codex_1`**
— contributor and outgoing coordinator, with no Arena authority after the transfer.
**`claude_1`** — active contributor; **`chatgpt_1`** — contributor and reviewer. Handover brief:
`coordination/HANDOVER-2026-08-06-local_codex_1-to-local_claude_1.md`. Roles are defaults, not
capability limits; a task record says who owns that particular outcome, and the user may reassign
at any time.

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

Kinds: `claim`, `progress`, `question`, `blocker`, `policy`, `stop`, `takeover`,
`handoff`, `ack`, `release`, `integrated`, `correction`. Messages are immutable once
published; here **published means committed and pushed to `origin`**. A correction is a
new pushed `correction` message at a new immutable path whose `supersedes` array names the
exact superseded message path; the superseded message stays immutable and visible. Moving
or copying an old message between refs is not a new coordination event. All kinds except
`progress`, `ack`, `release` and `integrated` require an `ack` from the recipient's own
namespace (`correction` requires acknowledgement by default).

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

## 6. Arena authority (replaces the source protocol's contest-submission section)

Read-only platform work (leaderboard reads, replay collection) may be delegated to any
agent under the existing authorization rules in `docs/STATE.md` §3. **Mutations — any
submission, TestSession game, or anything that changes our ladder standing — are
serialized through the single arena controller**, per `docs/PROMOTION-RUNBOOK.md`. Since
2026-07-30 the owner's per-candidate permission gate is **lifted** (standing authorization —
see `docs/STATE.md` §3), but the requirements it protected are not: a **QUALIFIED verdict
from a frozen protocol**, expected gain above the arena noise band, the full runbook, and
owner notification before and after each cycle. **No peer agent or subagent may submit** —
serialization through the single controller, currently `local_claude_1`, is the point.

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
