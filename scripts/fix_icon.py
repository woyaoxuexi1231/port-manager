"""Run: python scripts/generate_icons.py"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    script = Path(__file__).with_name("generate_icons.py")
    subprocess.run([sys.executable, str(script)], check=True)
