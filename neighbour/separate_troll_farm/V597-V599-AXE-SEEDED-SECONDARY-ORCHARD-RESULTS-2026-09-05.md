# V597--V599 axe-seeded secondary orchard

## Verdict

Giving V595's empty axe a persistent one-seed transaction was safe and profitable, but did not
create parallel orchard throughput. Cap-one V597 scored `+0.00/+3.46/+14.13` at turn
100/200/final on the 24-game behavior smoke, retained V468's two harvests, gained 3.25 wood, and
improved outcomes from 19/1/4 to 20/3/1. It was the best arm. Caps two and three progressively
lost turn-200 and final value despite allowing more live secondary crops.

The new layer improved V595 by only 0.29 plants, 1.00 wood, and 3.67 final points per game. V468's
harvest-zero axe already planted 8.58 crops on this panel; V597 planted only 6.00 with that worker.
The overlay therefore rescheduled an existing seed/chop loop instead of adding a new producer.
Increasing the cap from one to three recovered only 0.33 axe plantings, added movement and game
length, and reduced final score by 1.13. The same worker cannot simultaneously multiply plots and
fell them.

All arms failed the required `+40` final gain, so no frozen 192-game panel, fresh maps, duels,
packaging, audit, or platform publication ran. `bot.rs`, `submission.rs`, and the live V543 agent
remain unchanged.

## Isolated candidates

All three candidates derive from V595. One real V468 controller still runs first on every state
and chooses every producer action. The new controller can replace only the action slot belonging
to the exactly-two-worker roster's harvest-zero/chop-positive axe.

Through turn 100 commands are untouched. Later, an empty axe adjacent to its own bank may replace
only a `WAIT`, `CHOP`, or tree-targeted `MOVE`, and only when at least two units of one fruit are
banked. `PICK` consumes exactly one according to the referee, leaving a one-seed reserve. A
persistent `(fruit, plot)` job moves that seed to an empty, reachable own-half grass cell within
two bank steps. The target excludes doors, iron, water, plants, units, and the producer's projected
landing. Collision handling either waits safely or abandons to V468.

Issued plants enter both V595's persistent own-crop provenance and a secondary-crop set. V595's
existing size-one protection and size-two positive felling priority then own the rest of the
lifecycle. The only arm difference is the simultaneous live secondary-crop cap:

| arm | live secondary cap | compact UTF-16 units |
|---|---:|---:|
| V597 | 1 | 92,494 |
| V598 | 2 | 92,494 |
| V599 | 3 | 92,494 |

The modules normalize to exact equality after replacing that constant. All readable programs
compile independently, all paired runners compile, and all 215 repository tests pass.

## Behavior smoke

Each arm ran map seed 9,941,000 in both seats against all 12 frozen opponent families: 24 games
per arm. Deltas are candidate minus exact V468.

| arm | turn 100 | turn 200 | final | candidate W/T/L | wood delta | decision |
|---|---:|---:|---:|---:|---:|---|
| V597 cap one | +0.00 | +3.46 | +14.13 | 20/3/1 | +3.25 | reject |
| V598 cap two | +0.00 | +2.79 | +13.54 | 20/1/3 | +3.13 | reject |
| V599 cap three | +0.00 | +0.46 | +13.00 | 19/1/4 | +3.00 | reject |

V468 scored 94.67/160.67/215.46, banked 53.21 wood, and went 19/1/4. V597 scored
94.67/164.13/229.58 and banked 56.46 wood. It gained own score against every opponent family,
from +6 against `compact_gold` to +28 against `script_boss`. Opponents also gained 8.13 points as
games ran 7.17 turns longer, so the better outcomes remain a safety observation rather than the
selector.

All 24 rows retained exactly two workers and the same `TRAIN 3 2 0 2` at median turn 6. There were
zero legality, critical, or unclassified issues. Every arm's first command divergence was between
turns 102 and 266 with median 234, exactly the late intervention interval already seen in V595.
At the first differing turn the axe issued a `PICK` in 12 rows and a `MOVE` in 12. V597 differed
on 59.96 command turns per game.

## Mechanism

The intended safety boundary held: producer harvests remained exactly 2.00 in V597, and the final
gain was almost entirely explained by 3.25 more banked wood. The intended scaling boundary did
not hold. Command streams showed that the supposed spare axe already owns most of V468's seed
loop:

