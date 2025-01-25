#!/bin/bash
echo "Running database migrations..."
alembic upgrade head

echo "Starting backend application..."
uvicorn app.main:app --host 0.0.0.0 --port 80 --reload