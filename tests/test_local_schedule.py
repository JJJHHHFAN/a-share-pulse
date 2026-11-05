"""Run the scheduler against a fixed clock and local command stubs, never the network."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("zsh"), "zsh is required for the Mac scheduler")
class LocalScheduleTest(unittest.TestCase):
    def run_schedule(self, now, archived_date=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            shutil.copy(ROOT / "scripts/update_local.sh", root / "scripts/update_local.sh")
            commands = root / "bin"
            commands.mkdir()
            date = commands / "date"
            date.write_text(
                f"#!{sys.executable}\n"
                "import os, sys\n"
                "from datetime import datetime\n"
                "from zoneinfo import ZoneInfo\n"
                "now = datetime.fromisoformat(os.environ['FIXED_UTC'])\n"
                "now = now.astimezone(ZoneInfo(os.environ['TZ']))\n"
                "fmt = sys.argv[1]\n"
                "print(now.isoweekday() if fmt == '+%u' else now.strftime(fmt[1:]))\n"
            )
            git = commands / "git"
            git.write_text(
                "#!/bin/sh\n"
                "case \"$*\" in\n"
                "  'branch --show-current') echo main ;;\n"
                "  'status --porcelain') ;;\n"
                "  *) echo \"$*\" >> \"$GIT_TRACE_FILE\" ;;\n"
                "esac\n"
            )
            python = root / ".venv/bin/python"
            python.parent.mkdir(parents=True)
            python.write_text('#!/bin/sh\nprintf fetched > "$FETCH_TRACE_FILE"\n')
            for script in (date, git, python):
                script.chmod(0o755)
            if archived_date:
                history = root / "docs/data/history"
                history.mkdir(parents=True)
                (history / f"{archived_date}.json").write_text("{}")
            git_trace = root / "git.trace"
            fetch_trace = root / "fetch.trace"
            env = dict(os.environ, TZ="America/Los_Angeles", FIXED_UTC=now,
                       PATH=str(commands) + os.pathsep + os.environ["PATH"],
                       GIT_TRACE_FILE=str(git_trace), FETCH_TRACE_FILE=str(fetch_trace))
            result = subprocess.run(
                ["zsh", str(root / "scripts/update_local.sh")], env=env,
                text=True, capture_output=True, timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            return git_trace.read_text() if git_trace.exists() else "", fetch_trace.exists()

    def test_collects_after_shanghai_close_even_if_host_is_before_close(self):
        calls, fetched = self.run_schedule("2026-11-06T08:31:00+00:00")
        self.assertIn("pull --rebase origin main", calls)
        self.assertTrue(fetched)

    def test_skips_before_shanghai_close_even_if_host_is_after_close(self):
        calls, fetched = self.run_schedule("2026-11-06T07:29:00+00:00")
        self.assertEqual(calls, "")
        self.assertFalse(fetched)

    def test_skips_shanghai_weekend_even_if_host_is_friday(self):
        calls, fetched = self.run_schedule("2026-11-06T23:31:00+00:00")
        self.assertEqual(calls, "")
        self.assertFalse(fetched)

    def test_checks_archive_using_shanghai_date(self):
        calls, fetched = self.run_schedule("2026-11-06T07:31:00+00:00", "2026-11-06")
        self.assertIn("push origin main", calls)
        self.assertFalse(fetched)
