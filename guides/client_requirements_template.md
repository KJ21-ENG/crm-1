# CRM Client Requirements Analysis Template

## 1. BUSINESS PROCESS MAPPING

### Lead Management Process
- [ ] How do leads come in? (Website forms, calls, referrals, etc.)
- [ ] Who handles leads? (Sales team structure)
- [ ] What information is captured for leads?
- [ ] Lead qualification criteria?
- [ ] Lead assignment rules?

### Deal Management Process
- [ ] Deal stages/pipeline (map to CRM statuses)
- [ ] Deal approval process
- [ ] Team collaboration requirements
- [ ] Reporting needs for deals

### Contact & Organization Management
- [ ] Types of contacts (prospects, customers, partners)
- [ ] Organization hierarchy needs
- [ ] Contact data requirements

## 2. FIELD REQUIREMENTS

### Required New Fields
```
Example:
- Lead Source: Dropdown (Website, Referral, Cold Call, Social Media)
- Budget Range: Currency field
- Decision Timeline: Date field
- Pain Points: Long text field
```

### Fields to Hide/Remove
```
Example:
- Annual Revenue (if not relevant)
- WhatsApp number (if not used)
- Industry (if single industry client)
```

### Modified Field Labels
```
Example:
- "Lead Owner" → "Sales Representative" 
- "Organization" → "Company"
```

## 3. WORKFLOW CUSTOMIZATIONS

### Status Customizations
**Lead Statuses:**
- [ ] Current: New, Contacted, Nurture, Qualified, Unqualified, Junk
- [ ] Client Needs: [List custom statuses]

**Deal Statuses:**
- [ ] Current: Qualification, Demo/Making, Proposal/Quotation, Negotiation, Ready to Close, Won, Lost
- [ ] Client Needs: [List custom statuses]

### Automation Requirements
- [ ] Auto-assignment rules
- [ ] Email notifications
- [ ] Follow-up reminders
- [ ] SLA requirements

## 4. INTEGRATION REQUIREMENTS

- [ ] Email integration (Gmail, Outlook, etc.)
- [ ] Phone system integration
- [ ] WhatsApp integration
- [ ] Website form integration
- [ ] Existing CRM data migration
- [ ] Other software integrations

## 5. REPORTING REQUIREMENTS

- [ ] Sales pipeline reports
- [ ] Lead conversion reports
- [ ] Team performance reports
- [ ] Custom reports needed

## 6. USER ACCESS & SECURITY

### User Roles & Permissions
- [ ] Sales Representatives
- [ ] Sales Managers  
- [ ] Administrators
- [ ] Read-only users

### Data Access Rules
- [ ] Territory-based access
- [ ] Team-based access
- [ ] Manager override access

## 7. DEPLOYMENT PREFERENCES

- [ ] Cloud hosting (Frappe Cloud)
- [ ] Self-hosted on client infrastructure
- [ ] On-premise installation
- [ ] Domain requirements
- [ ] SSL certificate needs
- [ ] Backup requirements

## 8. TRAINING & SUPPORT

- [ ] Admin training needs
- [ ] End-user training needs
- [ ] Documentation requirements
- [ ] Ongoing support expectations