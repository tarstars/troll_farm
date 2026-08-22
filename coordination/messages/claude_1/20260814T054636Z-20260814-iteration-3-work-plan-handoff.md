---
schema_version: 2
type: handoff
task_id: 20260814-iteration-3-work-plan
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260814T054636Z-20260814-iteration-3-work-plan-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 2ab0be5d66026181369b61ca8a54854a10bfa367
artifact_paths: ["claude_1/rulings/c5-instrument-ruling-2026-08-14.md"]
created_utc: 2026-08-14T05:46:36Z
---

- To: local_claude_1, codex_1
- CC: user
- Task: 20260814-iteration-3-work-plan
- Requires acknowledgement: yes

# A-1 delivered: the c5 instrument CAN see what D-9 (b)–(d) police — and has almost never seen it

## For the owner, in plain terms

Three automatic checks watch whether our bot trains its second worker **later than** the reference
bot, **not at all**, or **with different settings**. All three were marked *"our recording
equipment cannot see this."*

**That label is wrong, and I can show the equipment seeing it.** The setup runs the reference bot
alongside ours and keeps its full list of moves, then hands that list to the checks. I fed it three
deliberately broken cases and watched each check fire — and a fourth, honest case stay quiet.

**But being able to see a thing is not the same as having seen it.** Across 240 recorded games the
bots train a second worker in only **2 games**, and in both, ours and the reference trained at the
same moment with the same settings — so there was nothing to catch. One of the three checks needs a
situation that occurred in **zero** of the 240.

Those are two separate facts, and the old label had merged them into one wrong word. The equipment
is fine; the recordings are nearly empty of the event.

## Ruling

Record: `claude_1/rulings/c5-instrument-ruling-2026-08-14.md` at `2ab0be5d` (pushed, remote
verified). Instrument `fuzz-panel/5-two-player-phase-merged-referee`, corpus
`c5-two-player-phase-merged-2026-08-11`.

| row | clause | ruling | witnessed population in c5 |
|---|---|---|---|
| (b) | `train_late` | **SUPPORTED** | **0 of 240** |
| (c) | `train_missing` | **SUPPORTED** | **0 of 240** (its precondition never occurs) |
| (d) | `train_stats_differ` | **SUPPORTED** | **0 of 240** |
| (a) | `banana_before_train` | applicability → **APPLICABLE** | **196 episodes / 74 of 240 games** |

**Why supported.** The three are paired clauses, live only when `detect_d9` gets a parent command
stream (`trace_detectors.py:1204`). The panel supplies one on every job: it runs the parent binary
(`fuzz_panel.py:1975`), parses its commands (`:1982`), and forwards them through `eval_p1`
(`:1986`) to `td.run_all(tr_c, parent_cmds)` (`:1804`). Both configs pin a parent, so no job lacks
one; and each game row already records `parent_train_events` with turn, talents and cost — the
exact tuple row (d) compares.

**Observed firing through the instrument's own path** — `fuzz_panel.eval_p1`, not the detector in
isolation: parent-trains/candidate-never → `train_missing`; parent t2 / candidate t4 →
`train_late`; same turn, different talents → `train_stats_differ`; same turn, same talents →
silent. The innocent case is in there deliberately, because three clauses that fire on everything
would also have "fired" here.

**Where the stale label came from.** `INSTRUMENT_UNSUPPORTED` describes the **standalone CLI**,
which needs `--parent-commands-file` (`trace_detectors.py:73`, `:1177`). The panel never uses that
flag because it obtains the stream directly. The label was true of one caller and was carried onto
the row as if it were a property of the instrument.

## The restriction that must travel with this ruling

**SUPPORTED means "can observe", not "has observed."** `successful_train` occurs 2 times in 2 of
240 games in *both* runs; both are map `m040` seats 0/1; candidate and parent train at the same
turn (33, 19) with identical talents `[1,1,0,1]`. So both-trained = 2, parent-trained-only = 0, and
every paired clause was correctly silent.

**Do not read a silent (b)–(d) in a c5 run as those clauses having been exercised.** Same shape as
the D-3 `NO_WITNESSED_POPULATION` caveat, and it should be recorded the same way — an applicability
ruling and a population statement are different facts, and merging them is exactly what produced
the label I am retiring.

## What I did NOT do

**I have not touched the ledger.** Rows 43–46 still read `INSTRUMENT_UNSUPPORTED` on applicability.
The ruling decides that axis, but applying my own unreviewed conclusion to shared tallies — which
feed the audit's published counts and its prose-vs-data check — is the same error class as taking a
denominator decision on my own work. **The four applicability edits are held pending your
acceptance**; on your word I apply them in one commit and re-run the check.

No detector predicate changed. No fixture written — that is A-2. No Arena action.

## For A-2, if this is accepted

Recalibration is **fixturing, not corpus work**: the four demonstrated cases promote into
`test_trace_detectors.py` with their `D9-M*` mutants named, under the standing both-halves rule.
**A corpus with witnessed training is not required for A-2 and I do not recommend commissioning
one for it** — fixtures pin implementation against spec, and a witnessed population answers a
different question (whether the behaviour occurs in real play) that these rows are not blocked on.

**I authored this ruling and review none of it.**
