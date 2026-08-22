# Exact readable no-orchard Arena submission

The owner-requested readable source is live on CodinGame as agent `6593838`, submission
`41089629`. The platform accepted exactly one canonical mutation call with HTTP 200 and returned
an unambiguous submission id. No retry or restore occurred.

The submitted artifact is
`local_codex_1/readable-orchard-code-cost/e7a-without-orchard-readable.rs`: 75,634 bytes,
1,475 physical lines / 1,470 nonblank/noncomment code lines, SHA-256
`98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`. Read-only recovery from
the platform after acceptance returned exactly 75,634 bytes with that full SHA, proving that the
readable text itself—not only a compact equivalent—was stored.

Initial submission-scoped health at 2026-08-04T11:28:53Z has ten parsed finished games plus one
pending, score 18.38, rank 87/137, zero catastrophes, negative-margin mass 21, zero runtime
signals, and clean agent/submission identity. This is a cold-start health check, not a value
verdict. The requested source remains active.

The pre-mutation orchard baseline was `6592744`/`41087983`, 22.88/rank 32 over 160 finished games,
with exact source and clean runtime/identity. Exact orchard remains the deliberate safety default
in `cgauto/api_submit.py`; that default was not used after the healthy submission.
