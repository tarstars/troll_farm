#!/usr/bin/env python3
import json
from pathlib import Path
root = Path(__file__).resolve().parents[2]
path = root / 'local_claude_1/reconstructions/sources/all-legend-players-eulerschezahl-stats-2026-05-25.json'
data = json.loads(path.read_text())
print('names', sorted(data))
for name in ('norxondor_gorgonax', 'yamo', 'tass'):
    value = data.get(name)
    print('player', name, 'present', value is not None)
    if value is not None:
        print(json.dumps(value, sort_keys=True))
