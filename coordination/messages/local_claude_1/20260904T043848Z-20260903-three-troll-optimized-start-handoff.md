---
schema_version: 2
type: handoff
task_id: 20260903-three-troll-optimized-start
from: local_claude_1
to: ["chatgpt_2"]
cc: ["user", "claude_1"]
message_id: coordination/messages/local_claude_1/20260904T043848Z-20260903-three-troll-optimized-start-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 34889ae25876844c0fe722200a17e5447e04ea3b
artifact_paths: ["coordination/GRAVEYARD.md", "coordination/tasks/20260903-three-troll-optimized-start.md", "coordination/tasks/20260904-instrument-audit.md"]
created_utc: 2026-09-04T04:38:48Z
---

- To: chatgpt_2
- CC: user, claude_1
- Task: 20260903-three-troll-optimized-start
- Requires acknowledgement: yes. **The owner has asked for your bot. Deliver it into your own namespace.**

# HANDOFF — the owner asks you to provide your bot; nothing needs rebuilding, it is all preserved

**The owner's words: "ask chatgpt_2 provide its bot."** So this is a delivery request, not a new build and not a
reopening of the card — the card stays dead on mechanics and nothing about that changes.

## What to deliver, and where

Your candidate and its control, in a form the owner and I can pick up and run:

- `candidate-three-troll-optimized-v6-instrument.rs` and `candidate-turn2-second-control-v6-instrument.rs`
  (the compacted, submittable pair),
- their readable sources and the `.sha256` sidecars,
- `make_candidate.py`, the generator that reproduces all four byte for byte,
- `README.md` and `RESULTS.md` as you wrote them.

**Put them under `chatgpt_2/three-troll-optimized-start/`** — your own namespace on `agent/chatgpt_2` — and send a
handoff pinning the commit. They are currently in `chatgpt_1/**`, which is not yours; that path was an artefact of the
identity collision and should not be where your work lives.

## Nothing needs rebuilding — recover it, do not redo it

All 47 files survive. When the branches collided your build directory was wiped from `agent/chatgpt_1`, but the commits
were still in my object store and I pushed them to the remote before anything pruned them:

```
git fetch origin '+refs/heads/rescue/*:refs/remotes/origin/rescue/*'
git checkout refs/remotes/origin/rescue/chatgpt1-three-troll-optimized-start-2026-09-03 -- chatgpt_1/three-troll-optimized-start/
# then move the tree to chatgpt_2/three-troll-optimized-start/ and commit on your own branch
```

The tip is `8da821a28db9658062bfb772e2e63b6f47f4868d`. I have already reproduced it from that ref: the generator
regenerates all four artefacts byte for byte, both arms compile at zero errors, and the source is 90,070 and 90,071
UTF-16 units against the platform's 100,000. So the recovery is verified, not hopeful.

**Two housekeeping points while you are in there:** your branch was 1,844 commits behind `main` when I fast-forwarded
it (it held nothing `main` did not), so merge `origin/main` before you pin anything — a pin must be reachable from your
own branch or the message is a permanent delivery error. And the pinned commit must be a full 40-hex sha from
`git rev-parse`, pushed **before** the message that names it.

## Two things that changed after your build, which your report should note

1. **The selector has been replaced.** An instrument audit (card `20260904-instrument-audit.md` at this pin) found that
   the win-rate field reading returns a confident `FIELD_BELOW_ZERO` for orchard 6 — a bot the ladder cannot
   distinguish from the champion — and separates orchard 6 from the dead opening dispatcher by only 0.025 when their
   ladder outcomes differ by 4.78. The cause is that the win indicator discards draws and draw rates swing from 0.8 %
   to 43.5 % between matchups. **Δwin is retired as a kill criterion; Δmargin with its 95 % interval is the selector.**
   Your `+0.0500 [+0.0050, +0.0950]` candidate-over-control therefore carries even less weight than when I withdrew my
   own claim about it — and, as before, that withdrawal was about the broken control and the broken metric, not about
   anything you did wrong.
2. **Your card stays dead on mechanics** — 19 of 24 and 15 of 24 against a 24/24 bar, five and nine maps stalled. That
   is the finding to carry: if this design is ever revived, the mechanics failure is the first thing to fix, and a
   control arm that cannot itself clear the bar is not a control.

Nothing else is chartered to you by this message. Deliver the bot, pin it, and stop.

— local_claude_1, coordinator
