import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_bot_runs_on_sample_and_emits_commands():
    sample = (ROOT / "tests" / "sample_input.txt").read_text()
    out = subprocess.run([sys.executable, str(ROOT / "bot" / "main.py")],
                         input=sample, capture_output=True, text=True, timeout=10)
    line = out.stdout.strip().splitlines()[0]
    parts = line.split(";")
    # one command per own troll (ids 0 and 2), each a valid verb
    verbs = {p.strip().split()[0] for p in parts}
    assert verbs <= {"MOVE", "HARVEST", "DROP", "WAIT", "PICK", "PLANT", "TRAIN", "MSG"}
    assert any(p.strip().startswith(("MOVE", "HARVEST")) for p in parts)
