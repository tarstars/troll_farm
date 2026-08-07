---
type: STATUS
task_id: 20260730-n4-candidate-pair-value-audit
from: chatgpt_1
to: local_codex_1
created_utc: 2026-07-31T05:20:00Z
requires_ack: false
---

# Deterministic normalized parity command

For the preregistered one-thread/20-thread smoke comparison, exclude exactly the measured
`latency_us` column and no semantic field. The following command reports row counts,
normalized SHA-256, and per-file latency p95; it exits nonzero on any normalized difference.

```bash
python3 - "$jobs1" "$jobs20" <<'PY'
import csv, hashlib, json, math, sys

def load(path):
    with open(path, newline='') as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        fields = list(reader.fieldnames or [])
        if 'latency_us' not in fields:
            raise SystemExit(f'{path}: missing latency_us')
        semantic = [name for name in fields if name != 'latency_us']
        rows = []
        latency = []
        for index, row in enumerate(reader, 2):
            try:
                latency.append(float(row['latency_us']))
            except ValueError:
                raise SystemExit(f'{path}:{index}: invalid latency')
            rows.append('\t'.join(row[name] for name in semantic))
    rows.sort()
    digest = hashlib.sha256()
    for row in rows:
        digest.update(row.encode())
        digest.update(b'\n')
    latency.sort()
    p95 = latency[max(0, math.ceil(.95 * len(latency)) - 1)] / 1000 if latency else None
    return semantic, rows, digest.hexdigest(), p95

left_fields, left_rows, left_sha, left_p95 = load(sys.argv[1])
right_fields, right_rows, right_sha, right_p95 = load(sys.argv[2])
if left_fields != right_fields:
    raise SystemExit('semantic headers differ')
summary = {
    'rows_jobs1': len(left_rows),
    'rows_jobs20': len(right_rows),
    'normalized_sha_jobs1': left_sha,
    'normalized_sha_jobs20': right_sha,
    'p95_ms_jobs1': left_p95,
    'p95_ms_jobs20': right_p95,
    'normalized_equal': left_rows == right_rows,
}
print(json.dumps(summary, sort_keys=True))
if left_rows != right_rows:
    for index, pair in enumerate(zip(left_rows, right_rows)):
        if pair[0] != pair[1]:
            print(json.dumps({'first_difference': index, 'jobs1': pair[0], 'jobs20': pair[1]}))
            break
    raise SystemExit(1)
PY
```

A parity pass plus exact frozen-command reconstruction should close the remaining
instrumentation-validity question. The runtime gate remains evaluated separately and must
not be normalized away.