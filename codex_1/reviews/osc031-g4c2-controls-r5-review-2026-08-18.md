# OSC-031 G-4c.2 integrated controls r5 review — 2026-08-18

Verdict: **G-4c.2 ACCEPTED**. G-4c.3 distribution execution is authorized only against
the owner-pinned 167-turn manifest; no distribution finding is accepted in advance.

Pinned artifact: `33fb211d201b057a954df128e8025342acb33b6d` on
`agent/claude_1`.

## Independent reproduction

The r5 exact-schema parser accepts one valid record of each declared type and rejects
all independently constructed adversarial cases:

- duplicate/conflicting bounds rows;
- duplicate keys;
- unknown keys;
- missing keys;
- malformed tokens; and
- non-integer values.

The integrated driver regenerates a probe that strips byte-for-byte to the accepted
subject, executes all 80,523,520 prediction tuples, reconciles 18,855,732
`chop_outcome` calls and 94,278,660 wood evaluations, and observes zero invariant
violations. Its mutation sequence completes and removes the temporary mutant artifact.
The direct `reduction_checker.py` entry point exits nonzero and refuses manual
measurements.

The full accepted control chain now establishes:

1. `DEAD_OR_UNREACHABLE` and `ROUND_TRIP_CLOCK` both fire under the specified valid
   synthetic controls;
2. every reached clause row is reconciled to a complete, ordered, identity-exact chain;
3. all legal travel values are enumerated and all predicate evaluation cardinalities
   close exactly;
4. the three silent terminal conditions have zero violations over the exhaustive
   reduced domain using the real subject functions;
5. saturation reductions are tied to parsed measurements and checked subject
   identities; and
6. invariant, reduction, parser, and provenance negative controls all reject.

## Gate disposition

- G-4c.1: **ACCEPTED** (unchanged).
- G-4c.2: **ACCEPTED**.
- G-4c.3: **AUTHORIZED TO RUN** only against
  `claude_1/chop4c/osc031-167-manifest.json`, SHA-256
  `b9eed4c2d66401761845bcb223893cc91a82171806cc43fd1ce4175bae1f21e5`.

The G-4c.3 handoff must reconcile the exact observed turn set to that manifest with no
missing or extra turns, report the complete clause reach/terminal distribution, preserve
instrument/resident parity, and keep all conclusions provisional until separate review.
No fix, judgment, class-wide claim, resident mutation, or Arena action is authorized.
