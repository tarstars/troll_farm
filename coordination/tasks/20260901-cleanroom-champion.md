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
- chatgpt_1: the leakage audit of `CHAMPION-BEHAVIOUR.md` and `DOMAIN.md`.
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
