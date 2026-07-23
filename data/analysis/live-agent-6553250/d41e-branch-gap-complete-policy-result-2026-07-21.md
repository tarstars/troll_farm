# D41e branch-gap complete-policy selector — result (2026-07-21)

## Verdict

**Reject the exact D41e rule on its sole failed gate; do not run Stage B or adjust the thresholds on
the consumed bank.** The candidate is a real, clean improvement over D40—paired mean margin
**+4.116**, descriptive normal 95% interval **[+2.533,+5.700]**—but the preregistered Stage-A floor
was +5. All other gates pass.

This is the strongest prospective complete-policy result in D41 so far, but it is not a qualified
checkpoint or submission candidate. Maps 9,771,000--9,771,063 remain unopened because the runner
correctly stopped after Stage A. Confirmation, deployment construction, TestSession, submission,
and Arena remain sealed.

## Fresh complete-policy result

Stage A evaluated 64 official maps, both seats, and all eight opponents: 1,024 tasks on maps
9,770,000--9,770,063. Two fresh candidate processes are behaviorally identical, including terminal
rows and decision hash.

| metric | D40 | D41e | delta |
|---|---:|---:|---:|
| mean own score | 226.111 | 227.291 | **+1.180** |
| mean opponent score | 174.168 | 171.231 | **-2.937** |
| mean margin | +51.943 | +56.060 | **+4.116** |
| worker two | 98.73% | 98.73% | 0.00 pp |
| worker three | 93.16% | 93.16% | 0.00 pp |
| crop creation | 100% | 100% | 0.00 pp |
| catastrophes (`margin <= -100`) | 96 | **88** | **-8** |

The same-bank random arm has -123.364 mean margin, so D41e is +179.424 above random. There are zero
illegal actions, direct-command failures, provenance failures, relevant prediction failures,
worker-cap breaches, rule mismatches, or reward-identity failures above tolerance.

## Activation and breadth

D41e changes 488 of 176,766 decisions (**0.2761%**) across 304 episodes:

- 0 `train` overrides;
- 0 `deficit` overrides;
- 16 `evacuation` overrides;
- 472 `rate` overrides;
- 281 early, 0 middle, and 207 late overrides.

Seven opponent-family means improve; the eighth is essentially neutral:

- `compact_gold` +10.734;
- `gold_adaptive` +7.438;
- `mybot` +6.617;
- `norx_native_three` +5.656;
- `legend_balanced` +1.688;
- `script_boss` +0.938;
- `silver_boss` +0.008; and
- `resident` -0.148.

The worst family remains far above the -10 gate. Thus the failure is magnitude versus the frozen
+5 target, not collapse, narrow opponent specialization, or a negative tail trade.

## Consumed-bank mechanism diagnosis

The exact post-result diagnostic shows **coverage, not repeated-override dilution**, caused the
shortfall.

- Changed episodes average +13.865 margin with lower bound +8.688, but only 304/1,024 = 29.69% of
  episodes activate. At the observed value, approximately 65 additional equivalent changed
  episodes would be required to reach +5 globally.
- Rate-only changed episodes contribute +4.093 of the +4.116 global gain and average +14.552.
- Evacuation-only episodes contribute -0.009 and average -0.818; D41d's evacuation discovery signal
  does not replicate prospectively at this sparse support.
- One-override early-rate episodes average +12.561; one-override late-rate episodes average +6.541.
- Mean value rises rather than falls with repeated activation: +9.923 for one override, +18.194 for
  two, +23.524 for three, and +27.000 for four or more.

The next experiment must therefore close evacuation, preserve exact D40 in train/deficit/middle
rate, and collect fresh one-deviation labels below the current early/late rate-gap boundary. It
must not simply lower 0.280 and rerun D41e on either Stage-A or unopened Stage-B maps.

## Gate table

Pass: complete grid, candidate repeat exactness, integrity, exact rule/branch isolation, bounded
activation, own-score floor, opponent breadth/tail, workforce/crops, catastrophe nonincrease, and
random-margin floor.

Fail: paired mean margin is +4.116 rather than at least +5, despite its interval excluding zero.

## Evidence

- protocol SHA-256: `7efa92992191bb8699cef2b41fe34f5cd1ce34a1ea709afd37974c6ff29a0552`;
- prospective result SHA-256: `3619d394ce42d5d257ca59894b5e2b482eef70dbc117f03bb070d6c9d166a17e`;
- mechanism analysis SHA-256: `1f4f34c470a2c76481ed90f98edaa16b4b457718df42ee7c4c013d263b50b8c7`;
- candidate decision hash (both replicas):
  `78b0efb22b3a160e90677e24a63a3f4b0de8a5c2ba3d84d3accebe3eaf9d2011`;
- prospective wall time: 553.281 seconds;
- focused verification: eight selector/D41d tests and four mechanism/evaluator tests pass.
