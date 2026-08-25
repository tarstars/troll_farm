"""The 05:17 collector's last run before 2026-08-10 failed on a TLS timeout (exit=1) and
nothing noticed. This watchdog is the 'noticing'."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_cron_health as cch

NOW = datetime(2026, 8, 10, 12, 0, 0, tzinfo=timezone.utc)


def _write(tmp_path, *lines):
    p = tmp_path / "collect_wide.log"
    p.write_text("\n".join(lines) + "\n")
    return p


def test_recent_success_exits_0(tmp_path):
    p = _write(tmp_path, "start", "2026-08-10T05:20:01Z end exit=0")
    assert cch.main(log_path=p, now=lambda: NOW) == 0


def test_last_run_failed_exits_2(tmp_path):
    p = _write(tmp_path, "2026-08-09T05:20:01Z end exit=0",
               "2026-08-10T02:18:09Z end exit=1")
    assert cch.main(log_path=p, now=lambda: NOW) == 2


def test_stale_log_exits_2(tmp_path):
    p = _write(tmp_path, "2026-08-07T05:20:01Z end exit=0")
    assert cch.main(log_path=p, now=lambda: NOW) == 2


def test_missing_log_exits_2(tmp_path):
    assert cch.main(log_path=tmp_path / "absent.log", now=lambda: NOW) == 2
