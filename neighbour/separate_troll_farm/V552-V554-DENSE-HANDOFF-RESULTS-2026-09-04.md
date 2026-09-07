# V552--V554 dense-controller handoff results

## Outcome

V552--V554 ran exact V468 through turns 80, 100, or 120, then lazily initialized V546's repaired
R1FA controller with its ten-tree source cap. All three failed. The handoff preserved the intended
opening boundary and eliminated legality defects, but the late controller could not inherit
V468's specialized two-worker economy: none of the turn-101 states could afford even the cheapest useful
third worker, so it dismantled the active apple-and-chop loop for 80--130 turns to gather a new
bill. The best final result was still 52.7 points below V468.

No candidate advanced to fresh maps, duels, packaging audit, or the platform. V543 remains the
published bot.

## Design and build

`build_v552_dense_handoff.py` starts from the V468 development base through the existing repaired
R1FA insertion and V546's three maintenance-cap changes from six verified trees to ten. It then:

1. replaces the opponent-signature latch with a deterministic boundary;
2. evaluates only V468 before the boundary and only R1FA afterwards;
3. initializes R1FA plant provenance on its first call rather than assuming that call is turn 1;
4. treats existing handoff trees as neutral instead of falsely labeling them opponent crops; and
5. prevents harvest jobs from being assigned to V468's harvest-zero chopper.

The three compact files are 99,743, 99,744 and 99,744 UTF-16 units. All readable and compact forms
compiled under optimized Rust and accepted empty input. Five focused builder tests passed before
the final panels.

The first V552 attempt exposed the fifth requirement: R1FA assumes both of its first two native
workers can harvest, while V468 normally trains a harvest-zero chopper. It emitted 30,031
`no_harvest` issues and collapsed to 95.7 points. That pre-fix panel and binary are retained in
the archive. Tests were extended first, both harvest-assignment sites gained a capability guard,
and the final panels below contain no critical or unclassified issues. V552 has one noncritical
`move_blocked`; V553 and V554 have zero issues.

## Development panels

Each candidate ran on seeds 9,941,000--9,941,007, both seats and the frozen 12 families, for 192
paired games against V468:

| candidate | last V468 turn | turn-100 delta | turn-200 delta | final delta | final wood | final workers | extra-worker games | W/T/L |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V552 | 80 | -9.3 | -44.0 | -52.7 | 40.1 | 2.93 | 142; 37 reached four | 150/0/42 |
| V553 | 100 | +0.0 | -34.5 | -60.1 | 37.5 | 2.77 | 136; 12 reached four | 147/0/45 |
| V554 | 120 | +0.0 | -25.4 | -59.9 | 36.9 | 2.66 | 125; 2 reached four | 154/2/36 |
| V468 | n/a | baseline | baseline | baseline | 45.0 | 2.00 | 0 | 177/3/12 |

The first divergent commands occurred no earlier than turns 81, 101, and 121 respectively, with
those same medians. V553 and V554 therefore reproduce V468 exactly through the turn-100
checkpoint. Delaying the handoff improves turn 200 because V468 runs longer, but it leaves less
time for the replacement economy; final score does not recover.

The transition also loses V468's local production rather than adding to it:

| measure per game | V468 | V552 | V553 | V554 |
|---|---:|---:|---:|---:|
| final score | 247.2 | 194.5 | 187.2 | 187.3 |
| ring harvests | 68.3 | 43.9 | 43.5 | 43.7 |
| ring chops | 58.3 | 18.9 | 17.3 | 19.5 |
| all CHOP commands | 155.1 | 114.8 | 112.3 | 112.0 |
| all MOVE commands | 193.3 | 356.4 | 341.3 | 322.2 |

## Mechanism

At V553's turn-101 boundary, none of the 192 exact V468 states could afford any worker with at
least one harvest and one chop power. Even the cheapest `1/1/1/1` worker costs three each of plum,
lemon, apple, and iron for the third hire. V468 had fewer than three plums in every game: zero in
144 states, one in 24, and two in 24. The fixed R1FA `2/2/1/2` bill was affordable in zero games.

Consequently, the first additional worker arrived at median turns 202.5, 223, and 249 in
V552--V554. The switch does not hand a ready economy to a new worker; it assigns bill production
to the two workers already producing V468's score.

Map 9,941,004, seat 1 against `legend_balanced`, shows the teardown directly. At turn 101 V468
had score 98, 21 wood, two workers, and an active planted-tree ring. V468 continued the starter's
ring route and the second worker's chopping. V553 instead sent the chopper to `PICK LEMON`, planted
lemons on turns 106 and 109, and redirected the starter to harvest and plant plums. It did not
train the third worker until turn 191 or the fourth until turn 298. V468 finished that game at
277 score and 69 wood; V553 finished at 240 and 58 while allowing the opponent 23 more points.

The standalone V546 recheck closes the possibility of selecting dense-from-turn-one only on good
states. It gains at least 40 final points in 160 of 192 rows, but its turn-100 delta is negative in
191. The sole nonnegative row is +1 at turn 100 and only +8 final; no row meets all gate
conditions. Even an oracle whole-game selector cannot combine this controller with exact V468 to
pass both the checkpoint average and +40 final requirement.

## Consequence

A wholesale controller switch is closed. The dense economy is valuable only when it owns the
opening that funds its worker specifications and source provenance; starting it later forces it
to purchase those prerequisites by abandoning V468's existing roles. Preserving V468 longer
changes when the loss occurs, not whether it occurs.

The next step is an evidence-only same-state audit of chopper target quality in mature platform
losses. V543's live opponents rated 14+ planted 45.5 trees and banked 100.3 wood against 21.1 and
80.9, while early opponent crops often remained ripe without contact. Before reopening any closed
farm or denial branch, the audit will determine whether the existing power-2/3 chopper actually
has a reachable higher-wood cycle that its current target scoring misses.

## Evidence

- V552 panel SHA-256: `76b9167e8284d26d591b3502762cf1c0fc3cc10729796116b8f697187e66d456`
- V553 panel SHA-256: `8691abc39b91889153c50064c339449004b74874fac93e65769b3b0ed69ced13`
- V554 panel SHA-256: `c7b0fbc8084015152b9e6429e56e468c2e5ec2185eef431c8f37625728a894b7`
- gate JSON SHA-256 values: V552 `e3a19b0bf71f471e82d8aa64e2ac28c24d09a2cf8b26bef762ecd9ffb9f4eca1`, V553 `b824dc42fd4946a8629951caae1264f71386a3ee9f44ed61ed539eefc882d9b8`, V554 `ddfd4e2ac08a65ebf802c7fe8f77400d9138ee587ac240cde9d76e788d6101b1`
- compact SHA-256 values: V552 `627d1d803ab3b9e01c86b5db4fddfbc685214aeec66aec33096c57a0f1b40545`, V553 `165bac62d62b7d6048e82d6913c37062b4507c3597682a5673fae0392152a69c`, V554 `bd6dc7786f7fd4883edb60715bdb11f3658abbbe82271691b441a43ec5c7391a`
- V546 recheck SHA-256: `61214ac51ca9dfe267ceecb1141778f8d29cc41456062f3a571dd4014a6f741c`
- archive: `/data/separate_troll_farm-working/archive/2026-09-04-v552-v554-dense-handoff/`
