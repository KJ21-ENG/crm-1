# 🏢 Eshin Broking CRM System

## Overview

**Eshin Broking CRM** is a customized Customer Relationship Management system specifically designed for Eshin Broking's financial services operations. This system is based on Frappe CRM 2.0.0-dev (frozen version) and has been tailored for brokerage and financial services workflows.

## 🎯 Key Features

### Financial Services Focused
- **Prospect Management**: Complete prospect-to-client journey
- **KYC/AML Compliance**: Built-in compliance workflows
- **Portfolio Tracking**: Client portfolio and investment tracking
- **Regulatory Reporting**: Automated compliance reporting
- **Risk Assessment**: Client risk profiling and monitoring

### Customized Terminology
- **Prospects** (instead of Leads): Financial prospects tracking
- **Relationship Managers** (instead of Lead Owners): Dedicated client managers
- **Investment Categories** (instead of Industries): Financial product focus
- **Acquisition Channels** (instead of Sources): Client acquisition tracking
- **Net Worth/AUM** (instead of Annual Revenue): Financial metrics

## 🚀 Quick Start

### Development Environment
```bash
# Start all services
./start_eshin_crm_dev.sh

# Check status
./status_eshin_crm_dev.sh

# Stop services
./stop_eshin_crm_dev.sh
```

### Access URLs
- **Development**: http://localhost:8080
- **Production**: http://127.0.0.1:8000/crm
- **Admin Panel**: http://127.0.0.1:8000

### Login Credentials
- **Username**: Administrator
- **Password**: admin

## 🏗️ Architecture

### Backend
- **Framework**: Frappe Framework (Independent)
- **Database**: MariaDB
- **Cache**: Redis
- **Queue**: Redis Queue

### Frontend
- **Framework**: Vue.js 3
- **UI Library**: Frappe UI
- **Build Tool**: Vite
- **Hot Reload**: Development mode

## 📊 Customizations

### Eshin Broking Specific Features
1. **Prospect Management**: Tailored for financial prospects
2. **Compliance Module**: KYC/AML workflows
3. **Portfolio Tracking**: Investment portfolio management
4. **Risk Assessment**: Client risk profiling
5. **Regulatory Reporting**: Automated compliance reports

### Custom DocTypes
- **CRM Prospect** (customized from CRM Lead)
- **CRM Client Account** (customized from CRM Deal)
- **CRM Portfolio** (new for investment tracking)
- **CRM Compliance Record** (new for regulatory compliance)

## 🔧 Development

### Project Structure
```
eshin-broking-crm-system/
├── crm/                    # Core CRM application
├── frontend/               # Vue.js frontend
├── scripts/               # Development scripts  
├── deployment/            # Cloud deployment configs
└── customizations/        # Eshin-specific customizations
```

### Making Changes
1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and test
3. Commit: `git commit -m "feat: description"`
4. Push: `git push origin feature/new-feature`
5. Create pull request for review

## 🌐 Deployment

### Production Environment
- **URL**: https://eshin-crm.com
- **Hosting**: Cloud (AWS/DigitalOcean/Frappe Cloud)
- **SSL**: Automated certificate management
- **Backups**: Daily automated backups
- **Monitoring**: System health monitoring

### Deployment Process
```bash
# Deploy to production
git checkout main
git pull origin main
./deploy_production.sh
```

## 📞 Support

### Development Team
- **Lead Developer**: [Your Name]
- **Email**: dev@yourcompany.com
- **Phone**: [Your Phone]

### Eshin Broking Team
- **Primary Contact**: [Client Contact]
- **Email**: tech@eshinbroking.com

## 📝 License

**Proprietary License**
This software is exclusively licensed to Eshin Broking. All rights reserved.
No part of this software may be reproduced, distributed, or transmitted without explicit written permission.

## 🔄 Version History

### v1.0.0 (Current)
- Initial release based on Frappe CRM 2.0.0-dev
- Eshin Broking customizations
- Financial services workflows
- Compliance module
- Independent repository setup

---

**© 2024 Eshin Broking. All rights reserved.**
