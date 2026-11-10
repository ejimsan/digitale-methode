#!/bin/bash
# Start from this file's directory, regardless of where Finder launched it.
cd "$(dirname "$0")" || exit 1
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
LOG_FILE="$PWD/startup.log"
printf '\nOracc × eBL — offline\n' | tee -a "$LOG_FILE"
printf 'Working folder: %s\n' "$PWD" | tee -a "$LOG_FILE"
printf 'Local data search\n' | tee -a "$LOG_FILE"
PYTHON_EXEC="$(command -v python3)"
if [ -z "$PYTHON_EXEC" ]; then
  echo 'Python 3.10 or newer is required. Python 3 was not found.' | tee -a "$LOG_FILE"
  read -r -p 'Press Return to close: ' _
  exit 1
fi
"$PYTHON_EXEC" - <<'PY' 2>&1 | tee -a "$LOG_FILE"
import sys
if sys.version_info < (3, 10):
    raise SystemExit('Python 3.10+ required. Detected: ' + sys.version)
print('Python:', sys.version.split()[0], flush=True)
PY
version_status=${PIPESTATUS[0]}
if [ "$version_status" -ne 0 ]; then
  read -r -p 'Press Return to close: ' _
  exit "$version_status"
fi
printf 'Preparing local corpus index and launching browser…\n' | tee -a "$LOG_FILE"
"$PYTHON_EXEC" -u app.py 2>&1 | tee -a "$LOG_FILE"
status=${PIPESTATUS[0]}
if [ "$status" -ne 0 ]; then
  printf '\nProgram exited with an error. See startup.log in this folder.\n' | tee -a "$LOG_FILE"
else
  printf '\nProgram stopped normally.\n' | tee -a "$LOG_FILE"
fi
read -r -p 'Press Return to close: ' _
exit "$status"
