# Independent reproduction of codex_1's one-file clone bot (VM, claude_1)

Task `20260829-nn-bot-way-b-export`. Charter: the coordinator's handoff of 2026-08-30 15:35Z.
Run on the VM (`compute-vm-4-16-20-ssd-1785607330087`) from `main@b6075fe8f76dbe7ed453472e6bccd1bac55046be`
(codex_1's corrected artifact `agent/codex_1@5be68352`, merged onto main), merged into
`agent/claude_1`; every pinned path is byte-identical to the pin (`git diff --stat` empty).

Verdict: **REPRODUCED — PASS on all four items.** No fix, no edit to codex_1's code, no platform action.

## Inputs, as received

| file | SHA-256 | matches report |
| --- | --- | --- |
| `local_claude_1/nn-bot/results/clone-2026-08-30-a/clone-pilot.pt` | `970097ed0842463b…` | yes |
| `codex_1/results/nn-bot-way-b-export/clone-int8.bin` (72,660 B) | `4ea9c80db7ee7832…` | yes |
| `codex_1/results/nn-bot-way-b-export/clone-int8-manifest.json` | `6612bf9d2727cf45…` | yes |
| `cgauto/submissions/candidate-nn-clone.rs` | `36bf2f2e23f849bc522614ed5fe7950e40fcede62e535dee5a692cf7ac059cff` | yes |
| corpus `states-pilot.jsonl.gz` (restored) | `1df412f0425d8856…` | matches `SHA256SUMS`, `sha256sum -c` OK on all four files |

## 1. Focused suite — PASS

`PYTHONPATH=. python3 -m pytest -q tests/test_export_full_actor.py` → **7 passed** (2.49 s).
The venv `/home/tarstars/venvs/nn-bot` had no `pytest`; installed `pytest==9.1.1` into it with `uv pip`
(nothing deleted, ~2 MB). That is the only environment change I made.

## 2. Deterministic regeneration — PASS, byte-identical

`generate_full_bot.py` from the manifest + payload, written to a scratch path
(`/tmp/claude-1000/nnrepro/`, so codex_1's tracked artifacts were not overwritten):

- compacted candidate: SHA-256 `36bf2f2e23f849bc522614ed5fe7950e40fcede62e535dee5a692cf7ac059cff`,
  **52,854 characters**, 140,046 UTF-8 bytes — identical to the shipped candidate;
- readable source: SHA-256 `39851d29d754b47a…`, 158,016 bytes — identical to codex_1's copy.

## 3. The 48-game bed with the parity probe — PASS

`PYTHONPATH=local_claude_1/nn-bot python3 local_claude_1/nn-bot/bed_full_bot.py --rustc <stable 1.97.1>`
(`--out` to scratch, then copied here as `bed-full-bot-claude1.json`). All seven gates true:

- Python quantized export vs the signed original clone: **48/48 games, 13,206/13,206 commands**, difference list empty;
- compiled Rust bot vs the same signed stream: **48/48 games, 13,206/13,206 commands**, difference list empty;
- replay-stream hashes as reported: reference `6eceb8caf5b07cf1…`, quantized `03a1ef8ba5becef0…`;
- direct seat-parity probe, both absolute seats, four-troll state with a staged non-MOVE DROP:
  observation, spatial mask, plan mask, decoded command and seat all equal on both cases
  (seat 0 obs `8f14ff89ca0457b0…`, seat 1 obs `6a7a4d60ca2b121c…`; shared plan mask `afb6cecb558a0858…`);
  the malformed turn-one id set is rejected (`turn1_invalid_id_set_rejected: true`);
- size: 52,854 characters, under the 100,000 limit;
- champion pin unchanged: `0e92f8fa1e9097dd…`.

### Timing on the VM (report the numbers, the host's are of record)

| measure | VM (this run) | host (codex_1's final) | gate |
| --- | --- | --- | --- |
| first turn max | **22.255 ms** | 14.781 ms | ≤ 500 ms — pass |
| first turn median | 10.089 ms | — | — |
| warm median | 6.585 ms | 6.505 ms | — |
| warm p99 | **14.642 ms** | 9.718 ms | ≤ 15 ms — pass, with 0.36 ms of margin |
| warm max | 28.607 ms | 15.095 ms | no gate |

The VM's p99 passes but sits close to the gate; the VM is the slower machine and was carrying nothing
else I started. I do not call this a failure of the artifact, and codex_1's disclosed 15.126 ms sample
on the host says the same thing from the other side: this bot's p99 lives within a millisecond or two
of the 15 ms line, so a machine-to-machine claim of comfortable margin is not supported.

## 4. The 370-game corpus check — PASS

`--seat-corpus /home/tarstars/nn-data/dataset-v400-2026-08-30/states-pilot.jsonl.gz` (checksum verified
before the run): **370 seat-0 turn-one games, 0 exceptions**, `turn1_id_corpus.valid: true`. This is the
second, independent execution of the check codex_1 could not rerun when the shard was missing from the VM.

## The VM's disk (asked for by the handoff)

96 % full, **792 MB free** after this run (the run itself cost ~10 MB of scratch, released). I deleted nothing.
`du -xsh /home/tarstars/*`, largest first:

```
7.0G  /home/tarstars/prj          853M  /home/tarstars/venvs
776M  /home/tarstars/launcher-clone   250M  /home/tarstars/launcher-state
42M   /home/tarstars/preserved    14M   /home/tarstars/nn-data
```

Outside the home directory: `/usr` 1.8G, `/tmp` 939M, `/opt/troll_farm` 620M, `/var` 602M, `/boot` 117M.
Inside `prj` the weight is repeated checkouts of this repository: `separate_troll_farm` 1.8G (of which
`candidate-v89-vs-v66-panel-open128.tsv` alone is 355M and `target/` 257M), `troll_farm` 1.2G (461M of it
`.git`), `troll_farm-codex_1` 1017M, `troll_farm-claude_1` 843M, `troll_farm-plan` 775M (298M `.git`),
`troll_farm-plan-agent` 487M, plus three more claude_1 checkouts totalling ~920M.

Two observations for the owner's decision, not actions: the old panel TSVs under `separate_troll_farm`
(~370M in two files) and `/tmp`'s 939M of extraction scratch are the cheapest space if any is ever wanted;
and the seven full checkouts, several with their own `.git` and `target/`, are what actually fills the disk.
Nothing here is mine to remove.

## Reproduction commands

```
git merge b6075fe8f76dbe7ed453472e6bccd1bac55046be
PYTHONPATH=. /home/tarstars/venvs/nn-bot/bin/python3 -m pytest -q tests/test_export_full_actor.py
PYTHONPATH=. /home/tarstars/venvs/nn-bot/bin/python3 local_claude_1/nn-bot/generate_full_bot.py \
  codex_1/results/nn-bot-way-b-export/clone-int8-manifest.json \
  codex_1/results/nn-bot-way-b-export/clone-int8.bin \
  --readable-output /tmp/claude-1000/nnrepro/readable.rs --output /tmp/claude-1000/nnrepro/candidate.rs
PYTHONPATH=local_claude_1/nn-bot /home/tarstars/venvs/nn-bot/bin/python3 local_claude_1/nn-bot/bed_full_bot.py \
  --rustc /home/tarstars/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc \
  --seat-corpus /home/tarstars/nn-data/dataset-v400-2026-08-30/states-pilot.jsonl.gz \
  --out /tmp/claude-1000/nnrepro/bed-full-bot-claude1.json
```
