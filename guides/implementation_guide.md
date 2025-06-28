# CRM Implementation Guide - Step by Step

## STEP 1: SETUP DEVELOPMENT ENVIRONMENT

### 1.1 Create Development Instance
```bash
# Create a development site for testing
bench new-site client-crm-dev.local --install-app crm
bench use client-crm-dev.local

# Enable developer mode
bench set-config developer_mode 1 client-crm-dev.local
bench restart
```

### 1.2 Create Custom App (for client-specific customizations)
```bash
# Create custom app for your client
bench new-app client_customizations
bench install-app client_customizations
```

## STEP 2: MASTER DATA SETUP

### 2.1 Configure Lead/Deal Statuses
Go to: **Settings > CRM Settings > Lead Status**
```
- Delete unwanted statuses
- Modify existing status names
- Add new statuses with proper colors
- Set correct position/order
```

### 2.2 Configure Industries, Territories, Lead Sources
```
- Remove irrelevant options
- Add client-specific options
- Set default values
```

## STEP 3: FIELD CUSTOMIZATIONS

### 3.1 Add Custom Fields (via UI - Easier Method)
1. Go to **Customize Form**
2. Select DocType (CRM Lead / CRM Deal)
3. Add new fields:
   - Click "Add Row" in Fields table
   - Set fieldname, label, fieldtype
   - Set options for Select/Link fields
   - Save

**Example: Adding Budget Range to CRM Lead**
```
Fieldname: budget_range
Label: Budget Range  
Fieldtype: Select
Options: 
Under $10K
$10K - $50K  
$50K - $100K
Above $100K
```

### 3.2 Hide Unwanted Fields
1. Go to **Customize Form**
2. Find the field to hide
3. Check "Hidden" checkbox
4. Save

### 3.3 Change Field Labels
1. Go to **Customize Form** 
2. Find the field
3. Change "Label" value
4. Save

## STEP 4: LAYOUT CUSTOMIZATIONS

### 4.1 Modify Quick Entry Layouts
```python
# Access via: http://your-site:8000/app/crm-fields-layout
# Find: "CRM Lead-Quick Entry"
# Edit the JSON layout to:
# - Rearrange fields
# - Hide sections
# - Add new custom fields
```

**Example JSON modification:**
```json
[
  {
    "name": "contact_section", 
    "columns": [
      {
        "name": "column_1",
        "fields": ["first_name", "email", "budget_range"]
      },
      {
        "name": "column_2", 
        "fields": ["last_name", "mobile_no", "lead_source"]
      }
    ]
  }
]
```

### 4.2 Modify Side Panel Layouts
Similar process for "CRM Lead-Side Panel" and "CRM Deal-Side Panel"

## STEP 5: REMOVE UNWANTED FEATURES

### 5.1 Hide Menu Items (For Client Users)
Create custom role and restrict access:

1. **Create Client Role**
```
Go to: Users and Permissions > Role
Create: "Client Sales User"
```

2. **Set Permissions**
```
DocType Permissions:
- CRM Lead: Read, Write, Create (NO Delete, Import, Export)
- CRM Deal: Read, Write, Create (NO Delete, Import, Export)  
- Contact: Read, Write, Create
- CRM Organization: Read, Write, Create

Hide from Role:
- CRM Fields Layout
- CRM Form Script  
- CRM Global Settings
- System Settings
```

### 5.2 Custom Home Page (Remove unwanted sections)
```python
# In your custom app, create custom workspace
# Copy frappe-crm workspace and modify
```

## STEP 6: AUTOMATION & WORKFLOWS

### 6.1 Auto-Assignment Rules
```python
# Create custom script in CRM Lead doctype
# File: client_customizations/overrides/crm_lead.py

def autoassign_lead(doc, method):
    if doc.territory == "North":
        doc.lead_owner = "north.sales@client.com"
    elif doc.territory == "South":
        doc.lead_owner = "south.sales@client.com"
```

### 6.2 Email Notifications
Set up in **Settings > Email > Notification**

## STEP 7: DATA MIGRATION

### 7.1 Prepare Data Templates
Download standard import templates and modify:
```
- CRM Lead template
- Contact template  
- CRM Organization template
```

### 7.2 Data Import Process
1. Clean and validate client data
2. Map to CRM fields
3. Import in stages (Organizations → Contacts → Leads → Deals)

## STEP 8: CLIENT-SPECIFIC BRANDING

### 8.1 Logo and Branding
```
- Upload logo via Website > Website Settings
- Customize colors in custom CSS
- Set website title and favicon
```

### 8.2 Custom CSS (if needed)
```css
/* Add in Website Settings > Custom CSS */
:root {
  --primary-color: #your-brand-color;
}
```

## STEP 9: USER SETUP

### 9.1 Create User Roles
```
1. Client Admin (full access except system settings)
2. Sales Manager (team access + reports)
3. Sales Representative (own records + assigned records)
4. Read Only User (reports only)
```

### 9.2 Create Users
- Import users via User template
- Assign appropriate roles
- Set territories/permissions

## STEP 10: TESTING

### 10.1 Test All Workflows
- Lead creation and conversion
- Deal management
- Contact/Organization linking
- Email notifications
- Data import/export
- User permissions

### 10.2 Performance Testing
- Test with realistic data volume
- Check page load times
- Verify mobile responsiveness

## STEP 11: PRODUCTION DEPLOYMENT

### 11.1 Production Setup
```bash
# Method 1: Frappe Cloud (Recommended)
# - Sign up at frappecloud.com
# - Deploy CRM app
# - Apply your customizations

# Method 2: Self-hosted
# - Setup production server
# - Install frappe-bench
# - Deploy with proper SSL/security
```

### 11.2 Data Migration to Production
1. Export all customizations from dev
2. Import to production
3. Migrate client data
4. Test everything again

## STEP 12: CLIENT HANDOVER

### 12.1 Admin Training Documentation
Create docs covering:
- User management
- Basic settings changes
- Data import/export  
- Report generation
- Basic troubleshooting

### 12.2 User Training
- Sales process training
- System navigation
- Mobile app usage
- Best practices

### 12.3 Support Setup
- Define support channels
- Create escalation process
- Set SLA for issues
- Provide emergency contacts

## POST-DEPLOYMENT MONITORING

### Month 1: Close Monitoring
- Daily check for issues
- User adoption tracking
- Performance monitoring
- Quick fixes as needed

### Month 2-3: Optimization
- Analyze usage patterns
- Optimize slow queries
- Additional customizations based on feedback
- Advanced training sessions

### Ongoing: Maintenance
- Regular backups
- System updates
- Performance optimization
- Feature enhancements