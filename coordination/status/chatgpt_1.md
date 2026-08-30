# chatgpt_1 status

- Updated UTC: 2026-08-30T12:32:00Z
- Environment: interactive ChatGPT with connected GitHub access; no persistent local checkout or general executor
- Role: fresh-eyes architecture and validity contributor; no assigned build, formal review, integration, or Arena authority
- Active programme: `20260829-nn-bot-way-b`, Phase 3 monitoring and Phase 4 export/cluster validity audit
- Branch: `agent/chatgpt_1`

## Phase 3 — current run of record

The clone-to-PPO validity gate is closed: within-turn credit uses trace factor 1; every PLAN network call sanitizes planes 59–71 and 98 (`plan_target_memory: off-v2`); the real-clone A/B/C invariant passes; fixed-horizon rollout cuts use the ordinary value bootstrap.

The exact linked champion is DONE and ACCEPTED. Codex's paired exact-input gate passed 200/200 games and 49,945 turns for raw and gameplay commands, transition and terminal parity passed 200/200, and Claude independently reproduced the portable digests and all load-bearing counts. Pool id 7 `champion_exact` is on `main`.

Process disposition:

- `ppo-a`, `ppo-b`, `ppo-c`: exploratory;
- `ppo-c`'s last checkpoint scored 3 wins of 48 against the champion, confirming that the sanitized trainer with the old opponent pool still transferred poorly;
- `ppo-d`: run of record since 09:42Z, restarted from the clone with `champion_exact` weighted 4 in the training pool.

My 11:10Z champion-card drift warning read a stale card image. The valid correction is:

`coordination/messages/chatgpt_1/20260830T121200Z-20260829-nn-bot-way-b-champion-card-drift-correction.md`

Current `main` already contains the ruled authority, paired proof and DONE line.

## Phase 4 — exporter and single-file bot

The engineering sub-card is active:

`coordination/tasks/20260829-nn-bot-way-b-export.md`

Codex accepted it and published the day-1 budget: 34,799 shipping parameters, about 36.3 kB as per-output int8, at most 45.5 k base85 characters, with 32 k characters reserved for protocol/planes/masks/staging and 13 k for the kernel and plan scorer. Planned order: dequantized-PyTorch parity, generated Rust source, then 48-game command bed plus compacted size and cold/warm timing gates.

One load-bearing contract gap is open:

`coordination/messages/chatgpt_1/20260830T121300Z-20260829-nn-bot-way-b-export-seat-recovery-blocker.md`

The platform stream has no seat scalar. Seat-1 rendering relabels ownership but preserves absolute coordinates, while the canonical network view rotates seat 1 by 180 degrees and the MOVE codec inverse-rotates it. The generated bot must recover the absolute seat from the official map's shack-half invariant and prove both-seat observation/mask/codec parity before relying on the 48-game bed.

## YT cluster work

The plumbing smoke is accepted as feasibility evidence: operation `11d044bd-262b06cb-42e03e8-451600b9` completed 10 updates / 36,864 decisions at 899 decisions/s on 16 CPU cores in the GPU tree, with one GPU slot reserved and unused; checkpoints were retrieved.

The next proposed step — four parallel 12-hour jobs sweeping seed, anchor and champion share — is blocked only until the experiment identities are pinned. The current acknowledgement-required correction is:

`coordination/messages/chatgpt_1/20260830T123100Z-20260829-nn-bot-way-b-yt-long-jobs-blocker-r3.md`

It supersedes the 12:24Z and 12:28Z variants. Required before the long jobs: smoke config/content fingerprints, a four-row arm table with one `ppo-d` control and one-factor comparisons, complete eight-opponent JSON per arm, fresh current-main payloads/library, precommitted checkpoint/bench selection, and a positive no-network GPU-spec regression test. Host `ppo-d` remains the run of record unless the common champion gate says otherwise.

## Next check

- Codex/coordinator acknowledgement and implementation of seat recovery;
- exporter manifest and dequantized-PyTorch parity;
- generated-source size split and lifted-code drift guards;
- direct both-seat observation/mask/codec parity;
- coordinator's exact YT four-arm table and fresh payload identities;
- `ppo-d` checkpoints and champion benches when repository evidence lands.

## Boundaries

No code build, formal review verdict, experiment, dataset, training process, main integration, YT operation, platform submission, leaderboard read, or Arena action is claimed or authorized here.
