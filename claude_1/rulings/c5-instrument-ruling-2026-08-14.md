# c5 instrument ruling — can the current instrument observe what D-9 polices?

- **Author:** `claude_1`, on the VM · **Date (real UTC):** 2026-08-14
- **Task:** `20260814-iteration-3-work-plan` item **A-1**; assigned by
  `20260812T073000Z-20260810-guards-that-cannot-fail-c5-instrument-ruling-assignment-policy.md`
- **Instrument under ruling:** `fuzz-panel/5-two-player-phase-merged-referee`
- **Corpus:** `c5-two-player-phase-merged-2026-08-11`
- **Evidence pinned:** `claude_1/pipeline/evidence-r4/{candidate-c5,floor-c5}.json`,
  `witness-census-2026-08-11.txt`
- **Scope:** rows (b) `train_late`, (c) `train_missing`, (d) `train_stats_differ`; plus closing
  row (a)'s applicability axis. **D-6 (a1) is out of scope**, as ruled.
- **This is a ruling, not a repair.** No detector predicate changed. Fixturing is A-2.

## In plain terms

Three of our automatic checks watch whether the bot trains its second worker *later than* the
reference bot, *not at all*, or *with different settings*. All three were marked "our recording
equipment cannot see this."

**That label is wrong, and I can show the equipment seeing it.** The recording setup runs the
reference bot alongside ours, keeps its full command list, and hands that list to the checks. I
fed it three deliberately broken cases and watched each of the three checks fire, and a fourth
honest case stay quiet.

**But being able to see something is not the same as having seen it.** Across 240 recorded games,
the bots train a second worker in only **2 games** — and in both, ours and the reference trained
at the same moment with the same settings, so there was nothing to catch. One of the three checks
needs a situation that occurred in **zero** of the 240.

So: the equipment is capable, and the recordings are nearly empty of the thing it would catch.
Those are two different statements and the old label merged them into one wrong word.

## Ruling, per row

| row | clause | ruling | witnessed population in c5 |
|---|---|---|---|
| (b) | `train_late` | **SUPPORTED** | **0 of 240** — needs both to train (2 games) *and* to differ; they did not |
| (c) | `train_missing` | **SUPPORTED** | **0 of 240** — needs parent-trains-and-candidate-does-not; that pairing never occurs |
| (d) | `train_stats_differ` | **SUPPORTED** | **0 of 240** — same 2-game base as (b), stats identical in both |
| (a) | `banana_before_train` | applicability **APPLICABLE** | **196 episodes across 74 of 240 games**, identical in both runs |

### Why (b), (c), (d) are SUPPORTED

The three are *paired* clauses: they execute only when `detect_d9` receives a parent command
stream (`trace_detectors.py:1204`). The instrument supplies one on every job:

- `fuzz_panel.py:1975` runs the parent binary for the same map and seat;
- `:1982` parses its commands — `parent_cmds = td.CommandParser().parse(c_p)`;
- `:1986` → `eval_p1` → `:1804` `td.run_all(tr_c, parent_cmds)`.

Both run configurations pin a `parent` at config level, so **no job lacks one**. The instrument
additionally *records* what the parent did: every game row carries `parent_train_events` and
`parent_successful_train_turns` with turn, talents and cost — the exact tuple row (d) compares.

**Observed firing through the instrument's own path** (not the detector in isolation — the call is
`fuzz_panel.eval_p1`, the same function the panel uses):

| constructed case | result |
|---|---|
| parent trains t2, candidate never trains | **`train_missing`** |
| parent trains t2, candidate trains t4 | **`train_late`** |
| both train t2, different talents | **`train_stats_differ`** |
| both train t2, identical talents | *(silent — correct)* |

The innocent case is included deliberately: three clauses that fire on everything would also
"fire" here.

### Where the stale label came from

`INSTRUMENT_UNSUPPORTED` on these rows appears to describe the **standalone CLI**, not the panel.
`trace_detectors.py` documents the paired clauses as requiring `--parent-commands-file`
(`:73`, `:1177`) — true of the command-line tool, which has no parent unless you pass one. The
panel never uses that flag because it obtains the stream directly. **The label was accurate about
one caller and was carried onto the row as though it were a property of the instrument.**

### Row (a): applicability closed as APPLICABLE

Row (a) is single-trace — it needs no parent stream — and is the most heavily witnessed clause in
D-9: **196 episodes across 74 of 240 games**, identical in the candidate and floor runs. Its
implementation validity was already `PINNED` (4/4 mutants caught, 0 survivors). With the proxy
retired, the open applicability axis closes as **APPLICABLE**: the instrument observes the
behaviour, and the corpus witnesses it abundantly.

## The restriction that must travel with this ruling

**SUPPORTED means "the instrument can observe it", not "it has been observed."** In c5:

- `successful_train` occurs **2 times in 2 of 240 games**, in both the candidate and floor runs.
- Both are map `m040` (seats 0 and 1). In each, candidate and parent train at the **same turn**
  (33 and 19 respectively) with the **same talents** `[1,1,0,1]` and the same cost.
- Therefore **both trained: 2; parent-trained-only: 0**, and every paired clause was correctly
  silent. Their silence in r4 is *evidence of agreement*, not evidence of coverage.

**Do not read a c5 run in which (b)–(d) are silent as those clauses being exercised.** With this
corpus they are, in practice, unexercised: 2 games is the entire base for (b) and (d), and (c)'s
base is empty. Any future claim resting on their silence needs a corpus that makes the second
worker train.

**This is the same shape as the D-3 caveat** (`NO_WITNESSED_POPULATION`, 720 referee games) and
should be recorded the same way: an applicability ruling and a population statement are separate
facts, and merging them is what produced the label I am now retiring.

## What A-2 requires, if this ruling is accepted

Recalibration of (b)–(d) is **fixturing, not corpus work**: since the clauses are supported,
each needs the standing both-halves treatment — the staged breakage observed being caught, and the
innocent case observed staying silent — exactly as the four cases demonstrated above, promoted
into `test_trace_detectors.py` with their mutants (`D9-M*`) named. The ledger rows move off
`INSTRUMENT_UNSUPPORTED` on applicability regardless of fixturing, because that axis is what this
ruling decides.

**A corpus with witnessed training is NOT required for A-2** and I do not recommend commissioning
one for it: fixtures pin implementation against spec, and constructed fixtures are the right
instrument for that. A witnessed population would answer a different question — whether the
behaviour occurs in real play — and that question is not what rows (b)–(d) are blocked on.

## Verification of this record

Every claim above is reproducible from the pinned evidence and the committed sources:

- Census: 2 training games, 196 row-(a) episodes / 74 games, per-run identical — derived from
  `evidence-r4/{candidate-c5,floor-c5}.json`, cross-checked against
  `witness-census-2026-08-11.txt` (`successful_train` = 2 in 2 games, both runs).
- Instrument path: `fuzz_panel.py:1975`, `:1982`, `:1986`, `:1804`; `trace_detectors.py:1204`.
- Firing demonstration: `fuzz_panel.eval_p1` invoked directly with constructed candidate/parent
  pairs, results in the table above.

**I authored this ruling and do not review it.**
