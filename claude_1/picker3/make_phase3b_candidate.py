#!/usr/bin/env python3
r"""Phase 3b — ONE patch generator, TWO subjects: make the idle fallback EXTEND, not REPLACE.

Task `20260820-pair-selector-anti-benching`. Built to the r2 design
(`claude_1/picker3/phase3b-design-proposal-r2-2026-08-22.md`, `75085260…`) as accepted at G-f by
codex_1 (`20260822T193100Z`) and authorized for build by local_claude_1 (`20260823T063300Z`).

The subjects are the two pinned P1+P2 candidates — the Phase-2 package's own outputs — because the
fallback text and its position are identical in both, and the anti-benching change is defined on
top of P1+P2, not on the bare champions.

## Guards, all fail-closed, same house pattern as Phase 2's builder

1. **Subject digest verified** from `claude_1/picker2/build-manifest-2026-08-20.json` before a byte
   is read for patching. An unknown or drifted subject is refused, not patched.
2. **The anchor must occur exactly once** in each subject. Zero or two occurrences are a hard error.
3. **The edit is confined to `main_candidates`.** After patching, everything outside the located
   function body must be byte-identical to the subject. A patch that reaches wider is refused even
   if it compiles.
4. **The generated unified diff must be byte-identical across the two subjects** (`--check`), so the
   record shows one change, not two coincidentally similar ones.
5. **The shipped diff must be exactly the §1 hunk** — one hunk, and its added/removed lines must
   equal the ruled text. This is design §5's probe-shim inertness check (a): the source that G-c/G-d
   grades is the pinned source plus exactly this hunk and nothing else. The probe binaries built
   later carry recorders; they are built from these outputs, never the reverse.

Run:  python3 claude_1/picker3/make_phase3b_candidate.py --check
"""
from __future__ import annotations

import argparse, difflib, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
P2 = REPO / "claude_1" / "picker2"
MANIFEST = P2 / "build-manifest-2026-08-20.json"

SUBJECTS = {
    "cureC": {"src": P2 / "candidate-cureC-p1p2.rs", "out": HERE / "candidate-cureC-p3b.rs"},
    "door1": {"src": P2 / "candidate-door1-p1p2.rs", "out": HERE / "candidate-door1-p3b.rs"},
}

# The function the change lives in; the union of its span is the ONLY region the patch may touch.
FN_HEAD = "            fn main_candidates(view:&GameState,unit:&Unit,"
FN_TAIL = "            fn carried_fruit(unit:&Unit)->Option<PlantKind>{"

OLD = """                if idle_regeneration&&chops.is_empty(){
                    let mut fallback=vec![MoisanBot::wait()];
                    fallback.extend(Self::idle_harvest_candidates(view,unit));
                    if unit.total_carried()>0{
                        fallback.extend(Self::bank_candidates(view,unit));
                        }
                    return fallback;
                    }
"""

# The ruled form, kept rather than tidied so the built diff and the ruled diff are one object.
NEW = """                if idle_regeneration&&chops.is_empty(){
                    out.extend(Self::idle_harvest_candidates(view,unit));
                    if unit.total_carried()>0{
                        out.extend(Self::bank_candidates(view,unit));
                        }
                    return out;
                    }
"""


class BuildError(Exception):
    """Anything that would make the output mean something other than it says."""


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def expected_digests() -> dict:
    """Subject digests come from the Phase-2 build manifest, not from this file."""
    man = json.loads(MANIFEST.read_text())
    missing = [n for n in SUBJECTS if not isinstance(man.get(n, {}).get("cand_sha256"), str)]
    if missing:
        raise BuildError(f"no cand_sha256 in the Phase-2 build manifest for {missing}")
    for name in SUBJECTS:
        recorded = man[name]["out"]
        if recorded != str(SUBJECTS[name]["src"].relative_to(REPO)):
            raise BuildError(f"{name}: manifest names {recorded}, not the subject being patched")
    return {n: man[n]["cand_sha256"] for n in SUBJECTS}


def locate_fn(text: str) -> tuple[int, int]:
    head = text.find(FN_HEAD)
    tail = text.find(FN_TAIL)
    if head < 0 or text.count(FN_HEAD) != 1:
        raise BuildError(f"main_candidates head anchor occurs {text.count(FN_HEAD)} times")
    if tail < 0 or text.count(FN_TAIL) != 1:
        raise BuildError(f"carried_fruit tail anchor occurs {text.count(FN_TAIL)} times")
    if tail <= head:
        raise BuildError("tail anchor precedes head anchor")
    return head, tail


def patch(name: str, text: str) -> str:
    if text.count(OLD) != 1:
        raise BuildError(f"{name}: fallback anchor occurs {text.count(OLD)} times, expected 1")
    head, tail = locate_fn(text)
    if not (head < text.find(OLD) < tail):
        raise BuildError(f"{name}: the fallback anchor is outside main_candidates")
    patched = text.replace(OLD, NEW)
    # Guard 3: confinement. Everything outside the function body must be untouched.
    new_head, new_tail = locate_fn(patched)
    if text[:head] != patched[:new_head] or text[tail:] != patched[new_tail:]:
        raise BuildError(f"{name}: patch reached outside main_candidates")
    return patched


