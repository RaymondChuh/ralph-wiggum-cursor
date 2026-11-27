#!/usr/bin/env bash
# Optional headless loop, Ralph-style: each iteration is a FRESH Claude Code context running `/next`.
# Stops at the first gate or hardware step that needs the human, when the project is done, or when
# two iterations in a row produce no commit (the "gutter").
#
#   scripts/autopilot.sh [-n MAX_ITERATIONS] [--budget USD_PER_ITERATION] [--model MODEL]
#                        [--permission-mode MODE]
#
# Defaults: 5 iterations, US$3 per iteration, the default model, permission mode acceptEdits.
# In headless mode, any command not allowed in .claude/settings.json is denied (flashing is
# always denied here), so agents fall back to preparing a hardware-in-the-loop step for you.
set -euo pipefail
cd "$(dirname "$0")/.."

MAX=5
BUDGET=3
MODEL=""
MODE="acceptEdits"
while [[ $# -gt 0 ]]; do
  case "$1" in
    -n|--iterations) MAX="$2"; shift 2 ;;
    --budget) BUDGET="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --permission-mode) MODE="$2"; shift 2 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

command -v claude >/dev/null || { echo "claude CLI not found" >&2; exit 1; }
mkdir -p logs
no_progress=0

for ((i = 1; i <= MAX; i++)); do
  next_json="$(python3 scripts/harness.py next --json)"
  kind="$(printf '%s' "$next_json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["kind"])')"
  message="$(printf '%s' "$next_json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["message"])')"
  case "$kind" in
    wait_gate|wait_hil|done|blocked)
      echo "autopilot: stopping before iteration $i: [$kind] $message"
      exit 0 ;;
  esac

  echo "autopilot: iteration $i/$MAX: [$kind] $message"
  before="$(git rev-parse HEAD 2>/dev/null || echo none)"
  log="logs/autopilot-$(date +%Y%m%d-%H%M%S)-$i.log"
  args=(-p "/next" --permission-mode "$MODE" --max-budget-usd "$BUDGET")
  [[ -n "$MODEL" ]] && args+=(--model "$MODEL")
  claude "${args[@]}" < /dev/null 2>&1 | tee "$log" || echo "autopilot: claude exited non-zero (see $log)"
  after="$(git rev-parse HEAD 2>/dev/null || echo none)"

  if [[ "$before" == "$after" ]]; then
    no_progress=$((no_progress + 1))
    echo "autopilot: no new commit this iteration ($no_progress in a row)"
    if (( no_progress >= 2 )); then
      echo "autopilot: stuck (gutter). Run 'claude' interactively and type /next to see what's wrong."
      exit 1
    fi
  else
    no_progress=0
  fi
done
echo "autopilot: reached $MAX iterations. Run again to continue."
