#!/usr/bin/env bash
# sharpen.sh — deterministic helpers for the aa:sharpen-skill loop.
#
#   sharpen.sh start  <dir>            backup SKILL.md, report eval + unvibe state
#   sharpen.sh create <dir>            unvibe --create (only when no eval exists)
#   sharpen.sh verify <dir> [args...]  run unvibe; exit code is the eval result
#   sharpen.sh diff   <dir>            line delta + unified diff vs the backup
#   sharpen.sh resolve                 print the resolved unvibe command
#
# unvibe resolution order: $UNVIBE_BIN -> `unvibe` on PATH.
# Using uvx is an explicit, human-approved opt-in via $UNVIBE_BIN; never fetch it
# automatically.
set -euo pipefail

resolve_unvibe() {
  if [ -n "${UNVIBE_BIN:-}" ]; then
    read -r -a UNVIBE <<< "$UNVIBE_BIN"
  elif command -v unvibe >/dev/null 2>&1; then
    UNVIBE=(unvibe)
  else
    return 1
  fi
}

need_skill() { [ -f "$1/SKILL.md" ] || { echo "error: no SKILL.md in $1" >&2; exit 2; }; }
count()      { wc -l < "$1" | tr -d ' '; }

cmd_resolve() { resolve_unvibe && echo "${UNVIBE[*]}" || { echo "unavailable"; exit 1; }; }

cmd_start() {
  local dir="$1"; need_skill "$dir"
  if [ -f "$dir/SKILL.md.orig" ]; then
    echo "backup: SKILL.md.orig already exists (kept)"
  else
    cp "$dir/SKILL.md" "$dir/SKILL.md.orig"; echo "backup: SKILL.md -> SKILL.md.orig"
  fi
  [ -f "$dir/EVALUATIONS.yaml" ] && echo "eval: frozen (pre-existing)" || echo "eval: none (generate + prune)"
  if resolve_unvibe; then
    echo "unvibe: ${UNVIBE[*]}"
  else
    echo "unvibe: unavailable (installation or uvx use requires explicit human approval)"
  fi
  echo "lines: $(count "$dir/SKILL.md") (SKILL.md)"
}

cmd_create() {
  local dir="$1"; need_skill "$dir"
  resolve_unvibe || { echo "error: unvibe unavailable" >&2; exit 3; }
  "${UNVIBE[@]}" --create "$dir"
}

cmd_verify() {
  local dir="$1"; shift; need_skill "$dir"
  resolve_unvibe || { echo "error: unvibe unavailable" >&2; exit 3; }
  "${UNVIBE[@]}" "$dir" "$@"
}

cmd_diff() {
  local dir="$1"; need_skill "$dir"
  [ -f "$dir/SKILL.md.orig" ] || { echo "error: no SKILL.md.orig backup" >&2; exit 2; }
  echo "lines: $(count "$dir/SKILL.md.orig") -> $(count "$dir/SKILL.md")"
  diff -u "$dir/SKILL.md.orig" "$dir/SKILL.md" || true
}

sub="${1:-}"; shift || true
case "$sub" in
  resolve) cmd_resolve ;;
  start)   cmd_start "${1:?usage: start <dir>}" ;;
  create)  cmd_create "${1:?usage: create <dir>}" ;;
  verify)  cmd_verify "${1:?usage: verify <dir> [args]}" "${@:2}" ;;
  diff)    cmd_diff "${1:?usage: diff <dir>}" ;;
  *) echo "usage: sharpen.sh {start|create|verify|diff|resolve} <dir>" >&2; exit 64 ;;
esac
