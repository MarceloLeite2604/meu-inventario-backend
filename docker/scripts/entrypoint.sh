#!/bin/sh

if [ -z "${MNZ_MI_WORK_DIRECTORY:-}" ]; then
    echo "Error: MNZ_MI_WORK_DIRECTORY environment variable is not set."
    exit 1
fi

ALEMBIC="$MNZ_MI_WORK_DIRECTORY/.venv/bin/alembic"
ALEMBIC_INI="$MNZ_MI_WORK_DIRECTORY/database/scripts/alembic.ini"

echo "Running database migrations..."
MIGRATION_LOG=$(mktemp)
"$ALEMBIC" -c "$ALEMBIC_INI" upgrade head > "$MIGRATION_LOG" 2>&1
MIGRATION_EXIT=$?
cat "$MIGRATION_LOG"

if [ $MIGRATION_EXIT -ne 0 ]; then
    if grep -qE "DuplicateTableError|already exists" "$MIGRATION_LOG"; then
        echo "Tables already exist without migration tracking. Stamping database to current head..."
        "$ALEMBIC" -c "$ALEMBIC_INI" stamp head
        STAMP_EXIT=$?
        rm -f "$MIGRATION_LOG"
        if [ $STAMP_EXIT -ne 0 ]; then
            echo "Error: Failed to stamp database. Exiting."
            exit 1
        fi
    else
        rm -f "$MIGRATION_LOG"
        echo "Error: Database migration failed."
        exit $MIGRATION_EXIT
    fi
else
    rm -f "$MIGRATION_LOG"
fi

echo "Starting application..."
"$MNZ_MI_WORK_DIRECTORY/.venv/bin/python" -m src.main "$@"
