#!/usr/bin/env bash
# Установка скилла gdebenz-api для разных ИИ-агентов.
# Копирует skills/gdebenz-api/ в директорию скиллов агента.
#
# Usage:
#   bash scripts/install.sh                  # определить агента автоматически
#   bash scripts/install.sh --agent hermes   # явно указать агента
#   bash scripts/install.sh --agent openclaw
#   bash scripts/install.sh --agent claude   # Claude Code
#   bash scripts/install.sh --agent cline
#   bash scripts/install.sh --dir ~/custom/path   # куда угодно
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO_DIR/skills/gdebenz-api"
AGENT=""
DIR=""

usage() {
  echo "Usage: $0 [--agent hermes|openclaw|claude|cline|codex|cursor] [--dir PATH]"
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT="$2"; shift 2 ;;
    --dir)   DIR="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "Неизвестный аргумент: $1"; usage ;;
  esac
done

# Автоопределение агента по окружению
if [[ -z "$AGENT" ]]; then
  if command -v hermes &>/dev/null; then AGENT=hermes
  elif command -v openclaw &>/dev/null || [[ -d "$HOME/.openclaw" ]]; then AGENT=openclaw
  elif [[ -d "$HOME/.claude" ]]; then AGENT=claude
  elif [[ -d "$HOME/.cline" ]]; then AGENT=cline
  else AGENT=manual; fi
fi

case "$AGENT" in
  hermes)   DEST="${DIR:-$HOME/.hermes/skills}" ;;
  openclaw) DEST="${DIR:-$HOME/.openclaw/skills}" ;;
  claude)   DEST="${DIR:-$HOME/.claude/skills}" ;;
  cline)    DEST="${DIR:-$HOME/.claude/skills}" ;;   # Cline читает ту же папку
  codex)    DEST="${DIR:-$HOME/.codex/skills}" ;;
  cursor)   DEST="${DIR:-$HOME/.cursor/skills}" ;;
  manual)   DEST="${DIR:?Укажите --dir, чтобы выбрать куда ставить}" ;;
  *) echo "Неизвестный агент: $AGENT"; usage ;;
esac

mkdir -p "$DEST"
cp -r "$SRC" "$DEST/"
echo "✅ Скилл gdebenz-api установлен: $DEST/gdebenz-api"
echo "Проверка: $DEST/gdebenz-api/SKILL.md"
