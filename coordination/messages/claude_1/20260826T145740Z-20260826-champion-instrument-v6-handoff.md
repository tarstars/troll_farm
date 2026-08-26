---
schema_version: 2
type: handoff
task_id: 20260826-champion-instrument-v6
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260826T145740Z-20260826-champion-instrument-v6-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 7f52c8c3101d25b6ab82088ffc7bb43670fa4570
artifact_paths: ["claude_1/instrument6/champion-v6-instrument-2026-08-26.md", "claude_1/instrument6/champion-v6-instrument.rs", "claude_1/instrument6/make_champion_v6.py", "claude_1/instrument6/parity.py", "claude_1/instrument6/fixtures.py", "claude_1/instrument6/wire_budget.py", "claude_1/instrument6/results/build.json", "claude_1/instrument6/results/parity-panel.json", "claude_1/instrument6/results/fixtures.json", "claude_1/instrument6/results/wire-budget.json", "cgauto/submissions/candidate-champion-v6-instrument.rs", "readable/reports/champion-v6-instrument.round-trip.json", "readable/diffs/champion-v6-instrument.diff"]
created_utc: 2026-08-26T14:57:40Z
---

- To: codex_1 (the one review round)
- CC: local_claude_1 (board row 0-3a and the submission), user, chatgpt_1
- Task: 20260826-champion-instrument-v6
- Requires acknowledgement: yes — your review is the last step before the coordinator submits

# 0-3a — the champion with v6 telemetry: built, gated, compacted, and ready for slot 1

Report: `claude_1/instrument6/champion-v6-instrument-2026-08-26.md`.
Diff of record: `readable/diffs/champion-v6-instrument.diff` (+926 / −8 against `ad1ae4ef`).

## The objects

| | path | sha256 |
|---|---|---|
| base (readable) | `readable/door1-champion.rs` | `ad1ae4ef…0bfb` |
| base (on the ladder now) | `cgauto/submissions/candidate-door1-pure-deletion.rs` | `547fa706…70b0` |
| one source | `claude_1/cure3/cure3-keep-v6.rs` | `01b61444…b3b3` |
| the arm | `claude_1/instrument6/champion-v6-instrument.rs` | `0f75e7d6…4141` |
| **the submission** | `cgauto/submissions/candidate-champion-v6-instrument.rs` | `72673124…8c82`, 63,962 bytes |

The arm is the Candidate 3 source with its single flag line (line 602) set to
`KEEP_RULE_ENABLED = false; NARRATE_V6_ENABLED = true`. Keep rule off = **no rule change**: what
is left over the champion is the narrator and the instrumented resolver that feeds it, and both
only read. It is byte-for-byte your already-reproduced `claude_1/cure3/arm-ruleoff.rs`, and
`make_champion_v6.py` refuses to produce anything else — it regenerates from the source and
compares, so the lineage is checked rather than asserted.

## The gates

**Probe parity, 240 panel games, command-stream level** (`results/parity-panel.json`):
240/240 byte-identical to the champion with `MSG` stripped from both sides · 240/240 same
opponent stream · own-score 5,712 vs 5,712, 0 games differing · 48,000 `MSG` lines decoded,
**0 decode errors** · 240/240 still announce `yamo-carry-regen-transit-idle-harvest-rust` exactly
once, so attribution of the collected games is preserved.

This is **not** the `panel_read.py` containment number. That compared the two seats' *scores*, and
equal scores are not parity: two different command streams can score the same. This compares the
streams, and it had not been computed before.

Worth your eye: stripping `MSG` from only the arm's side scores **0/240**, because the champion is
itself an `MSG` speaker (`door1-champion.rs:1136`). That was the first run of this gate; it is in
the report rather than quietly fixed.

**34 fixtures** (`results/fixtures.json`): 34/34 parity without `MSG`, 34/34 identical referee
state, 34/34 deterministic when the same start is run twice (`MSG` payloads included), 34/34 the
**compacted submission** plays identically to the readable arm, 0 telemetry errors. The 34 are
retired as gates (row 0-1) and are used here only as a differential bed between two of our own
binaries; the count is not offered as a behaviour result.

**Round trip** (`readable/reports/champion-v6-instrument.round-trip.json`): `compact(arm)` is the
submission byte-for-byte, and `compact(readable champion)` shares the token stream of `547fa706…`
— so the base of this arm is provably the bot on the ladder.

## What I did not spend

No panel run: the bytes under test are the bytes Candidate 3's panel ran, and its archive keeps
both command streams per game. If you judge that a fresh 240 is required rather than a re-read,
say so in your one round and it will be run — I did not spend a panel on my own authority. The
archive is `/tmp/claude-1000/cure3/ruleoff/games/games.jsonl.gz`; every derived row is committed.

## The one open risk, measured

`wire_budget.py` → `results/wire-budget.json`: 67,355 `MSG` payloads across our 290 collected
games, **longest 127 characters**; ours reaches **328** (widest command line 350 vs the champion's
70). The capability audit recorded the `MSG` round trip as byte-preserved but never at what
length. It is an absence of evidence, not a limit — the ask is that the first collected game after
submission is decoded before any telemetry is read as data.

## To reproduce

```bash
python3 claude_1/instrument6/make_champion_v6.py
python3 claude_1/instrument6/parity.py
python3 claude_1/instrument6/fixtures.py
python3 claude_1/instrument6/wire_budget.py
```

Each refuses on a hash it does not expect rather than producing a plausible file.
