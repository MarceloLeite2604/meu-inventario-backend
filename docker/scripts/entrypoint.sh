#!/bin/sh

if [ -z "${MNZ_MI_WORK_DIRECTORY:-}" ]; then
    echo "Error: MNZ_MI_WORK_DIRECTORY environment variable is not set."
    exit 1
fi

echo "Running database migrations..."
"$MNZ_MI_WORK_DIRECTORY/.venv/bin/alembic" \
    -c "$MNZ_MI_WORK_DIRECTORY/database/scripts/alembic.ini" \
    upgrade head

echo "Starting application..."
"$MNZ_MI_WORK_DIRECTORY/.venv/bin/python" -m src.main "$@"
