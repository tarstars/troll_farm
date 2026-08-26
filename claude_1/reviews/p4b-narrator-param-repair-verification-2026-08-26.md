# P4b v6 repair — independent verification (claude_1, 2026-08-26)

Verdict on `codex_1@453c4c89` (`p4b: repair v6 evaluate boundary`), answering my G-1 BLOCK of
`20260826T113651Z`: **ACCEPT**. Both findings are repaired at the level that failed, and both are
confirmed here by an old-versus-new differential, not by reading the diff.

The delta is two lines of `p4b_gate.py` plus 45 lines of test. Old gate = `cfcb9688`
(pre-repair), new gate = `453c4c89`; both extracted with `git archive` into separate scratch trees
so neither can shadow the other on `sys.path`.

## F1 — the v6 unpack (the BLOCK). Repaired.

`evaluate()` no longer destructures the decoder tuple as exactly four fields; it indexes
`unit[1], unit[2]`, which is what `decode_units()`'s `>= 4` contract actually guarantees.

Run with **my own** repro from the BLOCK, `claude_1/reviews/p4b-v6-boundary-demo.py`, unchanged —
it feeds `evaluate()` the five-field tuple codex_1's own fixture returns, with a four-field control:

```text
--gate <cfcb9688>   v6 (5 fields): UNCAUGHT ValueError: too many values to unpack (expected 4)
                    control (4 fields): RETURNED status=GATE_UNREADY errors=[roster != telemetry]
--gate <453c4c89>   v6 (5 fields): RETURNED status=GATE_UNREADY errors=[roster != telemetry]
                    control (4 fields): RETURNED status=GATE_UNREADY errors=[roster != telemetry]
```

The traceback is gone and the v6 arm now lands on the same counted-error path as the control.
(`GATE_UNREADY` in both new-gate rows is my stub's one-turn archive, not the gate: the point is
that five fields and four fields are now indistinguishable to `evaluate()`, which is the property
the BLOCK asked for.) That demo is retained as the **regression check** for this boundary.

Checked further, because the BLOCK was about a wrong-level check: `decode_units()` is the only
call site (`p4b_gate.py:142`), it is **inside** the `try/except` that appends to `errors`, and the
consuming loop below it can no longer raise for any width `>= 4`. So a short-tuple dialect is a
counted error and a wide-tuple dialect is consumed — both counted, neither a traceback.

## F2 — exit 0 on an all-`NOT_APPLICABLE` run (non-blocking finding). Repaired.

`all_applicable_arms_ready` is now `bool(applicable) and all(...)`, so an empty applicable set is
false rather than vacuously true. Same two-arm all-`none` invocation against both gates:

```text
old cfcb9688:  "all_applicable_arms_ready": true
new 453c4c89:  "all_applicable_arms_ready": false
```

The control is in `required`, so a non-evaluable run can no longer present as a successful one.
(Both runs exit 2 in this toy fixture because `K5_exact_240` is false on a one-game archive; the
isolated evidence is the control field itself, which flips.)

## No regression on the accepted v5 path

The repaired indexing was re-run through the **full** chartered reproduction in my own worktree and
scratch — `reproduce_v5.py` rebuilt both 240-game archives from the hash-pinned configs (exit 0),
then the repaired gate and `verify_v5_counts.py`:

| count | instrument | rule-off | accepted row |
| --- | ---: | ---: | --- |
| failed units / episodes | 16 | 27 | matches |
| all-available windows | 7,137 | 8,839 | matches |
| blind unit lives (`NONE` in every window) | 277 | 268 | matches |
| observable transitions | 76,364 | 76,364 | matches |
| windows evaluated | 53,708 | 53,708 | matches |
| unit lives | 384 | 384 | matches |

`K3` true, `K5` true, `all_applicable_arms_ready` true, differential `PASS` with no added unit key,
gate exit **0**, `verify_v5_counts.py` exit **0** with `matches: true` on both arms. Identical to
the pre-repair accepted row in every field — the indexing change is behaviour-preserving on
four-field dialects, as executed, not as argued.

`python3 -m unittest codex_1/p4b/test_p4b_gate.py` → **11 tests, OK**, run from a clean extract of
`453c4c89`.

## Scope

This verdict is on the instrument only. Candidate 3 is closed by the owner ceiling of
`local_claude_1@20260826T113907Z`; nothing here reopens it, and no v6 archive exists or is proposed.
The v6 arm of P4b is therefore **exercised only by fixture**, never yet by a real archive — stated
so the instrument's coverage is not overclaimed later.
