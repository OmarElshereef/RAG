#!/bin/bash
set -e

echo "Running database migrations..."
cd /app/src/models/db_schemas/minirag
alembic upgrade head
cd /app

echo "Entrypoint received args: $@"
exec "$@"
