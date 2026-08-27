# GRAVEYARD — one paragraph per dead task (created 2026-08-26)

Format: **what it was · what killed it · what we learned · what would reopen it.** A dead task is
closed, not "in progress"; this file is the library the graveyard was missing. Older closures live
in `docs/CONSTRAINTS.md` (the register); from 2026-08-26 every kill lands here first.

- **2026-08-26 — Candidate 0, the champion's replant fallback fix** (`20260826-candidate-0-regeneration-fallback`).
  One-hunk change: when a troll's idle-regeneration plan has no chops, extend the command list
  instead of replacing it. Killed at G-1, reproduced by codex_1: blocking games 118/240 vs 43/240 —
  the surviving 7,500-point regeneration `PICK` beats every job for an empty-handed troll next to
  the shack, the bank clause offers `DROP` next turn, nothing links `PICK` to `PLANT`: a PICK↔DROP
  two-cycle. Learned: the regeneration value is real (+530 own-score points across the panel) but
  only a *plan-keeping* successor can capture it; also, the "−75 on m061" was Candidate 2's cost,
  not the champion's. Reopens only as Candidate 3's plan-keeping case (`PICK` and `PLANT` share
  `Target::Cell(c)`), tested on `m061` at G-2.

- **2026-08-25 — Candidate 1, the resolver hold** (`cure1`). A hold in the resolver against the
  dance; fired 253× on 160 real games, kept every bound, and appeared in **0 of 25** recorded
  dances — real dances are permanent-block dances, not transient ones. Learned: the library's
  idle-blocker fixture shape is 0 of 80 in real games; measure on real games before building.
  Reopens: never in this form; the code is kept.

- **2026-08-25 — Candidate 2, the swap, as a qualified cure** (`cure2`). Panel dances 27→13, 16
  controls pass, but the pre-committed stops fired: the goals stay with the cells, so the two
  trolls swap and swap back (the loop, C-5 = 5), −5/game. Learned: a swap needs goals that travel
  with the troll — that is Candidate 3. Reopens: on top of Candidate 3, only if Candidate 3's
  panel shows an own-score gain (owner bound 08-26).

