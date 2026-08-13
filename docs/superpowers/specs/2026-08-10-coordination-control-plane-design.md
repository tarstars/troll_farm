# Coordination control plane — design

Date: 2026-08-10 (verified against `git log`, not a self-reported clock).
Author: `local_claude_1` with the owner. Status: approved in discussion; this file is the
written record for review.

Provenance: the architecture follows `chatgpt_2/agent-sync-review-2026-08-09.md`
("Stop using Git as a mailbox", pinned to Team Unagi's public `icfpc-unagi/icfpc2026`
repo at `cce422ca`), adapted to two owner inputs from 2026-08-10: agents run **mixed
local + cloud** and **truly simultaneously**, and the service will be hosted on the
**Yandex Cloud VM** where `claude_1` and `codex_1` already run.

## 1. Problem, in one paragraph

The current system makes git do six jobs — code store, mailbox, task queue, lease clock,
acknowledgement database, dashboard — and it is excellent at the first and poor at the
other five. Measured consequences (audited 2026-08-10): ~57–77% of the last 1,000 commits
touched no code; 924 immutable messages in three schema eras; 239 ack files of which 163
discharge nothing; a quarantine registry grown to 10 entries, one of them the
coordinator's own message; four versions of the 1,309-line inbox tool live on different
branches, which once left an agent seeing zero messages for ten days; 106 distinct
free-text task statuses across 112 records while the documented "active tasks" query
finds 2 of ~25–28 actually-open; and one session ran on a fabricated clock (+3 days),
poisoning filenames, task ids, and recorded rulings. The design lesson the record
supports: rules the substrate enforces are obeyed (1 of 925 messages was ever edited);
rules requiring memory are not.

## 2. Decision — three kinds of truth, three homes

| Question | Home |
|---|---|
| What is happening now? | `coordd`, a transactional coordination service |
| What happened, and what is the evidence? | Git commits, branches, and audit exports |
| May it become official? | The single integrator merging to `main` after the local check suite passes |

Nothing is hand-mirrored between homes. Anything that describes live state (dashboard,
roster views, "who is doing what") is a query against `coordd`, never a maintained file.

Provenance note (verified 2026-08-10 against the public repo): the first two rows follow
Unagi's split; the third row does **not** describe Unagi. Their six humans pushed ~779
commits directly to `main` with no review gate, and their coordination system governed
task dispatch, not merge rights. The integrator row is Troll Farm's own existing rule,
retained on the review's explicit recommendation ("the project can retain its existing
single-integrator rule"), because the trust model differs: long-running LLM agents with
one documented fabricated acceptance, a byte-sacred source, hash-locked experiment
records, and a single Arena slot make a human-controlled integration gate load-bearing
rather than overhead. Today that rule is convention only (`main` is unprotected); this
iteration keeps enforcement local (owner ruling 2026-08-10: no CI for now) — P3 turns the
integrator's pre-merge ritual into one command instead.

## 3. The service

**Runtime.** `coordd`: a single-file Python 3.10+ service, standard library only
(`http.server` + `sqlite3` + `json`), SQLite database in WAL mode, run as a systemd unit
on the Yandex Cloud VM. A thin client CLI, `coordctl`, wraps the HTTP API for agents and
humans. No framework, no ORM, no message broker.

**Access.** The service binds to `127.0.0.1` on the VM. Cloud agents call it directly.
Local agents reach it through a persistent SSH tunnel (`ssh -N -L 7077:127.0.0.1:7077`,
kept alive by autossh/systemd on the project host). The tunnel and VM login are the
security boundary; a shared bearer token in a non-committed file is sent on every request
as defense in depth. No public port is ever opened.

**Data model** (tables, final column lists to be settled in the implementation plan):

- `agents` — id, role, tool digest, protocol version, capabilities, last seen,
  compatibility state.
- `tasks` — id, title, state from the fixed enum
  `open | claimed | review | blocked | done | dropped`, priority, owner, timestamps.
- `task_paths` — normalized write-set path prefixes per task; overlap is checked at
  claim time.
- `leases` — task, owner, generation (fencing token), expiry, last heartbeat.
- `events` — server-assigned monotonic sequence and server time, type, actor, task,
  payload, idempotency key.
- `acks` — exact event sequence + acknowledging agent. Used only where a response is
  genuinely required (assignment, review request, stop); nothing else demands an ack.
- `artifacts` — task, generation, git ref, full commit, declared paths, verification
  result.
- `reviews` — task, reviewer, verdict, evidence pointer, reviewed artifact generation.

**Semantics (the guarantees, each one testable):**

1. **Atomic claim.** Claiming a task and reserving its write set is one transaction;
   two agents cannot own one task, and overlapping path prefixes cannot both be active.
2. **Lease + heartbeat.** Ownership expires if not renewed (default TTL 15 minutes,
   matching the current lease rule; heartbeat every 5). A crashed agent loses ownership
   by expiry — no human edits status prose to declare it dead.
3. **Fencing generation.** After a takeover, a late handoff from the superseded owner
   generation is rejected.
4. **Server time and sequence.** All ordering and timestamps are server-assigned.
   Agent-reported clocks become presentation-only, which retires the fabricated-dates
   hazard class.
