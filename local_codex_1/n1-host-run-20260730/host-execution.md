# N1 host execution record

- Executed UTC: 2026-07-30T15:42Z
- Source branch: `refs/remotes/origin/agent/chatgpt_1-n1`
- Detached source commit: `836cfff055c4c07964cbb6d2e1730a316f1f1675`
- Worktree: `/tmp/troll-farm-n1-chatgpt1`
- Snapshot root:
  `/home/tarstars/prj/troll_farm/data/raw/snapshots`
- Output root:
  `/tmp/n1-maturity-result-chatgpt1-20260730T1541Z`

## Validation

```text
python3 -m py_compile chatgpt_1/n1_maturity_io.py \
  chatgpt_1/n1_maturity_model.py cgauto/maturity_curve_audit.py
exit 0

python3 cgauto/maturity_curve_audit.py --self-test
self-test: ok
exit 0
```

## Empirical command

```bash
python3 cgauto/maturity_curve_audit.py \
  --snapshot-root /home/tarstars/prj/troll_farm/data/raw/snapshots \
  --output-dir /tmp/n1-maturity-result-chatgpt1-20260730T1541Z \
  --resident-agent-id 6561795 \
  --interim-score 24.70 \
  --target-score 25.40 \
  --bootstrap 1000 \
  --seed 20260730
```

Exit code: **0**

Stdout:

```json
{"output_dir": "/tmp/n1-maturity-result-chatgpt1-20260730T1541Z", "snapshots": 7, "support": "PARTIAL", "verdict": "IMMATERIAL"}
```

Stderr: empty.

## Snapshot IDs

1. `20260721T105508Z-d61p`
2. `20260727T130712Z-d61p`
3. `20260728T050038Z-d61p`
4. `20260728T050038Z-d61p-wide21to50`
5. `20260728T110709Z-d61p-wide`
6. `20260729T021701Z-d61p-wide`
7. `20260730T021701Z-d61p-wide`

Load errors: none.

## Output SHA-256

- `coverage-and-result.json`:
  `ebafcdbe1ad300973302a2db6b05e24bd4d643957d4cc27be022d495ccdac435`
- `intervals.csv`:
  `39f7f4bfade672bc31a896f47a9fd95676a5c034442f31f75aad86802f835c9d`
- `panel.csv`:
  `148a1dee8b41d4324f0afc3e2f90670441817e40c382e1970c04c83b2f84efbb`
- `report.md`:
  `20f7f4be2fb338cfa70300f1ec70fad3968b6cb6d7b40291225d67e27a36c3a0`

The four copied artifacts in this directory are byte-identical to the `/tmp` outputs.
