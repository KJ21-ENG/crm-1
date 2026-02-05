# Production Hardened Deployment

Secure, production-ready deployment for Eshin CRM.

---

## Security Checklist Before Deployment

- [ ] Strong admin password set
- [ ] Database password rotated
- [ ] Firewall configured
- [ ] SSH keys only (no password auth)
- [ ] Automatic security updates enabled

---

## Production Configuration

### 1. Configure Firewall

```bash
# Install UFW
sudo apt install ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow required ports
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# Enable firewall
sudo ufw enable
```

### 2. Configure Fail2Ban

```bash
# Install fail2ban
sudo apt install fail2ban

# Create jail for nginx
sudo nano /etc/fail2ban/jail.local
```

```ini
[nginx-http-auth]
enabled = true

[nginx-botsearch]
enabled = true
```

```bash
sudo systemctl restart fail2ban
```

### 3. Production Site Config

Update `site_config.json`:

```json
{
    "db_name": "eshin_db",
    "db_password": "strong_random_password",
    "developer_mode": 0,
    "maintenance_mode": 0,
    "server_script_enabled": 1,
    "deny_multiple_sessions": 0,
    "allow_tests": 0
}
```

### 4. Worker Configuration

For production workloads, configure workers in Procfile:

```procfile
# Recommended for production
web: bench serve --port 8000
socketio: bench serve-socketio
schedule: bench schedule
worker_short: bench worker --queue short 1>> logs/worker.log 2>&1
worker_default: bench worker --queue default 1>> logs/worker.log 2>&1
worker_long: bench worker --queue long 1>> logs/worker.log 2>&1
```

### 5. Redis Configuration

For production, tune Redis:

```bash
sudo nano /etc/redis/redis.conf
```

```conf
# Memory management
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistence
appendonly yes
appendfsync everysec
```

### 6. MariaDB Optimization

```bash
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```

```ini
[mysqld]
# InnoDB settings for production
innodb_buffer_pool_size = 2G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT

# Query cache
query_cache_type = 1
query_cache_size = 64M

# Connections
max_connections = 150
```

---

## Supervisor Production Config

Create `/etc/supervisor/conf.d/frappe-bench.conf`:

```ini
[program:frappe-bench-web]
command=/home/frappe/frappe-bench/env/bin/gunicorn -b 127.0.0.1:8000 -w 4 frappe.app:application
directory=/home/frappe/frappe-bench/sites
user=frappe
autostart=true
autorestart=true
redirect_stderr=true
startsecs=1
stopwaitsecs=3

[program:frappe-bench-schedule]
command=/home/frappe/.local/bin/bench schedule
directory=/home/frappe/frappe-bench
user=frappe
autostart=true
autorestart=true

[program:frappe-bench-worker-default]
command=/home/frappe/.local/bin/bench worker --queue default
directory=/home/frappe/frappe-bench
user=frappe
autostart=true
autorestart=true
stopwaitsecs=360

[program:frappe-bench-worker-short]
command=/home/frappe/.local/bin/bench worker --queue short
directory=/home/frappe/frappe-bench
user=frappe
autostart=true
autorestart=true
stopwaitsecs=360

[program:frappe-bench-socketio]
command=/usr/bin/node /home/frappe/frappe-bench/apps/frappe/socketio.js
directory=/home/frappe/frappe-bench
user=frappe
autostart=true
autorestart=true
```

---

## Nginx Production Config

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;
limit_conn_zone $binary_remote_addr zone=addr:10m;

upstream frappe-bench-frappe {
    server 127.0.0.1:8000 fail_timeout=0;
}

upstream frappe-bench-socketio {
    server 127.0.0.1:9000 fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL (managed by certbot)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000" always;
    
    # Rate limiting
    limit_req zone=one burst=20 nodelay;
    limit_conn addr 10;
    
    root /home/frappe/frappe-bench/sites;
    
    location /assets {
        try_files $uri =404;
        expires 30d;
    }
    
    location /socket.io {
        proxy_pass http://frappe-bench-socketio;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location / {
        proxy_pass http://frappe-bench-frappe;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50m;
    }
}
```

---

## Monitoring Setup

### System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# View real-time stats
htop  # CPU/Memory
iotop # Disk I/O
nethogs # Network
```

### Log Rotation

Ensure logs don't fill disk:

```bash
sudo nano /etc/logrotate.d/frappe-bench
```

```
/home/frappe/frappe-bench/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
}
```

---

## Backup Configuration

Enable automatic backups:

```bash
# Add to crontab
crontab -e
```

```cron
# Daily backup at 2 AM
0 2 * * * cd /home/frappe/frappe-bench && bench --site eshin.localhost backup
```

---

## Verification Checklist

- [ ] HTTPS working (certificate valid)
- [ ] All services running
- [ ] Firewall active
- [ ] Fail2ban running
- [ ] Backups scheduled
- [ ] Monitoring in place
- [ ] Log rotation configured

---

## Rollback Steps

If deployment fails:

1. Stop services: `sudo supervisorctl stop all`
2. Check logs: `tail -f ~/frappe-bench/logs/*.log`
3. Fix issues
4. Restart: `sudo supervisorctl start all`

For complete rollback:
```bash
# Restore from backup
bench --site eshin.localhost restore ~/backups/latest.sql.gz
```

---

## Related Guides

- [Backup & Restore](backup-restore.md)
- [Security Checklist](security-checklist.md)
- [Upgrading & Patching](upgrading-patching.md)
