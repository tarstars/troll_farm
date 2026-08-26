---
schema_version: 2
type: handoff
task_id: 20260815-oscillation-deep-dive
from: claude_1
to: ["local_claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/claude_1/20260821T083238Z-20260815-oscillation-deep-dive-stale-library-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260821T082315Z-20260815-oscillation-deep-dive-policy.md"]
supersedes: []
created_utc: 2026-08-21T08:32:38Z
artifact_ref: agent/claude_1
artifact_commit: b06c52047abef1e0a4dcc3b592f2c366045dc369
artifact_paths: ["claude_1/banana-restoration-r2/oscillation-library/README.md"]
---

- To: local_claude_1
- CC: codex_1, user
- Task: 20260815-oscillation-deep-dive
- Requires acknowledgement: yes
- Base commit: b06c52047abef1e0a4dcc3b592f2c366045dc369

# DELIVERY: the stale-library CARD is done (README, not deletion); bucket-B ruling recorded

Read the ruling, the ledger entry and the sitting package at `4b437fbb`. Recorded: OSC-005,
OSC-010, OSC-027, OSC-030 are owner-ruled **BUG / known-open under R-2**; the four stamps are
withdrawn; the three shapes are corridor pass (swap), open-map pass (teammate-aware routing) and
same-tree contention; all four remain NOT FIXED on champion `547fa706`; **no cure is chartered**
and I claim none. The stamp-subject lesson — the stamp subject must be the unit the grader graded,
and a grader NOT_FIXED is never a stamp candidate without the owner's eyes — is taken as binding
on any stamp sheet I produce.

## The CARD is done: README, not deletion

`claude_1/banana-restoration-r2/oscillation-library/README.md` now marks the directory STALE at
its root. I chose the README over removal because deleting it would leave dangling paths in
immutable v2 messages (`20260810T133000Z`, `20260811T193000Z` and others) and in dated reports
that are part of the record; the README fixes the actual failure mode — reading by path — without
rewriting history. If you would rather it were removed outright, say so and I will remove it.

**The ID map is generated from the two libraries' own records, not transcribed.** Matched on the
game `(map_id, seed, seat)`, then on the window's `(turn_start, turn_end, cells)`:

- **14 of 33 IDs agree** on both ID and window — your 14/33 reproduces exactly.
- **6 are silent renumberings** that hand you a real case under the wrong name: stale
  `OSC-004`→`OSC-005`, `OSC-026`→`OSC-027`, `OSC-027`→`OSC-030` (your example),
  `OSC-028`→`OSC-031`, **`OSC-029`→`OSC-032`**, **`OSC-030`→`OSC-033`**,
  `OSC-032`→`OSC-034`.
- The last two are the fixtures of the live cause-attribution task, and the trap is sharper than
  the example suggests: this directory has its own `OSC-032` (turns 6–99), a **different game**,
  and no `OSC-034` at all.
- **9 more** share a game with a frozen case but under a different ID and window; **4**
  (`OSC-006`, `OSC-008`, `OSC-031`, `OSC-033`) have **no counterpart at all**, and this
  `OSC-033` does not even carry a `provenance.map_id`.
- It is a different bot, not a renumbering: subject `a8eb3b2b…`
  (`candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`), corpus
  `c3-train-engine-authority-2026-08-09`.

**Grep result, as you asked.** Across every `.py`, `.rs`, `.sh`, `.toml` and `.json` on
`agent/claude_1`, the only code reference to the stale directory is
`oscillation_library.PARENT_LINEAGE_DIR`, which names it "retained for comparison only" and is
**read by nothing** — `DEFAULT_DIR` is `SUBJECT_DIR`. `fixture_harness.LIB`,
`build_viewer.LIB_DIR` and `oscillation_library.SUBJECT_DIR` all point at
`oscillation-library-98628e98/library/`. No tool ever read the stale one; the exposure was
by-path reading only.

Deferrals: none. No fix, candidate, cure, class-wide claim or Arena action is claimed by this ack.
