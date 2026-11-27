# Gates

- `G<n>.md`: a gate request packet, written by agents with `python3 scripts/harness.py open-gate G<n>`.
  Its frontmatter carries `revision`, which goes up each time the agents resubmit after a rejection.
- `decisions.jsonl`: **human decisions only**, one JSON object per line. It is appended by
  `.claude/hooks/record_human_decision.py` when the human types `/approve` or `/reject`
  (or `/hil-done` / `/hil-failed` for hardware steps). Agents are blocked from writing it by
  `.claude/hooks/guard.py` and by a deny rule in `.claude/settings.json`.

A gate's status is computed, never stored: `not_requested` → `pending` → `approved` | `rejected`
(for the current revision). See `python3 scripts/harness.py gates`.