| per-game command count | V468 axe | V597 axe | delta |
|---|---:|---:|---:|
| `PICK` | 8.58 | 6.00 | -2.58 |
| `PLANT` | 8.58 | 6.00 | -2.58 |
| `MOVE` | 131.88 | 151.08 | +19.21 |
| `CHOP` | 87.25 | 81.79 | -5.46 |
| `DROP` | 25.21 | 21.79 | -3.42 |

State divergence moved some work to the producer: its plant count rose from 4.79 to 6.25 and its
chops rose from 95.54 to 107.71. Across both workers V597 still planted only 12.25 crops versus
V468's 13.38. Relative to V595's 11.96 crops, the explicit secondary transaction added only 0.29.
Thus the fruit reserve and plot geometry were reachable, but worker action capacity—not the cap—
was binding.

The cap sweep confirms that diagnosis. Relative to cap one, cap two added 0.13 total plants and
2.83 turns but lost 0.58 final points; cap three added 0.33 plants and 4.83 turns but lost 1.13.
V599 issued 5.29 more moves and 3.79 more chops than V597, yet banked 0.25 less wood. More allowed
plots made the serial planter/feller busier without producing parallel mature-tree cycles.

The next architectural interval should retain V468's producer `PICK`, `PLANT`, `HARVEST`, and
`DROP` actions, but replace selected post-turn-100 power-one producer `CHOP` opportunities with
bounded seed and ripe-own-crop work. V597 left 107.71 producer chops per game while the
power-two axe handled 81.79; shifting only low-efficiency chops can create a second orchard lane
without repeating V591's whole-producer handoff.

## Reproduction and integrity

- builder/test: `build_v597_axe_seeded_secondary_orchard.py` /
  `test_build_v597_axe_seeded_secondary_orchard.py`
- canonical runners, smoke panels, gates, and diagnostics:
  `/data/separate_troll_farm-working/archive/2026-09-05-v597-v599-secondary-orchard/`
- V597/V598/V599 panel SHA-256: `1f951461c55ad0e0698fbdf0810cb5bbd872c63ed16a2cf47dde50e8bed968b8` /
  `d0d37bdfbf1a20a727fdc8a189a53000a5a5f3162b5e48553512f87912887396` /
  `37c62645c3c4f7b23d478a62c72d41c4db8b7aa7e6caf2333ddb219c99c21020`
- V597/V598/V599 gate SHA-256: `e2274fbaddb19308350e53de63aa4cf38cf943f039b2f84678f4dabb6ea01348` /
  `5841b9945b582125b79389a5f51c0263800ff4695358298c86a6a031d792782d` /
  `0c69e7106f6dadc7407109a82e0af278b238385bc30f21d61904587449c17a88`
- V597/V598/V599 diagnostics SHA-256: `ad3c0e0e55ca5a42cb6aab3ccd20c49f303a7f2b002559c79539a980716c91c3` /
  `2b33f4504cbe690849a61222482b04e664c1a3ac45ed94da44b68e9eac9a530b` /
  `c9acc1ea7e8f009a116c424d3b30d126fde763177b2e9e9547cb7fd7328fe592`
- V597/V598/V599 module SHA-256: `f57a0490585b777a5be80c9058228af45807b4464947576916e477a847f1e2b8` /
  `937d52ae19af376f8d631c30872144e48c6bc370b369297c0a3a77bf2423020d` /
  `e9ef85e0feac9f821cdba2b54b718caadb7609c13a7cde8984c8d66ebfc1ec04`
- V597/V598/V599 compact SHA-256: `5535513c06e979f4fdf697612171742cf8c73f3657eec5b6e390dea79e11448d` /
  `1ecad78dfa7313bb5fea1e46a82ae9016079ccc47cd059f56465e295924df20a` /
  `4df65a426ead685305b2f20942948bc02ba7b94436304ecadc41980e337274db`
- V597/V598/V599 runner SHA-256: `46aea8b7b4910f30d19d9d699ce96f6cfbdc48e8fba226f742de8014564d1533` /
  `2e3c536a696a00664384807cc0fbed3b3a3b99118be5e113d12c2f4b980e71b3` /
  `d627ca149cf56a377307cefed337656545981e0827f8b3bbac111f6984d8ab1d`
- builder/test SHA-256: `d286094b51d291f31766311c9ff314aa37d672125a60a12391ca57fa7f7125e2` /
  `17dceddee9b813d61f516f4ff4d39c6250b2d4c14bcbcf8bfa9fba01e0228612`
- production hashes retained: `bot.rs`
  `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
  `submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
- read-only neighbor remained at `370fa63cae12eda129ff5553c33a7086dfcb87c2`
