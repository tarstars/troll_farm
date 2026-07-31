# S2 opening-book scope audit — frozen protocol

Date frozen: 2026-07-31

## Question

Is a precomputed opening book by map class ready for an implementation protocol, already
covered by failed opening classes, or blocked on a missing action library and prospective
map representation?

This is a written-evidence dependency audit. It does not enumerate openings, fit a map
classifier, run games, consume labels/maps, modify a policy, or estimate Arena value.

## Objects that must remain separate

1. **Opening action library:** the bounded first-K sequences the book may select.
2. **Terminal value labels:** exact continuation value for every library sequence.
3. **Map representation:** features available before the first action that assign a new map
   to a class.
4. **Book policy:** a prospective class→sequence mapping with abstention and held-map /
   held-opponent transfer.
5. **Runtime lookup:** hashing/features and lookup within the live turn-one budget.

Low lookup latency cannot compensate for a missing or non-transferable object upstream.

## Frozen evidence matrix

Audit the exact coverage and disposition of:

- all 27 harvest-0 first-worker specs;
- farm-first/max-bank/later-funding opening macros;
- the terminal-valued turn-one rollout and its Arena result;
- fixed one-source opening prefixes;
- eight-action recurrent opening portfolios;
- all one- and two-batch semantic sequences;
- E1's surviving multi-turn resident candidate-pair oracle and its N4 dependency;
- D63/D64 static map selection;
- D91 first-boundary map selection;
- Phase 15 expanded map-only worker-three selection;
- D153 map-fold conditional value;
- the generated-versus-official map-domain constraint.

For each row record action surface, label horizon, selection information, development /
validation support, disposition, and whether it can supply S2.

## Integrity gates

1. Every numerical claim cites its canonical report/ledger/CONSTRAINTS entry.
2. Frozen/consumed classes and panels are not reinterpreted as available holdouts.
3. Opponent families are never relabeled map classes.
4. E1/N4, S2, H11, and learned-selector responsibilities remain non-overlapping.
5. The exact source and sacred resident are read-only and hash-verified.

Failure returns `UNIDENTIFIABLE`.

## Adjudication

- `READY_FOR_PROTOCOL` only if a non-closed sequence library has terminal value evidence
  and a pre-action map representation has prospective disjoint-map and held-opponent
  transfer support.
- `VOID_PREMISE_DUPLICATE` if every proposed library/class object is already closed.
- `DEPENDENCY_GATED` if the only surviving action/value surface depends on unfinished
  N4/E1 work.
- `REPRESENTATION_BLOCKED` if an action/value surface exists but every available
  pre-action map representation is closed or unsupported.
- `DEPENDENCY_GATED_REPRESENTATION_BLOCKED` if both independent blockers apply.

No verdict authorizes sequence enumeration, feature fitting, new maps, a book, source,
candidate, or Arena action. A future reopening requires a new claim and frozen protocol
after its named blockers clear.

## Planned artifacts

- compact evidence matrix:
  `data/analysis/live-agent-6553250/s2-opening-book-scope-audit-result-2026-07-31.json`;
- human report beside it;
- compact manifest under `local_codex_1/s2-opening-book-scope-audit/`.
