#!/bin/zsh
set -euo pipefail

repo_dir="${0:A:h:h}"
label='com.floptropical.a-share-pulse'
plist="$HOME/Library/LaunchAgents/$label.plist"
log_dir="$HOME/Library/Logs/a-share-pulse"

mkdir -p "$HOME/Library/LaunchAgents" "$log_dir"
cat > "$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$label</string>
  <key>ProgramArguments</key><array>
    <string>/bin/zsh</string>
    <string>$repo_dir/scripts/update_local.sh</string>
  </array>
  <key>StartInterval</key><integer>900</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$log_dir/update.log</string>
  <key>StandardErrorPath</key><string>$log_dir/error.log</string>
</dict></plist>
EOF

launchctl bootout "gui/$(id -u)" "$plist" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$plist"
echo "Installed $label: checks every 15 minutes after 15:30 on weekdays"
