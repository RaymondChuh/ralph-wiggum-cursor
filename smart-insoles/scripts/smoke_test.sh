#!/usr/bin/env bash
# Harness self-check: unit tests, state validation, settings JSON, and the strict docs build.
# Usage: bash scripts/smoke_test.sh
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0
step() { printf '\n== %s\n' "$1"; }

step "Unit tests (state machine, decision hook, guard hook, search parsers)"
python3 -m unittest discover -s scripts/tests || fail=1

step "Harness state validation"
python3 scripts/harness.py validate || fail=1

step "Claude Code settings are valid JSON"
python3 -m json.tool .claude/settings.json >/dev/null && echo "ok" || fail=1

step "Agent and skill frontmatter"
python3 - <<'EOF' || fail=1
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from harness import parse_frontmatter
bad = 0
agents = sorted(Path(".claude/agents").glob("*.md"))
skills = sorted(Path(".claude/skills").glob("*/SKILL.md"))
for f in agents:
    m = parse_frontmatter(f)
    if not (m.get("name") and m.get("description") and m.get("tools")):
        print(f"missing name/description/tools: {f}"); bad += 1
for f in skills:
    if not parse_frontmatter(f).get("description"):
        print(f"missing description: {f}"); bad += 1
print(f"{len(agents)} agents, {len(skills)} skills checked")
sys.exit(1 if bad else 0)
EOF

step "Docs site (mkdocs build --strict)"
if command -v mkdocs >/dev/null 2>&1; then
  out="$(mktemp -d)"
  NO_MKDOCS_2_WARNING=1 mkdocs build --strict -q -d "$out" && echo "ok" || fail=1
  rm -rf "$out"
else
  echo "skipped: pip install -r requirements-docs.txt to enable"
fi

printf '\n'
if (( fail )); then echo "SMOKE TEST FAILED"; else echo "SMOKE TEST PASSED"; fi
exit $fail
