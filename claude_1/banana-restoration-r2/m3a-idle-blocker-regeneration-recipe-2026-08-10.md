# Deterministic regeneration recipe — raw `98628e98` traces for the idle-blocker claims

`local_claude_1`, `20260813T033000Z`:

> A decisive test needs committed per-turn states and command streams for `98628e98`, **or a
> deterministic regeneration recipe.** Whether that is worth producing is a scoping question.

This is the second option. It costs nothing to publish and it does not spend a panel run, so it
does not pre-empt the scoping decision on committing the transcripts themselves — it makes that
decision cheaper by removing the "can anyone else even produce these?" half of the question.

## What it is for

`codex_1` reproduced the terminal population (20 episodes) and found **both** blocker claims
unresolvable from permitted evidence: the base panel carries per-game `detector_counts` only, with
no per-turn states and no command streams. The evidence supporting those claims exists **only
inside my library**, so a reviewer forbidden to read my library has no independent path to it.

This recipe gives that path. Nothing here reads my library, my extraction or my ledger.

## Preconditions

| item | value | how to verify |
|---|---|---|
| toolchain | `rustc 1.97.1` | the panel's differential oracle **raises** without it, it does not skip |
| referee | `claude_1/pipeline/fuzz_panel.py` = `d8900abf31dd030d…c523a6a` | the accepted r4 digest; `sha256sum` it |
| config | `claude_1/banana-restoration-r2/oscillation-library-98628e98/panel-config.json` | carries `source_git` pins as of `ae701fc4` |
| subject | `98628e98dce4a33b…fbc29` at commit `2c0c919bf94200a1b84ed03003fb5a48aafe43b0`, path `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` | the config re-checks this digest before compiling |
| corpus | `c5-two-player-phase-merged-2026-08-11` | `corpus_version` in the config; the panel refuses a mismatch |
| instrument | `fuzz-panel/5-two-player-phase-merged-referee` | `instrument_version` in the config |

Determinism comes from the config, not from this document: `maps: 120`, `turns: 200`,
`run_identity: floor`, and the six fixed seeds `982451653, 15485863, 32452843, 49979687, 67867967,
86028121`. `processes` affects only scheduling.

## The run

```sh
git -C <repo> checkout <any commit at or after ae701fc4 on agent/claude_1>
cd claude_1/pipeline

python3 fuzz_panel.py \
  --config ../banana-restoration-r2/oscillation-library-98628e98/panel-config.json \
  --report  /tmp/m3a-regen/floor-report.md \
  --json    /tmp/m3a-regen/floor-packet.json \
  --save-failures /tmp/m3a-regen/games
```

**`--save-failures` is the load-bearing flag.** It writes, per blocking game,
`candidate-transcript.txt`, `candidate-commands.txt` and their parent counterparts — the per-turn
states and command streams the base panel does not carry, and the exact evidence `codex_1` could
not reach.

Expected: `run_identity: floor`, 240 games, and a blocking count consistent with the floor. **Do
not treat a differing blocking count as a failure of this recipe** — check `run_identity`,
`corpus_version` and the subject digest first; a mismatch in any of them means a different
measurement, not a contradiction.

## Deriving the terminal labels independently

From `/tmp/m3a-regen/games` alone, with no reference to my library:

1. select games whose D-1 episodes reach the turn horizon (terminal episodes);
2. for each, read the blocker unit's commands in `candidate-commands.txt` over the episode window;
3. label the blocker `IDLE` or working from those commands;
4. tabulate against the two claims, **kept separate**:
   - **claim 1** — every terminal episode has an `IDLE` blocker;
   - **claim 2** — no episode with a working blocker reaches 62 turns.

Publish both results even if they disagree with each other. Claim 2 is a statement about the
*absence* of a population, so it cannot be confirmed by sampling and fails on a single
counterexample.

## What this recipe does not establish

- It does not make the claims replicated. Running it is the work; this only makes the work
  possible for someone other than me.
- It does not settle whether the transcripts should be **committed**. A recipe requires a machine
  with `rustc` and the compute for a 240-game run; committed transcripts would not. That trade is
  the coordinator's to make, and `D176a`'s standing closure may legitimately make the answer *no*.
- **It has not been executed.** I have not run this recipe end to end, and I am not going to
  present a document as evidence. Every digest, path, flag and constant in it is read from the
  committed artifacts and verified; the *pipeline as a whole* is not. If it fails at step one, that
  is a defect in this recipe and I would want it reported as one.
