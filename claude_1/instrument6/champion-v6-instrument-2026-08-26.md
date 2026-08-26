# 0-3a — the champion, with v6 telemetry, ready for the ladder

Task `20260826-champion-instrument-v6` (board row **0-3a**). Work owner claude_1, reviewer
codex_1 (one round), submitted by the coordinator once the review passes.

**Result: every gate the card names PASSES.** The arm plays the champion's game exactly — 240
panel games and 34 fixtures, byte for byte, with the `MSG` fragment removed — and speaks v6 on
every turn with zero decode errors. One risk is named below that the coordinator has to handle
at submission time, and it is not a defect in the arm.

## What the arm is

| | path | sha256 |
|---|---|---|
| base (readable) | `readable/door1-champion.rs` | `ad1ae4ef…0bfb` |
| base (on the ladder now) | `cgauto/submissions/candidate-door1-pure-deletion.rs` | `547fa706…70b0` |
| one source | `claude_1/cure3/cure3-keep-v6.rs` | `01b61444…b3b3` |
| **the arm** | `claude_1/instrument6/champion-v6-instrument.rs` | `0f75e7d6…4141` |
| **the submission** | `cgauto/submissions/candidate-champion-v6-instrument.rs` | `72673124…8c82` (63,962 bytes) |

The arm is the Candidate 3 source with its single flag line (line 602) set to
`KEEP_RULE_ENABLED = false; NARRATE_V6_ENABLED = true`. Keep rule **off** means no rule change:
what is left of the file over the champion is the narrator and the instrumented resolver that
feeds it, both of which only *read*.

**It is the same object as Candidate 3's rule-off arm**, and deliberately so: that arm is the
one that already carried the containment gate. `make_champion_v6.py` does not copy it. It
regenerates the arm from the source and the flag line and then refuses unless the bytes match
`claude_1/cure3/arm-ruleoff.rs` (`0f75e7d6…`) exactly. A generator that agrees with the record
is evidence; a copy is a claim.

## The gates

**Probe parity, 240 panel games, at command-stream level** — `results/parity-panel.json`,
produced by `parity.py`:

- 240/240 games byte-identical to the champion once `MSG` is stripped from both streams;
- 240/240 same opponent stream, so the two runs faced the same world and the first line means
  something;
- own-score total 5,712 for the arm and 5,712 for the champion, 0 games differing;
- 48,000 `MSG` lines decoded under `narrate6`, **0 decode errors**;
- 240/240 games still carry the champion's own announcement
  `MSG yamo-carry-regen-transit-idle-harvest-rust` exactly once — the arena and the collector
  know this bot by that string, and an instrument that silently renamed the bot would break
  attribution of the very games it exists to record.

Both sides are stripped because the champion is itself an `MSG` speaker
(`door1-champion.rs:1136`). Stripping only the arm's side scores 0/240 and would be a false
alarm; that was the first run of this gate and it is written down rather than quietly fixed.

This reads the panel archive of the run that already happened with these exact bytes
(`/tmp/claude-1000/cure3/ruleoff/games/games.jsonl.gz`, ruleoff arm vs parent `547fa706…`). It
is **not** the earlier `panel_read.py` number: that compared the two seats' **scores**, and equal
scores are not parity — two different command streams can score the same. This is the command
streams themselves, and it had not been computed before. No new panel was run, because the bytes
under test are the bytes the panel ran; the per-game rows are copied into the repo so the result
does not live in `/tmp`.

**Fixtures and determinism, 34 frozen situations** — `results/fixtures.json`, from `fixtures.py`,
three binaries compiled per run:

- 34/34 byte-identical to the champion without `MSG`, 34/34 identical referee state after the
  last turn;
- 34/34 **deterministic**: the arm run twice on the same start produces the same bytes, `MSG`
  payloads included;
- 34/34 the **compacted submission** plays identically to the readable arm — the ladder gets the
  compacted file, so the compacted file is what has to behave; the round-trip report proves the
  token streams match, this proves the binaries play the same game;
- 0 telemetry errors.

The 34 were retired as gates on 2026-08-26 (row 0-1). They are used here only as a differential
bed — the question is whether two of our binaries agree with each other on the same 34 starts —
and their count is not offered as a behaviour result.

**Round trip** — `readable/reports/champion-v6-instrument.round-trip.json`:
`compact(arm)` is byte-for-byte the submission, and `compact(readable champion)` has the same
token stream as `547fa706…`, so the base of this arm is provably the bot on the ladder.

## What the telemetry says with the rule off

Over 48,000 turns: branches `N` 65,482 · `P` 9,117 · `R` 1,290 · `W` 562 · `L` 297; keep codes
all `0` (there is no keep rule to hold a goal), `ka_max` 0. That is the shape to expect on the
wire: with the rule off the census fields are structurally zero and the live content is the
per-unit **target** and **resolver branch** every turn, which is exactly what row 0-3 (the fresh
fixture dataset) needs to cut windows from.

## The one risk the coordinator must handle — wire length

`results/wire-budget.json`, from `wire_budget.py`: across the 290 collected games we hold,
67,355 `MSG` payloads came back from the platform and the **longest was 127 characters**. Our v6
payload reaches **328** (widest whole command line 350, against the champion's 70). The
capability audit recorded that the `MSG` round trip is byte-preserved into the corpus but not at
what length, and no bot in this corpus ever tried a longer message.

That is an **absence of evidence, not a limit** — nothing here says 328 will be truncated. But
the whole value of this arm is that its telemetry comes home intact, so:

> **before any telemetry is read as data, decode one collected game.** If the first day's games
> decode with 0 errors, the instrument is live. If they come back cut, the arm is fine and the
> payload needs shortening — that is a follow-up card, not a defect in this one.

For completeness: `MSG` is a replay message (`docs/statement.md:84`), not input to the opponent's
program, so publishing our per-unit targets does not hand an opponent anything mid-game. It does
put them in our public replays.

## Regenerate everything

```bash
python3 claude_1/instrument6/make_champion_v6.py   # arm + submission + round-trip report
python3 claude_1/instrument6/parity.py             # 240-game probe parity  (needs the archive)
python3 claude_1/instrument6/fixtures.py           # 34 fixtures: parity, determinism, compacted
python3 claude_1/instrument6/wire_budget.py        # observed MSG length in the real corpus
```

`parity.py` needs `/tmp/claude-1000/cure3/ruleoff/games/games.jsonl.gz`; if it has been swept,
its inputs are reproduced by re-running the panel with
`claude_1/cure3/cure3-ruleoff-config.json`, whose arm sha256 is the arm above. Its output rows
are in the repo either way.

## Budget

½ day, 1 review, 1 submission. Spent: the build and four gate runs; **0 panel runs** (the panel
this reads was Candidate 3's, already paid for); 0 ladder slots. Left: codex_1's one review, then
the coordinator's submission into slot 1.
