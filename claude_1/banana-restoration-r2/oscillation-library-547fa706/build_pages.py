#!/usr/bin/env python3
"""Build the champion library's viewer pages with the accepted generator.

`claude_1/viewer/build_viewer.py` is called, not copied. Two arguments it did not have
before are passed here: the expected situation count (its frozen-count guard, pinned to
THIS tree's 21 so a count drift still fails closed) and the subject block out of the
library's own index, so the header names the champion instead of the string
`readable__no_orchard` that used to be hard-coded into it.

    python3 build_pages.py [--out out/]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "viewer"))
sys.path.insert(0, str(HERE.parent))

import build_viewer as bv    # noqa: E402

#: The champion tree's frozen count. Pinned, exactly as 34 is pinned for the old tree:
#: a change in count means the wrong tree or a mutated one, and must not render.
CHAMPION_SITUATIONS = 21


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(HERE / "viewer"))
    args = ap.parse_args(argv)
    sits = bv.load(str(HERE / "library"))
    index = json.loads((HERE / "library" / "index.json").read_text())
    written = bv.build(args.out, situations=sits,
                       expected=CHAMPION_SITUATIONS, subject=index["subject"])
    print("wrote %d files to %s" % (len(written), args.out))
    print("open %s" % (Path(args.out) / "index.html"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
