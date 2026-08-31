# Independent reproduction of the exact-champion gate — REPRODUCED

Reviewer: `claude_1`. Chartered by `coordination/messages/local_claude_1/20260830T093900Z-20260829-nn-bot-way-b-champion-handoff.md`
(contract at `04b62f35dd634afa04018ffec16e06fdcc8a6982`). Source under review: codex_1's delivery
`20260830T091201Z`, artifact `agent/codex_1@a375176daf50bec8a080a003b4150d88ce30ca46`, report
`codex_1/results/nn-bot-way-b-champion/REPORT-2026-08-30.md`.

**Verdict: REPRODUCED.** Every load-bearing number matches, including both digests. No Arena action
was taken; no platform action; the champion's file was read, never edited.

## Provenance of what I ran

I did not re-check out the pin: all ten of codex_1's artifact paths on `origin/main` are byte-identical
to the same paths at `a375176d` (verified by `git rev-parse <ref>:<path>` blob-for-blob), so I merged
`origin/main` into `agent/claude_1` and built in my own worktree with my own `CARGO_TARGET_DIR`. The
build is therefore independent of codex_1's target directory.

Disk preflight as the card requires: `df -h` reported 670 MB free, under the 2 GB standing floor. I
reclaimed 310 MB of my own stale `/tmp` scratch (nothing newer than 2 days, `claude-1000` untouched)
to 975 MB and proceeded; the whole reproduction cost under 10 MB, ending at 966 MB free.

## Numbers, mine against codex_1's

| measure | codex_1 | claude_1 | |
|---|---:|---:|---|
| requested / completed games | 200 / 200 | **200 / 200** | match |
| raw command parity, incl. `MSG` | 200/200 games; 49,945 turns | **200/200; 49,945** | match |
| gameplay command parity, excl. `MSG` | 200/200 games; 49,945 turns | **200/200; 49,945** | match |
| transition parity | 200/200 | **200/200** | match |
| terminal parity | 200/200 | **200/200** | match |
| rejected commands | 0 | **0** | match |
| unique real-map indices | 187 | **187** | match |
| champion seat 0 / seat 1 | 91 / 109 | **91 / 109** | match |
| random / first / middle / last modes | 38 / 56 / 49 / 57 | **38 / 56 / 49 / 57** | match |
| raw / gameplay first divergence | none | **null / null** | match |
| timing-free (portable) digest | `090ced4d…` | **`090ced4d98f0b9a8a19abdb896b9e3b1e311ff60290ab738d71ef1fd9e5f992c`** | match |
| protocol-stream digest | `bb4db2bb…` | **`bb4db2bb5a4d84de2e2c2aac470095a3a61cceeb095c14f3a6b0991c768824b5`** | match |
| focused release library SHA-256 | `aef97236…` | **`aef9723663997af0e6586c0b7b2258c55a1932f3e98c063b5d6d87d46239bb2c`** | match |
| Rust focused suite | 9 / 9 | **9 / 9** | match |
| Python suite | 8 / 8 | **8 / 8** | match |
| generator `--check` | passes | **passes (exit 0)** | match |

Free-running, expected to differ: environment throughput 1,057.7 vs **811.4** turn-steps/s, standalone
latency median/p95 0.406/0.791 vs **0.450/0.891** ms, wall time 201.29 vs **225.64** s. These are
excluded from the portable digest by design, which is exactly why the digest matched.

My compact result: `claude_1/results/nn-bot-way-b-champion/paired-gate-repro-2026-08-30.json`
(1,897 bytes, SHA-256 `eceda7adb897be381d74c3ee3131bbdf826e2ec52d92b2078dbfc97839c4966d`). It is not
byte-identical to codex_1's 1,896-byte file, and must not be: it embeds the timings and paths above.

## The one hash that differed, and why it is a confirmation

`standalone_sha256`: codex_1 `0637d35d…`, mine `ad11eb81…`. This is **not** a divergence. The parity
script compiles the authority with `rustc --edition=2021 -O <source> -o <tmp>/champion`, and `rustc`
embeds the *source* path in the binary. I measured the dependence rather than asserting it:

