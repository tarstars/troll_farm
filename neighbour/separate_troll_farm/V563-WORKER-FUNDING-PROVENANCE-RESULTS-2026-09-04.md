# V563 rating-18+ worker-funding provenance audit

## Verdict

The strong opponents do not fund extra workers from spare capacity hidden inside an active wood
loop. They stop chopping entirely while accumulating each bill, repeatedly harvest a small
plum/lemon/apple source set, mine the exact iron, and issue `TRAIN` immediately on first
affordability. The useful new signal is the third worker's specification: in the two rating-18+
four-worker games, the opponent and V543 reached worker three at the same mean turn, 61, but the
opponents used capacity three or four and reached worker four at mean turn 101; V543 used capacity
two and reached four at 145.5.

The rating-14+ sensitivity group supports a focused candidate. Every observed `2/3/1/2` third
worker reached worker four (6/6), as did the single elite `3/4/2/3`; none of the other eleven
third-worker instances did. This is associated evidence from repeated opponent identities,
not a causal estimate, but it is materially narrower than another generic farm or funding retry.
Queue item 11 will test a higher-capacity third worker inside the already-repaired dense economy.

V563 is an evidence-only audit. It changed no gameplay source and could not publish anything.
`bot.rs`, `submission.rs`, and the live V543 agent remain unchanged.

## Frozen population and validation

The source is V543's immutable mature 160-game package. Five records had opponents rated at least
18. Two—Pduhard- and gaha—contained only two decoded states and were the known first-batch startup
timeouts. The three played games were:

| opponent | rating | opponent score | V543 score | margin over V543 | final workers |
|---|---:|---:|---:|---:|---:|
| abdelmathin | 18.62 | 441 | 247 | +194 | 2 |
| bl4sterino | 19.34 | 792 | 468 | +324 | 4 |
| BoatBuilder | 23.60 | 701 | 504 | +197 | 4 |

All seven opponent `TRAIN` commands matched a new unit with the commanded statistics in the next
decoded state, an exact inventory debit after same-turn `PICK`/`DROP` effects, and a matching
tooltip at twice the game-turn index. State births, successful command turns, and tooltip turns
were identical. There were no rejected commands in the primary population.

The decoder tracks every live tree generation as natural, opponent-planted, or planted by the
audited side. For each between-hire interval it records per-worker actions, harvest yield by crop
and tree provenance, mine yield, exact drop payload, seed picks/plants, score, wood, and the first
turn on which the ultimately selected specification was affordable. Bank conservation from the
prior post-hire state to the next pre-hire state was exact in every interval.

## Hire timelines

| opponent | opponent hires | V543 hires in the same game |
|---|---|---|
| abdelmathin | t72 `2/4/0/3` | t2 `2/1/1/3`; t100 `2/2/1/2`; t258 `2/4/0/3` |
| bl4sterino | t1 `2/2/2/1`; t74 `3/4/2/3`; t105 `3/4/0/3` | t2 `2/2/1/1`; t67 `2/2/1/2`; t146 `2/4/0/3` |
| BoatBuilder | t2 `2/2/1/1`; t48 `2/3/1/2`; t97 `2/4/0/3` | t2 `2/2/1/2`; t55 `2/2/1/2`; t145 `2/4/0/3` |

Every third and fourth hire occurred on its first affordable turn. The three second hires had
affordability delays 0, 0, and 1; BoatBuilder spent one lemon on turn 1 and trained on turn 2.
The important comparison is not earlier access to worker three. Bl4sterino/BoatBuilder reached it
on turns 74/48, exactly mean 61, while V543 reached it on 67/55, also mean 61. Their stronger third
workers then funded worker four in 31/49 turns, against V543's 79/90 turns.

The two scaling opponents were slightly behind V543 at turn 100—mean score 26.5 versus 29.5 and
wood 0 versus 2—but were already at mean 3.5 workers versus 3.0. By turn 200 they led 377 to 226
in score and 92 to 49 in wood; at turn 300 the gaps were 746.5 to 486 and 186.5 to 103.5.

## Bill provenance and opportunity cost

Across all between-hire intervals, the opponents harvested 130 bill fruits: 84 lemons, 33 plums,
12 apples, and one banana. Ninety came from their own planted trees, 32 from natural trees, and
eight from V543-planted trees. They deposited 79 lemons, 34 plums, 11 apples, one banana, and 39
iron. Lemons supplied 65% of harvested bill fruit and own-planted sources supplied 69%.

