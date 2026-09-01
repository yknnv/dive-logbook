#!/bin/sh
# Сборка журнала и проверка результата.
set -e
cd "$(dirname "$0")"
python3 src/logbook.py
for f in dist/*-final.pdf; do
    echo "--- $f"
    python3 src/check_margins.py "$f"
done
