---
name: sign
description: Add a guardrail ("sign") to state/guardrails.md so future sessions avoid a mistake.
disable-model-invocation: true
argument-hint: "<the lesson, in your own words>"
---

The human wants this lesson recorded: `$ARGUMENTS`

1. Turn it into a sign and append it under `## Learned signs` in `state/guardrails.md`:

   ```markdown
   ### Sign: <short imperative name>
   - **Trigger**: <when this applies: task type, file, situation>
   - **Instruction**: <what to do instead, concrete and checkable>
   - **Added after**: <today's date>, human request: "<their words>"
   ```

2. If an existing sign covers it, sharpen that sign instead of adding a duplicate.
3. If the lesson implies a change to an agent's instructions (`.claude/agents/*.md`) or a skill,
   propose the diff to the human; do not apply it silently.
4. Commit: `insoles(signs): <sign name>`.
