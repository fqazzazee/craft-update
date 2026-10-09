#!/usr/bin/env bash
# SPDX-License-Identifier: MIT OR Apache-2.0
# Install craft-update for the current user.
#
#   ./install.sh              link craft-update into ~/.local/bin and enable the daily timer
#   ./install.sh --no-timer   link craft-update only
#   ./install.sh --uninstall  remove the link and the timer (apps and their repos stay)
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
BIN="$HOME/.local/bin/craft-update"
UNITS="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"

case ${1:-} in
  --uninstall)
    systemctl --user disable --now craft-update.timer 2>/dev/null || true
    rm -f "$UNITS/craft-update.service" "$UNITS/craft-update.timer"
    systemctl --user daemon-reload
    rm -f "$BIN"
    echo "Removed craft-update. Your apps, their repos and ~/.config/craft-update are untouched."
    exit 0
    ;;
  --no-timer|"") ;;
  *) echo "usage: $0 [--no-timer | --uninstall]" >&2; exit 2 ;;
esac

mkdir -p "$(dirname "$BIN")"
ln -sfn "$HERE/craft-update" "$BIN"
echo "Linked $BIN -> $HERE/craft-update"

if [[ ${1:-} != --no-timer ]]; then
  mkdir -p "$UNITS"
  install -m644 "$HERE/systemd/craft-update.service" "$HERE/systemd/craft-update.timer" "$UNITS/"
  systemctl --user daemon-reload
  systemctl --user enable --now craft-update.timer
  systemctl --user list-timers craft-update.timer --no-pager | sed -n 2p
fi

case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) echo "Note: ~/.local/bin is not on your PATH; add it so craft-update and the apps can be found." ;;
esac
echo "Run 'craft-update' to build the apps listed in ~/.config/craft-update/apps."
