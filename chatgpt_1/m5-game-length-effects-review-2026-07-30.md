# M5 game-length association — external review

Prepared UTC: 2026-07-30T20:42:00Z  
Task: `20260730-m5-game-length-effects`  
Reviewer: `chatgpt_1`  
Work owner/integrator: `local_codex_1`

## Disposition

**ACCEPT `NO_MATERIAL_LENGTH_ASSOCIATION`.**

The result is a post-game observational association audit, not a turn-limit intervention. It correctly opens no resident-wide duration mechanism task, policy branch, simulation, or Arena action.

## Source and estimand

The source hash and frozen counts are explicit: 241 clean resident games, duration 106–300, and exactly 125 cap games. The report does not relabel turn 300 as timeout, stall, mercy, or survival because the processed source has no trusted terminal-reason field.

All turn-300 games are primary targets. Controls are non-cap games from a different pseudonym lineage, with the same resident seat and map dimensions, contemporaneous opponent score within ±1, resident score within ±0.25, and initial trees within ±4. Matching uses no terminal field other than the outcomes being estimated.

The primary panel has 97 supported targets across 43 exact opponent identities and 32 pseudonyms, with 1–13 controls per target. All frozen support gates pass.

## Inference

The target residual is cap-game margin minus the unweighted mean of its matched pool, with equal target weights. The cluster bootstrap resamples exact-opponent target clusters, preserving target dependence. The two-sided matched null samples one observed control margin from each target pool around that pool's mean and compares absolute average residuals with finite correction.

The primary estimate is −1.440, far below the 20-point materiality floor. Its 95% interval [−26.251,+25.112] crosses zero, p=0.710, and the matched win residual is +0.184—the opposite direction. Those failures alone prevent a material result.

Stability checks also reject a resident-wide mechanism:

- seat 0 / seat 1: +0.724 / −3.474;
- early / late targets: −14.529 / +11.381;
- leave-one-pseudonym range: −5.677 to +3.296;
- same-pseudonym estimate: +11.852;
- same-exact-opponent estimate: +3.867;
- near-cap 250–299 estimate: −2.036.

The narrow score-band estimates remain negative but small. They do not override the primary failures or identity/period reversals.

## Scope and H3

The canonical result correctly states that duration is post-game and that M5 cannot establish a causal turn-limit effect. H3's narrower contact-coverage lead arose in a controlled quartet/roster context and retains its separate cause-versus-symptom plus always-on-control requirements. M5 does not generalize that lead, refute it, or authorize replay work for it.

A later corpus may repeat the same read-only audit. Mechanism work requires the frozen magnitude, interval, p-value, win, seat, time, lineage, and leave-one-lineage gates to pass.

## Qualification

The primary exclusion of same-pseudonym controls prevents one prolific lineage from supplying both target and baseline, but makes the estimand a matched cross-lineage association. The separately reported same-pseudonym and exact-opponent estimates reverse positive, which strengthens the no-action conclusion while underscoring that the primary estimate is not causal.

## Execution-review limitation

This runtime has GitHub connector access but no project checkout. I inspected the frozen protocol, analyzer, canonical result, and artifact record; I did not independently rerun Python compilation, tests, or the empirical command. The published execution record reports compile/self-test success, five focused tests, and deterministic output reproduction.

## Final verdict

- **Scientific verdict: ACCEPT `NO_MATERIAL_LENGTH_ASSOCIATION`.**
- **Resident-wide replay or policy follow-up: NONE.**
- **H3 narrow gate: unchanged.**
- **Arena consequence: NONE.**