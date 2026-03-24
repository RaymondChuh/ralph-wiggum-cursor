#!/bin/bash
# Ralph Wiggum: One-click installer
# Usage: curl -fsSL https://raw.githubusercontent.com/agrimsingh/ralph-wiggum-cursor/main/install.sh | bash

set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com/agrimsingh/ralph-wiggum-cursor/main"

echo "═══════════════════════════════════════════════════════════════════"
echo "🐛 Ralph Wiggum Installer"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Check if we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo "⚠️  Warning: Not in a git repository."
  echo "   Ralph works best with git for state persistence."
  echo ""
  echo "   Run: git init"
  echo ""
fi

# Check for cursor-agent CLI
if ! command -v cursor-agent &> /dev/null; then
  echo "⚠️  Warning: cursor-agent CLI not found."
  echo "   Install via: curl https://cursor.com/install -fsS | bash"
  echo ""
fi

# Check for gum and offer to install
if ! command -v gum &> /dev/null; then
  echo "📦 gum not found (provides beautiful CLI menus)"
  
  # Auto-install if INSTALL_GUM=1 or prompt user
  SHOULD_INSTALL=""
  if [[ "${INSTALL_GUM:-}" == "1" ]]; then
    SHOULD_INSTALL="y"
  else
    read -p "   Install gum? [y/N] " -n 1 -r < /dev/tty
    echo
    SHOULD_INSTALL="$REPLY"
  fi
  
  if [[ "$SHOULD_INSTALL" =~ ^[Yy]$ ]]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
      if command -v brew &> /dev/null; then
        echo "   Installing via Homebrew..."
        brew install gum
      else
        echo "   ⚠️  Homebrew not found. Install manually: brew install gum"
      fi
    elif [[ -f /etc/debian_version ]]; then
      echo "   Installing via apt..."
      sudo mkdir -p /etc/apt/keyrings
      curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg
      echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list
      sudo apt update && sudo apt install -y gum
    elif [[ -f /etc/fedora-release ]] || [[ -f /etc/redhat-release ]]; then
      echo "   Installing via dnf..."
      echo '[charm]
name=Charm
baseurl=https://repo.charm.sh/yum/
enabled=1
gpgcheck=1
gpgkey=https://repo.charm.sh/yum/gpg.key' | sudo tee /etc/yum.repos.d/charm.repo
      sudo dnf install -y gum
    else
      echo "   ⚠️  Unknown Linux distro. Install manually: https://github.com/charmbracelet/gum#installation"
    fi
  fi
  echo ""
fi

WORKSPACE_ROOT="$(pwd)"

# =============================================================================
# CREATE DIRECTORIES
# =============================================================================

echo "📁 Creating directories..."
mkdir -p .cursor/ralph-scripts
mkdir -p .ralph

# =============================================================================
# DOWNLOAD SCRIPTS
# =============================================================================

echo "📥 Downloading Ralph scripts..."

SCRIPTS=(
  "ralph-common.sh"
  "ralph-setup.sh"
  "ralph-loop.sh"
  "ralph-once.sh"
  "ralph-parallel.sh"
  "stream-parser.sh"
  "task-parser.sh"
  "ralph-retry.sh"
  "init-ralph.sh"
)

for script in "${SCRIPTS[@]}"; do
  if curl -fsSL "$REPO_RAW/scripts/$script" -o ".cursor/ralph-scripts/$script" 2>/dev/null; then
    chmod +x ".cursor/ralph-scripts/$script"
  else
    echo "   ⚠️  Could not download $script (may not exist yet)"
  fi
done

echo "✓ Scripts installed to .cursor/ralph-scripts/"

# Download multi-round prompt so the agent can run without a task file
mkdir -p .cursor/ralph-scripts/assets
MULTI_ROUND_PROMPT="MULTI_ROUND_EXECUTION_AGENT_PROMPT.md"
if curl -fsSL "$REPO_RAW/assets/$MULTI_ROUND_PROMPT" -o ".cursor/ralph-scripts/assets/$MULTI_ROUND_PROMPT" 2>/dev/null; then
  echo "✓ Multi-round prompt installed (no task file required)"
else
  echo "   ⚠️  Could not download multi-round prompt; create a task file in project root for legacy mode"
fi


# =============================================================================
# INITIALIZE .ralph/ STATE
# =============================================================================

echo "📁 Initializing .ralph/ state directory..."

cat > .ralph/guardrails.md << 'EOF'
# Ralph Guardrails (Signs)

> Lessons learned from past failures. READ THESE BEFORE ACTING.

## Core Signs

### Sign: Read Before Writing
- **Trigger**: Before modifying any file
- **Instruction**: Always read the existing file first
- **Added after**: Core principle

### Sign: Test After Changes
- **Trigger**: After any code change
- **Instruction**: Run tests to verify nothing broke
- **Added after**: Core principle

### Sign: Commit Checkpoints
- **Trigger**: Before risky changes
- **Instruction**: Commit current working state first
- **Added after**: Core principle

---

## Learned Signs

(Signs added from observed failures will appear below)

EOF

cat > .ralph/progress.md << 'EOF'
# Progress Log

> Updated by the agent after significant work.

## Summary

- Iterations completed: 0
- Current status: Initialized

## How This Works

Progress is tracked in THIS FILE, not in LLM context.
When context is rotated (fresh agent), the new agent reads this file.
This is how Ralph maintains continuity across iterations.

## Session History

EOF

cat > .ralph/errors.log << 'EOF'
# Error Log

> Failures detected by stream-parser. Use to update guardrails.

EOF

cat > .ralph/activity.log << 'EOF'
# Activity Log

> Real-time tool call logging from stream-parser.

EOF

echo "0" > .ralph/.iteration

echo "✓ .ralph/ initialized"

# No task file is created by default; agent follows the multi-round prompt (process/ and backlog).
# A task file can be added for legacy mode if desired.

# =============================================================================
# UPDATE .gitignore
# =============================================================================

if [[ -f ".gitignore" ]]; then
  if ! grep -q "ralph-config.json" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# Ralph config (may contain API key)" >> .gitignore
    echo ".cursor/ralph-config.json" >> .gitignore
  fi
else
  cat > .gitignore <<'EOF'
# Ralph config (may contain API key)
.cursor/ralph-config.json
EOF
fi
echo "✓ Updated .gitignore"

# =============================================================================
# SUMMARY
# =============================================================================

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "✅ Ralph installed!"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "  📁 .cursor/ralph-scripts/   – Ralph scripts + multi-round prompt"
echo "  📁 .ralph/                 – State (guardrails, progress, logs)"
echo ""
echo "Next steps:"
echo "  1. Run: ./.cursor/ralph-scripts/ralph-setup.sh"
echo ""
echo "  The agent follows the multi-round process (process/, product-opportunities)."
echo "  Single iteration:  ./.cursor/ralph-scripts/ralph-once.sh"
echo "  Monitor:           tail -f .ralph/activity.log"
echo ""
echo "Learn more: https://ghuntley.com/ralph/"
echo "═══════════════════════════════════════════════════════════════════"
