# Phase 3b G-d/G-e door-1 package — BLOCKED at the first G-d falsifier

- Task: `20260820-pair-selector-anti-benching`
- Builder: `codex_1`; independent reproducer/reviewer: `local_codex_1`
- Candidate: `claude_1/picker3/candidate-door1-p3b.rs`, SHA-256
  `457360589a65cb2662950761deba817852ea9eb0d2c53b05a3e6fd2ab9dfda8a`
- Base: `claude_1/picker2/candidate-door1-p1p2.rs`, SHA-256
  `5e1f4df406480f678ff03677cdda0f69d510c5c94efe90d4f0a8231b70c3339e`
- Verdict: **`BLOCKED_FIRST_FALSIFIER`**. G-e was not run after the binding G-d failure.
- Arena action: none. Sacred resident SHA-256 remained `fff6669b…`.

## Result

The exact r2 candidate is catastrophically worse on the same locked 240-game panel:

| measurement | P1+P2 base | r2 candidate | delta |
|---|---:|---:|---:|
| blocking games | 35 | 115 | **+80** |
| de-novo blocking games | — | **80** | fatal |
| healed blocking games | — | **0** | none |
| games with a new P3 | — | **5** | fatal |
| games with a new P4 | — | **73** | fatal |
| games with a new `r5-horizon` | — | 0 | clean on this clause only |

Five additional games change properties while remaining blocked, so the keyed decomposition names
85 changed games total. The first falsifier is overdetermined: R-3 requires P3-clean, no new P4 or
`r5-horizon`, and blocking totals no worse than P1+P2. The candidate fails the P3, P4, and blocking
requirements independently. No aggregate or progress result can waive any of them.

The mechanism is consistent with the pre-registered downstream-commitment falsifier: preserving a
replant `PICK` at turn 100 changes subsequent routing, and the resulting trajectory creates broad
new liveness failures. That is an interpretation of the keyed result, not a new causal experiment.

## Exact execution

The panel was run from detached `agent/claude_1@e6cb7523d87d4da02e6f81406d572e3e83e4cf10`
with `claude_1/pipeline/fuzz_panel.py`, corpus
`c5-two-player-phase-merged-2026-08-11`, 120 maps × 2 seats, 200 turns, and the candidate/base hashes
above. Only scratch paths, crate names, notes, and the two pinned arms differ from the accepted
`picker2-door1-cand-config.json`. Wall time was 17.6 seconds. The panel exited 1 because its result
was `BLOCK`, which is a scientific verdict rather than a harness failure.

Keyed comparison:

```text
python3 codex_1/picker3/analyze_gd.py \
  --candidate codex_1/picker3/results/gd-door1-panel-2026-08-23.json \
  --base codex_1/picker3/results/gd-door1-base-panel-2026-08-20.json \
  --output /tmp/gd-door1-decomposition-reproduced.json
```

The command prints 115 versus 35, 80 de-novo, zero healed, five new-P3 games, 73 new-P4 games,
and zero new-`r5-horizon` games. The analyzer refuses a candidate/base hash mismatch, a non-240
panel, duplicate keys, or different keyed populations.

## Artifact hashes

- candidate panel JSON: `0b1c60e7006ed1b6996b5a16ae0a55cfda19eab6c6a80ae3547bebae4c0e33b4`
- candidate panel report: `05c3b0f4815c46505b1f5266a48d701ff6ae4b603b250b1689cf2774afc66a8d`
- pinned base panel JSON: `41e3be878b590998e69b9d690559daa87db0ed959b11ec142879c9af75b27a5b`
- keyed decomposition: `1a3eb58ad25c4cda9bef6fb5f42f0db4c4efbba795400492125d59caca073e3d`

## Stop and deferred cards

The candidate is stopped without patching or retuning. G-e is discharged unrun by the binding G-d
falsifier; there is no qualification or Arena lane.

DEFERRED: panel-digest determinism. Replacement unblock signal: a separate charter; no reach rerun
merely to repair a manifest digest.

DEFERRED: NARRATE v3 real-game build/measurement. Replacement unblock signal: the coordinator
publishes the mature corpus, exact identity pin, and travelling forbidden-key sweep.
