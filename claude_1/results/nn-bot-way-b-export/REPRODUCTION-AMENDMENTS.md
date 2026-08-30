# Reproduction of codex_1's amendments (d), (e), (f) — the portable one-file neural clone

- Reproducer: `claude_1`, on the VM (`/home/tarstars/prj/troll_farm-claude_1`).
- Under review: `agent/codex_1@c4355caa2c8a8d7a7e46eb3e46628d1e4b832f22`, delivered 2026-08-30 16:31Z.
- Standard: the coordinator's handoff of 16:15Z — amendment (d) the AVX2 runtime dispatch with a
  baseline fallback, (e) the frozen three-run timing rule, (f) the UTF-16 size gate.
- Verdict: **REPRODUCED — the functional amendments (d) and (f) PASS, and (e)'s machinery works as
  specified. The timing numbers are information only and are reported below without a verdict; one
  of my three runs breached the 20 ms per-run ceiling and I disclose why.**
- I changed none of codex_1's code and took no platform, Arena or submission action.

## 0. The pinned artifact is what I ran

All seven declared paths in my worktree are byte-identical to the pin (SHA-256 prefixes):

| path | sha256 (16) |
|---|---|
| `local_claude_1/nn-bot/generate_full_bot.py` | `4754d664ff5d54f2` |
| `local_claude_1/nn-bot/bed_full_bot.py` | `b1821e2a822f2431` |
| `cgauto/submissions/candidate-nn-clone.rs` | `4c5a096d627932ed` |
| `tests/test_export_full_actor.py` | `5b23a7a5c6bf1f4b` |
| `codex_1/results/nn-bot-way-b-export/REPORT.md` | `195a8078f796ac5b` |
| `codex_1/results/nn-bot-way-b-export/bed-full-bot.json` | `4bf53e9a93786149` |
| `codex_1/results/nn-bot-way-b-export/candidate-nn-clone-readable.rs` | `0139149db5110f6d` |

## 1. The focused tests — PASS

`tests/test_export_full_actor.py`: **10 passed, 2.16 s** (was 7 before the amendments).

## 2. Regeneration — PASS, byte-identical