- **2026-08-26 — Candidate 3, the fixed-margin form** ("keep unless a challenger is clearly
  better by `M`"). Falsified, not mis-tuned: on the six loop games the challenger's advantage
  rises monotonically as the shared tree nears completion (0.02 → 0.27), so no constant `M`
  proves "no second exchange". Learned: a margin cannot bound a quantity that grows with the
  loop's length. Replaced by the absolute-keep form (same task, still alive).

- **2026-08-26 — Candidate 3, "a troll keeps its goal" (absolute form)** (`20260826-candidate-3-keep-your-goal`).
  A troll keeps its chosen goal until done (a tree: chopped there and carry full), gone, impossible
  or dead; when two kept goals cannot be paired the younger is released (contested release);
  telemetry v6. Built and measured in one day under the owner's bound. **What it did:** the loop it
  was built to remove is gone (`xc = 0` on all six loop games; blocking games 52 → 40; D-1 27 → 23;
  containment perfect, 0 telemetry errors over 48,000 turns). **What killed it:** its own
  pre-registered risk gate — **−65 own-score points over 240 games** (`m061` −47/−43, D-9 24 → 28)
  and a goal kept **171 turns** against a 30-turn stop; the packet says "the absolute form is too
  strong" and forbids repairing it with a margin. **Learned:** goals that travel with the troll do
  cure the swap loop, so the *mechanism* is right; a keep with no release for "a better tree is
  now beside me" is a keep that outlives its usefulness — the release list, not the keep, is the
  design problem. Also: a rule that is inert on `>= 3` units and never made a partner wait (`xp`,
  `xg`, `xw` all 0) is cheaper than feared on those axes. **Would reopen it:** a *bounded* keep —
  release on a strictly-better adjacent goal or a turn cap — as a new candidate with its own
  card, only if a top-10 read (Track T) says goal stability is something the strong bots have.
  Diff kept on `main`: `readable/diffs/candidate-3-keep-your-goal.diff`; packet
  `claude_1/cure3/g1-packet-2026-08-26.md`; codex_1's reproduction is the last act.

- **2026-08-26 — the 34 frozen oscillation fixtures (OSC-001…034) as gates** (`20260826-fixture-drift`).
  Cut in July from local games of the very-old bot `98628e98`; "reproducible on base" meant the
  candidate replays that bot's exact episode, so every bot generation since silently failed more of
  them (23 of 34 by the champion). Killed by the owner's ruling to retire old data and generate
  fixtures from fresh instrumented real games instead. Learned: a frozen position from an old bot is
  a wasting asset; fixtures must be a script's output tagged with the bot hash. The files and the
  08-21 verdicts stay as history. Would reopen: never as gates; the successor is
  `20260826-fresh-fixture-dataset`.

- **2026-08-26 — Candidate 3b, Candidate 3 plus the stuck-holder release** (`20260826-candidate-3b-stuck-holder-release`).
  The bounded successor the Candidate 3 obituary asked for: keep your goal, but release a troll that
  has held one goal too long while a partner waits. Nine gates were written into the card at 15:16Z
  before any source existed. **What it did:** the release fires exactly twice in 240 games, at
  `m061:0` t73 and `m061:1` t109 — the two seats and almost the two turns D-3 predicted (t72/t108) —
  cures the kept-goal age on those seats (171/170 → 43/78), and is otherwise free: 238 of 240 games
  are byte-for-byte Candidate 3, containment is command-identical on all 240 panel games and
  byte-identical on 34/34 fixtures, `xc = 0` on all six loop games, determinism 0/240.
  **What killed it:** gate 4 — the release recovers **none** of the lost points. `m061` still scores
  32/35, identical to Candidate 3, still −43/−47 against the champion. Gate 6 also fails (max kept-goal
  age 88, on `m068:1`, a game the rule does not touch — that pre-commitment was mis-specified, and
  saying so is part of the record). **Learned:** the −44/−47 on `m061` is **not** caused by the long
  kept goal. Two candidates now agree on it: cure the age and the points do not come back, so the
  cost lives somewhere else in the absolute keep and the release list is not the whole design problem
  after all. Also learned that a pre-committed gate can be *wrong* — gate 6 measured a game outside
  the rule's reach — and that the honest move is to fail on it anyway rather than rewrite it after
  seeing the number. **Would reopen it:** only on a new mechanism for `m061`'s deficit found by
  measurement first (what those two seats actually lose points doing), never as a retune of this rule.
  Packet `claude_1/cure3b/g1-packet-3b-2026-08-26.md`; diff
  `readable/diffs/candidate-3b-stuck-holder-release.diff` (+80/−3); result
  `claude_1/cure3b/results/panel-read3b.json` (SHA-256 `8280f927c2900559…`). codex_1's independent
  reproduction (`codex_1/reviews/candidate-3b-reproduction-2026-08-26.md`, commit `4dcd3d82`) was the
  last allowed act and returned **REPRODUCED FAIL** with a byte-identical verdict JSON.

- **2026-08-26 — the banana wood farm, first build** (`20260826-banana-farm-candidate`). Stopped at
  its own first validity gate the same night it was chartered, and reproduced by the second bot.
  **What it did:** containment perfect (with the farm switched off it is byte-identical in play to
  the champion on all 240 panel games and 34 fixtures); the diagnostic dialect decoded with zero
  errors; on the local bench its own score was **+3,100 over 240 games** — the opposite sign to the
  pre-registered expectation. **What stopped it:** blocking games rose **52 → 96** (50 new, 6
  cured), and on 35 of the 50 the cause is `opp_harvested_ours` — *the opponent walks onto our hut
  ring and eats the fruit we grew*. The pre-committed stop-latch fired in **0 of 240** games because
  it counts enemy **chops** on the ring while the theft that actually happens is **harvests**: one
  design defect showing up twice. **Learned:** the owner's stop criterion ("the farm is more
  profitable for the enemy than for us") is right, but its observable must count harvests, not
  chops; and a ring next to our own hut does not protect the crop — the enemy pays the trip. Denial
  was a formality on this corpus (509 turns in denial against 28,239 farming; in 141 of 240 games
  there was no aim tree left to deny when the second troll appeared). **Would reopen it:** a bounded
  repair with the latch counting harvests and a placement rule that does not hand the enemy a
  standing crop — the owner's call. Packet `claude_1/farm/g1-panel-farm-2026-08-26.md`; reproduction
  `codex_1/reviews/banana-farm-panel-reproduction-2026-08-26.md`; design
  `claude_1/farm/g0-farm-2026-08-26.md`; contract `docs/BANANA-FARM-CONTRACT-2026-08-26.md`.

- **2026-08-27 — the banana farm line, CLOSED by the owner** ("closed", 10:04Z; `20260826-banana-farm-candidate`,
  board row F-2). **What happened after the first build stopped:** the owner had it put on the ladder
  for one hour to be *seen* — 10.8 at rank 172 of 176 (submission `41201668`); its 160 games, collected
  and decoded from the farm's own telemetry, split 81 wins / 79 losses, mean margin −26 (own 169 vs
  opponent 195), 24 losses by 150 or more with the opponent near 400. **Correction to the paragraph
  above:** on the ladder the denial stage was *not* a formality — it ran ~65 turns a game in every game
  (ended: all aim trees felled 66, regrowth 35, opponent's third troll 31, deadline 14, still denying
  at the end 14); the local panel's maps and opponents were not the ladder's. The farm planted 16
  bananas a game and harvested 4.8 from mothers; the latch fired twice. **What killed the line:** the
  owner's judgment that the farm changed several things at once ("a dirty experiment"); a one-variable
  ablation of the champion's own denial rule was run instead and became the champion; then "closed".
  **Learned:** experiments change one variable; the ladder's answer differs from the bench's (the
  panel said denial never ran, the ladder said it always did); a hut-ring farm feeds a harvesting
  opponent. **Would reopen it:** only the owner's word; the denial-first repair the owner chose on
  the morning of 2026-08-27 (chop the opponent's plums and lemons first with hard priority, nothing
  planted until denial ends, farm afterwards) is written into the card for that day. Games
  `local_claude_1/farm-watch/games-41201668/`; readable diff `readable/diffs/banana-farm-vs-v6-instrument.diff`.

