#!/usr/bin/env python3
"""One-time idempotent repair of the first published generator packet.

The diagnostics arm and owner-readable source intentionally differ outside the feature edit;
only compact(arm) is the submitted identity. The first packet incorrectly required them to have
one token stream. This script makes that boundary explicit before generation and is committed by
the workflow together with the generated artefacts.
"""
from pathlib import Path

p = Path(__file__).with_name("make_candidate.py")
s = p.read_text()
old = '    require(token_stream(arm) == token_stream(readable), "arm and readable token streams differ")\n\n'
new = (
    '    # The diagnostics arm and owner-readable source intentionally carry different\n'
    '    # non-feature tokens. Both receive the same anchored edit and compile independently;\n'
    '    # only compact(arm) is the submission identity.\n\n'
)
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit("generator boundary anchor not found")
s = s.replace(
    '        "arm_readable_same_token_stream": True,\n',
    '        "arm_readable_same_token_stream": token_stream(arm) == token_stream(readable),\n',
    1,
)
p.write_text(s)
print("generator boundary repaired")
