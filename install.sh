#!/usr/bin/env bash
# Installs the app-map skill for your AI coding agents.
#
#   ./install.sh                     into the current git repo (shared with your team)
#   ./install.sh --user              for you, in every repo
#   ./install.sh --repo <path>       into another repo
#   ./install.sh --link              symlink instead of copy (a `git pull` here updates it)
#
# One copy goes to .agents/skills/app-map — the shared Agent Skills folder read by OpenAI Codex,
# Gemini CLI, GitHub Copilot (CLI, VS Code, JetBrains, cloud agent) and Cursor. Links make it
# visible to Claude Code (.claude/skills) and Cursor (.cursor/skills); a Cursor rule points
# older Cursor versions at it. Claude Code users can also install the plugin instead:
#   /plugin marketplace add yonivav/app-map  then  /plugin install app-map@app-map
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
source_dir="$here/skills/app-map"
scope=project target="" mode=copy
while [ $# -gt 0 ]; do
  case "$1" in
    --user) scope=user ;;
    --repo) target="$2"; shift ;;
    --link) mode=link ;;
    -h|--help) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1 (see --help)" >&2; exit 2 ;;
  esac
  shift
done

if [ "$scope" = user ]; then
  base="$HOME"
else
  base="$(git -C "${target:-.}" rev-parse --show-toplevel 2>/dev/null)" ||
    { echo "Not in a git repo: run it from your app's repo, or pass --repo <path> or --user." >&2; exit 2; }
fi

skill="$base/.agents/skills/app-map"
mkdir -p "$base/.agents/skills"
rm -rf "$skill"
if [ "$mode" = link ]; then
  ln -s "$source_dir" "$skill"
else
  # Everything the skill needs; not the Dart tool's build output.
  rsync -a --exclude '.dart_tool' --exclude 'pubspec.lock' --exclude '__pycache__' "$source_dir/" "$skill/"
fi

# Tools that look in their own folder get a link to the one copy.
for folder in .claude/skills .cursor/skills; do
  mkdir -p "$base/$folder"
  rm -rf "$base/$folder/app-map"
  ln -s "../../.agents/skills/app-map" "$base/$folder/app-map"
done

# Cursor versions without Agent Skills read rules: one that sends the agent to the skill.
if [ "$scope" = project ]; then
  mkdir -p "$base/.cursor/rules"
  cat >"$base/.cursor/rules/app-map.mdc" <<'RULE'
---
description: App map of this repo — build, update or read the architecture map (UML per module, clickable code). Use for "app map", "architecture map", "UML of the app", or after code changes to a mapped module.
alwaysApply: false
---
Follow the app-map skill: read `.agents/skills/app-map/SKILL.md` and do what it says. Its only
command is `.agents/skills/app-map/scripts/app-map` (run it with no arguments for the list).
RULE
fi

echo "app-map installed ($scope, $mode): $skill"
echo "  read by Codex, Gemini CLI, Copilot and Cursor (.agents/skills), Claude Code (.claude/skills)"
[ "$scope" = project ] && echo "  commit .agents/, .claude/skills/app-map, .cursor/ to share it with your team"
echo "Then ask your agent: \"build an app map of this repo\"."
