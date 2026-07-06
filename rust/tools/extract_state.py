#!/usr/bin/env python3
"""R3a one-shot: extract the state layer from src/botmain.rs into src/botmain/state.rs.

Anchor-based (no hardcoded line numbers). Moves: TOTAL_TURNS, item-index consts,
plant_cooldown/water_boost, Cell/Troll/Tree/State + impls, ortho_neighbors/bfs_distances/
manhattan/training_cost/afford_fruit_only, mb_afford, ge_fruit_ty. Adds `pub ` to top-level
items, struct fields, and impl methods. Leaves `mod state; pub use state::*;` behind.
Gated afterwards by: cargo build+test, equality vs reference_bin, bundle gates.
"""
import os, re

SRC = "src/botmain.rs"
DST = "src/botmain/state.rs"

lines = open(SRC).read().split("\n")


def find(pred, start=0):
    for i in range(start, len(lines)):
        if pred(lines[i]):
            return i
    raise SystemExit(f"anchor not found from {start}")


def block_end(start):
    """index of the first '}' at column 0 after start."""
    return find(lambda l: l == "}", start)


ranges = []  # (start, end) inclusive


def take(start_pred, end_mode, start_from=0):
    s = find(start_pred, start_from)
    e = block_end(s) if end_mode == "brace" else s
    ranges.append((s, e))
    return s, e


# 1. TOTAL_TURNS (single line)
take(lambda l: l.startswith("const TOTAL_TURNS"), "line")
# 2. item indices comment .. water_boost end
s2 = find(lambda l: l.startswith("// Item indices"))
e2 = block_end(find(lambda l: l.startswith("fn water_boost"), s2))
ranges.append((s2, e2))
# 3. data structures .. afford_fruit_only end
s3 = find(lambda l: l.startswith("// ── data structures"))
e3 = block_end(find(lambda l: l.startswith("fn afford_fruit_only"), s3))
ranges.append((s3, e3))
# 4. mb_afford
take(lambda l: l.startswith("fn mb_afford"), "brace")
# 5. ge_fruit_ty
take(lambda l: l.startswith("fn ge_fruit_ty"), "brace")

# collect + remove (preserve original order)
ranges.sort()
moved = []
for s, e in ranges:
    moved.extend(lines[s : e + 1])
    moved.append("")
keep = []
removed = set()
for s, e in ranges:
    removed.update(range(s, e + 1))
insert_at = ranges[0][0]  # where TOTAL_TURNS was: put the mod decl here
for i, l in enumerate(lines):
    if i == insert_at:
        keep.append("mod state;")
        keep.append("pub use state::*;")
    if i not in removed:
        keep.append(l)

# visibility transform on the moved code
out = []
depth = 0
in_struct = False
struct_depth = 0
in_impl = False
impl_depth = 0
for l in moved:
    stripped = l.strip()
    # top-level declarations get pub
    if depth == 0:
        m = re.match(r"^(const |fn |struct |type |thread_local)", l)
        if m and not l.startswith("pub"):
            l = "pub " + l
        if re.match(r"^(pub )?struct ", l):
            in_struct, struct_depth = True, depth
        if l.startswith("impl "):
            in_impl, impl_depth = True, depth
    else:
        if in_struct and depth == struct_depth + 1:
            fm = re.match(r"^(\s+)([a-z_][a-z0-9_]*):", l)
            if fm and not stripped.startswith("pub"):
                l = fm.group(1) + "pub " + l.strip()
        if in_impl and depth == impl_depth + 1 and stripped.startswith("fn ") :
            l = l.replace("fn ", "pub fn ", 1)
    opens = l.count("{") - l.count("}")
    depth += opens
    if in_struct and depth <= struct_depth:
        in_struct = False
    if in_impl and depth <= impl_depth:
        in_impl = False
    out.append(l)

os.makedirs(os.path.dirname(DST), exist_ok=True)
with open(DST, "w") as f:
    f.write(
        "//! State layer (R3a): game-state types, item indices, and pure helpers shared by\n"
        "//! every decider. Extracted VERBATIM from botmain.rs (only visibility added);\n"
        "//! behavior equality is enforced by the black-box harness (src/bin/equality.rs).\n"
        "use std::collections::{HashMap, HashSet, VecDeque};\n\n"
        + "\n".join(out).rstrip()
        + "\n"
    )
with open(SRC, "w") as f:
    f.write("\n".join(keep))
print(f"moved {sum(e-s+1 for s,e in ranges)} lines -> {DST}; botmain.rs now {len(keep)} lines")
