---
name: project-status
description: Show where the smart-insole project stands. Phases, task progress, gates, hardware steps waiting on the human, recent decisions, and the next action.
argument-hint: "[gates]"
---

1. Run `python3 scripts/harness.py status` and `python3 scripts/harness.py gates`.
2. Present a compact summary to the human:
   - a progress line per phase (✓ done, ▶ current, · not started, ⤼ skipped);
   - **anything waiting on the human first**: pending gates or hardware steps, with the file to read
     and the exact command to type;
   - the next action the agents will take on `/next`;
   - the 3 most recent journal entries in `docs/journal/` (title + date).
3. If `harness.py validate` reports errors, list them and offer to fix them.

Do not change any files.
