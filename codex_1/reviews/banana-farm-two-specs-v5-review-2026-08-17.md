# Banana-farm two-spec v5 review — 2026-08-17

Verdict: **GATE_ACCEPTED_FOR_OWNER_REVIEW**.

Pinned artifact: `3cc51122980b5947475ea5c267508b1028d9be1f`.

Both v4 blockers are closed:

- each OWNER-DECISION register now exposes the completion gate as a separate new
  mechanism that the owner must adopt or strike;
- §4 defines completion from previous state, our emitted command, current state, and
  guaranteed lethal chop power; ambiguous disappearance fails closed; count/reset/
  confirmation ordering is fixed; and GK binds its positive arm to that definition.

The original v3 corrections remain intact: the abort sensor admits and measures both
failure directions; `K_futility` is a frozen heuristic rather than a false latency
bound; and the long-in-flight negative gate is structural. Sections 3–8 remain
byte-identical between A and B except for their intentionally spec-specific material
outside that shared extraction.

The specs are ready for the explicitly required owner decisions and approval. This
verdict does not itself decide B-1, `K_futility`, or the completion gate, and it does
not authorize implementation, measurement, resident mutation, or Arena action.

