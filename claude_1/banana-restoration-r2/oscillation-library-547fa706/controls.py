#!/usr/bin/env python3
"""G-2 controls for `20260821-champion-subject-library`. Every check is OBSERVED, never asserted.

    PATH=~/.cargo/bin:$PATH python3 controls.py [--scratch <dir>] [--games <games.jsonl.gz>]

C-4 deliberately edits the accepted builder for the length of one subprocess call and restores
it in a `finally`; the run asserts the restored digest before it exits, so a crash in between is
visible as a dirty worktree rather than as a silent pass.
"""
import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
NEW = Path(__file__).resolve().parent
R2 = NEW.parent
REPO = R2.parent.parent
OLD = R2 / "oscillation-library-98628e98"
_ap = argparse.ArgumentParser()
_ap.add_argument("--scratch", default=os.environ.get(
    "CHAMPLIB_SCRATCH", "/tmp/claude-1000/-home-tarstars-prj-troll-farm-claude-1/champlib"))
_args = _ap.parse_args()
SCRATCH = Path(_args.scratch)
sys.path.insert(0, str(R2)); sys.path.insert(0, str(REPO / "claude_1/pipeline"))
cases = []

def case(name, ok, detail):
    cases.append({"check": name, "pass": bool(ok), "detail": detail})
    print(("  PASS " if ok else "  FAIL ") + name + " -- " + detail)

# ---- C-1: the OLD library rebuilds byte-identically from the same builder ----------
from test_oscillation_library import materialise_pinned_sources
work = SCRATCH / "oldrebuild"; work.mkdir(parents=True, exist_ok=True)
cfg = json.loads((OLD / "panel-config.json").read_text())
cfg = materialise_pinned_sources(cfg, work)
cfg["games_dir"] = str(work / "games")
run_cfg = work / "panel-config-materialised.json"
run_cfg.write_text(json.dumps(cfg, indent=1, sort_keys=True) + "\n")
r = subprocess.run([sys.executable, str(REPO / "claude_1/pipeline/fuzz_panel.py"),
                    "--config", str(run_cfg), "--report", str(work / "r.md"),
                    "--json", str(work / "p.json")], capture_output=True, text=True)
print((r.stdout + r.stderr).strip().splitlines()[-1])
out = work / "library"
r2 = subprocess.run([sys.executable, str(OLD / "build_subject_library.py"),
                     "--games", str(work / "games/games.jsonl.gz"),
                     "--out", str(out)], capture_output=True, text=True)
print((r2.stdout + r2.stderr).strip().splitlines()[-4:][0] if r2.stdout else r2.stderr[-400:])
old_idx = json.loads((OLD / "library/index.json").read_text())
new_idx = json.loads((out / "index.json").read_text()) if (out / "index.json").exists() else {}
from oscillation_library import payload_sha256
FROZEN_CFG = old_idx["panel_config_sha256"]
LIVE_CFG = hashlib.sha256((OLD / "panel-config.json").read_bytes()).hexdigest()

