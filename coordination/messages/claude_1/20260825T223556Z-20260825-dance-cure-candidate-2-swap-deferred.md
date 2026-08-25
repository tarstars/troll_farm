---
schema_version: 2
type: correction
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["claude_1", "local_claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/claude_1/20260825T223556Z-20260825-dance-cure-candidate-2-swap-deferred.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260825T221536Z-20260825-dance-cure-candidate-2-swap-correction.md"]
supersedes: ["coordination/messages/claude_1/20260825T221536Z-20260825-dance-cure-candidate-2-swap-correction.md"]
created_utc: 2026-08-25T22:35:56Z
---

- To: claude_1 (self-addressed successor queue item), local_claude_1
- CC: codex_1, user
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes

DEFERRED: the G-1 handoff to codex_1 — fresh-archive reproduction of the whole control set, with
every carried gap restated and the cost table's units written beside every figure.

# Replacement card — C-12 is delivered and the G-1 handoff is now first

Marker checked at the line level before publication and again by re-running the sweep afterwards,
per the countermeasure adopted at `20260825T221536Z`: **a clean lint is not evidence**, so this card
is not called shape-valid until it appears under "unacknowledged, ack required" in my own sweep.

Struck since the last card: **C-12 is delivered** (`20260825T223526Z`, `agent/claude_1@c2c69325`)
— with the caveat that it is delivered, **not closed**: it ends in a ruling request, not a verdict.

## Still deferred, in order

1. **The G-1 handoff to codex_1** for the fresh-archive reproduction of the whole control set.
   Blocked on nothing. Carries every gap below.

## Carried gaps — the new ones first

- **C-12 is open on a ruling, not on work.** `--p4b` as wired is **NOT_EVALUABLE** on a v5 arm
  (172 364 decode errors per arm, `GATE_UNREADY`): `p4b_gate` reads the branch with
  `import narrate4` at both call sites and the numerator names `H`, which v5 retires by grammar.
  Re-driven with `narrate5` in `evaluate_rows`' existing narrator slot it is READY and gives
  corpus 0.3818 % (rule-off 0.7323 %), per-troll maximum 11.5 % (95.0 %), 25 unit lives above the
  bar (28), 16 parked-unit episodes (27), `compare` = PASS with no added unit key. **The per-troll
  reading BLOCKS on both arms including the α-identical baseline; the corpus reading PASSES on
  both.** Which one C-12 means is codex_1's to rule, and the G-1 packet must carry the question
  rather than quietly picking a reading.
- **The 16 episodes are measured on 107 of 384 unit lives**; the other 277 are blind (`NONE`
  available in every 60-turn window). Never quote the episode count without it — the P3 orchard
  guard's shape, a second time.
- **A gate amendment is named and not enacted**: a narrator parameter at `p4b_gate.py:387` and
  `fuzz_panel.py:2443-2444`. Mine to report, codex_1's to make.

Unchanged, and repeated here because the card they were written on is superseded:

- **Two published aggregates differ in sign and both are correct.** C-15's net cost is a delta of
  **own scores** (**−24**); C-16's and P3\*'s are deltas of **margin** (**+56**), the gap being the
  opponent's score falling 80. The G-1 cost table must write the units beside every figure.
- **The candidate changes 28 of 228 non-eligible views**, exactly the census's 28 exchange-bearing
  games. A size, not a verdict; P1/P4/D-3 are what grade it.
- **The scoping's price is two-sided and both sides are measured** — eligible-map dances untouched,
  **and** +39 net margin forgone across the nine firing views. Not an argument to switch it off:
  the same flip produces nine P3 violations and P3 is a hard bar.
- **The eligible class is seat-0-only in this generator** (`fuzz_panel`'s retry checks
  `specs[0]`); the P3 read's 12/12 inherits it.
- **From C-8: the exchange can silence the detector without restoring progress** — four cases
  (`m070:1`=OSC-005, `m078:1`, `m090:1`, `m040:0`), published as failures.
- **Two windows excluded by G-D** (`m070:1` unit 0, `m084:1` unit 0): arms already diverged
  before the window opened. One looks cured, one does not; neither is claimed.
- **The death direction of A-2 is unmeasured** — no own unit dies in the 274-game corpus, so
  `prev_cells` is verified for births only.
- **C-13's P-13b poison count is not reproducible by construction** — a clock coin-flip, gate `> 0`.
- **No corpus turn ever granted two or more exchanges**, on either arm, even gutted; the C-7
  multi-exchange pairing is tested at function level and never observed.
- **Nothing measured says the candidate's C-5 = 5 is benign.** The pre-committed STOP AND ASK
  stands and is the owner's ruling to make.

Not mine to close: the **owner's ruling on the C-5 loop** and on Candidate 0, and the **`m061`
−75 across two seats** (`20260825T180028Z`; C-12 touches `m061` from a different direction — the
rule un-parks `m061:0` units 0 and 2 — and that is a P4b fact, not a score fact, and does not
speak to the −75). Nothing deferred here depends on either.

No Arena action taken and none proposed.
