---
name: next
description: Advance the smart-insole project by exactly one step (one task, or up to the next human gate/hardware step), following the CLAUDE.md session protocol.
disable-model-invocation: true
argument-hint: "[TASK-ID to work on a specific actionable task]"
---

Run **one iteration** of the session protocol in `CLAUDE.md`.

1. Run `python3 scripts/harness.py next --json` and read `state/guardrails.md`.
   - If the human passed a task id (`$ARGUMENTS`), work on that task instead, but only if it is not
     done and not blocked by an unapproved gate or a pending hardware step. Otherwise explain why
     not and use the harness's choice.
2. Act on the `kind` / `mode` exactly as `CLAUDE.md` § Session protocol describes:
   - `wait_gate` / `wait_hil`: summarise the request file for the human in ≤ 10 lines. Tell them
     what to read and the exact command to type. Then stop.
   - `revise_gate`: plan the rework from the human's notes, add or re-open tasks, and report. Stop
     unless a rework task is now actionable and small.
   - `prepare_gate`: delegate to the phase lead to fill `state/gates/<G>.md` (`harness.py
     open-gate`).
   - `task`: delegate to the owner agent with a self-contained brief (task, acceptance criteria,
     inputs, outputs, relevant signs and gate decisions, return format). For HIL modes, include the
     `hardware-in-the-loop` skill instructions.
3. Check the returned work against the acceptance criteria. Then close out: tick the task, write a
   journal entry (`harness.py devlog`), add signs if needed, run `harness.py validate`, and commit
   (`insoles(<TASK>): ...`).
4. End with a short report:
   - **Done:** what changed (files);
   - **Next:** the result of `harness.py next`;
   - **Needs you:** any decision or physical step, with the exact command.

   Suggest `/clear` before the next `/next` to keep context fresh.
