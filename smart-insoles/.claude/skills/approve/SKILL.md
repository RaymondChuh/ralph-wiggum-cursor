---
name: approve
description: The human approves a gate (G1–G5). The decision is recorded by the UserPromptSubmit hook from the typed command; this skill only guides the follow-up.
disable-model-invocation: true
argument-hint: "<GATE> [option] [notes]"
---

The human typed `/approve $ARGUMENTS`.

The `UserPromptSubmit` hook (`.claude/hooks/record_human_decision.py`) has already processed that
typed command. Its result is in your context as a line starting with `[harness]`.

**If the line says `RECORDED`:**

1. Confirm the decision back in 1–2 lines: gate, revision, option, notes.
2. Act on the notes. If they narrow or change the plan (e.g. "approve but drop source X", "use the
   standard tier without the IMU upgrade"):
   - add a `## Decision notes (revision N)` section to `state/gates/<GATE>.md` quoting the notes
     verbatim;
   - add or adjust backlog tasks;
   - update affected files (e.g. `research/sources.yaml` statuses after G1, ADR statuses to
     `accepted` after G3).
3. Run `python3 scripts/harness.py next` and tell the human what is now unblocked.
4. Commit: `git add state/ research/ design/ && git commit -m "insoles(<GATE>): human approved revision N"`
   (only paths that exist and changed).
5. Ask whether to continue with `/next`.

**If the line says `NOT recorded`, or there is no `[harness]` line:** explain the reason and how to
fix it. For example: the gate has no request yet, it needs an option, or hooks are not active
because Claude Code was not started inside `smart-insoles/`. **Never record, simulate or assume the
decision yourself**, and never write `state/gates/decisions.jsonl`.
