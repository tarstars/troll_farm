# 20260810-guards-that-cannot-fail: find and fix every check that passes regardless of what it checks

- Status: **OPEN — owner-directed 2026-08-10.** Sub-items G1–G6 have individual owners.
  **2026-08-12:** G1 ✅ integrated (merge `59415301`, project_host gate 1679/0). G3+G4
  claimed by `local_claude_1`. **G6 owner go-ahead GRANTED — full scope, D-9 row (a)
  first** (in-session owner decision 2026-08-12, relayed in
  `coordination/messages/local_claude_1/20260812T061500Z-20260810-guards-that-cannot-fail-g6-go-ahead-policy.md`).
- Record owner / integrator: `local_claude_1`
- Area: tooling integrity; successor to the failures listed below
- Base commit: `origin/main` at claim time
- Progress lease: 15 minutes without remotely inspectable progress; phase markers renew it
- Created UTC: 2026-08-10T08:30:00Z

## Outcome

Every guard in this repository either demonstrably fails when the thing it guards is broken, or
is removed. A check that cannot fail is worse than no check: it costs the same to run and it
buys false confidence.

## Why now — seven instances in one week, and I caused four

| # | instance | class |
|---|---|---|
| 1 | `tool_drift` test would have asserted against a precondition the fixture never built (`origin/main:scripts/` absent → comparison returns `None` unconditionally) | **no precondition** |
| 2 | exit-2 wrapper lived inline in `__main__`, unreachable by any test; shipped unexercised | **unreachable guard** |
| 3 | 92 tests passed across a change that introduced a crash — the malformed-field test publishes as `PEER`, routing through a different code path than the one changed | **wrong path** |
| 4 | `lint_outbox` run as `lint \| tail -3 && commit && push` — pipeline exits with `tail`'s status, so `&&` never gated on the lint. Ran that way a whole session; it printed `errors (1)` and the push proceeded | **disarmed harness** |
| 5 | `run_mutations.py` ended `return 0 if control_green else 1` — an experiment whose mutants never patched or compiled still reported success | **disarmed harness** |
| 6 | first M3a verification passed on **pre-repair** code; the control was never shown to fail | **no negative control** |
| 7 | 22 of 47 detector branches have no fixture at all — never shown to fire | **no fixture** |

Instances 1, 2, 3 and 4 are the integrator's. This task exists because that rate is not
survivable.

## Measured surface (integrator, 2026-08-10)

```text
test files 426 · test functions 1587
[A] no check of ANY kind (bare assert / assertX / pytest.raises):   6
[B] assertion that cannot fail (tautological range or literal):     6
```

**Read [A] carefully:** a naive scan for bare `assert` reported **83**; counting `self.assertX`
and `pytest.raises` brings it to **6**. The first number was 92% false positive. Do not re-run
the naive version and report 83.

## Sub-items

### G1 — the twelve known vacuous checks · owner `codex_1`

The 6 [A] and 6 [B] above. For each: break the thing it checks, confirm the test fails, restore.
Fix or delete any that cannot be made to fail. Two of [B] are the integrator's own
(`test_inbox_sweep.py`), and `assert result.returncode in (0, 1, 2)` is true of essentially every
run. Mechanical, bounded, no design judgement.

**✅ DONE 2026-08-11 / INTEGRATED 2026-08-12.** Implementation `7af07a6f`; report
`codex_1/reviews/g1-vacuous-check-repair-2026-08-11.md` (pinned at `559030c3`); nine
deliberate production mutations across all twelve classes caught; full-suite gate on
project_host 1679 passed / 0 failed; integration merge `59415301`.

### G2 — negative controls for the transport suite · owner `claude_1`

96 tests in `test_inbox_sweep.py` + `test_lint_outbox.py`, authored by the integrator, guarding
tooling the integrator also wrote. Establish which of them actually fail when their subject is
broken. Full mutation is likely overkill; a sampled or targeted pass is acceptable if the sampling
rule is stated. **Reviewer must not be the integrator** — this is the one sub-item where that
matters most.

### G3 — precondition audit · owner `local_claude_1` (claimed 2026-08-12)

Find tests whose setup never creates the condition being asserted (instance 1). Hard to automate:
the signature is a fixture that silently returns the empty/None case. Start with tests that depend
on `origin/*` refs or on files the fixture does not create.

### G4 — unreachable guards · owner `local_claude_1` (claimed 2026-08-12)

Find production code that no test can reach (instance 2): `if __name__ == "__main__"` bodies,
bare `except` handlers, fail-safe branches. Mechanically approachable via coverage.

### G5 — disarmed harnesses · owner `local_claude_1`

Places where a check runs and its result is discarded (instances 4, 5). Includes **shell
invocation patterns**, not just code — the `| tail` defect is invisible to any code review because
it lives in how the tool is called. Mine, because both instances are mine.

### G6 — the 22 detector branches with no fixture · owner `claude_1` — **go-ahead GRANTED 2026-08-12**

The bite-test audit's own headline: *"22 of 47 branches — nearly half the detector surface — have
no fixture at all. That, not the kill rate, is the load-bearing measurement."* Real work with no
score attached, competing with the σ measurement and the banana question. ~~Do not start without
an explicit owner go-ahead.~~ **Granted 2026-08-12** (in-session owner decision): fixture all 22,
and **pin D-9 row (a) first** — the branch policing the no-banana-before-second-troll rule,
currently surviving all three of its mutations (D9-M1/M2/M3). A fixture that leaves any of the
three alive has not pinned the row.

## Boundaries

Tooling and tests only. No bot source, no candidate, no detector *predicate* change, no gate
change, no Arena action. `rust/src/bin/yamo_orchard_live.rs` stays byte-exact `fff6669b`.
G1–G5 may change tests and harnesses; **G6 adds fixtures and changes no predicate.**

## Acceptance

- every fixed guard is demonstrated failing against a deliberate break, and the break is described
- no guard is deleted without stating what it was supposed to catch and why nothing now needs to
- `python3 -m pytest tests/ -q` stays green at the end of each sub-item

## Standing rule this task establishes

**A new test is not finished until it has been observed failing.** Write it, break the subject,
watch it fail, restore, keep it. State in the commit what you broke. This is already how the
strongest work this week was done — `claude_1`'s speed-0 divergence tests and its M3a control that
failed first — and every instance in the table above is a case where it was skipped.
