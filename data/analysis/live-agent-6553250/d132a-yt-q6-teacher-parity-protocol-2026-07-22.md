# D132a YT q6 exact-teacher parity pilot — frozen protocol

Date: 2026-07-22  
Status: frozen before any D132 YT table or operation is created

## Purpose

D131 shows that four-seed selection on a 16-map fit panel does not transfer. A larger independent-
block teacher corpus is now justified. Before moving collection to YT, prove that the existing
Rust D112 collector is byte-exact on that backend.

Use only already-consumed map seed `9,843,780`, both seats, and all eight fixed opponents. Attach
the exact local release binary SHA-256
`5bed211a33393f041221dcda81bdd2bf5d11522ad1aa3978fe4d3b79492f6d02` and expert-bank SHA-256
`87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8` to one token-free YT CPU
map job. Allocate 16 CPUs and run the collector with 16 threads. Stream each generated TSV line,
its record type, shard, and row index through a YT JSON table; reconstruct local arm/baseline TSVs
without parsing numeric fields.

The exact reference is the seed-9,843,780 subset of the frozen D126 artifacts: 2,232 arm rows and
16 baselines, plus one header in each file. Require equal headers, row order, row counts, file
bytes, and SHA-256 values. Require mapper-reported collection wall time at most 240 seconds. Record
operation id/state and table paths without recording credentials.

Any parity or active-time failure closes YT for this collector and leaves all new seeds untouched.
A full pass authorizes a separately frozen multi-shard corpus operation; it does not qualify a
model, open final validation seeds `9,843,800--9,843,815`, create a submission, or touch Arena.
