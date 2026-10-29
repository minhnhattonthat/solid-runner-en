"""check.py: the one-command check. The pre-commit hook runs it; exit code gates the commit.

The pytest suite holds the text lint too: tests/test_batches.py (every English entry, as tools/insert.py lays it
out, fits its box; control codes match the JP) and tests/test_insert.py (the English build: write log, allowed
ranges, every slot reaches its English).
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.exit(subprocess.call([sys.executable, "-X", "utf8", "-m", "pytest", "-q", str(ROOT / "tests")], cwd=ROOT))
