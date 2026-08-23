# NARRATE v3 G-P and sanitized-corpus independent review

Task: `20260823-narrate-real-game-telemetry`

Artifacts reviewed:

- NARRATE v3: `agent/claude_1@ada0a9f7ef7062cca6101669bb4ed76d0c785935`
- sanitized 149-game corpus: `agent/local_claude_1@ac65523baf1e1a6f0722e1cbc9bec83da31605a1`
- v2 decoder: `agent/claude_1@b62e5ec2f64947b12959046b062db181d42ff671`
- G1 idleness panel: `agent/claude_1@c563e449860473d290ed000e2f7989cdbe6a6b21`

Verdict: **ACCEPTED_WITH_PLATFORM_CONDITION**. The complete offline G-P v3 package reproduces,
and the sanitized-corpus correction changes only the corpus byte pin. The earlier v2 decoder and
G1 idleness verdicts stand without a changed count. Platform non-interference remains unmeasured:
the offline referee does not react to command count, ordering, or line length, so this review does
not authorize or substitute for the coordinator's live identity check.

## V3 independent execution

I created a detached worktree at the exact v3 artifact commit and ran:

```text
python3 claude_1/narrate3/run_gp3_parity.py
python3 claude_1/narrate3/gp3_controls.py
python3 claude_1/narrate3/run_gp3_forks.py
git diff --exit-code -- claude_1/narrate3/results
```

Observed:

- G-P `34/34` byte-identical after removing the complete `MSG` fragment; zero telemetry errors;
- 12,981 unit rows, 773 `chosen != available`, including 315 `chosen=NONE` with a concrete
  `available`; these are fixture counts, not prevalence;
- `ABSENT` occurred zero times in ordinary fixtures and remains unattested in ordinary play;
- all 27/27 decode controls fired, including three-state distinction, malformed input refusal,
  bidirectional version refusal, and `ABSENT` rejection in the chosen position;
- all four compiled fork controls fired: `attest-absent` produced 6,800 `ABSENT` rows with 34/34
  parity; `poison-worst` produced 168 tie-parity errors and moved 315 discarded wants to zero;
  `poison-pair` moved parity to 3/6 and the subset census 49 to 38; `poison-score` moved parity to
  0/6 and the subset census 49 to 1,960;
- regenerated parity, decoder-control, and fork-control JSON files were byte-identical to the
  committed artifacts.

Hashes independently observed:

```text
bbbb75d3d3cfa9b5de05fdc68785fd2b2fb2de18d04344e021233ada26dc7fc3  candidate-swap-r1.rs
9a3e875823f3fc26bb7be04f67d872d5c5590f4479f771cae4402ed1e3281239  instrument-swap-r1-narrate-v3.rs
7ac88e3bb843607e02f3a50b9461ef5e07c4817e9796e750941e557f7b8a54f6  gp3-parity-2026-08-23.json
4ba7171c5ca63c01cdd1324ab5ff7e925be78476474a070a9ded3bd8fb884a1c  gp3-controls-2026-08-23.json
44c26f823d085ae5c42491128079d47fddcd930a08e6e0dd8ca71bf80f7d7df0  gp3-fork-controls-2026-08-23.json
```

## Sanitized-corpus re-pin

I extracted the sanitized corpus from its exact correction commit and reran the pinned v2 decoder
panel. It passed 149/149 games with zero refusals, 38,869 traced turns, 76,305 join rows, seat split
61/88, zero opponent NARRATE turns, and all 12/12 controls. The independently computed corpus
digest is:

```text
a319f02c055950dce81c7fa586af01cb3c60a3f873386fcce9e6dd05d323ac7c
```

I also rebuilt both binaries and reran the G1 idleness panel against those sanitized bytes. It
reproduced all six class counts, 109 selected-non-NONE/no-command rows, 120 divergences, 54
adjudicable rows (45 rewritten to WAIT, 9 manufactured), 66 parity-refused rows, and 8/8 controls.
The regenerated G1 panel differs from the committed panel only at `corpus.digest_sha256`, changing
from the stale `4393d05c...` pin to `a319f02c...`.

The standing labels remain binding: `commanded` is not an outcome test; 109 is selection-side only;
the seven `blocked-no-detour` rows are not a contention measurement; 773/315 are fixture counts,
not prevalence; and ordinary play has not attested `ABSENT` or `SHACK`.

DEFERRED: the live platform non-interference and v3 real-game corpus are coordinator-controlled.
G-d stays held until that corpus measures the discarded-want class and the coordinator issues the
written anti-benching ruling required by the replacement unblock signal.
