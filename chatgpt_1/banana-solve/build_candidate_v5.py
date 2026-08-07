#!/usr/bin/env python3
"""Fifth owner-directed Banana R2 build: restore a real renewable mother.

The conservative v1/v4 arm deliberately proved safety by refusing every
realistic diagonal founding.  This layer re-opens only the mechanics-grounded
safe window: both opponent harvester and chopper ETAs must exceed two full
banana cooldown periods.  That preserves enough time for the resident's
convert/abandon response while allowing the canonical far-opponent lifecycle.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("banana_owner_v4", HERE / "build_candidate_v4.py")
v4 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = v4
spec.loader.exec_module(v4)
base_patch = v4.patch_i1


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def patch_i1(text: str) -> str:
    text = base_patch(text)
    return replace_once(
        text,
        '''        let first_fruit = resident_eta + 4 * cooldown + 2;
        eta_h > first_fruit && eta_x > first_fruit
''',
        '''        // Two full cooldown periods are the bounded response window:
        // a far opponent cannot reach the fresh mother before the resident
        // can observe a lost race and convert/abandon it, while the canonical
        // eta-13 lifecycle remains available (dry threshold = 12).
        let response_window = 2 * cooldown;
        eta_h > response_window && eta_x > response_window
''',
        "renewable mother founding window",
    )


if __name__ == "__main__":
    raise SystemExit(v4.v3.main(patch_i1))
