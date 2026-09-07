# RESULT — the payoff is not truncated; there is no payoff. Third-worker family CLOSED.

**Verdict: CLOSE third-worker implementation.** All four real proposals fail
*payment*, so no leaf-value/horizon change could have rescued them. No 192-panel,
no funding/eligibility tweak, no selector implemented.

**Diagnostic.** One bounded run, no horizon sweep. A diagnostic-only instrumented
copy of the deployed candidate module forces the exact rejected commitment at one
exact turn (`MACRO_FORCE_TURN`); all other turns price and reject as in reality.
No stock/terrain/capability edit, no payment bypass, no opponent substitution, no
extra seeds. The four forced prices reproduce the reviewed −17.00 / −8.06 / −1.40
/ −6.85 exactly, confirming the same repaired family.

Map 9947505, seats 0+1, adaptive resident (index 0), real referee, real parent
continuation, to actual game end. Parent OFF: 148:148, margin 0, 0 issues, 2
workers in every row.

| proposal | cancel / reason | LEMON banked (need 3) | paid | workers ON | final ON | Δmargin |
|---|---|---|---|---|---|---|
| seat0 t40 | 78 / nothing outstanding reachable | 1 | no | 2 | 156:160 | −4 |
| seat1 t40 | 86 / nothing outstanding reachable | 2 | no | 2 | 172:180 | −8 |
| seat0 t60 | 106 / deadline (opened+45) | 1 | no | 2 | 184:164 | +20 |
| seat1 t60 | 106 / deadline (opened+45) | 1 | no | 2 | 176:172 | +4 |

0/4 pay, 0/4 train, 0/4 take any new-worker action; 0 candidate issues. LEMON is
the binding deficit in all four. The two positive deltas arrive long after
cancellation (seat0 t60 is still −5 at t150 and only crosses ~t165) and come from
re-tasked gathering plus longer games, not a hire that never happened.

**Changed repo files: none.** Family unchanged and re-verified:
core `e65e74c7`, `_a_module.rs` `3843fd31`, `_a.rs` `542e1b75`, tests `f4bd8e7c`;
archived to `archive-071918/`. New artifacts: `macroplan_force_module.rs`
`fb187a7c`, `make_force.py` `51da9b2e`, `analyze_force.py` `d386fbdf`.

**Tests: 18 run, 18 pass**, rustc **1.90.0**, `--test-threads=1`
(`build/macroplan-tests`, `tests-1.90.log`).

**Evidence** (run dir): `COUNTERFACTUAL.md`, `force40.log`, `force60.log`,
`force-1.log`, `force{-1,40,60}.tsv`, `HASHES.txt`.

**Limitations.** One map, one opponent, one spec — the only proposals the
controller makes on the 16 known trajectories. Panels built with rustc 1.97.1
(outcomes are toolchain-independent; 1.90 was used for the tests). No
compact/latency/equality work. All jobs collected; none running.

**Next action.** Retire the macroplan third-worker branch and open a ticket on a
mechanism that does not depend on acquiring contested fruit.
