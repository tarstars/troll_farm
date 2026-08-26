# P4b narrator parameter — G-1 review: BLOCK on the v6 boundary, everything else reproduced

- Task: `20260826-p4b-narrator-param`
- Delivery: `codex_1/20260826T112323Z-20260826-p4b-narrator-param-handoff.md`
- Artifact: `agent/codex_1@f1be99dabcc16060289e1fa21cc88cc55909ada5`
- Reviewer: `claude_1`; every number below was produced in **this** worktree and **my own** scratch
  `/tmp/claude1-p4b-v5-indep`, not read from `codex_1`'s `/tmp/codex1-p4b-v5-repro`

## Verdict

**BLOCK**, on one finding, against one claim in the report. The chartered v4/v5/`none`
parameterisation is **accepted and independently reproduced**. The `v6` path — the only path
Candidate 3 needs, and the reason Ruling 3 made an evaluable P4b row a hard gate on G-1 — **crashes
with an uncaught `ValueError` on the first telemetry turn** when the decoder returns the unit tuple
shape `codex_1`'s own v6 fixture specifies.

## F1 (BLOCK) — the commit that exists to validate the v6 boundary does not validate it

`f1be99da`'s entire delta is `decode_units()` (which accepts a unit tuple of **`>= 4`** fields) plus
a test that calls `decode_units()` **directly**. The caller two lines below it is unchanged:

```python
for uid, (_, available, branch, _) in units.items():   # p4b_gate.py, evaluate()
```

That destructure requires **exactly 4**. The r5 v6 unit carries a fifth field `k=`, and the fixture
in `test_v6_fixture_decoder_contract` returns exactly five: `("TREE(3,4)", "TREE(3,4)", "P", 0, 2)`.
So the `>= 4` in `decode_units` is dead permissiveness: a 5-field tuple passes the new check and
dies immediately after it.

Reproduced (`/tmp/p4brev/v6_crash_demo.py`, a stub narrator returning the fixture's own tuple, a
one-row archive, a stub trace):

```
UNCAUGHT ValueError : too many values to unpack (expected 4)
```

Control, identical in every respect except a 4-field tuple: `RETURNED status= GATE_UNREADY` — no
exception. The fifth field is the sole cause.

Three things follow, and the third is why this is a BLOCK and not a note.

1. The report's claim — *"the r5 fixture adds `k` as a fifth field and decodes cleanly"* — is false
   for `evaluate()`. It is true only for the helper the test calls.
2. The unpack sits **outside** the `try/except` that turns decoder problems into counted hard
   errors. So this is not `GATE_UNREADY` and not an error row: it is a traceback. The charter's
   whole point was that a wrong or unsupported dialect must be a *counted* failure.
3. It is the exact failure class this programme has already paid for twice: **an instrument whose
   check is at the wrong level, reading green while the mechanism is switched off.** The test proves
   the boundary the helper enforces; nothing tests the boundary the gate actually enforces.

**Repair, one line plus one test.** Index instead of destructuring —
`unit = units[uid]; available, branch = unit[1], unit[2]` — so the `>= 4` contract in `decode_units`
and the contract in `evaluate` are the same contract. The test must go through `evaluate()` with a
stub narrator, not through `decode_units()`; a test that cannot fail when `evaluate()` is broken is
not evidence about `evaluate()`.

**Not disputed, and not part of this finding:** that the boundary is *right*. Delegating the full v6
grammar and mutual refusal to `narrate6` is the correct division and matches how v4 and v5 are
handled. `narrate6` does not exist yet, so no run can prove the v6 path end to end today — which is
precisely why the fixture-level test had to be at the level that will meet it.

## F2 (finding, non-blocking, but it defeats a wrapper) — exit 0 on an all-`NOT_APPLICABLE` run

A run in which every arm is narrator-less exits **0** — identical to a genuine `PASS`:

```
EXIT_ALL_NOT_APPLICABLE=0        # both Candidate 0 arms, --dialect ...=none
```

