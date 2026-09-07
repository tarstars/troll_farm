# V551 third-troll prerequisite audit result

## Outcome

Queue item 4 was conditional on item 1 producing a farm surplus. Item 1, V548, failed both the
checkpoint and final-gain gates despite making the intended third-worker mechanism engage. There
is no measured surplus with which to fund another troll, so item 4 is closed by its explicit
precondition. V551 is an evidence audit, not a bot candidate; no gameplay source or platform
agent changed.

## Prerequisite evidence

V548 gave the second worker harvest power one and assigned it the opening farm's fruit bill. On
the same 192 development games it trained a third worker in 134 games instead of V481's 77 and
moved the median completion from turn 140 to 105. That is strong evidence that the mechanism ran,
not merely that its condition was unreachable.

The authoritative V548 gate report records:

| measure | V468 | V548 | delta |
|---|---:|---:|---:|
| own score at turn 100 | 93.01 | 52.31 | -40.70 |
| own score at turn 200 | 176.18 | 149.55 | -26.64 |
| final own score | 247.25 | 255.36 | +8.11 |
| final opponent score | 108.22 | 137.59 | +29.37 |
| final wood | 45.02 | 43.34 | -1.68 |
| W/T/L | 177/3/12 | 165/0/27 | -12/-3/+15 |

Relative to the exact V481 farm lineage, V548 gained 57 third-worker completions but lost 7.17
wood, 30.50 turn-100 points, 23.39 margin, and 13 outcomes. It issued 31.07 more HARVEST commands
per game while CHOP fell 16.27. Funding the third worker did not create surplus;
it reassigned the only productive axe to fruit collection and allowed opponents to score more.

## Cross-check against the earlier lineage

The earlier panels establish the same mechanism independently:

| candidate | funding path | checkpoint deltas at turns 100 / 200 / 300 | completion evidence |
|---|---|---:|---|
| V472 | starter gathers third-troll bill | -4.41 / -4.87 / +4.61 | 20/192; +24.9 when trained |
| V475 | second troll mines, wider window | -17.69 / -12.91 / -1.72 | 58/192; median turn 142 |
| V476 | opening mothers plus third troll | -5.34 / -4.25 / +10.78 | 56/192; median turn 122 |
| V481 | mothers plus explicit starter bill run | -10.21 / -8.19 / +12.99 | 77/192; median turn 140 |
| V548 | harvest-capable second-worker bill run | -40.70 / -26.64 / +8.11 | 134/192; median turn 105 |

When a `2/2/0/2` third troll arrives it can repay about 25 points, but gathering its bill removes
more early apple or wood production than it returns. More completions and earlier completion make
that tradeoff worse in V548, not better. V549 then showed that restricting the second worker to
an initial `WAIT` does not make the fruit free: mandatory travel and banking reduced chops by
18.01 and margin by 11.06. A new item-4 implementation would repeat this tested allocation under
a different name.

## Next mechanism

The evidence points away from another funding tweak and toward a controller handoff. V468 owns
the required early score curve, while the repaired R1FA controller and V546's denser source
orchard own the late parallel economy. Delaying hires inside R1FA (V547) recovered only 18.91 of
its 72.89-point turn-100 deficit because the slow opening is the whole controller, not just the
training spend. What has not been tested is running exact V468 through the opening and then
initializing the dense economy from the resulting two-worker state.

That handoff is now the next queue item. It is materially different from the closed farm lineage:
it preserves every V468 command through the selected switch turn instead of diverting a current
worker to pre-fund future capacity. It can pass only if the later controller can turn V468's
banked opening into at least +40 final score without regressing the frozen checkpoints.

## Verification and artifacts

No candidate, panel, holdout, packaging audit, or platform submission was opened. `bot.rs`,
`submission.rs`, `candidate_compare_panel_runner.rs`, the V468 baseline, maps, and 12-family pool
are unchanged.

Evidence:

- V548 192-game panel SHA-256: `f86fcb0aa43512382e20a61b8813b6ce3294d897cff08247b08fc2b50254cc67`
- V548 gate JSON SHA-256: `14fea6ee685384e95071ad55c52905bfff374195d858a522bd2a36bfcd8bd7ad`
- V548 diagnostics SHA-256: `bb4d5c7ae0cbf6e94c6db3de1ebcb197f127b6118eadd1582863d2cb1005da6f`
- V472 gate JSON SHA-256: `5ca3619ee7f159e0b102e37a5857e2ca5d2950256c9d27b667a9d885bfa9a618`
- V481 gate JSON SHA-256: `75251475cfbbd7167fe98e12c08f0f60c33ec101afb90a508b349136a738749b`
- mature V543 top-gap JSON SHA-256: `7fd6e180b7ad788b4d2651957a958d671463244dfc28383ba306215c4980c495`
