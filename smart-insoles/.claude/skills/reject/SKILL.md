---
name: reject
description: The human rejects a gate request (G1–G5) with notes on what to change. The decision is recorded by the UserPromptSubmit hook; this skill plans the rework.
disable-model-invocation: true
argument-hint: "<GATE> <what to change>"
---

The human typed `/reject $ARGUMENTS`.

The `UserPromptSubmit` hook has already processed that typed command. Its result is in your context
as a line starting with `[harness]`.

**If the line says `RECORDED`:**

1. Restate the human's concerns as a numbered list. If the notes are empty or ambiguous, ask
   clarifying questions before planning.
2. Plan the rework: add new tasks (next free ids in the gate's phase) or re-open existing ones in
   `state/backlog.md`. Name the owner agent for each and say which concern it addresses.
3. Add a `## Rejection notes (revision N)` section to `state/gates/<GATE>.md`, quoting the notes
   verbatim.
4. Commit: `insoles(<GATE>): human rejected revision N; rework planned`.
5. Tell the human the plan. Explain that `/next` will work through the rework and that the agents
   will submit revision N+1 (`harness.py open-gate <GATE>`) when the rework is done.

**If the line says `NOT recorded`, or there is no `[harness]` line:** explain why and how to fix it.
Never record the decision yourself.