def unified(name: str, before: str, after: str) -> str:
    return "".join(difflib.unified_diff(
        before.splitlines(keepends=True), after.splitlines(keepends=True),
        fromfile=f"a/{name}", tofile=f"b/{name}", n=3))


def hunk_images(diff: str) -> tuple[str, str]:
    """Reconstruct the hunk's before- and after-images from the unified diff itself."""
    before, after, in_hunk = [], [], False
    for line in diff.splitlines(keepends=True):
        if line.startswith("@@"):
            in_hunk = True
            continue
        if not in_hunk or line.startswith(("---", "+++")):
            continue
        if line.startswith("-"):
            before.append(line[1:])
        elif line.startswith("+"):
            after.append(line[1:])
        elif line.startswith(" "):
            before.append(line[1:])
            after.append(line[1:])
    return "".join(before), "".join(after)


def check_single_hunk(diff: str) -> None:
    """Guard 5: exactly one hunk, and it is exactly the ruled OLD -> NEW rewrite.

    The expectation is not a hand-copied line list, which would drift: the hunk's before- and
    after-images are reconstructed from the diff, and the after-image is required to be the
    before-image with the ruled OLD text replaced by the ruled NEW text and nothing else.
    """
    hunks = [l for l in diff.splitlines() if l.startswith("@@")]
    if len(hunks) != 1:
        raise BuildError(f"diff has {len(hunks)} hunks, expected exactly 1")
    before, after = hunk_images(diff)
    if before.count(OLD) != 1:
        raise BuildError(f"the hunk's before-image contains the ruled OLD text "
                         f"{before.count(OLD)} times, expected 1")
    if after != before.replace(OLD, NEW):
        raise BuildError(f"the hunk changes more than the ruled OLD -> NEW rewrite\n"
                         f"--- before\n{before}\n--- after\n{after}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="verify cross-subject diff identity and re-verify existing outputs")
    args = ap.parse_args()

    digests = expected_digests()
    diffs, manifest = {}, {"builder": "claude_1/picker3/make_phase3b_candidate.py",
                           "design": "claude_1/picker3/phase3b-design-proposal-r2-2026-08-22.md",
                           "design_commit": "75085260b026750201061760804257f422c88a6b",
                           "gf_ruling": "coordination/messages/codex_1/20260822T193300Z-"
                                        "20260820-pair-selector-anti-benching-phase3b-r2-ack.md",
                           "build_authorization": "coordination/messages/local_claude_1/"
                                                  "20260823T063300Z-20260820-pair-selector-"
                                                  "anti-benching-policy.md",
                           "subjects": {}}
    for name, spec in SUBJECTS.items():
        text = spec["src"].read_text()
        digest = sha256(text)
        want = digests.get(name)
        if want is None:
            raise BuildError(f"{name}: no subject digest found in the Phase-2 build manifest")
        if digest != want:
            raise BuildError(f"{name}: subject digest {digest[:16]} != manifest {want[:16]}")
        patched = patch(name, text)
        diff = unified(spec["src"].name, text, patched)
        check_single_hunk(diff)
        diffs[name] = diff
        spec["out"].write_text(patched)
        manifest["subjects"][name] = {
            "subject": str(spec["src"].relative_to(REPO)), "subject_sha256": digest,
            "output": str(spec["out"].relative_to(REPO)), "output_sha256": sha256(patched),
            "bytes_before": len(text), "bytes_after": len(patched),
        }
        print(f"  built {spec['out'].relative_to(REPO)}  sha256 {sha256(patched)[:16]}…")

    # Guard 4: one change, not two similar ones. File names and hunk line numbers are normalised
    # away — the two subjects carry the fallback at different offsets (the door-1 forecast hunk
    # sits above it), which the design states; the changed TEXT must still be one object.
    def body(diff: str) -> str:
        keep = [l for l in diff.splitlines(keepends=True)
                if not l.startswith(("---", "+++", "@@"))]
        return "".join(keep)

    normalised = {n: body(d) for n, d in diffs.items()}
    if len(set(normalised.values())) != 1:
        raise BuildError("the generated diffs are NOT identical across subjects")
    manifest["patch_body_sha256"] = sha256(next(iter(normalised.values())))
    print(f"  cross-subject diff identity: OK  (patch body sha256 "
          f"{manifest['patch_body_sha256'][:16]}…)")

    (HERE / "phase3b.diff").write_text(diffs["cureC"])
    (HERE / "build-manifest-phase3b-2026-08-23.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    if args.check:
        for name, spec in SUBJECTS.items():
            got = sha256(spec["out"].read_text())
            want = manifest["subjects"][name]["output_sha256"]
            if got != want:
                raise BuildError(f"{name}: written output does not re-hash")
        print("  --check: outputs re-hash, single ruled hunk, identical across subjects")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BuildError as exc:
        print(f"BUILD FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
