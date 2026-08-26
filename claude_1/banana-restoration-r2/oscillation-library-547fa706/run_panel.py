#!/usr/bin/env python3
"""Run the champion floor panel that this library is harvested from.

The committed `panel-config.json` names its bot sources by REPO-RELATIVE path
plus a `source_git` pin (commit + path + sha256).  That is the accepted
portability shape: provenance comes from the immutable commit, content from the
digest, and neither from whatever host happens to run it.  `fuzz_panel` itself
resolves `source` against the config's own directory, so the committed config
is a RECORD and is not runnable in place -- by design, it fails loudly rather
than silently picking up a stray file.

This runner does the one thing the record cannot: materialises both pinned
blobs into a scratch workdir with `test_oscillation_library.materialise_pinned_sources`
(the accepted, hash-checking helper -- imported, not reimplemented), restores
the config's own scratch output paths, and hands the result to `fuzz_panel`.
Nothing measured is touched: seeds, mixes, turns, corpus and instrument
versions and `run_identity` come from the committed config unaltered.

    python3 run_panel.py [--config panel-config.json] [--workdir <scratch>]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
R2 = HERE.parent
REPO = R2.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "pipeline"))
sys.path.insert(0, str(R2))

from test_oscillation_library import materialise_pinned_sources  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(HERE / "panel-config.json"))
    ap.add_argument("--workdir", required=True)
    args = ap.parse_args(argv)

    cfg_path = Path(args.config).resolve()
    cfg = json.loads(cfg_path.read_text())
    declared_out = {"bin_cache_dir": cfg.get("bin_cache_dir"),
                    "games_dir": cfg.get("games_dir")}
    workdir = Path(args.workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    cfg = materialise_pinned_sources(cfg, workdir)
    # materialise_pinned_sources drops the output paths (a replay wants a
    # throwaway).  This is a HARVEST, not a replay: the games dump is the
    # library's input and must land where the committed config says.
    for key, value in declared_out.items():
        if value:
            cfg[key] = value
            Path(value).mkdir(parents=True, exist_ok=True)

    run_cfg = workdir / "panel-config-materialised.json"
    run_cfg.write_text(json.dumps(cfg, indent=1, sort_keys=True) + "\n")
    print("record config   %s sha256 %s"
          % (cfg_path, hashlib.sha256(cfg_path.read_bytes()).hexdigest()))
    print("materialised at %s" % run_cfg)
    cmd = [sys.executable, str(REPO / "claude_1" / "pipeline" / "fuzz_panel.py"),
           "--config", str(run_cfg),
           "--report", str(workdir / "report.md"),
           "--json", str(workdir / "packet.json")]
    print("+", " ".join(cmd), flush=True)
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
