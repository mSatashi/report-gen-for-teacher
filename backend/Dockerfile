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

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Tambahkan user non-root untuk keamanan
RUN useradd -m appuser && chown -R appuser /app

# Ensure uploads directory exists
RUN mkdir -p /app/uploads /app/uploads/pdf

# Ekspos port aplikasi
EXPOSE 8000

# Setup entrypoint untuk handle permissions (run as root, then drop to appuser for uvicorn)
ENTRYPOINT ["/entrypoint.sh"]

# Jalankan aplikasi
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