Inputs verified first: manifest `6612bf9d…`, payload `4ea9c80d…`. Regenerating into scratch (so
codex_1's tracked files were untouched) gives

- candidate `4c5a096d627932edbb796e1af350e1a4518b702f959a05ed40cae515f0a53b06` — the pinned hash;
- readable source `0139149db5110f6d4ff7ed6c8e7337c543eec0ee349fb9b91d42f17c5c420111` — the pinned hash.

## 3. Amendment (f), the size gate — PASS, three counts confirmed independently

Counted by my own one-liner on the candidate file, not by the bed:

- **54,218** Unicode code points;
- **83,282 UTF-16 code units** — the gate, 16,718 units under 100,000;
- **141,410** UTF-8 bytes.

All three match the report and the bed's `candidate_size` block exactly.

## 4. Amendment (d), the AVX2 dispatch and the fallback — PASS, and one check the bed cannot make

The bed's own gates, from my run:

- runtime-selected path probe reports `avx2`; forced build reports `baseline_fallback`;
- runtime dispatch (AVX2): **48/48 games, 13,206/13,206 commands**, difference list empty;
- forced baseline fallback: **48/48 games, 13,206/13,206 commands**, difference list empty;
- fallback timing on this VM: first-turn max 33.680 ms, warm median 9.407 ms, warm p99 **18.878 ms**,
  warm max 32.753 ms — under the platform's 50 ms, so a non-AVX2 worker still plays legally;
- the direct seat-parity probe passes on both absolute seats (`DROP 2` on seat 0, `DROP 3` on seat 1),
  observation, spatial mask, plan mask, decoded command and seat all equal; the malformed turn-one id
  set is rejected.

### The gap I closed by hand

The bed proves the fallback *source* is correct by compiling a **different binary**
(`--cfg tf_nn_force_fallback`). That build is not the file we would submit: in it `use_avx2` is a
compile-time false, so the compiler is free to specialise the branch away. What the platform runs is
the *unmodified* candidate, where the choice is made at run time — and no bed on an AVX2 machine can
execute that binary's fallback branch.

So I disassembled both builds with `objdump` and counted AVX registers per symbol:

- the **shipping** build (no cfg) contains **two** kernels: `convolution_range` with SSE-only code
  (9 `mulps` on `%xmm`, **zero `%ymm`**) and one separate AVX2 symbol holding all 306 `%ymm`
  references, called from exactly one site;
- the **forced-fallback** build has the same shape, with zero `%ymm` anywhere inside the fallback
  symbol.

That is the missing link: the file we would actually submit really does carry a machine-code path
with no AVX instruction in it, reachable by the runtime branch. Neither build uses fused
multiply-add (`vfmadd` count 0 in both), which is what makes the two paths bit-identical rather than
merely close — and the 13,206/13,206 match on both paths is the empirical confirmation.

No emulator is installed on this VM (`qemu-x86_64` absent), so nobody here can *execute* the
shipping binary on a CPU without AVX2. The static check above is the strongest available evidence,
and I state it as such rather than as an execution.

## 5. The turn-one corpus — PASS, 370/370, third independent execution

`/home/tarstars/nn-data/dataset-v400-2026-08-30/states-pilot.jsonl.gz` is present on this VM and its
checksums verify (`sha256sum -c SHA256SUMS`: all four files OK; the shard is `1df412f0…`). Run with
`--seat-corpus` on the full shard: **370 seat-0 turn-one games, 0 exceptions.** codex_1 could not
read it (its storage preflight failed) and cited the accepted result; this run executes it a third
time and it holds.

## 6. Amendment (e), the timing rule — the machinery works; my numbers are information, and one run breached

The bed now always takes three complete timing samples and records every warm p99 and first-turn
maximum; `--timing-context host-of-record-quiet` is what turns them into a gate, and my run used
`information`, so `certified` is null. That is the rule as written and it is implemented correctly.

My VM's three warm p99 values: **26.151, 15.886, 15.139 ms**; median **15.886 ms**. First-turn
maxima: 39.074, 21.828, 25.758 ms.

**Disclosure about run 1.** I had two of my own `rustc -O` builds of the same candidate running in
the first minutes of the bed (they are the disassembly check in section 4). The machine was not
quiet, and run 1 is the run that produced 26.151 ms and a 76.3 ms warm maximum. I do not offer that
number as a property of the bot; I report it because a measurement I contaminated is still a
measurement I took, and hiding it would be the worse error. Runs 2 and 3 (15.886, 15.139) were taken
after my builds finished.

**What that leaves.** Even the two clean runs sit at or just above the 15 ms line on this VM, as they
did before the amendments. Nothing here contradicts codex_1's own VM figures (15.731, 13.363,
15.026). The honest reading is unchanged from my 15:40Z note and is now the reason amendment (e)
exists: **this bot's warm p99 lives within a millisecond of the gate, so the host-of-record run has
to be genuinely quiet or it will decide the artifact by accident.** My run is a small demonstration
of exactly that failure mode.

## Reproduction commands

```
git merge c4355caa2c8a8d7a7e46eb3e46628d1e4b832f22
PYTHONPATH=. /home/tarstars/venvs/nn-bot/bin/python3 -m pytest -q tests/test_export_full_actor.py
PYTHONPATH=. /home/tarstars/venvs/nn-bot/bin/python3 local_claude_1/nn-bot/generate_full_bot.py \
  codex_1/results/nn-bot-way-b-export/clone-int8-manifest.json \
  codex_1/results/nn-bot-way-b-export/clone-int8.bin \
  --readable-output /tmp/claude-1000/nnrepro2/readable.rs --output /tmp/claude-1000/nnrepro2/candidate.rs
PYTHONPATH=local_claude_1/nn-bot /home/tarstars/venvs/nn-bot/bin/python3 local_claude_1/nn-bot/bed_full_bot.py \
  --rustc /home/tarstars/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc \
  --seat-corpus /home/tarstars/nn-data/dataset-v400-2026-08-30/states-pilot.jsonl.gz \
  --out /tmp/claude-1000/nnrepro2/bed-full-bot-claude1.json
# the by-hand check of section 4
rustc --edition=2021 -O -Awarnings [--cfg tf_nn_force_fallback] cgauto/submissions/candidate-nn-clone.rs -o BIN
objdump -d --no-show-raw-insn BIN | awk '/^[0-9a-f]+ </{s=$0} /%ymm/{c[s]++} END{for(k in c) print c[k],k}'
```

The bed's raw record of this run is `bed-full-bot-claude1-amendments.json` beside this file.
