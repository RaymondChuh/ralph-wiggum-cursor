---
task: {{TASK}}
revision: 1
owner: {{OWNER}}
created: {{DATE}}
updated: {{DATE}}
estimated_minutes:
---

# Hardware step {{TASK}}: {{TITLE}}

> **You (the human) do this step. The agents cannot see or touch the hardware.**
> When finished: `/hil-done {{TASK}} [what you observed]`. If it went wrong:
> `/hil-failed {{TASK}} <what happened>`. Then run `/next` so the agent can verify or troubleshoot.

## Goal

<!-- One sentence: what this step proves or produces. -->

## Safety first

<!-- Specific hazards for THIS step (hot soldering iron, LiPo handling, short circuits, sharp tools)
     and how to avoid them. Always: unplug USB/battery before rewiring. -->

## You need

| Item | Qty | Notes |
|---|---|---|

## Steps

<!-- Numbered and atomic, one action per step. After every few steps add a checkpoint saying
     "You should now see ..." and what to do if you don't. Add wiring tables (from pin -> to pin). -->

1. ...

## Capture the evidence

<!-- Exact commands to run, where the output is saved (raw data goes to data/raw/hil/{{TASK}}/),
     and which photos are useful (no faces, no location). -->

## Report back

<!-- Exactly what to put in the /hil-done notes, e.g. "readings at 0 g / 500 g / 1000 g". -->

## Abort if

<!-- Stop conditions: smell of burning, anything getting hot, swollen battery, readings stuck at
     0 or max. Then run /hil-failed with what you saw. -->

## Agent verification (filled in by the agent after /hil-done)

<!-- What the agent checked, against which criteria, and the result. -->
