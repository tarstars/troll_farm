# Card 20260901-cleanroom-champion — the clean-room reimplementation of the champion

Born 2026-09-01 06:0xZ (the owner: "I like it", on the design of 05:5xZ). Coordinator:
`local_claude_1`. Spec-writer: `claude_1`. Implementer: **a fresh agent that has never seen this
repository's sources** (the mechanism is the owner's open choice, §Roles). Auditor: `chatgpt_1`
(the spec's code-leakage review). Runs fully parallel to Track N; touches nothing on its critical
path; **no platform action anywhere on this card.**

**The experiment.** Write a complete description of the champion of record — the game's rules,
the platform's constraints, the champion's observable behaviour, and the domain's hard-won facts
— into one self-sufficient package in a separate directory, and have a fresh agent reimplement
the bot from that package alone. The hope: a leaner implementation of equal strength; the
guaranteed by-product: a written specification of our own champion, which has never existed.

## The package (`cleanroom/package/`, six parts)

1. **`RULES.md`** — the game completely, including the referee's hard semantics as *physics*:
   movement-conflict resolution, tie-breaks by plant order, the TRAIN affordability dry-run,
   scoring (fruit 1, banked wood 4 at game end), the endings (turn 300, mercy, grace), map
   geometry (width = 2×height, 8–11, point symmetry). Nothing here is architecture.
2. **`CONSTRAINTS.md`** — one file, std only, 50 ms a turn (1,000 ms first), **100,000
   characters counted as UTF-16 units**, no AVX2 without a runtime check with a fallback, and
   the seat rule: the protocol carries no seat — recover it once on turn 1 from the starting
   troll's id, fail closed.
3. **`CHAMPION-BEHAVIOUR.md`** — the champion's observable play, written **from replays only**
   (its 160 collected ladder games, `local_claude_1/denial-ablation/games-41202036/`, plus
   locally generated games as needed): the turn-1 opening, what it trains and when (talents and
   timing distributions), harvest/chop/plant priorities as observed decision rules, target
   selection, movement habits, endgame. **Every stated rule cites at least one concrete game
   observation** (game id + turns). Neutral vocabulary — none of our internal terms.
4. **`DOMAIN.md`** — results, not designs, each line with its evidence level: what the top four
   players do in common; the tested-and-failed ladder list (each one line: the behavioural idea,
   the reading); the never-abandon finding; map statistics.
5. **The harness** — the champion **as a compiled binary only, never as source**, a map slice, a
   runner that plays the candidate against it and checks legality/completeness, and the
   acceptance ladder: legal complete games → the 48-game scout → the 144-cell locked panel →
   400 games.
6. **`EXCLUDED.md`** — the visible contract: every `.rs` of ours, the readable diffs, the
   simulator's source, the generator chain, and all our opinions about code structure are
   deliberately absent.

## Honesty about purity

Every current agent has seen the champion's source, so a perfectly unseen spec-writer does not
exist. The guards that do the real work: (a) the evidence-link rule — no behavioural claim
without a cited game observation; (b) the vocabulary ban; (c) chatgpt_1's adversarial audit of
the spec for code-leakage before the implementer sees it; (d) the *implementer* is genuinely
fresh and receives the package directory and nothing else, with the instruction not to read
beyond it (containment is by instruction and self-sufficiency; the harness cannot hard-wall the
filesystem — stated, not hidden).

## Roles and the one open choice

- claude_1: parts 1–6 assembled, the spec from replays, 2 days.
- **THE STOP (owner 2026-09-01 06:4xZ): when the package is delivered, the card HALTS.** Two
  reviews run before any implementer exists: chatgpt_1's adversarial cross-review (leakage,
  completeness, correctness of the cited observations) and **the owner's own read of the
  description**. The implementer is chartered only on the owner's explicit word after their
  review; the implementer-mechanism choice lands then too.
- chatgpt_1: the cross-review of `CHAMPION-BEHAVIOUR.md` and `DOMAIN.md` (leakage + completeness).
- **The implementer — the owner picks the mechanism**: (my recommendation) a new launcher agent
  entry (`fresh_1`) whose cwd is the package directory and whose charter is this card's
  implementation brief; or the owner runs a fresh session themselves in that directory. 3 days,
  one pre-registered refinement loop: bed the result against the champion binary, list the gaps
  *as game observations*, refine the spec once, rebuild.

## Done / Dead / Budget

**Done.** The reimplementation plays legal complete games and, after at most one refinement
loop, reaches parity with the champion on the locked panel (the paired protocol; parity = the
95 % interval of the per-cell margin delta contains 0 or better) — with the source length
recorded; or the experiment reports what the spec missed and why.
**Dead.** After the one refinement loop the reimplementation wins less than 40 % of the
champion's own win count on the scout panel — the line reports and stops (the spec remains a
deliverable regardless).
**Budget.** Spec + package 2 days; implementation 3 days; one refinement loop; zero platform
actions; the messages per the WIP rule.

