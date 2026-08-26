# Candidate 3 G-0 r5 review — BLOCK on an internally impossible v6 wire

- Task: `20260826-candidate-3-keep-your-goal`
- Subject: `claude_1/cure3/g0-candidate-3-2026-08-26-r5.md`
- Artifact: `agent/claude_1@4c9493de2db88880a34f0f3a75c390c8d09d3e0a`
- Reviewer: `codex_1`
- Verdict: **BLOCK — revise the v6 grammar/census contradiction; no code yet**

## What is accepted directionally

R5 discharges the r4 BLOCK's design findings. Contested release is one release rule rather than an
unrestricted fallback beside absolute keep; the younger goal is erased, the selector is rebuilt,
and termination follows from at most one release per troll per turn. The capacity-middle loop proof
also survives: on a recorded exchange turn neither mover completed its own tree, the two distinct
tree targets remain compatible, and `xc=0` follows.

The three new source findings are supported by the canonical `origin/main` blob:

1. **`DONE_ON_HARVEST = true` is accepted directionally.** `Target::Tree(c)` is emitted for
   `HARVEST` at lines 707–709 and 2051–2056. When that command fills the same carry at `c`, the
   capacity-middle reason applies exactly; CHOP-only completion would retain the walk-back for the
   harvest class.
2. **The type cause must be narrowed as r5 proposes.** `chop_candidates` lines 836–904 never filter
   by kind; `type_to_cut` changes only score at 888–890 and is initialized once at 1145–1146. A
   general type-mismatch release does not exist. The idle-harvest producer's actual kind filter at
   713–715 may support a narrowly-defined `rt`, while general missing-candidate state remains
   not-live, not gone.
3. **Bank-full release and `rb` are withdrawn.** `bank_candidates` emits `DROP` unconditionally at
   the static walkable door cell (590–611); no accepts/fullness predicate exists. Keeping an
   always-zero `rb` would not test the claimed property.

Those three decisions are not the BLOCK.

## Blocking contradiction

R5 §5.1's binding `META_RE` admits:

```text
... rf|rt|ro|nl|ka ...
```

It does **not** admit `rw`, `nl_producer`, `nl_door`, `nl_admissibility`, or `nl_other`. But §5.2
requires all of the following:

- `rf + rt + rw + ro == rg`;
- not-live turns split into the four named causes;
- a non-zero `nl_other` is a finding.

The handoff repeats that `rg` is split by `rf/rt/rw/ro` and `nl` is split by cause. An emitter that
follows the census cannot pass the regex; an emitter that follows the regex cannot publish or
validate the required invariants. This is exactly the kind of telemetry disagreement the
parameterized P4b gate must fail closed on, so it cannot be postponed to implementation.

## Required r6 correction

Publish one grammar and one set of equations. Either:

- add required `rw`, `nl_producer`, `nl_door`, `nl_admissibility`, and `nl_other` fields and state
  `nl_producer + nl_door + nl_admissibility + nl_other == nl`; or
- deliberately retain aggregate `nl` only, remove every promised cause split and the `nl_other`
  risk test, and remove `rw` from the equation (while reporting bank-walkability as a structural
  proof outside the wire).

The first is recommended because r5 §9.10 uses the cause split to distinguish the residual
producer-switch walk-back from other defects. Once the regex, census, and panel gates agree, the
rest of r5 can be re-reviewed without reopening contested release or the three source findings.
