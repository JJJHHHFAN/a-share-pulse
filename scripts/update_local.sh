#!/bin/zsh
set -euo pipefail

repo_dir="${0:A:h:h}"
cd "$repo_dir"

# launchd also runs on login or wake; only collect after the A-share close.
if [[ "$(date +%u)" -gt 5 || "$(date +%H%M)" -lt 1530 ]]; then
  exit 0
fi

today="$(date +%F)"
if [[ "$(git branch --show-current)" != main || -n "$(git status --porcelain)" ]]; then
  print -u2 "Automation checkout is not a clean main branch"
  exit 1
fi

git pull --rebase origin main
git push origin main  # Retry a data commit left unpublished by an earlier network failure.

if [[ -f "docs/data/history/$today.json" ]]; then
  exit 0
fi

"$repo_dir/.venv/bin/python" scripts/fetch_data.py
if [[ ! -f "docs/data/history/$today.json" ]]; then
  exit 0  # Holiday, stale market data, or today's daily bar is not ready yet.
fi

git add docs/data
if ! git diff --cached --quiet; then
  git -c user.name='A-Share Pulse Automation' \
      -c user.email='175279402+floptropical@users.noreply.github.com' \
      commit -m "snapshot: $today"
  git push origin main
fi
