# Single-Server Deployment

Deploy Eshin CRM on a single server for small teams or testing.

---

## Prerequisites

- Completed [Installation](installation.md)
- Server accessible via domain or IP
- SSH access to server

---

## Deployment Steps

### 1. Configure Site for Production

```bash
cd ~/frappe-bench

# Set site to production
bench --site eshin.localhost set-config developer_mode 0

# Disable maintenance mode
bench --site eshin.localhost set-maintenance-mode off
```

### 2. Setup Production Configuration

```bash
# Generate production configuration
sudo bench setup production frappe

# This creates:
# - Supervisor configuration
# - Nginx configuration
# - Systemd services
```

### 3. Configure Nginx

The setup creates `/etc/nginx/conf.d/frappe-bench.conf`:

```nginx
upstream frappe-bench-frappe {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name eshin.localhost your-domain.com;
    
    root /home/frappe/frappe-bench/sites;
    
    location /assets {
        try_files $uri =404;
    }
    
    location / {
        proxy_pass http://frappe-bench-frappe;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Start Services

```bash
# Restart nginx
sudo systemctl restart nginx

# Restart supervisor
sudo systemctl restart supervisor

# Check status
sudo supervisorctl status
```

### 5. Verify Deployment

```bash
# Check all services running
sudo supervisorctl status all

# Expected output:
# frappe-bench-frappe-web          RUNNING
# frappe-bench-frappe-socketio     RUNNING
# frappe-bench-frappe-schedule     RUNNING
# frappe-bench-frappe-workers:*    RUNNING
```

---

## Verification Checklist

- [ ] Site loads in browser
- [ ] Login works
- [ ] CRM app accessible
- [ ] Real-time updates work (WebSocket)
- [ ] Background jobs running

---

## Rollback Steps

If issues occur:

```bash
# Stop production config
sudo bench setup production frappe --disable

# Revert to development mode
bench --site eshin.localhost set-config developer_mode 1

# Restart manually
cd ~/frappe-bench
bench start
```

---

## Next Steps

- [Production Deploy](deploy-production.md) - For hardened setup
- [SSL Setup](ssl-email-setup.md) - Enable HTTPS