# C-1a: every MEASURED field of every situation is identical. The comparison is a full
# recursive walk, so it names the differing paths rather than reporting one digest.
def diff_paths(a, b, p=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k in a and k in b:
                out += diff_paths(a[k], b[k], p + "/" + k)
            else:
                out.append(p + "/" + k)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(p + " LEN")
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                out += diff_paths(x, y, p + "[%d]" % i)
    elif a != b:
        out.append(p)
    return out

allpaths = set()
for e in old_idx["situations"]:
    a = json.loads((OLD / "library" / e["file"]).read_text())
    b = json.loads((out / e["file"]).read_text())
    allpaths |= set(diff_paths(a, b))
case("C-1a the accepted 98628e98 library rebuilds with every MEASURED field identical",
     allpaths <= {"/content_sha256", "/provenance/panel_config_sha256"},
     "the ONLY differing paths across all %d situations are %s -- no window, world state, "
     "command line, classification or detector field differs"
     % (len(old_idx["situations"]), sorted(allpaths)))

# C-1b: and the payloads are byte-identical once the config digest the library was FROZEN
# with is restored. The live config was edited on 2026-08-12 by the source-portability
# repair (commit 07cb2bd7), AFTER the library was accepted on 2026-08-11; that edit touched
# only source/output paths, and the frozen provenance digest is what proves it is the only
# thing that moved. The frozen config is `d9d041bb:.../panel-config.json` = %s.
ident = 0
for e in old_idx["situations"]:
    a = json.loads((OLD / "library" / e["file"]).read_text())
    b = json.loads((out / e["file"]).read_text())
    b["provenance"]["panel_config_sha256"] = FROZEN_CFG
    b.pop("content_sha256", None)
    ident += (payload_sha256(b) == a["content_sha256"])
case("C-1b payloads are byte-identical once the FROZEN config digest is restored",
     ident == len(old_idx["situations"]),
     "%d/%d payload digests reproduce exactly; live config %s != frozen %s, an edit of "
     "2026-08-12 (07cb2bd7, source-portability) to a file the library had already pinned"
     % (ident, len(old_idx["situations"]), LIVE_CFG[:16], FROZEN_CFG[:16]))

case("C-1c the rebuilt index agrees on counts, histograms and every entry but its digests",
     all(old_idx[k] == new_idx.get(k) for k in
         ("situation_count", "episode_count", "mechanism_histogram",
          "blocker_state_histogram", "kind_histogram", "completeness_histogram"))
     and [{kk: vv for kk, vv in e.items() if kk != "content_sha256"} for e in old_idx["situations"]]
      == [{kk: vv for kk, vv in e.items() if kk != "content_sha256"} for e in new_idx.get("situations", [])],
     "%d situations / %d episodes, mechanisms %s"
     % (old_idx["situation_count"], old_idx["episode_count"], old_idx["mechanism_histogram"]))

# ---- C-2: a deliberately WRONG subject hash is refused -----------------------------
bad_cfg = json.loads((NEW / "panel-config.json").read_text())
bad_cfg["candidate"]["sha256"] = "0" * 64
bad_p = work / "bad-subject-config.json"
bad_p.write_text(json.dumps(bad_cfg, indent=1, sort_keys=True) + "\n")
r3 = subprocess.run([sys.executable, str(NEW / "build_subject_library.py"),
                     "--games", str(SCRATCH / "games/games.jsonl.gz"),
                     "--panel-config", str(bad_p), "--out", str(work / "never")],
                    capture_output=True, text=True)
case("C-2 a wrong subject sha256 in the panel config is REFUSED",
     r3.returncode != 0 and "not the champion" in (r3.stdout + r3.stderr)
     and not (work / "never").exists(),
     "exit %d, stderr %r, output dir created: %s"
     % (r3.returncode, (r3.stdout + r3.stderr).strip()[-90:], (work / "never").exists()))

# ---- C-3: a run_identity that is not `floor` is refused ----------------------------
bad2 = json.loads((NEW / "panel-config.json").read_text()); bad2["run_identity"] = "candidate"
bad2_p = work / "bad-identity-config.json"; bad2_p.write_text(json.dumps(bad2, indent=1, sort_keys=True) + "\n")
r4 = subprocess.run([sys.executable, str(NEW / "build_subject_library.py"),
                     "--games", str(SCRATCH / "games/games.jsonl.gz"),
                     "--panel-config", str(bad2_p), "--out", str(work / "never2")],
                    capture_output=True, text=True)
case("C-3 a non-floor run_identity is REFUSED", r4.returncode != 0 and "floor" in (r4.stdout + r4.stderr),
     "exit %d, %r" % (r4.returncode, (r4.stdout + r4.stderr).strip()[-70:]))

# ---- C-4: a MODIFIED builder is refused (the 'unmodified method' claim has teeth) ---
tmp = tempfile.TemporaryDirectory()
src = R2 / "build_oscillation_library.py"
backup = src.read_bytes()
try:
    src.write_bytes(backup + b"\n# drift\n")
    r5 = subprocess.run([sys.executable, str(NEW / "build_subject_library.py"),
                         "--games", str(SCRATCH / "games/games.jsonl.gz"),
                         "--out", str(work / "never3")], capture_output=True, text=True)
finally:
    src.write_bytes(backup)
case("C-4 a MODIFIED accepted builder is REFUSED", r5.returncode != 0
     and "has changed" in (r5.stdout + r5.stderr),
     "exit %d, %r" % (r5.returncode, (r5.stdout + r5.stderr).strip()[-90:]))
assert hashlib.sha256(src.read_bytes()).hexdigest() == \
    "4b9fce4ca49a6ce05b4f3f8cb8f7b81d78b7da3c863a4e1ad32fdd2f16aff9df", "builder not restored!"

# ---- C-5: the champion library rebuilds byte-identically from the same games -------
r6 = subprocess.run([sys.executable, str(NEW / "build_subject_library.py"),
                     "--games", str(SCRATCH / "games/games.jsonl.gz"),
                     "--out", str(work / "champ-rebuild")], capture_output=True, text=True)
a = json.loads((NEW / "library/index.json").read_text())["library_sha256"]
b = json.loads((work / "champ-rebuild/index.json").read_text())["library_sha256"] if r6.returncode == 0 else None
case("C-5 the champion library is deterministic (same games -> same library_sha256)",
     a == b, "%s vs %s" % (a[:16], str(b)[:16]))

# ---- C-6: the identity digest file detects a bent frozen payload -------------------
sys.path.insert(0, str(NEW))
import build_subject_library as bsl
sit = json.loads((NEW / "library/OSC-001.json").read_text())
ident = json.loads((NEW / "identity.json").read_text())
rec = {c["id"]: c for c in ident["cases"]}["OSC-001"]
bent = json.loads(json.dumps(sit))
bent["window"]["commands"][0]["line"] = "WAIT"
detected = bsl._sha(bsl._canonical_commands(bent["window"])) != rec["window_commands_sha256"]
bent2 = json.loads(json.dumps(sit))
bent2["world_state_at_entry"]["units"][0][2] += 1
detected2 = bsl._sha(bsl._canonical_entry(bent2["world_state_at_entry"])) != rec["entry_state_sha256"]
case("C-6 the identity digests REJECT a changed command line and a moved unit",
     detected and detected2, "commands detected=%s, entry detected=%s" % (detected, detected2))

out_json = NEW / "controls-2026-08-21.json"
out_json.write_text(json.dumps({"cases": cases,
                                "passed": sum(1 for c in cases if c["pass"]),
                                "total": len(cases)}, indent=1) + "\n")
print("%d/%d controls pass" % (sum(1 for c in cases if c["pass"]), len(cases)))
sys.exit(0 if all(c["pass"] for c in cases) else 1)
