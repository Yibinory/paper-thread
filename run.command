#!/bin/sh
cd "$(dirname "$0")" || exit 1
if [ -x .venv/bin/python ]; then
  exec .venv/bin/python -X utf8 scripts/start.py "$@"
fi
if command -v python3 >/dev/null 2>&1; then
  exec python3 -X utf8 scripts/start.py "$@"
fi
printf '%s\n' 'PaperThread requires Python 3.10 or newer: https://www.python.org/downloads/' >&2
exit 1
