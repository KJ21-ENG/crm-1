# Installation & Environment

Complete guide to setting up Eshin Broking CRM on a fresh server.

---

## System Requirements

### Operating System

| OS | Version | Support |
|----|---------|---------|
| Ubuntu | 22.04 LTS | ✅ Recommended |
| Ubuntu | 20.04 LTS | ✅ Supported |
| Debian | 11/12 | ✅ Supported |
| CentOS | 8+ | ⚠️ Limited |

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Disk | 40 GB SSD | 100+ GB SSD |
| Network | 100 Mbps | 1 Gbps |

### Software Dependencies

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.10+ | Backend runtime |
| Node.js | 18+ | Frontend build |
| MariaDB | 10.8+ | Database |
| Redis | 6+ | Caching & Queue |
| Nginx | 1.18+ | Web server |
| Supervisor | 4+ | Process manager |

---

## Installation Steps

### 1. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y git python3-dev python3-pip python3-venv \
    redis-server mariadb-server mariadb-client \
    nginx supervisor \
    libmysqlclient-dev libffi-dev libssl-dev \
    wkhtmltopdf
```

### 2. Configure MariaDB

```bash
# Secure installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
```

```sql
CREATE USER 'frappe'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON *.* TO 'frappe'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT;
```

### 3. Configure MariaDB Settings

```bash
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```

Add under `[mysqld]`:
```ini
[mysqld]
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
skip-character-set-client-handshake
innodb_file_per_table = 1
innodb_buffer_pool_size = 1G
```

```bash
sudo systemctl restart mariadb
```

### 4. Install Node.js

```bash
# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Yarn
sudo npm install -g yarn
```

### 5. Create Frappe User

```bash
# Create user
sudo adduser frappe
sudo usermod -aG sudo frappe

# Switch to frappe user
su - frappe
```

### 6. Install Bench

```bash
# Install bench CLI
pip3 install frappe-bench

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 7. Initialize Bench

```bash
# Create bench directory
bench init frappe-bench --frappe-branch version-15

cd frappe-bench
```

### 8. Create Site

```bash
# Create a new site
bench new-site eshin.localhost \
    --db-name eshin_db \
    --db-password your_db_password \
    --admin-password your_admin_password
```

### 9. Install CRM App

```bash
# Get CRM from repository
bench get-app crm https://github.com/KJ21-ENG/crm-1.git --branch development-kush-exp

# Install on site
bench --site eshin.localhost install-app crm
```

### 10. Build Frontend

```bash
# Build production assets
bench build --app crm
```

---

## Development Environment

### Quick Start

Use the provided scripts:

```bash
cd ~/frappe-bench/apps/crm

# Start all services
./start_crm_dev.sh

# Check status
./status_crm_dev.sh

# Stop services
./stop_crm_dev.sh
```

### Manual Development Start

```bash
cd ~/frappe-bench

# Start Frappe development server
bench start

# In another terminal, start frontend dev server
cd apps/crm/frontend
yarn dev
```

![Bench Start Terminal Output](../assets/screenshots/bench-start-terminal.png)
<!-- TODO: Capture terminal output showing bench start with successful service startup -->

### Access URLs

| Environment | URL |
|-------------|-----|
| Backend | http://localhost:8000 |
| Frontend Dev | http://localhost:8080 |
| Admin Panel | http://localhost:8000/app |

---

## Environment Variables

### Required Variables

| Variable | Description | Location |
|----------|-------------|----------|
| `DB_HOST` | Database host | site_config.json |
| `DB_NAME` | Database name | site_config.json |
| `DB_PASSWORD` | Database password | site_config.json |
| `REDIS_CACHE` | Redis cache URL | common_site_config.json |
| `REDIS_QUEUE` | Redis queue URL | common_site_config.json |

### Optional Variables

| Variable | Description |
|----------|-------------|
| `FRAPPE_SITE_NAME_HEADER` | For multi-tenant setup |
| `SOCKETIO_PORT` | WebSocket port |

---

## Configuration Files

### site_config.json

Located at `~/frappe-bench/sites/eshin.localhost/site_config.json`:

```json
{
    "db_name": "eshin_db",
    "db_password": "your_password",
    "db_type": "mariadb",
    "encryption_key": "generated_key"
}
```

![Site Config Location](../assets/screenshots/site-config-location.png)
<!-- TODO: Capture terminal showing site_config.json file path -->

### common_site_config.json

Located at `~/frappe-bench/sites/common_site_config.json`:

```json
{
    "redis_cache": "redis://localhost:6379",
    "redis_queue": "redis://localhost:6379",
    "redis_socketio": "redis://localhost:6379",
    "socketio_port": 9000
}
```

---

## Verification Checklist

After installation, verify:

- [ ] MariaDB running: `sudo systemctl status mariadb`
- [ ] Redis running: `sudo systemctl status redis`
- [ ] Site accessible: `curl http://localhost:8000`
- [ ] Admin login works
- [ ] CRM app visible in apps list

![Frappe Desk Apps](../assets/screenshots/frappe-desk-apps.png)
<!-- TODO: Capture Frappe desk showing CRM app installed -->

---

## Next Steps

- [Single-Server Deploy](deploy-single-server.md)
- [Production Deploy](deploy-production.md)
- [SSL & Email Setup](ssl-email-setup.md)
