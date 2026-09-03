# Task — the cheap third troll: the champion as it is, plus the weakest third troll worth having, bought as cheaply as possible (the successor to the port; owner 2026-09-02 18:0xZ: "yes")

- Born 2026-09-02 18:1xZ by the owner's word on the successor question ("1. yes"), after the port line closed under its
  dead condition (`coordination/GRAVEYARD.md`, 2026-09-02). Two reads point here: the endgame read (Track E: the last fifty
  turns are lost by the roster and an emptied map, not by idle trolls — roster ×0.70 of a 46-point gap) and the port's loss
  read (the fruit economy that funds a big roster loses the game before turn 100).
- Record owner: local_claude_1 (coordinator) · Work owner: **claude_1** (the read, then the build) · Verifier: **the
  coordinator** (reproduces every number and the build by execution — the two-agent separation restored: claude_1 builds,
  the coordinator judges) · Design reviewer: **chatgpt_1** (one round, on the owner's activation — the coordinator sends the
  assignment and asks the owner to switch it on) · Ladder: the coordinator submits; the owner's prediction is asked first.
- Status line: **DEAD ON PAPER 2026-09-03 05:2xZ — the read delivered 04:23Z, verified by execution by the coordinator (VM fallback seat), no build; the owner's one word ("build") reopens it with the 30-turn variant. Obituary in `coordination/GRAVEYARD.md`.**

## The idea (plain words)

Our champion plays with two trolls: the starting troll and one trained troll (2/2/0/2 — speed 2, carry 2, no harvest
power, chop 2) bought in the first twenty turns, then both chop wood to the end. Every earlier attempt at a third troll
(the 2/3/0/3 troll, three heroes, the seven orchards) paid for it with a long collecting phase — fruit trips, an orchard
— and that phase is what lost the games (three heroes 11.7 / 12.0; the orchards 13.5–18.8 against the champion's 18.2 the
same day). The port showed the general form: a fruit-first economy loses before turn 100. **This card asks the narrowest
question left: can the champion, playing exactly as it plays, buy the weakest third troll that still pays, with the
smallest possible detour — and does that troll earn back its bill?**

The price of a troll (the referee's rule): with `n` trolls already owned, a troll with talents speed `s`, carry `c`,
harvest `h`, chop `k` costs `n + s²` plums, `n + c²` lemons, `n + h²` apples and `n + k²` iron. With two trolls owned:

| third troll | plums | lemons | apples | iron | items in all |
|---|---:|---:|---:|---:|---:|
| 1/1/0/1 | 3 | 3 | 2 | 3 | **11** |
| 1/2/0/1 or 2/1/0/1 | 3 or 6 | 6 or 3 | 2 | 3 | 14 |
| 1/1/0/2 | 3 | 3 | 2 | 6 | 14 |
| 1/2/0/2 | 3 | 6 | 2 | 6 | 17 |
| 2/2/0/2 (the second troll's own shape) | 6 | 6 | 2 | 6 | 20 |
| 2/3/0/3 (the 08-28 card) | 6 | 11 | 2 | 11 | 30 |

So the cheapest troll costs about a third of what the earlier cards paid. Whether it is worth having is the read's job.

## Step 1 — THE READ (claude_1; budget one day; no build)

Everything from what we already hold: the champion of record's collected ladder games with the v6 telemetry (160 games of
`41230202`, `local_claude_1/ladder-queue/games-41230202/`; 160 of `41202036`, `local_claude_1/denial-ablation/games-41202036/`),
the exact per-turn board reconstruction (`data/processed/turns.jsonl.gz` and the referee-exact engine), and the field's
own trolls (the per-turn corpus, the second-troll census `local_claude_1/second-troll-census/`).

1. **What the champion banks and holds.** Per game: the fruit and iron in the bank after the second troll is trained (the
   opening's leftovers), and the fruit and iron banked afterwards (the loss read says 0.70 fruit in turns 1–50 and
   nothing later — measure it on our own games). How far each cheap bill is from what the bank already holds.
2. **What the trolls pass.** From the recorded moves and the board: how many fruit and iron items stand within one step of
   the paths the two trolls actually walk in turns 20–150, by kind — the pickups that cost one turn and no detour.
3. **The cost of the smallest dedicated detour.** From the champion's own opening (items banked per troll-turn in turns
   1–20 while it funds the second troll) and its chopping rate afterwards (wood items per troll-turn, from the loss read's
   phase table for the champion), the turns two trolls need to bank 11 / 14 / 17 / 20 items, and the wood they forgo
   meanwhile, in points (a wood is four points).
4. **What a weak troll earns.** From the field's trolls of many talents (the census and the per-turn corpus): wood banked
   per troll-turn by talent shape — a 1/1/0/1 against a 2/2/0/2 — and, on our own games, the wood a third troll would
   have banked from the turn it could exist to the end (the champion's games end at turn 300 with the board empty in most;
   Track E's roster factor applies to the last fifty turns).
5. **Two designs, costed, one recommended.** (A) *The opening buys it too*: the starting troll's opening bill grows by the
   cheap troll's bill, so the second and the third are trained back to back before chopping starts (what it delays, in
   turns and points). (B) *A minimal pass after the second troll*: once the second troll exists, both trolls collect the
   cheap bill only while it is within N trips of their current positions, then chop (what N, what it costs, how often it
   completes). The read gives, for each, the expected net points per game from the numbers above, and recommends one.

