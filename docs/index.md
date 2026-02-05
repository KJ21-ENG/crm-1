# Eshin Broking CRM

> **A customized Customer Relationship Management system for financial services operations**

Eshin Broking CRM is built on Frappe Framework, providing a comprehensive solution for managing leads, tickets, customers, call logs, and tasks. This system includes specialized features for the brokerage industry including WhatsApp integration, mobile call log synchronization, role-based permissions, and advanced analytics.

---

## Quick Start (5 Minutes)

Get productive with Eshin CRM in just 5 steps:

### Step 1: Login to the System

Navigate to your CRM URL and log in with your credentials.

```
URL: https://eshin.in/crm
```

![Login Screen](assets/screenshots/login.png)
<!-- UI File: frontend/src/pages/Login.vue -->

**Expected Result:** Dashboard appears showing your assigned leads and tasks.

---

### Step 2: Create Your First Lead

1. Click **Leads** in the sidebar
2. Click the **+ Create** button
3. Fill in required fields:
   - First Name
   - Mobile Number
   - Lead Source
4. Click **Save**

![Create Lead](assets/screenshots/leads-create.png)
<!-- UI File: frontend/src/components/Modals/LeadModal.vue -->

**Expected Result:** Lead appears in your leads list with status "New".

---

### Step 3: Log a Call Activity

1. Open the lead you just created
2. Click the **Call** icon or **+ Activity**
3. Select call type and add notes
4. Save the activity

![Log Activity](assets/screenshots/activity-log.png)
<!-- UI File: frontend/src/components/Activities/ -->

**Expected Result:** Call appears in the lead's activity timeline.

---

### Step 4: Create a Follow-up Task

1. From the lead detail page, click **+ Task**
2. Set task title: "Follow-up call"
3. Set due date and assign to yourself
4. Save

![Create Task](assets/screenshots/task-create.png)
<!-- UI File: frontend/src/components/Modals/TaskModal.vue -->

**Expected Result:** Task appears in your Tasks list and lead's activity feed.

---

### Step 5: View Your Dashboard

1. Click **Dashboard** in sidebar
2. Review your:
   - Today's tasks
   - Call statistics
   - Lead pipeline
   - Performance metrics

![Dashboard](assets/screenshots/dashboard.png)
<!-- UI File: frontend/src/pages/Dashboard.vue -->

**Expected Result:** See consolidated view of your CRM activities.

---

## Documentation Roadmap

| Guide | Description | Audience |
|-------|-------------|----------|
| [User Guide](user-guide/overview.md) | Daily CRM operations | Sales Users, Managers |
| [Admin Guide](admin-guide/installation.md) | System setup & maintenance | System Administrators |
| [Developer Guide](developer-guide/repo-structure.md) | Extending the CRM | Developers |
| [SOPs](sops/onboard-new-customer.md) | Step-by-step procedures | All Roles |
| [Architecture](architecture.md) | System design | Technical Teams |
| [Troubleshooting](troubleshooting.md) | Problem resolution | All Roles |

---

## Key Features

- **Lead Management** - Track prospects through conversion funnel
- **Ticket System** - Customer support with multi-assignee workflow
- **Call Logging** - Automatic sync from mobile devices
- **Task Management** - Due dates, assignments, notifications
- **WhatsApp Integration** - Customer communication via WhatsApp
- **Role-based Access** - Granular permissions by module
- **Analytics Dashboard** - Real-time performance metrics
- **Assignment Requests** - Approval workflow for lead/ticket transfers

---

## Support

- **Documentation Issues**: Create a ticket in the CRM
- **Technical Support**: Contact your system administrator
- **Development**: See [Developer Guide](developer-guide/repo-structure.md)
