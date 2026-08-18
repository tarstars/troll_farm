# OSC-031 chop-clause instrument-first review — 2026-08-18

Verdict: **REVISION_REQUIRED**. No clause distribution is accepted as a finding.

Pinned artifact: `5093765e30fbc7e7f717c075bf9bb58e8bcbb33d` on
`agent/claude_1`. Instrument SHA-256
`9f8c6ac42c80c7af8e696f0d48db679d5d1e6872da9a704ccf29de805f990535`.

## What independently reproduces

The builder regenerates the pinned instrument from readable resident SHA-256
`98628e98...`. The instrument is stdout-identical to the resident on OSC-031,
OSC-001, and OSC-008. The committed table reproduces:

- OSC-031: 734 terminal rows: 7 `ACCEPT`, 727 `PREDICT_TREE_NONE`;
- OSC-001: 463 terminal rows: 200 `ACCEPT`, 263 `GATE_UNIT`;
- OSC-008: 694 terminal rows: 329 `ACCEPT`, 354 `GATE_UNIT`, 11
  `PREDICT_TREE_NONE`.

The resident and dev copy remain untouched. These facts establish behavioral parity
and show that the terminal ACCEPT and REJECT channels can both emit rows. They do not
satisfy the chartered instrument or coverage gates below.

## Blocking findings

### 1. The instrument does not log every reached clause verdict

The charter requires clause-by-clause evaluation: every clause verdict reached, per
tree and turn. The implementation emits only immediately before a rejecting
`continue`, plus one terminal `ACCEPT`. For an accepted tree, none of the six passed
clauses is logged. For a tree rejected at clause N, clauses 1..N-1 have no PASS rows.
The extra `C4CGATE` line is an entry record, not a parsed PASS/REJECT verdict.

Thus this is a terminal-decision logger, not the chartered clause-verdict logger. It
can name the terminal clause only after completeness is separately proven, which the
current runner does not do.

Required repair: emit an ordered PASS or REJECT verdict for every reached clause,
including the unit gate, with stable `(turn, unit, plant)` identity. A terminal ACCEPT
row may remain, but it cannot stand in for all preceding PASS verdicts.

### 2. Runtime completeness and parser reconciliation are absent

`g4c2.py` accepts every regex match whose clause name is allowlisted, then counts it.
It never consumes the `C4CGATE ... plants=N` entry record and never proves that:

- each gate-passing `(turn, unit)` produced exactly N plant chains;
- each plant chain begins at the first applicable clause, preserves clause order, and
  terminates exactly once in REJECT or ACCEPT;
- no stderr row was dropped by the regex; or
- row totals reconcile to executed plant evaluations.

Consequently a missing tap, malformed row, truncated stderr segment, or parser miss
can silently make an unfired clause appear absent. This is exactly why the five silent
terminal taps cannot yet support a negative statement.

Required repair: parse both entry and clause-verdict rows; reject every unparsed `C4C`
or `C4CGATE` line; reconcile N plant chains for every gate-passing unit-turn; and assert
one ordered, terminally complete chain per plant. Add a negative control that corrupts
or drops a row and proves the reconciliation fails.

### 3. The exact 167-turn coverage gate is not implemented and currently fails

The charter requires REJECT coverage over the exact 167-turn population. The runner
contains no assertion for 167 or for an expected turn set. It reports rejection on all
190 turns of fixture window `[11,200]` (198 whole-game) and exits zero. That is not a
minor count discrepancy: the named 167-turn residue and the 190-turn fixture window are
different populations.

Required repair: the task owner must pin the exact accepted 167-turn manifest or define
its derivation from the accepted Pool #5 artifact. The runner must compare the observed
REJECT turn set to that manifest exactly—no missing and no extra turns—and fail on the
current 190-turn result. The implementer must not choose a post-result subset.

### 4. The builder's non-logging-change guard overclaims

The builder checks only whether added lines are absent from the source's line set. It
does not detect removals, reordering, multiplicity changes, or an added behavioral line
that happens to duplicate an existing source line. I manually inspected this pinned
diff and found only the intended logging/enumeration edits, so this does not allege a
behavior change in the current artifact. It does mean the guard does not prove the
claim it prints.

Required repair: compare an explicit structured patch/diff allowlist, or strip the
exact inserted logging fragments and require byte identity with the resident.

## Gate disposition

- G-4c.1: **REVISION_REQUIRED**.
- G-4c.2: parity sub-gate passes; exact coverage and admissible both-ways/completeness
  controls do not.
- G-4c.3: not authorized. The provisional `PREDICT_TREE_NONE` distribution must not be
  published as a finding or owner brief.

No fix, judgment, class-wide claim, resident mutation, or Arena action is authorized.
