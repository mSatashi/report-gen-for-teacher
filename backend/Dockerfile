FROM python:3.12-slim

WORKDIR /app

# Install dependencies (sistem dan Python) dalam satu layer untuk mengurangi ukuran image
RUN apt-get update && apt-get install -y \
    libpq-dev gcc build-essential libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Salin dan instal dependensi Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin kode aplikasi
COPY . .

# Tambahkan user non-root untuk keamanan
RUN useradd -m appuser && chown -R appuser /app \
    && mkdir -p /app/uploads /app/uploads/pdf

# Ekspos port aplikasi
EXPOSE 8000

# Setup entrypoint inline script untuk handle permissions
RUN cat > /entrypoint.sh << 'EOF'
#!/bin/sh
mkdir -p /app/uploads /app/uploads/pdf
chmod 777 /app/uploads
chmod 777 /app/uploads/pdf
echo "Permissions fixed:"
ls -la /app/uploads/
exec "$@"
EOF
RUN chmod +x /entrypoint.sh

# Jalankan aplikasi
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
