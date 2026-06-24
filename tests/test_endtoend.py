import subprocess
import sys
from pathlib import Path

from bot.main import VERSION

ROOT = Path(__file__).resolve().parents[1]


def test_bot_runs_on_sample_and_emits_commands():
    sample = (ROOT / "tests" / "sample_input.txt").read_text()
    out = subprocess.run([sys.executable, str(ROOT / "bot" / "main.py")],
                         input=sample, capture_output=True, text=True, timeout=10)
    assert out.returncode == 0
    line = out.stdout.strip().splitlines()[0]
    parts = [p.strip() for p in line.split(";")]
    # turn 1 emits the version MSG plus one command per own troll (ids 0 and 2)
    assert parts[0] == f"MSG v{VERSION}"
    troll_cmds = [p for p in parts if not p.startswith("MSG")]
    assert len(troll_cmds) == 2
    verbs = {p.split()[0] for p in troll_cmds}
    assert verbs <= {"MOVE", "HARVEST", "DROP", "WAIT", "PICK", "PLANT", "TRAIN"}
    assert any(p.startswith(("MOVE", "HARVEST")) for p in troll_cmds)
