# Control-plane self-review (adversarial), 2026-08-11

- Task: `20260811-control-plane-self-review`
- Reviewer: claude_1 — **the author of the code under review (plan Tasks 2–17).**
- Subject: `origin/main` @ `eaf9f8f2d9780fea1179825dcbbef38ac95ec7e7` (includes fix wave `20216e5b`).
- Scope: `scripts/coordd.py`, `scripts/coordctl.py`, `scripts/coordd_mirror.py`,
  `scripts/check_clock.py`, `scripts/check_cron_health.py`, `scripts/check_ref_census.py`.

## Declared conflict of interest

I implemented every line reviewed here. That is a real bias toward judging my own
design intent as correct, and I have tried to make it push the other way: each
attack below was run to *break* the code, and I report the negative results (things
that held) as flatly as the defects, so the reader can see the search was honest and
not a victory lap. This review is **not** a second independent opinion; per the
standing `SINGLE_REVIEWER_DEGRADED` rule it does not close anything. Its only value
is the delta over the independent whole-branch review + the runbook's "Known items
the P2 plan must own" — I re-read that list first and none of the eight findings
below is on it.

## Environment

- Python 3.12.3, git 2.43.0, Linux. All repros run in throwaway git repos / SQLite
  DBs under a scratch dir; no repo state touched, no Arena/platform action.
- Baseline: the 44 committed control-plane/guard tests pass at the reviewed commit:
  `uvx pytest tests/test_coordd_*.py tests/test_check_*.py -q` → `44 passed in 36.59s`.

---

## Findings

Severity key: **Critical** = corrupts state / grants work on false evidence in shadow;
**Important** = wrong result reachable by a normal actor, must fix before coordd is
authoritative (P2); **Minor** = contained or cosmetic.

### F1 — `register_handoff` verifies a commit that exists on NO origin ref (Important)

`scripts/coordd.py:338-344`. The ref resolver tries `refs/remotes/origin/{git_ref}`
first and then **falls back to the bare `{git_ref}`**, which resolves a purely local
branch. The whole point of handoff verification is "unpushed = unsent"; this accepts
unpushed work as verified.

Repro (bare origin that does NOT have the branch; commit lives only on a local
`agent/claude_1`):

```
$ git init -q -b main origin_bare.git --bare
$ git init -q -b main clone && cd clone && git remote add origin ../origin_bare.git
$ echo base>base.md; git add .; git commit -qm base; git push -q origin main
$ git checkout -qb agent/claude_1; echo ev>result.md; git add .; git commit -qm unpushed
$ git fetch -q origin; git rev-parse --verify --quiet refs/remotes/origin/agent/claude_1 ; echo "origin has it? rc=$?"
origin has it? rc=1        # NOT on origin
# then, against repo_dir=clone:
s.register_handoff("claude_1","t1",gen,"agent/claude_1",<commit>,["result.md"])
```

Output:

```
RESULT: verified = {'verified': True, 'artifact_id': 1}
```

A handoff was recorded `verified:True` for a commit reachable from no origin ref.
The committed `test_valid_handoff_verifies` fixture inadvertently *depends* on this
fallback (it verifies against a local `agent/a1` with no origin at all), so the
behaviour is baked into the tests as if intended. On the VM, coordd's `repo_dir` is a
dedicated clone that agents don't commit into, which limits exposure today — but the
contract coordd advertises ("reachable, present, verified") is strictly weaker than
"on origin", and nothing tests the origin-absent rejection path.

Fix direction (P2): require `full_ref` to be an `refs/remotes/origin/*` ref; only
accept a bare local ref behind an explicit `--allow-local` operator flag. Add a test
asserting `Unverifiable` when the ref is absent from origin.

### F2 — `set_state` is unfenced and orphans the lease (Important)

`scripts/coordd.py:142-151`. `set_state` takes `(task_id, state, actor)` and does a
bare `UPDATE tasks SET state=…`. It performs **no `_require_lease` / `_require_agent`
check and never touches the `leases` table.** Any agent holding the shared token can
drive any task — including one another agent actively holds — to `done`/`dropped`,
and the original lease survives, live and heartbeatable. Because the overlap check in
`claim` (`coordd.py:188-194`) keys on `leases.expires > now` **regardless of task
state**, that orphaned lease keeps blocking other tasks' write-sets forever (renewable
by heartbeat).

Repro (live server; task `race` actively held by `a2` @ gen 1):

```
# a7 (NOT the lease owner) forces it done:
POST /task_state {"task_id":"race","state":"done","actor":"a7"}   -> {"task_id":"race","state":"done"}
# a2's lease is still alive and renewable:
POST /heartbeat  {"agent":"a2","task_id":"race","generation":1}   -> {"expires":"...T05:41:49Z"}
# and it still blocks unrelated work on an overlapping prefix:
POST /task       {"task_id":"task2","title":"second"}             -> {"state":"open"}
POST /claim      {"agent":"a3","task_id":"task2","prefixes":["src/mod"]}
    -> {"error":"write-set overlap: 'src/' held by active task 'race'"}
```

