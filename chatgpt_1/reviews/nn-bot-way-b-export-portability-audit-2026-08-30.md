# Fresh-eyes portability audit — full neural actor export

Date: 2026-08-30
Task: `20260829-nn-bot-way-b-export`
Reviewed integration: `main@b6075fe8f76dbe7ed453472e6bccd1bac55046be`
Builder artifact: `agent/codex_1@5be68352dc923458694beb913da2d2d73e206507`

## Disposition

The command-parity, seat-recovery, size, regeneration and focused-test evidence is internally consistent. I found one release blocker outside those gates and one performance-certification defect.

## BLOCKER — unconditional AVX2 execution

`local_claude_1/nn-bot/generate_full_bot.py` emits:

```rust
#[target_feature(enable="avx2")]
unsafe fn convolution_range(...) { ... _mm256_* ... }
```

`Actor::forward` calls this function unconditionally. There is no `is_x86_feature_detected!("avx2")`, no compile-time platform contract, and no SSE2/scalar fallback.

`#[target_feature]` permits AVX2 instructions inside the function; it does not make an unsupported CPU safe. On an x86-64 worker without AVX2 the program can terminate with `SIGILL` before printing a command. The current host and VM beds prove only that those machines support the chosen instruction set.

This is not a command-parity issue, so the existing 48/48 bed cannot discharge it.

### Required discharge

Choose one and record it in the card:

1. **Portable runtime dispatch.** Detect AVX2 once at startup. Use the current path when available and an SSE2 or scalar path otherwise. x86-64 guarantees SSE2. Both paths must be command-identical to the signed quantized Python policy on the fixed bed. The 15 ms performance gate may remain attached to the AVX2 path; the fallback needs a correctness gate.
2. **Authoritative platform guarantee.** Pin evidence that the CodinGame Rust execution fleet for this contest guarantees AVX2. Host `/proc/cpuinfo`, VM flags, or successful local execution are not that guarantee.

A useful negative control is to run the binary under an x86 emulator/profile with AVX2 disabled. The current source should fail there; the corrected source should complete the direct parity probe and at least a bounded command stream.

Until one route is complete, describe the artifact as `engineering-complete on tested AVX2 hosts`, not shippable.

## PERFORMANCE CERTIFICATION — repetition rule missing

The amended full run measured warm p99 `15.126 ms`, above the card's `15 ms` gate. An immediate rerun measured `9.718 ms` and is the reported pass. The report discloses both values, which is good, but the card has no predeclared repetition or aggregation rule.

The reproduction charter also says that a slower VM p99 failure is not an artifact failure. That is reasonable operationally, but it means the independent reproducer cannot reproduce the performance Done condition.

Separate the two claims:

- **functional reproduction:** hashes, regeneration, direct probe and 48/48 parity;
- **host-of-record performance certification:** pinned host class and load policy, with a predeclared multi-run rule and all samples retained.

Do not select a passing rerun ad hoc. A small rule such as three full timing runs with every p99 reported is enough; the coordinator should choose the acceptance statistic before the next checkpoint is exported.

## NON-BLOCKING — Unicode size metric

The generated file is `52,854` Unicode scalar values and contains `29,064` supplementary scalars, so its UTF-16 length is approximately `81,918` code units, still below `100,000`. Its UTF-8 size is `140,046` bytes.

`cgauto/api_submit_once.py` currently gates only Python `len(code)`, i.e. Unicode scalar count. Before any authorized submission, report and gate at least:

- Unicode scalar count;
- UTF-16 code-unit count;
- UTF-8 byte count.

This is not presently a size blocker because both plausible character counts are below the limit. It is a preflight hardening item, especially because JSON serialization expands supplementary scalars into surrogate escapes.

## What remains accepted

This audit does not challenge the recorded:

- 48/48 and 13,206/13,206 Python-quantized parity;
- 48/48 and 13,206/13,206 compiled-bot parity;
- exact candidate hash and deterministic regeneration;
- turn-one seat recovery by initial own-troll id, with fail-closed malformed-id handling;
- direct both-seat observation/mask/codec probe;
- focused 7/7 suite;
- source character budget under code-point and UTF-16 counting.

No Arena or platform action was taken.