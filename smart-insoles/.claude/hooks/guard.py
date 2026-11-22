#!/usr/bin/env python3
"""PreToolUse hook: mechanical guardrails for agents (main session and subagents).

Denies:
  1. Any edit/write of state/gates/decisions.jsonl (only the human-decision hook writes it).
  2. Bash commands that touch decisions.jsonl other than read-only or git bookkeeping,
     or that invoke the human-decision hook script.
  3. Force-adding personal recordings under data/raw/ to git.
  4. `git commit` while anything under data/raw/ is staged.

Everything else passes through to the normal permission rules in .claude/settings.json.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DECISIONS = (ROOT / "state" / "gates" / "decisions.jsonl").resolve()
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
READ_ONLY_PREFIXES = ("cat ", "head ", "tail ", "grep ", "rg ", "wc ", "less ", "jq ", "python3 scripts/harness.py")
GIT_OK = re.compile(r"^\s*git\s+(status|diff|log|show|add|commit|blame)\b")


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def check_edit(tool_input: dict, cwd: str) -> None:
    raw = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not raw:
        return
    path = Path(raw)
    if not path.is_absolute():
        path = Path(cwd or ROOT) / path
    if path.resolve() == DECISIONS:
        deny(
            "state/gates/decisions.jsonl holds HUMAN decisions and is written only by the "
            "UserPromptSubmit hook when the human types /approve, /reject, /hil-done or /hil-failed. "
            "Ask the human to decide instead."
        )


def staged_raw_files(cwd: str) -> list:
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=cwd or ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
    except Exception:  # noqa: BLE001
        return []
    return [p for p in out.splitlines() if "data/raw/" in p and not p.endswith("data/raw/README.md")]


def check_bash(command: str, cwd: str) -> None:
    for segment in re.split(r"&&|\|\||;|\||\n", command):
        seg = segment.strip()
        if "record_human_decision" in seg:
            deny("Agents may not run the human-decision hook. Only the human records decisions.")
        writes = re.search(r">|\btee\b|\bsed\s+-i|\bdd\b|\btruncate\b|\bmv\b|\bcp\b|\brm\b", seg)
        if "decisions.jsonl" in seg and (writes or not (seg.startswith(READ_ONLY_PREFIXES) or GIT_OK.match(seg))):
            deny(
                "Only read-only commands may touch state/gates/decisions.jsonl. Human decisions are "
                "recorded by the UserPromptSubmit hook, never by agents."
            )
        if re.match(r"^\s*git\s+add\b", seg) and re.search(r"(\s-f\b|\s--force\b|\s-[a-zA-Z]*f)", seg) and "data/raw" in seg:
            deny("data/raw/ holds the human's personal recordings and must never be committed. "
                 "Put de-identified samples in data/samples/ instead (see the data-handling skill).")
        if re.match(r"^\s*git\s+commit\b", seg):
            raw = staged_raw_files(cwd)
            if raw:
                deny("Refusing to commit personal recordings staged from data/raw/: "
                     + ", ".join(raw[:5]) + ". Unstage them with `git restore --staged <path>`.")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        return 0
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    cwd = payload.get("cwd") or str(ROOT)
    if tool in EDIT_TOOLS:
        check_edit(tool_input, cwd)
    elif tool == "Bash":
        check_bash(tool_input.get("command", ""), cwd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
