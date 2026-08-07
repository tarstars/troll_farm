#!/usr/bin/env python3
"""Tenth owner-directed Banana R2 build: persistent bounded-footprint guard.

The strict private-founding v4 arm correctly vetoed inner-controlled banana
plants outside the home ring while the wrapper was Active/Lost.  The pinned
standing gate exposed a lifecycle seam: after the wrapper entered an ordinary
finished/abandoned state, the structural-identity early return bypassed that
post-edit, so an inner worker could later reuse wrapper-introduced banana stock
and PLANT outside the ring (m012 seat 0, turn 15, cell (4,1)).

This layer keeps only the *spatial* guard armed after the wrapper has either
withdrawn its bootstrap seed or founded its exact mother.  It does not restore
the rejected global PICK veto and does not reserve any worker or mother after
their existing finite lifetimes.  Inner economy work remains unrestricted
except that candidate-attributable BANANA PLANT commands must satisfy the same
bounded/safe ring predicate as during the active phase.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "banana_owner_v4", HERE / "build_candidate_v4.py"
)
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
    old = '''        let lost = self.banana_enabled == Some(true) && self.banana_lost;
        if wrapper_action.is_none() && claim.is_none() && !active && !lost {
            // Structural identity: no post-edit outside banana activation
            // (dormant/disabled/never-lost-abandoned turns).
            return commands;
        }
'''
    new = '''        let lost = self.banana_enabled == Some(true) && self.banana_lost;
        // Once this wrapper has introduced/claimed banana stock, its bounded
        // spatial footprint remains observable even after the active asset has
        // completed.  Keep only the PLANT guard alive; worker reservation,
        // mother claim and PICK ownership retain their existing finite lives.
        // This closes the m012 seam where the structural-identity return let
        // the inner policy replant wrapper-origin stock outside the ring.
        let footprint_guard = self.banana_enabled == Some(true)
            && (self.banana_bootstrap_used || self.banana_mother.is_some());
        if wrapper_action.is_none()
            && claim.is_none()
            && !active
            && !lost
            && !footprint_guard
        {
            // Structural identity before banana ownership/footprint exists.
            return commands;
        }
'''
    text = replace_once(text, old, new, "persistent footprint early-return guard")
    return text


if __name__ == "__main__":
    raise SystemExit(v4.v3.main(patch_i1))
