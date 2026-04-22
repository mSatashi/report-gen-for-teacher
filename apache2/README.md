## 1. Instalasi Apache & Module

# Ubuntu/Debian
sudo apt update
sudo apt install apache2 -y

# Aktifkan module yang dibutuhkan
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod proxy_wstunnel   # untuk WebSocket/Vite HMR
sudo a2enmod headers          # untuk security headers
sudo a2enmod deflate          # untuk gzip
sudo a2enmod rewrite          # untuk SPA routing

sudo systemctl restart apache2

Konfigurasi Virtual Host
- Buat file baru: sudo nano /etc/apache2/sites-available/myapp.conf

Aktifkan & Uji Konfigurasi
# Nonaktifkan config default Apache
sudo a2dissite 000-default.conf

# Aktifkan config baru
sudo a2ensite myapp.conf

# Validasi sintaks
sudo apachectl configtest
# Expected: Syntax OK

# Reload Apache
sudo systemctl reload apache2

Setting HTTPS dengan SSL (Let's Encrypt)
# Install Certbot
sudo apt install certbot python3-certbot-apache -y

# Generate SSL otomatis (akan update config Apache sendiri)
sudo certbot --apache -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (sudah otomatis, tapi bisa test)
sudo certbot renew --dry-run

Setelah certbot berjalan, Apache otomatis menambahkan blok <VirtualHost *:443> dengan SSL.

Pengujian di Server
# Cek status Apache
sudo systemctl status apache2

# Uji semua route
curl -I http://yourdomain.com/              # React SPA
curl http://yourdomain.com/api/v1/          # FastAPI
curl http://yourdomain.com/docs             # Swagger
curl -I http://yourdomain.com/uploads/pdf/test.pdf

# Uji header keamanan
curl -I http://yourdomain.com/ | grep -E "X-Frame|X-Content|X-XSS|Referrer"

# Uji gzip
curl -H "Accept-Encoding: gzip" -I http://yourdomain.com/

# Pantau log real-time
sudo tail -f /var/log/apache2/myapp_error.log
sudo tail -f /var/log/apache2/myapp_access.log

Firewall (UFW)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
sudo ufw status