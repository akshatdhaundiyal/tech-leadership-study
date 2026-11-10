#!/usr/bin/env sh
# Installs this skill into one or more agent tools by symlinking (default) or
# copying the repository folder into the tool's skills directory.
#
#   ./install.sh                 # user-level, every tool whose config dir exists
#   ./install.sh claude codex    # only these tools
#   ./install.sh --project cursor copilot   # project-level dirs in the current repo
#   ./install.sh --copy all      # copy instead of symlink (for machines without git)
#
# Tools: claude codex cursor copilot gemini agents (the shared .agents/skills dir)
set -eu

SRC="$(cd "$(dirname "$0")" && pwd)"
NAME="system-design-first"
MODE="link"
SCOPE="user"
TOOLS=""

for arg in "$@"; do
  case "$arg" in
    --copy) MODE="copy" ;;
    --project) SCOPE="project" ;;
    --user) SCOPE="user" ;;
    all) TOOLS="claude codex cursor copilot gemini agents" ;;
    claude|codex|cursor|copilot|gemini|agents) TOOLS="$TOOLS $arg" ;;
    -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
    *) echo "unknown argument: $arg" >&2; exit 1 ;;
  esac
done

user_dir() {
  case "$1" in
    claude)  echo "$HOME/.claude/skills" ;;
    codex)   echo "${CODEX_HOME:-$HOME/.codex}/skills" ;;
    cursor)  echo "$HOME/.cursor/skills" ;;
    copilot) echo "$HOME/.copilot/skills" ;;
    gemini)  echo "$HOME/.gemini/skills" ;;
    agents)  echo "$HOME/.agents/skills" ;;
  esac
}

project_dir() {
  case "$1" in
    claude)  echo ".claude/skills" ;;
    codex)   echo ".codex/skills" ;;
    cursor)  echo ".cursor/skills" ;;
    copilot) echo ".github/skills" ;;
    gemini)  echo ".gemini/skills" ;;
    agents)  echo ".agents/skills" ;;
  esac
}

# Default: user scope, only tools that are already configured on this machine.
if [ -z "$TOOLS" ]; then
  for t in claude codex cursor copilot gemini agents; do
    parent="$(dirname "$(user_dir "$t")")"
    [ -d "$parent" ] && TOOLS="$TOOLS $t"
  done
  [ -z "$TOOLS" ] && { echo "no agent config dirs found; pass tool names explicitly (see --help)" >&2; exit 1; }
fi

for t in $TOOLS; do
  if [ "$SCOPE" = "user" ]; then base="$(user_dir "$t")"; else base="$(project_dir "$t")"; fi
  target="$base/$NAME"
  mkdir -p "$base"
  if [ -e "$target" ] || [ -L "$target" ]; then
    echo "skip   $target (already exists)"
    continue
  fi
  if [ "$MODE" = "link" ]; then
    ln -s "$SRC" "$target" && echo "linked $target -> $SRC"
  else
    cp -R "$SRC" "$target" && rm -rf "$target/.git" && echo "copied $target"
  fi
done