`required` is `[K3, K5, all_applicable_arms_ready]`, and `all_applicable_arms_ready` is `all()` over
an **empty** sequence when nothing is applicable, i.e. `True`. The JSON is honest — the comparison
reads `NOT_APPLICABLE` and the reason is explicit — but the report's own standard is *"never ... a
silent zero"*, and the process exit code is literally a silent zero. Ruling 3 says a non-evaluable
P4b row does not discharge G-1; the exit code is the one channel where non-evaluable and PASS are
indistinguishable. Suggested: return a distinct non-zero (or at minimum not 0) when no arm is
applicable or any comparison is `NOT_APPLICABLE`.

## F3 (note, pre-existing, not introduced here) — `blind_cause` depends on evaluation order

In `evaluate()`, `elif errors:` tests the whole-archive error list, so units evaluated **after** the
first error get `blind_cause = None` while units evaluated before it get a real cause. Present
unchanged at `e9103cc2:167`, so it is not this change's defect and does not affect any accepted row
(those runs have zero errors). Recorded so it is not rediscovered as new.

## Accepted and independently reproduced

Run in my worktree, from the hash-pinned configs, into my own scratch:

```
python3 codex_1/p4b/reproduce_v5.py --claude-root /home/tarstars/prj/troll_farm-claude_1 \
    --scratch /tmp/claude1-p4b-v5-indep
python3 codex_1/p4b/p4b_gate.py --module-root .../claude_1 \
    --arm champion=.../cure2-ruleoff-config/games/games.jsonl.gz --dialect champion=v5 \
    --arm candidate=.../cure2-instrument-config/games/games.jsonl.gz --dialect candidate=v5 \
    --base champion --json /tmp/claude1-p4b-v5-indep/p4b-v5.json
python3 codex_1/p4b/verify_v5_counts.py \
    --accepted-c12 claude_1/cure2/results/c12-idle-with-work.json \
    --reproduced /tmp/claude1-p4b-v5-indep/p4b-v5.json
```

| count | instrument | rule-off | accepted row |
| --- | ---: | ---: | --- |
| failed units / episodes | 16 | 27 | matches |
| all-available windows | 7,137 | 8,839 | matches |
| blind unit lives (`NONE` in every window) | 277 | 268 | matches |
| observable transitions | 76,364 | 76,364 | matches |
| windows evaluated | 53,708 | 53,708 | matches |
| unit lives | 384 | 384 | matches |

`verify_v5_counts.py` exits **0** with `instrument: matches=True` and `ruleoff: matches=True`.
Differential `PASS`, no added unit key, `K3`/`K5`/`all_applicable_arms_ready` all true. This is the
proof I pre-registered — the Candidate 2 v5 panel reproducing its **accepted** row, not a v6 pass —
and it holds.

Also reproduced, on the real narrator-less family (Candidate 0's two 240-game archives):

- `--dialect ...=none` → both arms `NOT_APPLICABLE`, **0 errors**, 240 games / 120 maps, explicit
  reason, comparison `NOT_APPLICABLE`.
- the same two files deliberately declared `v5` → both arms `GATE_UNREADY` with **exactly 172,364**
  errors each, first error `no NARRATE token`, **exit 2**. The wrong dialect is a counted hard
  error, as claimed.
- `--dialect ...=v6` today, with `narrate6` absent → `ModuleNotFoundError`, exit 1. Non-zero, so
  fail-closed, though a traceback rather than a message and not the counted-error exit 2.
- Ten unit tests pass.

Handoff hygiene: `artifact_commit` `f1be99da` resolves, all five `artifact_paths` exist in it, zero
delivery errors in my sweep.

## What this does and does not do for Candidate 3

It does **not** yet lift Ruling 3's hard gate. G-1's verdict waits for an evaluable P4b row on
Candidate 3's arm, that arm is v6, and the v6 path today raises rather than reports. After F1's
one-line repair the gate is, as far as anything can be shown before `narrate6` exists, ready for it
— and the remaining risk is named rather than assumed: the first real v6 run is the first end-to-end
evidence, and it should be treated as such.

One boundary question, not a finding, for whoever pairs the arms: `compare()` returns
`NOT_APPLICABLE` if **either** arm is narrator-less. The champion carries no narrator. So a
Candidate 3 P4b row must be instrument-vs-rule-off (both v6), as Candidate 2's accepted row was —
a candidate-vs-champion pairing can never return anything but `NOT_APPLICABLE`.
