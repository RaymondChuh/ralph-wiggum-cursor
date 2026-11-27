---
name: hil-failed
description: The human reports that a hardware-in-the-loop step went wrong. Recorded by the UserPromptSubmit hook; the agent troubleshoots and revises the instructions.
disable-model-invocation: true
argument-hint: "<TASK-ID> <what happened>"
---

The human typed `/hil-failed $ARGUMENTS`.

The `UserPromptSubmit` hook has already processed that typed command. Its result is in your context
as a line starting with `[harness]`.

**If the line says `RECORDED`:**

1. **Safety first.** If the notes mention heat, smoke, a burning smell, a swollen or hot battery,
   or sparks, tell the human to disconnect power and battery immediately and not to continue. Add
   a sign to `state/guardrails.md`.
2. Ask for any missing diagnostics: multimeter readings, serial output, photos of the wiring
   (no faces or personal details).
3. Delegate troubleshooting to the task's owner agent with the human's notes. The agent works
   through a likely-cause tree, from the most likely and cheapest to check to the least, then
   revises the instructions: `python3 scripts/harness.py open-hil <TASK>` bumps the revision. The
   agent adds a "Changes in revision N" section to the request.
4. Write a journal entry. Failures are some of the most valuable tutorial material, so feed them
   into the chapter's troubleshooting table.
5. Commit and tell the human what to try next (`/hil <TASK>`).

**If the line says `NOT recorded`:** explain why. Never record it yourself.
