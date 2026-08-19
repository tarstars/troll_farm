# Codex-lane latched doorbell — design

**Status: PROPOSAL for the owner. Not carded, not approved, and explicitly OUTSIDE the
`20260819-sentinel-wake-on-work` build/review unit** (`codex_1`, `20260819T144334Z`). The accepted
Codex lane remains the launcher redirect unless the owner separately rules otherwise. Nothing here
changes the Claude lane, the sentinel's chartered behaviour contract, or `codex_1`'s launcher work.

Author: `claude_1` · 2026-08-19

## 1. Problem

The chartered sentinel assumes: *background process exits → harness re-invokes the agent.*
Gate zero measured this on both harnesses and they disagree.

- **Claude harness — HOLDS.** Verified by execution, active and idle cases both, wake latency
  under 16 s (a bound that includes model generation time). Scope: harness-tracked background
  tasks, exit-0 only.
- **Codex harness — FALSIFIED.** Process exit injects no turn. An explicit `write_stdin` poll is
  required. The synchronous ceiling is a measured **30.000 s** per call, and longer work converts
  to a poll-driven session with the same no-wake defect.

So on Codex there is **no push, only pull**. The question this design answers is not "how do we
make Codex wake up" — it cannot be woken — but *"how does an agent that cannot be woken avoid
missing work?"*

### 1.1 The arithmetic that rules out the obvious answer

In-session waiting on Codex costs one tool call per 30 s of wall-clock, and no scheduling trick
beats that ceiling: backoff spaces out *sweeps*, not *waiting*, because there is no call that
blocks longer than 30 s. A genuinely idle hour costs ~120 calls. **Idle-polling is therefore
rejected**, not for elegance but for price.

## 2. Key idea — latch, don't ring

The sentinel's result is made **sticky**. It writes what it found to a latch file before exiting;
the record persists. An agent reading that file at any later time still learns *work arrived at T,
and here are the triggering paths.*

**Coarse polling then costs latency and never costs a missed message.** That single property is
what makes the whole design safe, and it is what lets `codex_1` skip idle-polling entirely:

- **while working** — one cheap `--check` at task boundaries; cost ≈ 0
- **when genuinely idle** — end the turn; the launcher daemon or the user starts the next one

This is an honest doorbell you *glance at*, not one that rings.

## 3. Architecture

One program, two modes. The latch lives **inside `sentinel.py`** (§7 records why).

```
sentinel.py                     # blocking mode, unchanged contract
  ├─ fetch + sweep continuously, block while nothing changes
  ├─ every heartbeat interval → latch.heartbeat_seq += 1, rewrite latch
  ├─ work found      → latch{code:0, paths[...]}  → exit 0
  ├─ fetch failure   → latch{code:3}              → exit 3
  ├─ keepalive exit  → latch{state:EXITED_KEEPALIVE, code:2} → exit 2
  └─ double start    → refuse, latch UNTOUCHED    → exit 1

sentinel.py --check             # inert reader: no git, no network, no sweep, no writes
  └─ read latch → print one line → exit with the latched code, or 4
```

### 3.1 Latch file

`.sentinel/latch.json`, written atomically (temp file + `os.replace`) so a reader never observes a
half-written record.

```json
{ "schema": 1,
  "state": "QUIET" | "WORK" | "FETCH_FAIL" | "EXITED_KEEPALIVE",
  "code": 0 | 2 | 3,
  "heartbeat_seq": 1187,
  "heartbeat_utc": "2026-08-19T14:52:03Z",
  "started_utc": "2026-08-19T14:02:11Z",
  "pid": 31182,
  "paths": ["coordination/messages/local_claude_1/2026....md"] }
```

### 3.2 Exit codes

`--check` returns the latched code, preserving the chartered interface:

| code | meaning |
|---|---|
| 0 | work latched — `paths` names it |
| 2 | quiet, sentinel alive (keepalive) |
| 3 | fetch failure latched |
| **4** | **doorbell unusable — stale or never started (new)** |
| 1 | never returned by `--check` (double-start refusal belongs to blocking mode only) |

## 4. The failure this design exists to prevent

**A dead sentinel and a quiet sentinel are indistinguishable from the latch alone.** If the
process crashes, the file simply stops changing, and a naive reader reports `QUIET` forever while
mail piles up. That is the recurring defect of this programme — a green guard structurally
incapable of seeing what it is trusted to cover — and it has already produced, in this repo: a
tautological cross-sum that "verified" its own definition; a five-hour run of "sweep clean" while
an addressed verdict sat unread; and an `EXIT=0` that was `grep`'s status rather than the sweep's.

Therefore:

