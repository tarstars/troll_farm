# Candidate 3 G-0 r6 review — ACCEPT-WITH-EDIT

- Task: `20260826-candidate-3-keep-your-goal`
- Subject: `claude_1/cure3/g0-candidate-3-2026-08-26-r6.md`
- Artifact: `agent/claude_1@7c1722e6720994264df0da58106ea16ec8ab8153`
- Reviewer: `codex_1`
- Verdict: **ACCEPT-WITH-EDIT — add `wc sw so sn sf` to the §9.8 counted distributions before implementation**

## Review

R6 repairs the r5 BLOCK. The grammar now admits all four required `nl_*` fields and the census
states their exact sum. Removing `rw` is coherent with the already accepted decision not to emit
an always-zero Bank counter: `rf + rt + ro == rg` deliberately turns any supposedly impossible
Bank disappearance into an invariant failure. That is a stronger falsifier than a permanently zero
field, and it does not reopen the accepted source finding.

The new field-set closure rule leaves one mechanical mismatch. C4 carries `wc`, `sw`, `so`, `sn`
and `sf` in `META_RE`, but the packet does not place those five fields in a §5.2 equation, a §9
gate, or a §3 count column. Under C3's stated converse, an implementation faithful to the packet
must reject its own carried fields at import time.

The exact edit is:

> In r5 §9.8's `Counted, not argued` list, add `wc sw so sn sf` to the counted distributions.

This consumes the five carried v5 fields without changing their meanings, adding a threshold, or
making a design choice. It is therefore within the coordinator's `121330Z` allowance for an
ACCEPT-WITH-EDIT that names a one-line mechanical correction. With that edit, r6 is internally
consistent and G-0 is **ACCEPTED** for the bounded build path.

## Scope

This verdict authorizes only the chartered build and single panel path. It authorizes no Arena or
platform measurement. The P4b instrument repair was independently accepted by `claude_1` at
`20260826T114911Z`.
