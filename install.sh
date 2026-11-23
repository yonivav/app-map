#!/usr/bin/env bash
# Installs the app-map skill for your AI coding agents.
#
#   ./install.sh                     into the current git repo (shared with your team)
#   ./install.sh --user              for you, in every repo
#   ./install.sh --repo <path>       into another repo
#   ./install.sh --link              symlink instead of copy (a `git pull` here updates it)
#   ./install.sh --auto [--map docs/app-map]
#                                    also keep the map current by itself: a rule in AGENTS.md /
#                                    CLAUDE.md (your agent updates the map with every code change)
#                                    and two GitHub workflows (check the map; update it on each PR)
#
# One copy goes to .agents/skills/app-map — the shared Agent Skills folder read by OpenAI Codex,
# Gemini CLI, GitHub Copilot (CLI, VS Code, JetBrains, cloud agent) and Cursor. Links make it
# visible to Claude Code (.claude/skills) and Cursor (.cursor/skills); a Cursor rule points
# older Cursor versions at it. Claude Code users can also install the plugin instead:
#   /plugin marketplace add yonivav/app-map  then  /plugin install app-map@app-map
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
source_dir="$here/skills/app-map"
scope=project target="" mode=copy auto=no map=docs/app-map
while [ $# -gt 0 ]; do
  case "$1" in
    --user) scope=user ;;
    --repo) target="$2"; shift ;;
    --link) mode=link ;;
    --auto) auto=yes ;;
    --map) map="$2"; shift ;;
    -h|--help) sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
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

# Automatic: the agent updates the map with each code change, and CI keeps it honest.
if [ "$auto" = yes ]; then
  [ "$scope" = project ] || { echo "--auto is per repo: run it without --user" >&2; exit 2; }
  rule="$(sed "s#MAP_DIR#$map#g" "$source_dir/assets/agents-rule.md")"
  # AGENTS.md (Codex, Cursor, Copilot, Gemini CLI…), CLAUDE.md (Claude Code), GEMINI.md if present.
  for file in AGENTS.md CLAUDE.md GEMINI.md; do
    path="$base/$file"
    if [ "$file" = GEMINI.md ] && [ ! -f "$path" ]; then continue; fi
    if [ -f "$path" ] && grep -q '<!-- app-map:start -->' "$path"; then
      python3 - "$path" "$rule" <<'PY'
import re, sys
path, rule = sys.argv[1], sys.argv[2]
text = open(path).read()
open(path, 'w').write(re.sub(r'<!-- app-map:start -->.*?<!-- app-map:end -->', lambda m: rule, text, flags=re.S))
PY
    else
      { [ -s "$path" ] && printf '\n'; printf '%s\n' "$rule"; } >>"$path"
    fi
  done
  mkdir -p "$base/.github/workflows"
  for workflow in app-map-check app-map-update; do
    sed "s#^  MAP_DIR: .*#  MAP_DIR: $map#" "$source_dir/assets/$workflow.yml" >"$base/.github/workflows/$workflow.yml"
  done
  echo "  automatic: the rule is in AGENTS.md and CLAUDE.md; .github/workflows/app-map-check.yml and"
  echo "  app-map-update.yml are added (the update needs an ANTHROPIC_API_KEY repository secret)"
fi

echo "app-map installed ($scope, $mode): $skill"
echo "  read by Codex, Gemini CLI, Copilot and Cursor (.agents/skills), Claude Code (.claude/skills)"
[ "$scope" = project ] && echo "  commit .agents/, .claude/skills/app-map, .cursor/ to share it with your team"
echo "Then ask your agent: \"build an app map of this repo\"."
