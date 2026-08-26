# Candidate 2 C-12 ruling reproduction — PASS

- Task: `20260825-dance-cure-candidate-2-swap`
- Policy: `agent/local_claude_1`, message `20260825T224354Z`
- Subject archive: `agent/claude_1@c2c69325cf5156d8a4ee0c88bf83f65b014a71b9`
- Verdict under the ruled definition: **C-12 PASS**

The coordinator ruled that the 1.5% bar is the corpus share used by Candidate 1, while the
per-unit discriminator is differential: the candidate must add no above-bar unit life relative
to the rule-off arm. On telemetry version 5, forced wait with a concrete want (`W`) is the
numerator; `H` is retired, and `X` is movement.

I extracted the pinned subject commit into a fresh temporary archive and ran:

```text
python3 claude_1/cure2/c12_idle_with_work.py
```

The run reproduced the committed result byte-for-byte:

```text
sha256(c12-idle-with-work.json)
db3a3cea1f911ffb3d8efe3d702ee4ae9335ac6388a71e2ab1f2d304a4048093
```

The accepted evaluator re-driven with `narrate5` was READY with zero decode errors on both arms.
The instrument arm's corpus idle-with-work share was **0.3818%**, versus **0.7323%** rule-off.
The candidate had **25 of 384** above-bar unit lives versus **28 of 384** rule-off; its added set
was empty and three unit lives were removed. The worst unit was **11.50%** (rule-off **95.00%**).
Parked-unit episodes were 16 versus 27, measured on 107 of 384 candidate unit lives, with 277
blind; this denominator remains attached to the episode count.

Therefore the ruled corpus bar passes and the differential passes. My earlier C-12 review ruled
the unresolved literal per-unit reading. This later coordinator ruling retires that interpretation;
the measurements themselves remain unchanged.

This closes only C-12. It does not resolve the C-5 repeat finding, the `m061` fallback finding,
the owner's Candidate 0 question, G-1 as a whole, or authorize any Arena action. The narrator
parameter remains follow-up task `20260826-p4b-narrator-param`, not an edit under this task.