The per-hire production makes the mechanism explicit:

| opponent hire | plants before hire | harvested bill fruit | mined iron | chop actions |
|---|---:|---:|---:|---:|
| abdelmathin second, t72 | 0 | 13 lemon | 0 | 0 |
| bl4sterino third, t74 | 6 | 35 | 10 | 0 |
| bl4sterino fourth, t105 | 0 | 36 | 12 | 0 |
| BoatBuilder third, t48 | 3 | 17 | 2 | 0 |
| BoatBuilder fourth, t97 | 0 | 29 | 15 | 0 |

The first two immediate hires were paid entirely from starting inventory. Bl4sterino planted one
apple, three lemons and two plums before worker three; BoatBuilder planted two lemons and one plum.
Neither planted another bill source between workers three and four. Instead all three workers
harvested the established sources, and the new third worker also mined. The higher capacity is used
immediately for fewer, larger bank trips.

Abdelmathin is a different but consistent specialization: its sole worker harvested and deposited
13 fruit from one natural lemon source, did no chopping before turn 72, bought a strong
harvest-zero chopper, and only then ran the 30-banana/109-wood finish. It proves that four workers
are not mandatory; it does not provide a free way to graft another worker onto V468.

The zero-chop result is the crucial negative finding. The elite bots are not preserving V468's
opening income while funding expansion. They make a deliberate early capital investment and rely
on the post-fourth-worker production curve to repay it. That agrees with V546's +131 final own
score but -73 turn-100 score versus V468, and explains why the late V552--V554 handoffs fail.

## Rating-14+ sensitivity

The same validator was run secondarily at rating 14. It selected 24 records: 21 active games and
three startup timeouts. Forty-six successful hires matched state births, debits, and tooltips.
One additional `TRAIN` was correctly rejected because a same-turn lemon `PICK` consumed the last
required lemon; the no-train bank transition was exact.

Eighteen games reached worker three and seven reached worker four. Six third workers had exact
specification `2/3/1/2`; all six reached four. The single `3/4/2/3` third worker also reached four.
The other eleven third workers covered eight specifications and none reached four. All seven
four-worker games again issued zero `CHOP` commands in every interval before their hires.

The six `2/3/1/2` observations are not six independent strategies: five are MTLKS games and one is
BoatBuilder. The result therefore supports testing the mechanism, not claiming a universal causal
law. It does rule out treating the two elite observations as an isolated decoding accident.

## Consequence

The next candidate should change the repaired dense controller's third worker from `2/2/1/2` to
the observed `2/3/1/2`, with the elite `3/4/2/3` as a bounded comparison. The parent already owns
the needed source-farm policy; this isolates whether capacity and harvest strength, rather than
more plots or another bill runner, cause the 44.5-turn fourth-worker gap. It must still face the
absolute V468 checkpoints and +40 final gate before any publication.

## Reproduction and integrity

- audit: `audit_worker_funding_provenance.py`
- focused tests: `test_audit_worker_funding_provenance.py` (7 focused; 97 repository tests pass)
- primary report: `/data/separate_troll_farm-working/analysis/2026-09-04-v563-worker-funding/worker-funding-provenance.json`
- rating-14 sensitivity: `/data/separate_troll_farm-working/analysis/2026-09-04-v563-worker-funding/worker-funding-provenance-rating14.json`
- archived copies: `/data/separate_troll_farm-working/archive/2026-09-04-v563-worker-funding/`
- frozen replay package SHA-256: `ccc45a23ea8ecc17ecb4215d8d52b4993e00c33fb830f6ad0b1786d6c713cbd1`
- primary/sensitivity SHA-256: `0accff48bd675719cc285bff527c4a4756140714d1ac2b6208f608539e7f95f0` /
  `00f3add404586e9989f68d77428a120936e67f79a857ad9d2f849bb640135416`
- audit/test SHA-256: `38969e96f47ac7971ef0c18cd7c000512ec41fdcca5549c1e9ab6b5f01698cd8` /
  `de3f4c9ea825d0fb0633b73dd6ba5be4f1383241fab3b6e9e1d146580ce32604`