1. **Liveness = wall-clock age of `heartbeat_utc`, corroborated by `heartbeat_seq`.**
   *Correction to an earlier draft of this document, which claimed the counter must be the
   decision variable because clock skew could fake staleness.* That reasoning was wrong here: the
   recorded skew incident (+4 to +42 minutes across nine messages) was **cross-host message
   stamps**. The sentinel and `--check` run on the **same host against the same clock**, so
   wall-clock age is sound, and a single stateless read can evaluate it — which the counter alone
   cannot, since one invocation has nothing to compare against.

   The counter still earns its place, for a case age cannot see: a **wedged sentinel** that keeps
   rewriting the file while making no progress. Age looks healthy; `heartbeat_seq` frozen across
   two invocations exposes it. `--check` therefore keeps its own tiny `check-state.json`
   (last seq + when observed) — reader state, never the latch (see the no-write control in §5).
   Threshold: `stale_after = 5 × heartbeat_interval`, generous on purpose.
2. **`STALE` gates the CONCLUSION, not the TASK.** Exit 4 does not abort what the agent is doing —
   a suspended laptop must not kill a turn mid-work. It makes two specific conclusions
   unavailable until the sentinel is relaunched:
   - "my queue is empty"
   - "I am going idle"

   This aims the guard at the actual failure. The danger was never *working* with a dead
   sentinel; it was *concluding there is nothing to work on*.
3. **Three distinct texts under exit 4**, because they share a code but not a diagnosis:
   - `never started` — no latch file at all → *launch it*
   - `exited normally (keepalive at T)` — `state: EXITED_KEEPALIVE`, a clean chartered exit →
     *relaunch, nothing is wrong*
   - `stopped` — latch present, heartbeat aged out with no keepalive record → *it died; relaunch
     and find out why*

   Collapsing the middle case into `stopped` would report a routine keepalive as a fault and
   train the reader to ignore exit 4 — which is how a real death gets missed.

## 5. Controls — each observed firing, both directions

A control that has only ever passed is not evidence. Required, in the runner:

| control | must |
|---|---|
| live + quiet sentinel | `--check` → 2, and NOT 4 |
| killed sentinel, counter frozen | `--check` → 4 `stopped` |
| no latch file at all | `--check` → 4 `never started` |
| work latched, read much later | `--check` → 0 with the same `paths` (stickiness) |
| **`--check` inertness** | run with `GIT_DIR` pointed at a nonexistent path → still correct. A reader that cannot reach git **cannot** fetch; this makes inertness demonstrated, not intended |
| `--check` never writes | latch bytes identical before/after (sha256 compared) |
| half-written latch | truncated/corrupt JSON → exit 4, never a silent `QUIET` |
| keepalive exit | `--check` → 4 `exited normally`, NOT `stopped` |
| wedged sentinel | file rewritten, `heartbeat_seq` frozen across two `--check` runs → exit 4 |
| `--check` vs double-start guard | with a sentinel running, `--check` still returns; it is never refused with 1 |

## 6. Unmeasured on Codex — must be probed, must not be assumed

Everything about the Codex harness below is **unverified**, and the design must not be built past
it:

- **P1: does a Codex background process survive across agent turns?** Their probe polled within a
  single turn. This decides only **who launches the sentinel** — `codex_1` itself if yes, the
  launcher daemon if no — and changes nothing about `--check`.
- **P2: does it survive session teardown / long idle?** If no, the launcher daemon owns the
  lifecycle outright.
- **P3: does `exec_command` return EARLY when the watched process exits inside the yield window,
  or always burn the full 30 s?** Their `sleep 35` + 30 s yield could not observe this — the
  process had not exited yet. It does not affect this design (no idle-polling), but it is a real
  unmeasured fact about the harness and should not be inferred from the existing probe.

## 7. Decision record

**Latch inside `sentinel.py` rather than a separate reader.** A separate reader must know the
heartbeat interval to judge staleness, so the threshold would exist in two places; drift then
yields either false `STALE` or — far worse — `QUIET` about a dead sentinel. That is the "second
copy of the arithmetic" defect `codex_1` required removed from `gate1_runner.py` on 2026-08-19,
and which `local_claude_1` named the distilled lesson of that gate ("one counting path"). It also
keeps the charter's ONE review unit intact and the exit codes identical by construction rather
than by convention.

The cost of that choice is that an inert reader now lives inside a program whose whole purpose is
git-fetch-and-sweep. It is bought back **structurally, not by intention**: git and sweep imports
happen inside the blocking function, never at module scope, so `--check` cannot reach them even by
mistake — and the poisoned-`GIT_DIR` control in §5 demonstrates it rather than asserting it.

**Rejected:** separate reader (duplicated threshold); no latch at all, polling the process session
(loses stickiness — a result observed only at poll time can be missed); idle-polling for parity
with the Claude lane (~120 calls/hour, §1.1).

## 8. Out of scope

The sentinel's chartered behaviour, the Claude lane's adoption, `codex_1`'s launcher daemon, and
any Arena action. This proposal adds one responsibility to one program and one reader mode. If the
owner declines it, the Codex lane proceeds unchanged under the launcher redirect.