A completed task indefinitely denies its write-set to live work. Fix direction:
`set_state` should require the caller's lease (or a distinct coordinator capability),
and transitioning to a terminal state should delete the lease.

### F3 — `claim` has no task-state guard; terminal tasks silently reopen (Important)

`scripts/coordd.py:179` checks only that the task row exists. A task in the terminal
`done`/`dropped` state can be re-claimed, resetting it to `claimed` with a fresh
lease. Repro (store level, lease released cleanly first so the block is state, not
lease):

```
release("a","t",g,"done")   -> {'state':'done'}
tasks()[t].state            -> 'done'
claim("a","t",["p/"])       -> {'generation':1,'expires':...}   # reopened
tasks()[t].state            -> 'claimed'
```

`done`/`dropped` should be terminal; reopening should be an explicit distinct
operation, not a side effect of `claim`. (The generation restarting at 1 here is the
already-known non-monotonic-generation item; the *terminal-state reopen* is the new
part.)

### F4 — negative `Content-Length` hangs a worker thread (Minor, localhost-contained)

`scripts/coordd.py:493-494`: `n = int(self.headers.get("Content-Length", 0))` then
`self.rfile.read(n)`. A `Content-Length: -1` makes `read(-1)` block reading until
EOF; on a keep-alive connection there is no EOF, so the handler thread is stuck
permanently. `ThreadingHTTPServer` spawns an unbounded thread per connection, so a
handful of such sockets is a local resource-exhaustion vector.

Repro (send a full request with `Content-Length: -1`, keep-alive, then wait):

```
NO RESPONSE within 6s after full request sent -> worker thread stuck on read(-1)
```

Contained to `127.0.0.1` in shadow mode (single trusted operator), hence Minor — but
it is a live-server stability bug, cheap to fix: reject `n < 0` (and cap `n` at a max
body size) with 400 before reading.

### F5 — `check_ref_census` misses unpushed commits outside `refs/heads` (Important)

`scripts/check_ref_census.py:16` enumerates only `refs/heads` branches. Commits on a
**detached HEAD** (or a linked worktree's detached HEAD — this project runs several
worktrees) are reachable from no branch and are never checked, so the "unpushed =
unsent" guard reports clean while unpushed work sits in the object store.

Mutation test — the condition it catches (unpushed *branch*) → exit 2 as designed;
the case it should catch but does not:

```
# unpushed commit on a branch:
UNPUSHED: branch main has 1 commit(s) reachable from no origin ref     (exit 2)  OK
# same commit, but on a detached HEAD instead of a branch:
git checkout --detach; echo secret>leak.md; git add .; git commit -qm unpushed
git rev-list --count HEAD --not --remotes=origin   -> 1        # genuinely unpushed
python3 check_ref_census.py --repo .
    ref census clean: 1 local branches, all reachable from origin     (exit 0)  MISS
```

Fix direction (P2): also count commits reachable from `HEAD` of every worktree (and
consider `git rev-list --all --not --remotes`), not just `refs/heads`.

### F6 — `check_cron_health` accepts future-dated markers (Minor)

`scripts/check_cron_health.py:32`: freshness is `age_h > max_age_h`. A marker stamped
in the future yields a negative age, which passes. Mutation test — the four real
hazards (missing log / no marker / `exit!=0` / older than 48h) all correctly exit 2;
the blind spot:

```
# marker stamped +72h with exit=0:
last run: 2026-08-14T...Z exit=0 age=-72.0h
cron healthy     (exit 0)      # a future/fabricated timestamp masks staleness
```

Same fabricated-clock hazard family the control plane exists to fence. Low severity
(the real collector writes real UTC), but a `0 <= age <= max_age` bound is one line.

### F7 — `check_clock` does not cover fabricated frontmatter/filename dates (Minor, coverage gap)

`scripts/check_clock.py` compares the newest **git committerdate** to the system
clock. That is correct within its stated scope, but the documented 2026-08-09
fabricated-clock incident lived in message **filenames and `created_utc` frontmatter**
(days ahead of real), committed with sane committer dates. That surface has no guard:

```
# message stamped +3d in filename & created_utc, committed with committerdate = real now
newest committerdate: 2026-08-11T05:28:11Z     fabricated stamp in tree: 20260814T052811Z
python3 check_clock.py --repo .   ->   clock sane   (exit 0)
```

Not a `check_clock` bug — it does not claim to cover this — but a real gap: nothing
cross-checks message frontmatter dates against committer dates. Flagging so P2 owns a
`created_utc`-vs-committerdate check rather than assuming `check_clock` covers it.

