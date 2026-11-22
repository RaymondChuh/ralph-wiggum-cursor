# Hardware-in-the-loop requests

One file per backlog task marked `hil: true`, created with
`python3 scripts/harness.py open-hil <TASK>` from `state/templates/hil-request.md`.

The human follows the steps, then types `/hil-done <TASK> [notes]` or `/hil-failed <TASK> <notes>`.
The agent then verifies the evidence (or troubleshoots and bumps the revision) before ticking the task.
