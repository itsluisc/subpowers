#!/usr/bin/env bash
# install.sh: give every agent on this machine the subpowers skill, CLI, and MCP server.
#
#   bash install.sh                  install for this user ($HOME)
#   bash install.sh --link           symlink ~/.claude/skills/subpowers to this checkout (no copy drift)
#   bash install.sh --dest DIR       install under DIR instead of $HOME (dry run for testing)
#   bash install.sh --no-doctor      skip the health check at the end
#
# What it does:
#   1. puts the skill at ~/.claude/skills/subpowers (Claude Code reads it there).
#      Cloned there already (or with --link)? It stays linked to your git checkout.
#   2. links it into ~/.agents/skills and ~/.codex/skills, plus ~/.gemini/config/skills,
#      ~/.cursor/skills, ~/.grok/skills, and ~/.hermes/skills when those harnesses exist
#   3. links `subpowers`, `subpowers-mcp`, and all painters into ~/.local/bin
#   4. installs the codex CLI if it is missing and npm or Homebrew is available
#   5. runs `subpowers doctor`
#
# Safe to re-run. Anything it replaces is moved to ~/.claude/backups/, never deleted.
# It never logs you in: run `codex login` (ChatGPT), `agy` (Antigravity), `grok login` (X Subscription),
# and/or `higgsfield auth login` (opt-in Higgsfield) yourself.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
root="$HOME"; doctor=1; link_mode=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dest) [[ $# -ge 2 ]] || { echo "usage: bash install.sh [--link] [--dest DIR] [--no-doctor]" >&2; exit 2; }; root="$2"; shift 2 ;;
    --link) link_mode=1; shift ;;
    --no-doctor) doctor=""; shift ;;
    *) echo "usage: bash install.sh [--link] [--dest DIR] [--no-doctor]" >&2; exit 2 ;;
  esac
done
mkdir -p "$root"; root="$(cd "$root" && pwd -P)"

ts="$(date +%Y%m%d-%H%M%S)"
target="$root/.claude/skills/subpowers"
backups="$root/.claude/backups/subpowers-$ts"

stash() {  # move an existing path aside, outside every skills folder
  mkdir -p "$backups"
  mv "$1" "$backups/$2"
  echo "  moved old $1 -> $backups/$2"
}

echo "subpowers install -> $root"

# 1. the skill itself
mkdir -p "$(dirname "$target")"
if [[ "$here" == "$(cd "$(dirname "$target")" && pwd -P)/subpowers" ]]; then
  echo "  running from $target (git checkout: $([[ -d "$target/.git" ]] && echo yes || echo no))"
elif [[ -n "$link_mode" ]]; then
  if [[ -L "$target" ]]; then ln -sfn "$here" "$target"
  else
    if [[ -e "$target" ]]; then stash "$target" "skill"; fi
    ln -s "$here" "$target"
  fi
  echo "  linked skill $target -> $here"
else
  if [[ -e "$target" || -L "$target" ]]; then stash "$target" "skill"; fi
  mkdir -p "$target"
  # A test HOME or --dest may be inside the checkout. Never archive our own output.
  excludes=(--exclude='.tmp-tests')
  if [[ "$target" == "$here/"* ]]; then excludes+=("--exclude=./${target#"$here/"}"); fi
  (cd "$here" && tar "${excludes[@]}" --exclude='.git' --exclude='__pycache__' --exclude='*.bak-*' --exclude='.DS_Store' -cf - .) \
    | (cd "$target" && tar -xf -)
  echo "  copied skill -> $target"
fi
chmod +x "$target"/bin/* "$target"/install.sh 2>/dev/null || true
# In a git checkout, ignore permission bits so this chmod never reads as a local edit
# (it made `subpowers update` stop with "commit your changes", 2026-09-26).
[[ -d "$target/.git" ]] && git -C "$target" config core.fileMode false 2>/dev/null || true

# 2. other agents' skill folders
link_into() {  # link_into <skills-dir>
  local d="$1/subpowers"
  mkdir -p "$1"
  if [[ -L "$d" ]]; then ln -sfn "$target" "$d"
  else
    if [[ -e "$d" ]]; then stash "$d" "$(basename "$(dirname "$1")")-skills-copy"; fi
    ln -s "$target" "$d"
  fi
  echo "  linked $d"
}
link_into "$root/.agents/skills"
link_into "$root/.codex/skills"
for harness_dir in "$root/.gemini/config" "$root/.cursor" "$root/.grok" "$root/.hermes"; do
  if [[ -d "$harness_dir" ]]; then link_into "$harness_dir/skills"; fi
done
if [[ -d "$root/.cursor" && -f "$target/rules/subpowers.mdc" ]]; then
  mkdir -p "$root/.cursor/rules"
  ln -sfn "$target/rules/subpowers.mdc" "$root/.cursor/rules/subpowers.mdc"
  echo "  linked $root/.cursor/rules/subpowers.mdc"
fi

# 3. terminal commands and shared stdio MCP server
mkdir -p "$root/.local/bin"
bins=(subpowers subpowers-mcp chatgpt-image antigravity-image grok-image grok-video higgsfield-image higgsfield-video higgsfield-soul elevenlabs-voice context-ref carousel)
for c in "${bins[@]}"; do
  [[ -e "$target/bin/$c" ]] && ln -sfn "$target/bin/$c" "$root/.local/bin/$c"
done
echo "  linked ${bins[*]} into $root/.local/bin"
case ":$PATH:" in *":$root/.local/bin:"*) ;; *)
  if [[ "$root" == "$HOME" ]]; then echo "  NOTE: add ~/.local/bin to your PATH to type subpowers anywhere (agents do not need this)"; fi ;;
esac

# 4. codex CLI (the ChatGPT painter's engine)
if [[ "$root" == "$HOME" ]] && ! command -v codex >/dev/null 2>&1; then
  if command -v npm >/dev/null 2>&1; then echo "  installing codex: npm install -g @openai/codex"; npm install -g @openai/codex || echo "  codex install failed; install it yourself: npm install -g @openai/codex"
  elif command -v brew >/dev/null 2>&1; then echo "  installing codex: brew install codex"; brew install codex || echo "  codex install failed; install it yourself: brew install codex"
  else echo "  codex not installed (needs Node.js or Homebrew). Only needed for the ChatGPT painter."; fi
fi

# 5. health check
echo
if [[ "$root" != "$HOME" ]]; then
  echo "(--dest install: skipped codex install and doctor)"
elif [[ -n "$doctor" ]]; then
  # No painter logged in yet is the normal state of a fresh install, not a failed one:
  # exit 0 and say what to log in to. Only a real install error exits non-zero.
  if ! bash "$target/bin/doctor"; then
    echo
    echo "Installed. Next: log in to at least one subscription, then run: subpowers doctor"
    echo "  ChatGPT:     codex login            (choose Sign in with ChatGPT)"
    echo "  Antigravity: agy                    (sign in once, then quit)"
    echo "  Grok:        grok login             (The X Subscription, formerly SuperGrok)"
    echo "  Higgsfield:  higgsfield auth login  (optional, spends plan credits)"
  fi
fi