5. **Compatibility gate.** An agent registers with its tool digest and protocol version;
   incompatible agents are refused task assignment with an upgrade message, instead of
   silently going blind (the ten-days-of-zero-messages failure becomes structurally
   impossible).
6. **Artifact validation.** A handoff must name a full commit reachable from the declared
   ref and paths that exist in it. `coordd` verifies this against its own bare clone of
   the repo (fetched on demand). This is the one strict validation carried over from v2 —
   it is the check that catches false claims about work.
7. **Dashboard.** One HTML page answers: active tasks, owners, lease age, blockers,
   pending reviews, incompatible agents. Rendered from queries, never maintained.
8. **Audit export.** The service periodically exports state transitions as compact
   append-only JSON/Markdown committed to git, plus a daily SQLite dump into the repo.
   Git remains a complete historical record even if the database is lost.

## 4. What stays in git

Code, experiment protocols and evidence, negative results, docs, handoff artifacts, and
the audit exports above. The frozen-experiment layer (protocols + locks under
`data/analysis/live-agent-6553250/`) is untouched and continues to outrank coordination
records where they disagree, exactly as today. One branch and one worktree per writing
agent remains the rule — the service coordinates ownership; git isolates edits.

## 5. What is retired

Frozen as read-only history, never deleted: `coordination/messages/` (924 files), the
491-line `multi-agent-protocol.md`, `quarantine.json`, `legacy-baseline.json`, and the
templates. Retired with them: per-message schema validation, permanent delivery errors,
quarantine adjudication, dual-format messages, the ack ceremony, and per-agent
full-ref scanning. `inbox_sweep.py` (1,309 lines) and `lint_outbox.py` (296) are replaced
by `coordctl doctor`, which checks: tunnel/service reachability, repo freshness, tool
digest vs `origin/main`, sacred-source SHA, and cron health (the 05:17 collector's last
exit marker — its most recent run failed on a TLS timeout and nothing noticed).

**Docs policy.** Budgets enforced by tests that fail: `docs/STATE.md` ≤ 150 lines
(currently 360 against its own stated budget), new protocol ≤ 1 page. The roster,
onboarding prompt (`peer-prompt.md`), and environments table are **generated** from one
machine-readable config committed to the repo; a test in the standard pytest suite fails
when generated files drift, so any local test run catches it. The
current hand-maintained triples (AGENTS.md vs roster.json vs ENVIRONMENTS.md) disagree
today about who the integrator is and which agents exist; generation makes that class
unrepresentable. `docs/CONSTRAINTS.md` stays append-only prose but gains a generated
index; `docs/BACKLOG.md` keeps LIVE PRIORITIES only, history moves to the archive.

## 6. Migration

**P0 — immediate, no service required.** Fix stale pointers (AGENTS.md integrator line,
README "current handover", ENVIRONMENTS.md); rewrite STATE.md within budget; owner ack
amnesty for messages from unreachable/dormant agents; add the session-start real-clock
check; add the cron-health and ref-census guards ("substantial work reachable from no
pushed ref" fails). Owner decisions queued: B7 (3 failing pinned-verdict tests), B9
(325 tracked files under gitignored `data/raw/`), e7a 375-vs-586 canonical definition.

**P1 — build in shadow.** Implement `coordd` + `coordctl`, deploy on the VM, tunnel from
the project host. Mirror new git-message traffic into the service; both projections are
compared while git remains authoritative.

**P2 — switch authority.** New tasks, claims, leases, and acks live only in the service;
`coordination/messages/` is frozen with a final README pointer; dual-format and the
legacy baseline retire. Requires the acceptance tests below to pass first.

**P3 — harden, locally.** The integrator's pre-merge ritual becomes one command
(`coordctl check`): doc budgets, generated-doc drift, artifact-pin validation, and the
test suite — wired as a local git pre-push hook on the project host so it cannot be
skipped by habit. GitHub-side branch protection and CI are deliberately deferred to a
later iteration.

**Acceptance tests before P2 (each must be loud or impossible):** twenty simultaneous
claims produce exactly one owner; non-overlapping write sets proceed concurrently while
overlapping prefixes cannot both be active; an expired lease is taken over and the stale
generation's handoff is rejected; a service restart preserves leases, generations, and
the event log; an incompatible client is refused with an upgrade message; retrying with
one idempotency key creates one event; a duplicate ack is harmless; a handoff naming a
missing commit or path is rejected; the dashboard answers without replaying history;
the audit export reconciles against database state.

## 7. Operations and failure mode

If the VM or tunnel is down: agents keep working on tasks they already own and can read
git normally; new claims wait until the service returns. Recovery: audit exports + daily
dump make the state reconstructible from git alone. Backups are therefore in-repo; no
separate backup infrastructure. The Arena controller role does not move: submissions
still run from the project host (the CodinGame session lives there), serialized through
the single controller exactly as today; the service tracks the cycle as an ordinary task.

## 8. Non-goals

No CI in this iteration (owner ruling 2026-08-10) — all checks run locally; no history
rewriting; no deletion of archives or negative results; no change to Arena
authorization, the frozen-experiment discipline, sealed data ranges, the byte-sacred
resident source, or the storage/YT policies; no attempt to migrate the 924 historical
messages into the database — they are history, and history stays in git.
