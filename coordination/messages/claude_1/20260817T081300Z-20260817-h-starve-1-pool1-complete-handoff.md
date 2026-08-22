---
schema_version: 2
type: handoff
task_id: 20260816-h-starve-1-standing-troll-audit
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/claude_1/20260817T081300Z-20260817-h-starve-1-pool1-complete-handoff.md
artifact_ref: agent/claude_1
artifact_commit: 94e193200bf6cf25a381b4e2cad2902f30c65d52
artifact_paths: ["claude_1/hstarve1/oracle.py", "claude_1/hstarve1/coverage.py", "claude_1/hstarve1/anchor.py", "claude_1/hstarve1/instrumented-hstarve2.rs"]
created_utc: 2026-08-17T08:13:00Z
---

- To: codex_1 (pool #2 re-review), local_claude_1
- CC: user
- Task: 20260816-h-starve-1-standing-troll-audit
- Requires acknowledgement: yes

# handoff: POOL #1 COMPLETE — all five instrument repairs done, ready for pool-#2 re-review

`Pool: 4/12 done` at time of writing; item 1 is now ready to close on your acceptance.
Artifact `94e19320`, pushed and remote-verified. **No cause label is asserted anywhere in this
handoff** — the evidence gate holds until you accept.

## For the owner, in plain terms

The measuring tool is rebuilt and ready for the reviewer. The last piece was the most
embarrassing: the tool never actually had a **rule** for which troll it was watching. It had an
unwritten habit — "the one that isn't the dancer" — with no definition and, worse, **no complaint
when it found nobody at all**.

That silence hid something. **Three of the 34 situations have only one troll**, so there was no
second troll to examine — and my earlier tables just printed 31 lines instead of 34 without
mentioning it. A missing line looked exactly like a situation with nothing to say. It now says so
out loud.

## The five repairs

| repair | evidence |
|---|---|
| eligible-action oracle (capability × per-turn fruit state × reachable sink) | 8 cases; OSC-012 `0/193` eligible vs old `193/193` |
| negative controls **observed firing** | zero-capability and walled-in arms, **each with a positive twin** |
| direct candidate-kind + chosen-action logging | verb of every candidate per unit-turn; emitted line per turn |
| exact one-row-per-turn coverage + duplicate rejection | 400 unit-turn / 200 chosen rows per situation; gaps and dupes both observed rejecting |
| **anchor-unit rule** | 6 cases; 31 anchored, **3 reported `NO_ANCHOR_SINGLE_UNIT`** |

**Runner parity is proven, not argued:** the diagnostic loop must produce a byte-identical command
stream to `regression_tests.run_binary_custom` on every situation or nothing downstream is
emitted — identical on all tested. It calls `apply()` **and** `grow()` and fails **closed** on
early stdout closure, the two defects my previous bespoke loop shipped.

## The anchor rule, stated so you can attack it

- **dancer** = the single unit named by `window.unit`;
- **anchor set** = every own unit present at entry that is not the dancer;
- an empty anchor set is **not skipped** — it is reported `NO_ANCHOR_SINGLE_UNIT`.

**`NO_ANCHOR_SINGLE_UNIT` is a coverage state, not a cause label.** It says which unit the
instrument looked at, never why anything happened. It is deliberately outside the registered
`CAUSE_LABEL_TOKENS` and will never be serialized into a cause table.

Validation refuses, each observed: a dancer absent from the entry roster, a dancer that is an
opponent unit, and a situation with no own units at entry.

**This is my definition, not one I was given.** I asked for the intended one an hour ago and
implemented my best reading rather than stall the gate. If the intended anchor differs — say, the
longest-idle unit rather than every non-dancer — it is a one-function change and I will make it
exactly.

## What I have deliberately not done

No sweep, no table, no labels. Pool #3 begins only on your acceptance, will serialize exactly
`NO_GOAL_ASSIGNED` / `GOAL_SPLIT_WRONG` / `WORLD_INTERACTION` / `CANNOT_USE_WORK` / `NOT_STARVED`,
and will carry `review_ref:` pointing at your acceptance review.

I will also not map my old labels onto the new five by inference from old data — that mapping has
to fall out of the new candidate/chosen logging, and if a case resists all five tokens I will say
so rather than force it.

## Boundaries

Resident byte-exact `98628e98…`; no cure code; no Arena action; T-1 frozen with the half-swap
fixture as recorded debt.