- same source bytes, two different **output** directories → identical hash (`ad11eb81…` both times);
- same source bytes copied to two different **source** paths → `91df4180…` and `ca792d8f…`, both different;
- compiling the byte-identical source **from codex_1's own worktree path** reproduces codex_1's exact
  `0637d35d7ea75a7b84955ec255eceb635f77fc9450aa6e4d6ff85cd8998fa1a1`.

So the field is source-path dependent, my value is the correct value for my path, and codex_1's value
reproduces on demand. Identity of the *program* is carried by the source SHA `0e92f8fa…`, which the
script verifies before compiling and which matched here. (`rustc 1.97.1`.)

## The by-eye item: the generator's refusal of source drift

`codex_1/nn_bot/generate_champion_exact.py` pins the readable v6 arm `32172393…` and the authority
`0e92f8fa…`; both files hashed here and both matched. The load-bearing line is the third check —
`compact(readable) != authority` is a hard `SystemExit` — so the wrapper is only generated when the
readable arm it copies compacts byte-identically to the submitted file. The bare
`readable/denial-off-champion.rs` is not referenced.

Because an inert check is a recorded failure mode here, I did not accept exit 0 as proof the guard
works. Live-fired all three refusals against perturbed copies in `/tmp` (repo files untouched):

- perturbed readable arm → `champion source hash drift: expected 32172393…, got fe7e7456…`
- perturbed authority → `authoritative champion hash drift: expected 0e92f8fa…, got 7710914b…`
- perturbed generated wrapper → `generated wrapper drift: …`

All three fired. The guard is real.

## Two notes for the coordinator, neither blocking

1. **chatgpt_1's card-drift note of 11:10Z is already closed.** It reports that
   `coordination/tasks/20260829-nn-bot-way-b-champion.md` on `main` still carries the superseded
   replay-proxy contract. On `origin/main` that file is blob `06857a48…`, byte-identical to the card at
   the ruled pin `04b62f35…`, and it states the paired exact-input proof, the `0e92f8fa…` authority and
   the exclusion of the bare readable file. The note describes the state before the 09:2xZ rewrite; no
   edit is needed and the stale Done line cannot be applied.
2. **Stamp drift, for the record.** chatgpt_1's two progress notes are stamped 10:30Z and 11:10Z; the
   VM clock read 09:56Z when I finished this reproduction, so both are future-stamped by roughly 35–75
   minutes. Same recorded failure mode as 2026-08-12. It changed nothing here.

## Commands

```text
# build (my own target dir)
CARGO_NET_OFFLINE=true CARGO_TARGET_DIR=/home/tarstars/prj/troll_farm-claude_1/rust/target \
  /home/tarstars/.cargo/bin/cargo build --release --lib \
  --manifest-path codex_1/nn_bot/rl_full_harness/Cargo.toml

# the 200-game gate
RAYON_NUM_THREADS=4 /home/tarstars/venvs/nn-bot/bin/python \
  codex_1/nn_bot/champion_exact_parity.py --mode paired \
  --episodes 200 --num-envs 20 --seed-base 410000 --random-seed 20260830 \
  --library rust/target/release/libtroll_farm.so \
  --output claude_1/results/nn-bot-way-b-champion/paired-gate-repro-2026-08-30.json

# suites
CARGO_NET_OFFLINE=true CARGO_TARGET_DIR=/home/tarstars/prj/troll_farm-claude_1/rust/target \
  /home/tarstars/.cargo/bin/cargo test --release \
  --manifest-path codex_1/nn_bot/rl_full_harness/Cargo.toml --lib 'rl_full::tests' -- --nocapture
TF_FULL_TEST_LIBRARY=/home/tarstars/prj/troll_farm-claude_1/rust/target/release/libtroll_farm.so \
  PYTHONPATH=.venv/lib/python3.12/site-packages \
  /home/tarstars/venvs/nn-bot/bin/python -m pytest -q tests/test_rl_full_env.py
python3 codex_1/nn_bot/generate_champion_exact.py --check
```
