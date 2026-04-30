#!/bin/sh
# Fix uploads directory permissions at runtime
mkdir -p /app/uploads /app/uploads/pdf

# Set full permissions
chmod 777 /app/uploads
chmod 777 /app/uploads/pdf

echo "Permissions fixed:"
ls -la /app/uploads/

# Run command directly (entrypoint will execute uvicorn as root, which is fine for containerized app)
exec "$@"
