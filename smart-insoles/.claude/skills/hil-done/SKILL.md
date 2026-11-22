---
name: hil-done
description: The human reports a hardware-in-the-loop step as completed. Recorded by the UserPromptSubmit hook; the agent then verifies the evidence.
disable-model-invocation: true
argument-hint: "<TASK-ID> [observations]"
---

The human typed `/hil-done $ARGUMENTS`.

The `UserPromptSubmit` hook has already processed that typed command. Its result is in your context
as a line starting with `[harness]`.

**If the line says `RECORDED`:**

1. Thank the human and restate their observations.
2. Run `python3 scripts/harness.py next`. It should return this task with mode `verify_hil`.
3. Delegate verification to the task's owner agent. The agent checks the captured evidence
   (`data/raw/hil/<TASK>/`, the human's notes, any photos) against the criteria in
   `state/hil/<TASK>.md` and fills in its "Agent verification" section.
4. If verification passes: tick the task, write a journal entry (what happened at the bench is
   prime tutorial material), commit, and report.
5. If verification fails or the evidence is missing: explain what's missing. Ask the human for it,
   or propose that they type `/hil-failed <TASK> <notes>` so the agents can troubleshoot and revise
   the instructions. Do not tick the task.

**If the line says `NOT recorded`:** explain why. Never record it yourself.
