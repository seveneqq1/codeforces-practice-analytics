#!/bin/zsh

set -e

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    osascript -e 'display alert "Python is required" message "Install Python 3 from python.org, then open Practice Lab again."'
    exit 1
fi

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

.venv/bin/python -m pip install --disable-pip-version-check --quiet -r requirements.txt
exec .venv/bin/python -m streamlit run app.py
