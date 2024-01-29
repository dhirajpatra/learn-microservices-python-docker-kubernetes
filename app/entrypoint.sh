#!/bin/bash
# entrypoint.sh

# Function to check if the database is ready
db_ready() {
    # Use a simple command to check the database connection
    python -c "from sqlalchemy import create_engine; \
    from sqlalchemy.exc import OperationalError; \
    engine = create_engine('postgresql://admin:password@db:5432/myapp'); \
    engine.connect()" 2>/dev/null && return 0 || return 1
}

# Wait for the database to be ready (up to 60 seconds)
echo "Waiting for the database to be ready..."
for i in {1..60}; do
    if db_ready; then
        echo "Database is ready!"
        break
    fi
    sleep 1
done

# Check if Alembic version table exists
if python -c "from sqlalchemy import create_engine, inspect; \
engine = create_engine('postgresql://admin:password@db:5432/myapp'); \
inspector = inspect(engine); \
print('alembic_version' in inspector.get_table_names())" 2>/dev/null; then
    echo "Alembic version table exists. Skipping migration steps."
else
    # Initialize Alembic migrations
    alembic init migrations

    # Generate and apply migrations
    alembic revision --autogenerate -m "create products table"
    alembic upgrade head
fi

# Start the FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
