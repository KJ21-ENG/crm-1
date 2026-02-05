# SSL & Email Setup

Configure HTTPS and email for production.

---

## SSL Certificate Setup

### Using Certbot (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

### Certificate Renewal

Certbot creates auto-renewal. Verify:

```bash
# Check renewal timer
sudo systemctl status certbot.timer

# Test renewal
sudo certbot renew --dry-run
```

---

## Email (SMTP) Setup

### Configure Site

In Frappe, go to Setup → Email Domain or configure in `site_config.json`:

```json
{
    "mail_server": "smtp.gmail.com",
    "mail_port": 587,
    "use_tls": 1,
    "mail_login": "your-email@gmail.com",
    "mail_password": "app-specific-password"
}
```

![Email Domain Settings](../assets/screenshots/email-domain-settings.png)
<!-- TODO: Capture Frappe Setup > Email Domain configuration screen -->

### Common SMTP Providers

| Provider | Server | Port | TLS |
|----------|--------|------|-----|
| Gmail | smtp.gmail.com | 587 | Yes |
| Outlook | smtp.office365.com | 587 | Yes |
| SendGrid | smtp.sendgrid.net | 587 | Yes |

### Test Email

```bash
bench --site eshin.localhost sendmail recipient@email.com
```

---

## Verification

- [ ] HTTPS works (check padlock)
- [ ] HTTP redirects to HTTPS
- [ ] Test email sends successfully
- [ ] Certificate auto-renewal scheduled

![SSL Padlock Verification](../assets/screenshots/ssl-padlock.png)
<!-- TODO: Capture browser showing valid SSL padlock icon -->

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| SSL error | Check certificate path in nginx |
| Email not sending | Verify SMTP credentials |
| Certificate expired | Run `sudo certbot renew` |
