"""check.py: the one-command check (pytest suite + text lint). The pre-commit hook runs it; exit code gates the commit."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# shortcut: no text lint yet (no script/ until phase 4); add it here when script/ exists.
sys.exit(subprocess.call([sys.executable, "-X", "utf8", "-m", "pytest", "-q", str(ROOT / "tests")], cwd=ROOT))
