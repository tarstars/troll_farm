# `readable__no_orchard` — reference record

Owner-assigned reference name, 2026-08-08. Use this name in all future discussion of this bot.

## Identity

| field | value |
|---|---|
| **reference name** | **`readable__no_orchard`** |
| source path | `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` |
| source SHA-256 | `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29` |
| registry `source_id` | `e7a-readable-no-orchard-code-cost` |
| agent / submission | `6593838` / `41089629` |
| file size | 75,634 bytes, 1,475 lines |
| real code size | **46,859 chars** (comments and all whitespace removed) |
| disposition | `displaced_superseded` — **not currently on the platform** |

## Why it has a name

Three properties hold simultaneously, and no other bot in the registry has any two of them:

1. **It is the only human-readable submitted source.** Every other registered bot is a single
   line of 55,000–99,000 characters. This one is 1,475 lines.
2. **It is the smallest bot we have**, by real code with formatting normalised away — 46,859
   characters against 54,720 for the bot currently live, a 14% reduction.
3. **It is the highest mature score we have ever measured**: **24.76, rank 21/137**, over a full
   160 games, 94W/2T/64L, identity and runtime clean.

## What is running instead

`e7a-r36-simplified` (`2caac7c6…`), submission `41090606` / agent `6594200`: minified,
single-line, 54,720 chars of real code, **22.81 at rank 32/137**. We replaced
`readable__no_orchard` with a bot that is 17% larger and ~2 points worse.

## Verified properties

- **It is the submitted artifact, not a reconstruction.** Its filename begins `submitted-`
  rather than `candidate-`, and normalising every registered source and every file in
  `cgauto/submissions/` finds no other file with matching normalised content. The bot that
  scored 24.76 was submitted in readable form.
- **The orchard is genuinely absent.** Nine `BANANA` references remain and every one is generic
  game plumbing — the item index, the `PlantKind` enum, string parse/format, growth cooldowns,
  tree-health parameters, the carry lookup. There is no pick-from-shack, no ring planting, no
  own-crop harvest. The only two occurrences of "orchard" are in its header comment.
- **Minification is behaviour-preserving**, so a minified and an expanded form of the same code
  are the same bot (owner ruling, 2026-08-08). Applying that test does **not** merge this bot
  with `e7a-r28-no-orchard-ablation`: normalised, they are 46,859 versus 55,116 characters —
  about 8,000 characters of genuinely different code, despite both being "no orchard" E7a
  derivatives. They are different bots and their runs do not pool.

## The caveat that governs any decision

**One mature run.** The registry raises this itself:

> `SINGLE_MATURE_RUN`: one mature run cannot distinguish the source's level from a lucky draw;
> the 2026-08-02 selection error had exactly this shape.

Supporting the caution: `e7a-r28-no-orchard-ablation`, a different but related no-orchard
source, scored **23.27** on its own single run. A 1.5-point spread between two no-orchard
variants is wider than the ±0.5–1 noise band we normally assume, so this bot's true level is
not established.

By *repeated* evidence the leaders are `preseed-e7a-lemon-near-tie` (median 24.41 over 2 runs)
and `preseed-orchard-coverage-slim` (median 24.19 over 4). `readable__no_orchard`'s single 24.76
exceeds both maxima but has no repetition behind it.

**The cheapest way to settle it is to re-run this exact source for a second mature
observation.** No code change, no detector gate, no dependence on the measurement apparatus
currently ruled `GATE_UNREADY`. It is an Arena action and needs owner authorisation.

## Oscillation: yes, and it is inherited — not caused by the orchard

Measured 2026-08-08 on the owner's expectation that this bot oscillates. It does.

`readable__no_orchard` judged against itself over the standard 240-game panel
(`local_claude_1/verification/readable-no-orchard-oscillation-2026-08-08.json`):

| | `readable__no_orchard` | banana parent `a8eb3b2b` |
|---|---:|---:|
| D-1 episodes | 34 | 35 |
| of which ≥62 turns (terminal mode) | 20 | 20 |
| games affected | 32 / 240 | 32 / 240 |
| longest episode | 194 turns | 194 turns |

Median episode 155 turns; the worst occupies **194 turns of a 200-turn game**. Unit 2 (the
second worker) accounts for 25 of the 34; unit 0 for 9.

**The decisive number: the same 32 of 32 `(map, seat)` pairs oscillate in both bots.** Not a
similar rate — the identical games. So the oscillation is **inherited from the shared E7a
movement core and has nothing to do with the orchard**, which this bot does not have. That is
consistent with `claude_1`'s root cause for D1-A: same-tree contention against a memoryless
detour tie-break in `resolve_move_conflicts_with_priority_and_forbidden`, which is core
movement code present in every variant.

Practical consequence: **stripping the orchard is not an oscillation fix, and any oscillation
work applies equally to every bot in this family.**

### Instrument caveat, and why it does not bite here

The panel is under `GATE_UNREADY` (`chatgpt_1` ruling 2026-08-08): its referee parses `TRAIN`,
silently discards it, and continues, so D-9 and P4 conclusions from it must not be quoted.

That ruling does **not** void this measurement, for three reasons: the ruling names D-9 and P4,
not D-1; the defect affects exactly two games, both on map `m040`, and **`m040` contributes zero
D-1 episodes** in either run; and the comparison is like-for-like — same instrument, same maps,
same seeds, same panel — so even if the absolute rate is questioned, the *equality* between the
two bots is robust.

## Header claim not verified

Its first lines read `Canonical readable expansion: orchard_stripped` and `Generated by
build_readable_orchard_cost.py; only comments and whitespace added.` The second claim implies a
minified ancestor with identical normalised content. **No such file is committed** — the search
above found none. The claim is therefore unverified and should not be relied on; what is
verified is that this file is the artifact that was submitted and scored.
