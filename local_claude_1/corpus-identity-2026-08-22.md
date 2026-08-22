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

## Two operational cautions

- **Do not run `data/scripts/parse.py` casually.** Its output paths are hardcoded to
  `data/processed/`, and `data/processed/stats.json` is *already modified in the working tree*
  on this machine. A careless rebuild overwrites tracked manifests.
- **Count by parsing.** Two independent greps gave 1,057 and 1,549 for the same question; the
  parsed answer is 8,590. Anything in this project that counts corpus membership with a text
  match is wrong and should be re-run.
