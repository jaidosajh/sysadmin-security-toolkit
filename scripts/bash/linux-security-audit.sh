#!/usr/bin/env bash
# Read-only, local Linux posture summary. Does not require sudo.
set -euo pipefail
printf '%s\n' '=== Linux security posture (read-only) ==='
printf 'Host: %s\n' "$(hostname)"
printf 'UTC: %s\n' "$(date -u +%FT%TZ)"
printf '\n%s\n' 'Kernel:'
uname -sr
printf '\n%s\n' 'Listening TCP sockets (if ss is available):'
if command -v ss >/dev/null 2>&1; then ss -ltn || true; else echo 'ss not installed'; fi
printf '\n%s\n' 'Firewall status (if available; may require elevated permissions):'
if command -v ufw >/dev/null 2>&1; then ufw status 2>&1 || true
elif command -v firewall-cmd >/dev/null 2>&1; then firewall-cmd --state 2>&1 || true
else echo 'No supported firewall status command found'; fi
printf '\n%s\n' 'Effective current user:'
id
printf '\n%s\n' 'No changes were made.'
