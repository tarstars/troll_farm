#!/usr/bin/env python3
"""Cure C — build the CANDIDATE from the byte-exact resident. Task 20260817-cure-c-implementation.

Owner-chartered 2026-08-17. One change and nothing else: at the `:1189` fall-through, a chopless
mid-game troll gets an explicit chain assembled from EXISTING generators instead of being routed
into the endgame planner.

    idle_harvest_candidates  ->  bank_candidates (only if carrying)  ->  EXPLICIT WAIT TAIL

The tail is written out. An undefined tail is how the next wall gets built
(`docs/DISCOVERY-two-correct-doors-make-a-wall-2026-08-17.md`) — the whole point of this cure is
that two locally-correct rules composed into one nobody designed, so the cure must not leave its
own composition implicit.

## Why no `endgame` parameter is threaded in

The charter says C applies only outside true endgame, and `main_candidates` never receives the
`endgame` flag. No plumbing is needed, because the fall-through is already unreachable in the
endgame arms — established two independent ways and ASSERTED here rather than trusted:

- by code: `commands()` reaches `main_candidates` from the `ENDGAME_CARRY` arm and the final
  `else`. `ENDGAME_CARRY` passes `idle_regeneration = false` literally (resident :1401), and it
  requires `carried_fruit(unit).is_some()`, which trips `main_candidates`' own early return at
  :1170 (`safe_regeneration` is `persistent_regeneration = true` for this resident);
- by measurement: all 485 observed fall-through turns carry `branch=MAIN`; none carry `ENDGAME`.

`verify_reachability_argument()` re-checks both textual premises against the resident on every
build, so the argument cannot silently rot if the subject is ever re-based.

## Diagnostic tap

The candidate also emits `CUREC turn= unit=` at the chain, to stderr only. It exists to close the
pre-registration limit declared in the registry: the fall-through set is otherwise invisible on
turns where the old code returned something non-WAIT. Stdout — the command protocol — is
untouched, and G1 proves that by parity rather than by this sentence.
"""
import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
RESIDENT = REPO / "cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs"
OUT = REPO / "claude_1/cure-c/candidate-cure-c.rs"
OUT_QUIET = REPO / "claude_1/cure-c/candidate-cure-c-quiet.rs"
RESIDENT_SHA = "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29"

OLD = '''                let chops=Self::yamo_chop_candidates(view,unit,type_to_cut,opponent_eta_penalty,);
                if idle_regeneration&&chops.is_empty(){
                    return Self::endgame_candidates(view,unit,type_to_cut,safe_regeneration,opponent_eta_penalty,);
                    }'''

NEW = '''                let chops=Self::yamo_chop_candidates(view,unit,type_to_cut,opponent_eta_penalty,);
                if idle_regeneration&&chops.is_empty(){
                    let mut fallback=vec![MoisanBot::wait()];
                    fallback.extend(Self::idle_harvest_candidates(view,unit));
                    if unit.total_carried()>0{
                        fallback.extend(Self::bank_candidates(view,unit));
                        }
                    return fallback;
                    }'''

NEW_LOGGED = '''                let chops=Self::yamo_chop_candidates(view,unit,type_to_cut,opponent_eta_penalty,);
                if idle_regeneration&&chops.is_empty(){
                    let mut fallback=vec![MoisanBot::wait()];
                    fallback.extend(Self::idle_harvest_candidates(view,unit));
                    if unit.total_carried()>0{
                        fallback.extend(Self::bank_candidates(view,unit));
                        }
                    eprintln!("CUREC turn={} unit={} n={}",view.turn,unit.id,fallback.len());
                    return fallback;
                    }'''

# textual premises of the "already non-endgame" argument, re-checked every build
PREMISES = [
    ("ENDGAME_CARRY arm passes idle_regeneration=false",
     "Self::main_candidates(view,unit,self.type_to_cut,false,true,self.opponent_eta_penalty,)"),
    ("main_candidates early-returns on carried fruit under safe_regeneration",
     "if safe_regeneration&&Self::carried_fruit(unit).is_some(){"),
    ("the resident enables persistent_regeneration (so safe_regeneration is true)",
     "bot.persistent_regeneration=true;"),
    ("the resident enables idle_regeneration (so the fall-through is live at all)",
     "bot.idle_regeneration=true;"),
    ("idle_harvest_candidates exists and takes (view, unit)",
     "fn idle_harvest_candidates(view:&GameState,unit:&Unit,)->Vec<Candidate>{"),
]


def verify_reachability_argument(src):
    """The 'C is already confined to non-endgame' argument, re-derived from the text each build.

    An argument that was true when written and is never re-checked is the same failure as a guard
    that never fires. Each premise is a literal the subject must still contain.
    """
    for name, needle in PREMISES:
        if src.count(needle) < 1:
            print(f"REFUSING: premise no longer holds — {name}\n  missing: {needle}")
            return False
    return True


def build(src, replacement, out):
    if src.count(OLD) != 1:
        print(f"REFUSING: fall-through anchor matched {src.count(OLD)} times, want exactly 1")
        return False
    text = src.replace(OLD, replacement)
    # the cure must change EXACTLY this site and nothing else
    if len(text) - len(src) != len(replacement) - len(OLD):
        print("REFUSING: edit changed more than the anchor")
        return False
    if "endgame_candidates(view,unit,type_to_cut,safe_regeneration" in text.replace(
            "Self::endgame_candidates(view,unit,type_to_cut,self.persistent_regeneration", ""):
        pass    # other endgame_candidates call sites are untouched by design; not an error
    out.write_text(text)
    print(f"wrote {out.relative_to(REPO)}")
    return True


def main():
    src = RESIDENT.read_text()
    digest = hashlib.sha256(src.encode()).hexdigest()
    if digest != RESIDENT_SHA:
        print(f"REFUSING: resident digest differs\n  want {RESIDENT_SHA}\n  got  {digest}")
        return 1
    if not verify_reachability_argument(src):
        return 1
    print("reachability premises: all 5 still hold in the subject")

    if not build(src, NEW_LOGGED, OUT):
        return 1
    if not build(src, NEW, OUT_QUIET):
        return 1

    quiet = OUT_QUIET.read_text()
    if "eprintln!" in quiet:
        print("REFUSING: the quiet candidate carries a diagnostic tap")
        return 1
    # scope discipline: the ONLY difference from the resident is the fall-through block
    import difflib
    diff = [l for l in difflib.unified_diff(src.splitlines(), quiet.splitlines(), lineterm="", n=0)
            if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
    print(f"\nquiet candidate vs resident: {len(diff)} changed lines, all in one hunk:")
    for line in diff:
        print(f"    {line}")
    hunks = sum(1 for l in difflib.unified_diff(src.splitlines(), quiet.splitlines(),
                                                lineterm="", n=0) if l.startswith("@@"))
    if hunks != 1:
        print(f"REFUSING: {hunks} hunks — the candidate must carry C and NOTHING else")
        return 1
    print("scope: exactly ONE hunk. The candidate carries C and nothing else.")

    assert hashlib.sha256(RESIDENT.read_bytes()).hexdigest() == RESIDENT_SHA
    print("resident byte-exact after build: verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