## Log

- 2026-09-01 06:0xZ: born; the design discussed with the owner 05:5xZ and approved ("I like it");
  claude_1 chartered for the package (the same hour's handoff). — coordinator
- 2026-09-01 06:4xZ: **the owner adds the review stop**: after the description is done, the card halts for the owner's own
  read and chatgpt_1's cross-review; the implementer starts only on the owner's word after that. — owner/coordinator
- 2026-09-01 07:5xZ: **the package delivered in 40 minutes and merged (`6fde2e78`)** — 33 files, ~1,000 doc lines, 26 cited
  observations over 7 matches; the champion ships as a stripped ELF with a 9,502-seat-turn parity proof; two leakage channels
  found and closed by the author (the NARRATE debug channel; the binary's symbol table) with full disclosure; the
  determined-vs-undetermined split names the two things replays cannot fix (tree choice, the train trigger). Structural
  verification by the coordinator: zero `.rs`, the binary a real stripped executable, the citation discipline on page one.
  **THE CARD IS HALTED per the owner's stop**: chatgpt_1's cross-review chartered (07:45Z); the owner's own read awaited;
  the implementer exists only on the owner's word after both. — coordinator
- 2026-09-01 09:3xZ: **the coordinator's own review of the package, at the owner's word ("make review of cleanroom"):
  ACCEPT-WITH-EDITS, round 1 of 2** — `local_claude_1/cleanroom-review/review-2026-09-01.md`, every number by execution.
  Passed: zero `.rs`, no internal vocabulary, the binary stripped (the one `_ZN` is the demangler's literal), the parity proof
  re-run from a fresh build (9,502 seat-turns, 0 differ), `measure.py` reproduces `observations.json` byte-for-byte, and
  `referee.py` replayed against all 160 real recordings (39,176 turns) agrees with the platform everywhere but one rule
  (87/87 early endings on the exact turn; all 1,164 move differences are the random tie-break). Seven edits, one
  substantive: (1) the substitute train rule in §4 matches the champion's purchase turn in only 63/160 and otherwise buys a
  median 10 turns early with a weaker worker — state the agreement honestly and ship the per-match data; (2) referee.py lets a
  seed planted this turn be chopped this turn, the platform does not (match 900572315 t258/t262) — the only rule
  disagreement; (3) the time rule is "third strike loses" in the platform's own words, not "fourth"; (4) the harness README's
  mirror baseline is wrong (measured 59–220, mean 130, 16 draws of 48); (5) the apple-farm line quotes one reading of six;
  (6) "latest purchase turn 32" vs the corpus max 35; (7) the platform accepts numeric item codes, referee.py calls them
  fatal. Back to claude_1 for the edits; chatgpt_1's cross-review still pending; the owner's read awaited; no implementer. — coordinator
- 2026-09-01 09:4xZ: **the owner: "fix clean room problems you found" → all fixed by the coordinator, in the package itself**
  (round 1 closed the same hour): §4 rewritten around the measured agreement + `champion-purchases.json` shipped (160
  matches, the shack turn by turn up to the purchase); referee.py — CHOP acts only on trees that stood before this turn's
  PLANTs, the third strike loses, numeric item codes accepted, a 5 s hang guard (`--wall`), a per-turn `--trace`; RULES §6/§9/§10/§12
  and CONSTRAINTS §3 corrected; the harness README's mirror baseline replaced by the measured one and shipped
  (`reference-vs-reference-48.json`); DOMAIN's apple-farm line now the whole series with same-day references. Re-verified:
  all 40,458 recorded turns replay through referee.py with nothing left but the random tie-break and one platform timeout;
  parity 9,502/0; the mirror baseline identical before and after. Still open: chatgpt_1's cross-review (now of the corrected
  pin), the owner's own read, the implementer on the owner's word. — coordinator
- 2026-09-01 10:1xZ: **the owner's read of the behaviour document: "too fine details … the main idea is to reproduce the bot
  from scratch and create a more compact and logical implementation; details like the order of seeds already make code
  bulkier" → "do it".** `CHAMPION-BEHAVIOUR.md` restructured: Part I = one page, ten principles each with its reason and a
  mark ESSENTIAL (carries score) / HABIT (free) / NOT DETERMINED (the implementer's judgement); Part II = the whole evidence
  base unchanged (every count, table and citation, now an appendix for audit and the refinement loop). The seed-order table
  becomes one sort key ("cheapest sapling first"); the README now says habits are not the specification and strength is
  measured on the harness, not by resemblance. No number changed. — coordinator
