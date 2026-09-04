#!/usr/bin/env python3
"""Idempotent repair for the planter self-occupancy transition.

The first execution exposed a pure instrument bug: once the planter reached a
candidate cell, `_next_empty_cell` saw that cell as occupied and discarded it,
so no PLANT could ever fire.  Occupancy by another unit still invalidates the
cell; occupancy by the selected planter is the precondition for PLANT.
"""
from pathlib import Path

path = Path(__file__).resolve().parent / "oracle.py"
text = path.read_text()
old = '''            if cell in ref.plants or any(tuple(unit["cell"]) == cell for unit in ref.units.values()):
                self.skipped_cells.add(cell)
                continue
'''
new = '''            if cell in ref.plants or any(
                uid != self.planter_id and tuple(unit["cell"]) == cell
                for uid, unit in ref.units.items()
            ):
                self.skipped_cells.add(cell)
                continue
'''
if old in text:
    if text.count(old) != 1:
        raise SystemExit(f"refusing ambiguous repair: old block count={text.count(old)}")
    path.write_text(text.replace(old, new, 1))
    print("repaired planter self-occupancy transition")
elif new in text:
    print("planter self-occupancy transition already repaired")
else:
    raise SystemExit("repair boundary not found")