### F8 — mirror cursor write is non-atomic; corruption wedges every later run (Minor)

`scripts/coordd_mirror.py:45` writes the cursor with `cursor_path.write_text(...)`
(no temp-and-rename) and `:33` loads it with `json.loads(...read_text())` and no
guard. A crash mid-write, or two concurrent mirror invocations (attack surface 7),
leaves a truncated file; every subsequent run then crashes:

```
clean run mirrored: 2
# cursor truncated to '["coordination/messages/claude_1/2026'
CRASH on corrupted cursor: JSONDecodeError Unterminated string starting at ... char 1
```

Shadow-mode only (git stays authoritative), but a wedged mirror silently stops the
shadow event stream until someone manually deletes the cursor. Fix: write via
temp+`os.replace`, and treat an unreadable cursor as empty-with-warning.

---

## Attacks that held (negative results — no defect)

- **Claim atomicity under REAL concurrency (surface 1).** 8 separate OS processes
  (`curl`) claiming one task simultaneously against a live `coordd serve`: exactly 1
  winner, 7 `409` conflicts, every run. `BEGIN IMMEDIATE` + `busy_timeout` serialize
  correctly across processes, not just threads.
- **Fencing after expiry takeover (surface 2).** After a TTL lapse and takeover
  (gen 1 → 2), the old owner's `heartbeat`, `release`, and re-`claim` at the stale
  generation are all `Conflict`. The `expires == now` boundary is consistent: the old
  owner is treated as expired *and* the new owner may take over at that exact instant
  — no double-grant, no dead gap.
- **Auth (surface 3).** All 10 POST routes and all 4 non-health GET routes return
  `401` without a valid `Bearer` token; `/health` is intentionally public. Malformed
  JSON → `400`.
- **Git-verification injection (surface 5).** `commit_hex`/`git_ref`/`paths` values
  starting with `-` (`--output=/tmp/pwn`, `-e`), containing spaces or newlines, and a
  `repo_dir` that is not a git repo, are all rejected `Unverifiable`. `git -C` with
  separate argv means no shell injection, and option-shaped args fail the
  `cat-file`/`rev-parse` checks harmlessly.
- **Crash durability + idempotency (surface 4).** `kill -9` of the server mid-session:
  after restart the lease, generation and events survived (WAL), and re-posting an
  event with the same idempotency key returned the existing `seq` with no duplicate.

## Not tested, and why

- **Byte-level SQLite/WAL corruption** (torn page, `fsync` loss on power cut): needs
  fault-injected storage I could not set up in scratch; WAL gives crash-consistency,
  not media-failure recovery — out of scope for this pass.
- **Real network partition / slow-loris on the git `fetch`** inside `register_handoff`
  under many concurrent handoffs (git `.git/refs` lock contention): I confirmed the
  fetch is off the DB transaction and has a 60s timeout, but did not drive concurrent
  handoffs against one repo_dir to force a lock collision.
- **`coordctl doctor` end-to-end on this VM** (sacred-source + inbox_sweep digest
  checks, `origin/main` git show): the reviewed `origin/main` is a different lineage
  than this checkout's `main`, and doctor's digests are pinned to VM paths; running it
  here would report drift for environmental reasons, not code reasons.
- **Prefix-normalization / non-monotonic-generation / export dedupe / mirror glob
  depth / doctor host-awareness**: deliberately skipped — already on the runbook's
  "Known items the P2 plan must own"; re-reporting them adds no signal.
- **Huge-body memory pressure**: `read(n)` for very large `n` is a real allocation,
  but on localhost with a trusted operator I judged it lower value than F4 (same
  worker-thread surface) and did not push a multi-GB body on the full disk.

## Verdict

None of the eight is a shadow-mode blocker in the strict sense — in shadow, git stays
authoritative and coordd only observes on `127.0.0.1` for a single operator. So:

- **Recommended before shadow deploy (stability, low-risk one-liners):** **F4**
  (reject negative/oversized `Content-Length`) and **F8** (atomic cursor write) — both
  are cheap and prevent a stuck server / wedged mirror during the shadow soak.
- **Must fix before coordd is promoted from shadow to authoritative (P2):** **F1**
  (handoff must require an origin ref), **F2** (fence `set_state` + release the lease
  on terminal transition), **F3** (no reopening terminal tasks via `claim`), and
  **F5** (census must see unpushed commits outside `refs/heads`). These are the ones
  that let a normal actor record false evidence or corrupt lease/state integrity once
  coordd actually gates work.
- **P2 backlog, low severity:** **F6** (future-dated cron markers) and **F7**
  (frontmatter-date guard) — both harden the fabricated-clock defenses the plane is
  meant to embody.

Because I authored the code, treat every "must fix" here as a claim to be re-checked
by the independent reviewer, not a settled disposition.
