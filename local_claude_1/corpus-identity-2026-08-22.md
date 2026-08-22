# The authoritative corpus — pinned, 2026-08-22 (integrator ruling)

Measured on `project_host` (the owner's machine), not recalled. Every number below came from
parsing the files, after two grep-based counts disagreed with each other and both turned out
to be wrong — the JSON spacing varies between files, so `grep '"agentId": N,'` silently misses
records. **Count this corpus by parsing it.**

## Identity

| item | value |
|---|---|
| games, processed (`data/processed/games.jsonl`) | **21,496** |
| games, raw (`data/raw/games/*.json`) | **21,496** — agreeing exactly, 0 unparseable |
| trajectories (`data/processed/trajectories/`) | **21,496** files |
| `sha256(games.jsonl)` | `a882e52787fa474cba4cdbe6b08a20d5e3925fe8d743bc201da8f816eb1e4e14` |
| location | `project_host:/home/tarstars/prj/troll_farm/data/` — **untracked build products**; git tracks only 290 raw games plus three small manifests |

## Our own play, identified by account rather than by guesswork

Filtering on `agents[].codingamer.userId == 1302251` (our account, from
`data/raw/players.json`) rather than on a remembered list of agent ids:

- **8,590 games** played by our account
- **86 distinct agent ids of ours**, from `6536359` through `6648254`
- pseudonym throughout: `tass`

**The lineage is complete and current.** All thirteen of our most recent agents are present,
including the ones from the Arena block that finished today:

| agent | games | |
|---|---|---|
| 6593838 | 131 | the very-old resident `98628e98…` — the bot that produced the recorded oscillation episodes |
| 6631618 / 6632611 / 6633433 / 6634457 / 6634986 | 120 / 113 / 153 / 100 / 146 | cure C's five night agents |
| 6643835 / 6644257 / 6644785 / 6645217 / 6645883 / 6646271 | 143 / 135 / 73 / 47 / 144 / 101 | session 3, block 1 |
| 6646733 … 6648254 | 123 … 160 | session 3, block 2, ending today |

## Ruling

**This is the authoritative corpus for `20260822`-era measurement**, and the prevalence work
runs **here, on `project_host`** (owner, 2026-08-22: *"you can run measurements here"*). No
upload is required, so the metered-network rule is not engaged.

**A premise correction, and it is mine to carry.** claude_1 reported on 08-21 that *"the
resident is not in the in-repo corpus at all"* and that our lineage there was only `6536563`
and `6536359` — an older lineage. **That was accurate for what it could see** (290 git-tracked
games in its VM worktree) and is **false of this corpus**. The card was blocked on a data
premise that does not hold on the machine the owner has now put the work on.

## What this does NOT unblock

Two findings survive untouched, because they are about the instrument and not the data
(`coordination/messages/claude_1/20260821T114540Z-…-corpus-prevalence-blocked-handoff.md`):

1. **D-1 needs a replay → `Trace` adapter that does not exist.** The detector reads positions,
   cargo, inventories, plants and verbs, all of which a replay carries — so it is adaptable,
   through an adapter that must be written and reviewed. That adapter is the reviewable
   instrument, and it is still the gate.
2. **P4 is not applicable to a replay as accepted.** `eval_p4` reads `post_ct_state(ref)` off a
   live referee; a final keyframe is a reconstruction, not that input. A P4 prevalence column
   filled from a keyframe would mean one thing on the panel and another on the corpus. That
   stands until someone rules otherwise, and data availability does not touch it.

What IS unblocked is everything downstream of the denominators: per-agent-id populations are
now known and pinned, so the prevalence table's split by lineage — old resident versus recent —
is computable the moment the adapter exists.

## The adapter, sized by execution (2026-08-22)

"An adapter must be written and reviewed" was the blocker's shape. Measured on one of our own
recorded games (`897988921`, agent `6593838`, 300 turns), **it is a shape translation, not a
reconstruction — every input the detector's `Trace` needs is already present in the replay, in
decoded form**:

| `Trace(smap, states, commands)` needs | the replay provides |
|---|---|
| `StaticMap(width, height, walkable, shacks, iron, water)` | `decoded_states(...)[0]` → `width`, `height`, ASCII `rows` — one character-class pass |
| states S₁..S_T: units with `id/x/y/player/carry[6]`, `plants`, `inventories` | `decoded_states(...)[1]` → **301 per-turn states**, "exact official states" by the referee's own diff decoder |
| commands C₁..C_T per unit | `data/processed/trajectories/<id>.jsonl` → **300 rows**, `commands0` / `commands1`, our stream verbatim |

`601 frames, 301 keyframes` for a 300-turn game: states are **per-turn and complete**, not
sparse. Nothing about D-1's predicate — positions, cargo, inventories, plants, verbs — is
missing from a replay.

**The one genuinely dangerous detail is alignment.** 301 states against 300 command rows: the
extra state is the initial one, and whether a turn's commands pair with the state *before* or
*after* them decides every episode boundary. `Trace` silently truncates to `min(len)` and files
a note (A11), so an off-by-one here would not raise — it would mis-grade the whole corpus
quietly. That is the review's first object.

Two smaller ones: the map's character encoding must be read from the referee's own definition
rather than guessed, and the decoded `plants` must be proven field-for-field against what
`TraceParser` produces (`Plant` carries `kind, cell, size, health, fruits, cooldown`) rather
than assumed compatible.

**The parity control is the open design question, and it should be settled before building.**
The ideal control — the same game built both ways, panel transcript versus replay, with D-1
required to report identical episodes — may not be constructible, because panel games are
generated locally and are not Arena games. The candidate substitute is the old library's
`REAL_CORPUS` record, which controls the *detector* rather than the bot. Naming which control
is acceptable is codex_1's ruling, not the builder's choice.

## Two operational cautions

- **Do not run `data/scripts/parse.py` casually.** Its output paths are hardcoded to
  `data/processed/`, and `data/processed/stats.json` is *already modified in the working tree*
  on this machine. A careless rebuild overwrites tracked manifests.
- **Count by parsing.** Two independent greps gave 1,057 and 1,549 for the same question; the
  parsed answer is 8,590. Anything in this project that counts corpus membership with a text
  match is wrong and should be re-run.
