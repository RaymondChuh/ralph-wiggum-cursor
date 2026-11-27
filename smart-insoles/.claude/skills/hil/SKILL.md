---
name: hil
description: Show the hardware-in-the-loop steps waiting on the human, as a friendly checklist built from state/hil/<TASK>.md.
disable-model-invocation: true
argument-hint: "[TASK-ID]"
---

1. If a task id was given (`$ARGUMENTS`), open `state/hil/$ARGUMENTS.md`. Otherwise run
   `python3 scripts/harness.py gates` and open every HIL request with status `waiting`.
2. Present each one to the human as a checklist they can follow at the bench:
   - goal (1 line) and estimated time;
   - **safety first** (verbatim from the file);
   - parts and tools;
   - the numbered steps with checkpoints;
   - evidence to capture (exact commands and the file locations under `data/raw/hil/<TASK>/`);
   - what to report back.
3. End with the exact commands: `/hil-done <TASK> <observations>` or
   `/hil-failed <TASK> <what happened>`.
4. If no steps are waiting, say so and show the next action from `python3 scripts/harness.py next`.

Do not change any files. Do not mark steps done.
