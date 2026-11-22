#!/usr/bin/env python3
"""SessionStart hook: put a short project brief into Claude's context.

State lives in files, not in conversation history, so every fresh session
(startup, /clear, resume, compaction) begins by re-reading where the project is.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))


def main() -> int:
    try:
        from harness import Harness

        lines = Harness(ROOT).status_lines(brief=True)
        print("[smart-insoles harness] Session brief (from state files):")
        for line in lines:
            print(f"  {line}")
        print("  Protocol: follow CLAUDE.md. One task per session; state lives in files and git.")
        print("  The human drives with /next, /project-status, /approve, /reject, /hil, /hil-done, /hil-failed.")
    except Exception as exc:  # noqa: BLE001 - never break session start
        print(f"[smart-insoles harness] status unavailable ({exc}); run `python3 scripts/harness.py validate`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