Deliverable: `claude_1/cheap-third-troll/READ-2026-09-0x.md` — one page for the owner (what a cheap troll costs, what it
earns, which design, the expected gain with its uncertainty) and the tables behind it; the code that produced every number
beside it; one ack-required handoff. **No build, no panel, no ladder, no platform action in this step.**

**Dead on paper (the read's own condition):** if the cheapest useful troll's bill costs more than about thirty turns of
two-troll chopping (about eight wood items, thirty points) *and* the read's expected earnings of that troll do not cover
it with margin, the card dies here: the obituary names the numbers and the owner hears "no build".

## Step 2 — the design round (≤ 2 rounds)

The coordinator's review by execution of the read's numbers; chatgpt_1's review of the recommended design (the
coordinator sends the assignment and asks the owner to activate chatgpt_1); the owner reads the one page. The design is
one variable on the champion of record (`readable/denial-off-champion.rs`, the diagnostics arm
`cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`, sha `0e92f8fa…`): everything else byte for byte.

## Step 3 — the build (claude_1), the bed, the smoke, the reproduction (the coordinator)

The generator chain (a `make_*.py` whose replacements match exactly once, modelled on `local_claude_1/the-floor/` and
`local_claude_1/third-troll/`), the 34-situation bed (plays, deterministic, compacted == readable, telemetry 0), a smoke of
full games on 24 real maps (in what share of games the third troll is trained and at which turn; the turns spent funding;
no stall, no lone-troll games), and the coordinator's byte-identity reproduction of all three.

## Step 4 — rung 1, the field reading (the selector)

claude_1's panel instrument as it judged the port: the candidate and the champion each against the same four local
opponents on the pinned 200-map panel (`77556dc9…`), 400 games each, paired by map and seat, `field.py`, the verdict on
the win indicator. **Dead if the field reading is below zero with its interval clear of zero.** A reading that straddles
zero goes to the real-field burst (`cgauto/field_panel.py`, the five Legend agents, 15 paired games) before any ladder
hour.

## Step 5 — the ladder

The owner's prediction asked before the submission; one hour; one reading; its 160 games collected and read (the third
troll's turn and share, wins by opponent roster, the games where the bill never completed).

## Done means

The ladder verdict on this card, or the on-paper death in step 1, or the field death in step 4.

## Dead means

Step 1's condition; the bed or the smoke showing a stall, a troll stuck funding, or lone-troll games; the field reading
below zero clear of zero.

## Budget

1 read (one day) · ≤ 2 design rounds · 1 build · 1 bed · 1 smoke · 1 reproduction · 1 field reading (+ 1 real-field burst if
it straddles zero) · 1 ladder hour · 1 reading. Nothing else is promoted, reverted or chartered by this card.

## Log

- 2026-09-02 18:0xZ owner: **"1. yes"** on the successor; **"2. codex_1 is dead for now. If we need review, we can ask it
  from chatgpt_1. But you need tell me to activate it after you send it assignment"**; **"3. extend"** on the orchard rows
  (a separate card's business; the orchard line gets one more reading as orchard 8). — owner
- 2026-09-02 18:1xZ coordinator: this card written; the cost table computed from the referee's rule
  (`training_cost`: `n + talent²` per kind); step 1 chartered to claude_1 by an ack-required handoff; the coordinator's
  own expectation, written before any number: the cheapest troll's bill is about 25 turns of two-troll collecting if the
  fruit is near the shack, and a 1/1/0/1 troll earns roughly a third of a 2/2/0/2 troll's wood; net a few points either
  way, so the read decides, and about one chance in three that a build beats the champion on the field. — coordinator
- 2026-09-03 04:02Z–04:23Z claude_1: step 1 delivered (`claude_1/cheap-third-troll/READ-2026-09-03.md`, pinned `54786b02…`;
  handoff `20260903T042300Z`): the bill short in 319 of 319 games (median 6 items); the fruit a 37-turn detour for the
  starting troll (the only harvester, carry 1) while the trained troll mines the iron in 9; wood forgone 11 points; fruit 8
  at face value, 25.5 as the seeds the champion turns 81 % of its plums and lemons into; the troll earns 30 [28, 32]. A1
  +11.0 [9.2, 13.0] / −6.5 [−8.4, −4.6]; A2 −7.0 / −24.5; B30 +5.1 / −0.8 in 107 of 319 games. Recommendation: no build. — claude_1
- 2026-09-03 05:2xZ coordinator (VM fallback): **verified by execution** — the three scripts re-run from the raw replays on
  the VM, all five JSONs identical to the pin, the headline counts recounted with independent code
  (`local_claude_1/cheap-third-troll/VERIFY-2026-09-03.md`). **Ruling: dead on paper, no build.** The card's own condition
  reads two ways and the read is honest about both: at face value the bill (11 + 8 = 19 points) is under the thirty-point
  line and the troll covers it (+11); at the seed value the bill is 36.5 points, over the line, and the troll does not cover
  it (−6.5, interval clear of zero). The measured 81 % swap rate makes the second reading the one the champion actually
  lives in; the only variant that loses under neither (buy only when the bill is within 30 turns) is worth +5 to −1 a game
  in a third of the games — below what the field panel can read (half-width about 4.5 points), so a build, a bed, a smoke
  and a field reading would end undecided. The two doors the read names (a harvest-1 second troll; a talent priced in
  bananas) are other cards, not this one. Step 2 (chatgpt_1's design review) is not sent. The owner hears "no build" on the
  board; "build" reopens the card at step 2 with the 30-turn variant. — coordinator (VM fallback)
