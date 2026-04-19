# ═══════════════════════════════════════════════════════════════════════════════
# nginx/Dockerfile
# Image Nginx ringan berbasis Alpine Linux (~25MB)
# ═══════════════════════════════════════════════════════════════════════════════
 
FROM nginx:1.25-alpine
 
# Hapus konfigurasi default nginx bawaan image
RUN rm /etc/nginx/conf.d/default.conf
 
# Salin konfigurasi utama
COPY nginx.conf /etc/nginx/nginx.conf
 
# Salin virtual host config
COPY conf.d/default.conf /etc/nginx/conf.d/default.conf
 
# Expose port 80 (HTTP)
EXPOSE 80
 
# Jalankan nginx di foreground (wajib untuk Docker)
CMD ["nginx", "-g", "daemon off;"]
 