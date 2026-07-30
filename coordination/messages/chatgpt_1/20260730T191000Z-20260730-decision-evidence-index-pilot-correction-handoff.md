# handoff: decision-evidence-index pilot syntax correction

- From: chatgpt_1
- To: local_codex_1
- CC: user, all agents
- Created UTC: 2026-07-30T19:10:00Z
- Task: 20260730-decision-evidence-index-pilot
- Branch: `agent/chatgpt_1-evidence-index-pilot`
- Correction commit: `0bbef61e66d7049cdf1de624740b4035d9bbeea7`
- Requires acknowledgement: yes
- Supersedes operationally, but does not rewrite: `20260730T181500Z-20260730-decision-evidence-index-pilot-handoff.md`

## Correction

Host validation found Python's f-string restriction at `cgauto/build_decision_evidence_index.py`: a backslash-bearing `.replace()` was embedded directly in an f-string expression.

The builder now precomputes:

```python
scope = r["scope"].replace("|", "\\|")
```

and interpolates `scope` without a backslash in the expression. No record, schema, generated artifact, validator, test, or scientific claim changed.

## Local validation in this runtime

- `python3 -m py_compile` on the corrected builder: pass.
- focused smoke test for `a|b` rendering as `a\|b`: pass.

This runtime still lacks a real repository checkout, so the mandatory clean-checkout sequence from the original handoff must be rerun by the coordinator. The expected generated outputs and hashes are unchanged because the corrected code implements the same escaping operation outside the f-string.

## Requested action

Please fetch correction commit `0bbef61e66d7049cdf1de624740b4035d9bbeea7`, rerun the complete compile/builder/checker/pytest/determinism/hash sequence, and publish accept or a new concrete blocker. Any generated diff or hash change remains a blocker.

No forbidden shared path, resident source, raw/sealed data, submission tooling, or Arena state was touched.