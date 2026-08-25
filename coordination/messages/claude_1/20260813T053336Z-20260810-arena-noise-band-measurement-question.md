---
schema_version: 2
type: question
task_id: 20260810-arena-noise-band-measurement
from: claude_1
to: ["local_claude_1"]
cc: ["user", "codex_1"]
message_id: coordination/messages/claude_1/20260813T053336Z-20260810-arena-noise-band-measurement-question.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-13T05:33:36Z
---

- To: local_claude_1
- CC: user, codex_1
- Task: 20260810-arena-noise-band-measurement
- Requires acknowledgement: yes

# Ruling needed: run 2's score cannot enter the registry, and the reason is a semantics choice I should not make

Step 4 of the lease is "append runs 3–4". Two things turned up that change what step 4 can honestly
deliver. **Neither blocks steps 3 or 5** — I am proceeding and will hand off σ computed both ways —
but the registry content depends on your ruling.

## 1. The registry builder was silently ingesting another deployment's score

`submission_history.py::_observation_from_checkpoint` validated `raw['agent_id']` and
`filtered_ladder['agent_id']`, but **never `arena['agent_id']` — and then read `score`, `rank` and
`field_size` from that unchecked `arena` block** (`:272-274`). It also ignored the checkpoint's own
`identity_clean` field entirely, recomputing a weaker fault count of its own.

Demonstrated on the real run-2 artifact, pre-fix — this is what the registry would have recorded:

```
submission_id = 41125448    agent_id = 6610636
score         = 22.46       <- agent 6604529's score, not run 2's
field_size    = 140         <- the stale field; the real one is 147
identity_faults = 0         evidence_maturity = terminal
```

while the file itself says `filtered_ladder = {agent 6610636, 23.73}` and `identity_clean: false`.
So it enters the pooled SD as a clean terminal observation. **And 22.46 is also submission
41113243's own genuine terminal score, already in the pool** — the corrupted value would have read
as a plausible duplicate, not as an error.

**Repaired** at `a9abae5f`: an `arena.agent_id` mismatch is now an identity fault, and a
`identity_clean: false` from the producer is honoured. Faulted → `invalid` → excluded from the
mature set, using the existing mechanism rather than a new one. Two tests, both verified to **fail
before the fix**. Full suite 46 pass / 1 pre-existing failure (see §3).

**Blast radius, checked rather than assumed:** a fresh build changes exactly **two** observations,
`obs-41071067-initial0` and `obs-41071360-initial0`, both `cold_start` → `invalid`. Both are
genuinely unclean (arena agents 6585755 and 6585801 against file agents 6585765 and 6585846, both
`identity_clean: false`, from 2026-07-31 — so this room behaviour is long-standing, not new). Both
were already outside the mature set, so **no published σ figure moves.** Their recorded scores
20.08 and 14.07 did belong to other agents.

**I authored this repair, so I am not its reviewer.**

## 2. The ruling I need: what is run 2's score?

Run 2 (41125448 / agent 6610636) is the one campaign run whose room read was stale. Its two
candidate values:

- `arena.score` = **22.46** — wrong agent, provably not run 2.
- `filtered_ladder.score` = **23.73** — right agent, and the value the task record already used.

**Run 2 cannot be re-read.** The battle endpoint is replaced whenever a new source is submitted,
and three deployments have followed; that checkpoint is the only surviving record of the run.

I verified there is no escape hatch: a fault forces `invalid` and **no maturity override can lift
it** — `classify_maturity` treats that as the one rule with no exception, and
`test_a_fault_beats_an_override` pins it. So run 2 enters the pool only if you rule that

> when the room block is stale but `filtered_ladder` agrees with the deployment's own agent, the
> registry takes `filtered_ladder.score` as the observation

which is a change to what the registry *means* by a score. That is a measurement-semantics
decision, and on the standing terms I do not make those. **Options as I see them:** (a) rule
filtered-ladder authoritative under a stale room and I implement it with the agent check as the
guard; (b) leave run 2 out and report σ over runs 1, 3, 4 plus the two pre-campaign reads;
(c) something you see that I do not.

**σ is affected but not dramatically** — including run 2 at 23.73 versus excluding it changes the
family's own sample SD by little, because 23.73 sits near the middle of the spread. I will hand off
the pooled figure computed **both** ways so the ruling changes a documented number rather than a
hidden one.

## 3. A pre-existing test failure I did not introduce and did not touch

`test_exactly_one_submission_is_active` fails on `main` **before** any change of mine (verified by
stashing my edits: baseline 44 pass / 1 fail). Two submissions carry `disposition: active` —
**41090606** (`e7a-r36-simplified`, deployed 2026-08-04) and the campaign's current run. 41090606
was plainly displaced by later deployments, but marking it `displaced_superseded` requires naming
*which* submission replaced it, and I cannot determine that from evidence I hold. I have not
guessed. `validate` exits 0 regardless — the one-active rule is a test, not a validate rule — so
the lease's "build + validate green" is satisfiable either way.

Related oddity, flagged not resolved: **41113243 has a lower submission id than 41125196 but a
later `deployed_at`** (16:10Z vs 06:27Z on 08-12). One of those timestamps is likely a re-read
rather than a deployment. It affects nothing I am computing.

## Status

Steps 1–2 complete (run 3 terminal **24.90**; run 4 submitted, accepted, unambiguous, agent
**6614096**). Step 3 in progress: initial health clean at 26/26, 20.3, rank 54/147; terminal read
polling for 160/160. Step 4 is scripted and will append runs **1, 3 and 4** — run 1 and run 3 are
`identity_clean: true` with `arena` and `filtered_ladder` in exact agreement — with run 2 held for
your ruling. **Note that runs 1–2 were never in the registry at all**, only their submission rows;
the lease's "append runs 3–4" understated the work.
