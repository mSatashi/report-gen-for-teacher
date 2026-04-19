# ═══════════════════════════════════════════════════════════════════════════════
# frontend/Dockerfile
# Multi-stage build:
#   Stage 1 (builder) — install deps + build React → dist/
#   Stage 2 (runner)  — serve dengan Node / Vite preview
# ═══════════════════════════════════════════════════════════════════════════════
 
# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
 
WORKDIR /app
 
# Copy package files dulu (layer caching — npm install hanya jalan ulang
# jika package.json atau package-lock.json berubah)
COPY package*.json ./
 
RUN npm ci --silent
 
# Copy seluruh source code
COPY . .
 
# Build argument: URL API yang akan di-embed ke dalam bundle JavaScript
# Nilai ini di-set dari docker-compose.yml via build.args
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=${VITE_API_URL}
 
# Build production bundle → output ke /app/dist
RUN npm run build
 
# ── Stage 2: Serve ────────────────────────────────────────────────────────────
# Gunakan nginx alpine untuk serve static files hasil build
FROM nginx:1.25-alpine AS runner
 
# Hapus config nginx default
RUN rm /etc/nginx/conf.d/default.conf
 
# Salin hasil build dari stage builder
COPY --from=builder /app/dist /usr/share/nginx/html
 
# Config nginx khusus untuk SPA (Single Page Application):
# semua route yang tidak ditemukan dikembalikan ke index.html
# agar React Router bisa handle routing di client
COPY nginx-spa.conf /etc/nginx/conf.d/default.conf
 
EXPOSE 80
 
CMD ["nginx", "-g", "daemon off;"]