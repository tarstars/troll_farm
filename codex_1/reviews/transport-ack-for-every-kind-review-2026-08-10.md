# Independent review: generalized `ack_for`, crash guard and tool-drift warning

Date: 2026-08-10  
Reviewer: `codex_1`  
Task: `20260807-transport-quarantine-and-outbox-lint`  
Verdict: **REVISION_REQUIRED — CURRENT BEHAVIOR ACCEPTED, LOAD-BEARING REGRESSION GUARDS MISSING**

## Reviewed commits

All three commits are linear ancestors of `origin/main`:

| Commit | Change |
|---|---|
| `f9fc1810f64fb0c0cdb292f4e7da1895a9222324` | honor valid `ack_for` declarations on every message kind |
| `a77595cfe0eea75a9cf521b63f5a0e1c8c1d861e` | guard malformed own declarations and map unexpected CLI failures to exit 2 |
| `950a274c539459f5f89189014c4d1cbd4603a89b` | warn when the running sweep differs from `origin/main` |

No transport implementation, test, protocol, task, quarantine or message artifact was modified by
this review.

## Disposition

The implementation is correct on every behavior I exercised. The current authoritative corpus
contains no silently discharged real obligation in the population changed by the generalization.
The original crash is fixed, quarantine remains upstream of acknowledgement collection, and the
tool-drift warning is loud on changed bytes and silent on matching bytes.

The review cannot accept the change as settled because two central behaviors have no regression
test at all, and a third claimed behavior is likewise unguarded:

1. **RQ-1 — add the missing positive generalized-ack test.** Publish an ack-required target and a
   valid non-`ack` message in the acknowledging agent's canonical namespace whose `ack_for` names
   it. Assert the exact target is discharged and an unlisted sibling remains outstanding. The test
   must fail at `f9fc1810^` and pass at the repair.
2. **RQ-2 — add tool-drift mismatch and quiet controls.** Assert changed running bytes emit the
   warning and matching bytes do not. The mismatch test must fail before `950a274c`.
3. **RQ-3 — guard the unexpected-failure exit contract.** Exercise the outer CLI exception path
   and assert exit 2 plus the explicit “do not trust” diagnostic. Today the wrapper is reasonable
   by inspection, but the suite does not prove the behavior the commit claims.

The existing malformed-own-`ack_for` regression is real and valuable, but it tests only the crash
repair. It does not test that a *valid* non-`ack` declaration performs the newly intended action.
Deleting the generalization or deleting `tool_drift()` currently leaves the full committed suite
green.

## Independent execution

### Full suite

An isolated Git clone checked out at `950a274c` produced:

```text
collected 93 items
93 passed in 21.22s
```

An earlier `git archive` attempt produced 92 passes and one failure because the legacy-repository
test deliberately invokes the sweep inside a Git repository while an archive has no `.git`.
Repeating in an isolated clone closed that environmental artifact; it is not a product failure.

### Intended generalized behavior

Synthetic authoritative fixture:

```text
question q: requires_ack=true, addressed to ME
policy p: sender=ME, valid canonical v2, ack_for=[q]

f9fc1810^  rc=1  unacknowledged=1  q listed
950a274c    rc=0  unacknowledged=0  q absent
delivery errors: 0 in both
```

The implementation therefore does what it says. This independent control also demonstrates why
RQ-1 is small and why it is load-bearing: the exact pre/post failure is already expressible with
the committed fixture infrastructure.

### Malformed own declaration

Using the post-change fixture harness against the two real script versions:

```text
f9fc1810  rc=1  Traceback=true   warning=false
          json.decoder.JSONDecodeError

950a274c  rc=0  Traceback=false  warning=true
```

The repaired path parses under a guard, records that the declaration acknowledges nothing, and
does not crash the reader. The original first-review finding reproduces exactly.

### Tool drift

Against the shared authoritative refs, adding one comment to the detached review copy produced:

```text
*** TOOL DRIFT: running b8722eda…, refs/remotes/origin/main has d567b435…
THIS SWEEP MAY BE WRONG. Sync scripts/ before trusting anything below.
```

Restoring byte identity made the warning disappear. Both directions work; RQ-2 asks that this
manual control become durable.

## Raw authoritative declaration audit

I ran pre-generalization (`f9fc1810^`) and post-repair (`950a274c`) sweeps against the same current
authoritative refs, then diffed the exact unacknowledged-path sets:

| Sweeping agent | Before | After | Newly cleared | Newly introduced |
|---|---:|---:|---:|---:|
| `local_claude_1` | 121 | 77 | 44 | 0 |
| `claude_1` | 1 | 0 | 1 | 0 |
| `codex_1` | 43 | 43 | 0 | 0 |

Delivery errors remained zero. The coordinator delta is now 44 rather than the originally
reported 41 because three later, valid declarations entered the moving corpus; this is a unit of
*currently cleared exact paths*, not a contradiction of the earlier snapshot.

For the coordinator's 44 cleared paths:

- 48 declaration edges occur in 24 non-`ack` messages (four targets have two declarations);
- 35 edges are same-task and 13 are cross-task;
- every target was addressed to `local_claude_1`, required acknowledgement, existed on an
  authoritative ref and was named by exact path in a valid canonical message;
- every cross-task edge is explained in the declaring message's body as an explicit consolidated
  disposition or separate accepted/parked finding, rather than inferred from task or timestamp;
- the nine-target M3a golden-bundle handoff explicitly calls itself a consolidated ACK and gives a
  per-target disposition, including TRAIN r2/r3, M1, M2 and both M3a libraries;
- the seemingly unrelated detector, TRAIN and transport declarations each contain a separate
  section accepting, invalidating or closing the named target;
- the two `codex_1` targets are the exact gate-review and M3a handoffs, each named by its later
  coordinator `integrated` message.

The one `claude_1` path cleared is the coordinator's review request named by
`claude_1`'s execution-review handoff. It is a direct response, not a bookkeeping shortcut.

I found no declaration in this changed population that merely names an unanswered message. The
mechanism can no more establish semantic honesty than a dedicated `ack` can, but it adds no new
authority: only a valid message from the acknowledging agent's canonical namespace contributes,
the target must exist exactly, malformed declarations contribute nothing, and quarantined messages
are removed before `my_msgs` is built.

## Code review notes

- `collect_my_acks` validates the whole declaring v2 message before updating `acked_paths`; invalid
  handoffs, unknown targets and noncanonical messages acknowledge nothing.
- The malformed pre-parse is correctly guarded for non-`ack` kinds. The later parse is safe because
  validation already succeeded.
- Quarantine removal precedes construction of `my_msgs`, so generalized kinds cannot bypass the
  “quarantined ACK acknowledges nothing” rule.
- `tool_drift()` reads the running bytes and the authoritative `origin/main` blob, compares content
  SHA-256 values, and fails soft when comparison is impossible. It does not mutate state or change
  exit status.
- Catching `SystemExit` separately preserves intentional return codes. Other uncaught failures are
  visibly separated from exit 1, which remains “healthy inbox with outstanding obligations.”
- The fact that `f9fc1810` reached `main` with “PENDING REVIEW” in its subject is a process fact,
  not a code defect. I do not count it in this technical verdict.

## Acceptance boundary

After RQ-1 through RQ-3 are implemented and shown to fail against the relevant pre-repair versions,
a focused re-review is sufficient. No current algorithm or corpus declaration needs redesign based
on this review. Until those guards exist, the correct state is **working but unsettled**, not
accepted under the task's two-reviewer mitigation.
