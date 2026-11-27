#!/usr/bin/env python3
"""UserPromptSubmit hook: record HUMAN gate and hardware-step decisions.

This is the ONLY writer of state/gates/decisions.jsonl. It fires on prompts the
human actually typed (interactive or `claude -p`), never on model tool calls, so
an agent cannot approve its own gates. The guard hook blocks agents from writing
that file directly.

Recognised prompts:
  /approve <GATE> [option] [notes...]
  /reject <GATE> [notes...]
  /hil-done <TASK> [notes...]
  /hil-failed <TASK> [notes...]

Plain-text stdout is added to Claude's context, so the agent sees the result.
The hook always exits 0: it never blocks the human's prompt.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from harness import Harness, now_iso  # noqa: E402

PROMPT_RE = re.compile(r"^\s*/(approve|reject|hil-done|hil-failed)\b(.*)$", re.S)


def handle(payload: dict, harness: Harness) -> str:
    prompt = payload.get("prompt") or ""
    m = PROMPT_RE.match(prompt)
    if not m:
        return ""
    cmd = m.group(1)
    tokens = m.group(2).strip().split(None, 1)
    if not tokens:
        return f"[harness] NOT recorded: `/{cmd}` needs an id, e.g. `/{cmd} {'G1' if cmd in ('approve', 'reject') else 'P5-06'}`."
    item_id = tokens[0].upper().rstrip(".,:;")
    rest = tokens[1].strip() if len(tokens) > 1 else ""

    if cmd in ("approve", "reject"):
        if item_id not in harness.gate_defs:
            return f"[harness] NOT recorded: unknown gate '{item_id}'. Known gates: {', '.join(harness.gate_defs)}."
        status, _, rev = harness.gate_status(item_id)
        if status == "not_requested":
            return f"[harness] NOT recorded: gate {item_id} has no request packet yet (state/gates/{item_id}.md)."
        if status in ("approved", "rejected"):
            return (
                f"[harness] NOT recorded: gate {item_id} revision {rev} was already {status}. "
                f"The agents must submit a new revision first."
            )
        option = None
        options = harness.gate_options(item_id)
        if cmd == "approve" and options:
            first, _, remainder = rest.partition(" ")
            match = next((o for o in options if o.lower() == first.lower().rstrip(".,:;")), None)
            if match:
                option, rest = match, remainder.strip()
            elif harness.gate_defs[item_id].get("required_options"):
                return (
                    f"[harness] NOT recorded: gate {item_id} needs an option. "
                    f"Use `/approve {item_id} <{'|'.join(options)}> [notes]`."
                )
        decision = {
            "ts": now_iso(),
            "kind": "gate",
            "id": item_id,
            "revision": rev,
            "decision": "approved" if cmd == "approve" else "rejected",
            "option": option,
            "notes": rest,
            "source": "UserPromptSubmit hook",
            "session_id": payload.get("session_id", ""),
        }
    else:
        task = next((t for t in harness.tasks() if t.id == item_id), None)
        if task is None or not task.hil:
            return f"[harness] NOT recorded: '{item_id}' is not a hardware-in-the-loop task in state/backlog.md."
        status, _, rev = harness.hil_status(item_id)
        if status == "not_prepared":
            return f"[harness] NOT recorded: no instructions exist yet for {item_id} (state/hil/{item_id}.md)."
        if status in ("done", "failed"):
            return (
                f"[harness] NOT recorded: {item_id} revision {rev} is already marked {status}. "
                f"The agents must revise the instructions first."
            )
        decision = {
            "ts": now_iso(),
            "kind": "hil",
            "id": item_id,
            "revision": rev,
            "decision": "done" if cmd == "hil-done" else "failed",
            "option": None,
            "notes": rest,
            "source": "UserPromptSubmit hook",
            "session_id": payload.get("session_id", ""),
        }

    harness.decisions_path.parent.mkdir(parents=True, exist_ok=True)
    with harness.decisions_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(decision, ensure_ascii=False) + "\n")
    opt = f", option {decision['option']}" if decision.get("option") else ""
    notes = f' Notes: "{decision["notes"]}"' if decision["notes"] else ""
    return (
        f"[harness] Human decision RECORDED by hook: {decision['kind']} {item_id} revision {decision['revision']} "
        f"-> {decision['decision']}{opt}.{notes}"
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        message = handle(payload, Harness(ROOT))
    except Exception as exc:  # noqa: BLE001 - never block the user's prompt
        message = f"[harness] decision hook error, nothing recorded: {exc}"
    if message:
        print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
