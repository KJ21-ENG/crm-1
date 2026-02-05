# Security Checklist

Security best practices for Eshin CRM production deployment.

---

## Critical Security Items

### Authentication
- [ ] Strong admin password (16+ characters)
- [ ] Disable default/guest accounts
- [ ] Enable multi-factor authentication (if available)
- [ ] Session timeout configured (default: 120 hours)

### Access Control
- [ ] Role permissions reviewed and minimized
- [ ] Module access restricted by role
- [ ] Sensitive data fields permission-protected

### Network Security
- [ ] HTTPS enabled (SSL certificate valid)
- [ ] HTTP redirects to HTTPS
- [ ] Firewall enabled (UFW/iptables)
- [ ] Only required ports open (22, 80, 443)
- [ ] Fail2ban installed and configured

### Database Security
- [ ] Database password is strong and unique
- [ ] Database not exposed to public network
- [ ] Database user has minimal required privileges
- [ ] Remote database access disabled

### Server Security
- [ ] SSH key authentication only (password auth disabled)
- [ ] Root login disabled via SSH
- [ ] Automatic security updates enabled
- [ ] Regular system updates scheduled

---

## User Management

### Password Policy

Enforce strong passwords:
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, special characters
- No dictionary words

### Role Assignment

| Role | Access Level | Assign To |
|------|--------------|-----------|
| Administrator | Full | IT Team only |
| System Manager | High | Department heads |
| Sales Manager | Medium | Sales management |
| Sales User | Limited | Sales staff |
| Support User | Limited | Support staff |

### User Audit

Regularly review:
- Active user list
- Last login times
- Inactive accounts (disable after 90 days)

---

## Data Protection

### Sensitive Fields

Masked fields in system:
- Mobile numbers (partial mask)
- PAN numbers
- Aadhar numbers
- Bank details

### Data Access Logging

Enable audit trail for:
- Login/logout events
- Data exports
- Permission changes

---

## Backup Security

- [ ] Backups encrypted
- [ ] Backups stored off-site
- [ ] Backup access restricted
- [ ] Backup restoration tested monthly

---

## Incident Response

### If Security Breach Detected

1. **Isolate**: Disconnect affected systems
2. **Preserve**: Save logs before they rotate
3. **Investigate**: Determine scope of breach
4. **Notify**: Inform stakeholders
5. **Remediate**: Fix vulnerability
6. **Document**: Record incident and response

### Contact Information

- Security Team: security@yourcompany.com
- Emergency: [Phone number]

---

## Regular Audits

| Audit | Frequency |
|-------|-----------|
| User access review | Monthly |
| Permission audit | Quarterly |
| Security scan | Monthly |
| Penetration test | Annually |
