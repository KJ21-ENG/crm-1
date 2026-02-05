# Dashboard

The Dashboard provides at-a-glance analytics and quick access to your CRM data.

---

## Purpose

The Dashboard helps you:
- Monitor key performance metrics
- Track daily/weekly activity
- View team performance (managers)
- Quick-navigate to filtered data

**Typical Users:** All CRM users

---

## Dashboard Sections

### Personal Dashboard

| Widget | Data Shown |
|--------|------------|
| **Today's Tasks** | Tasks due today |
| **Leads Summary** | Lead counts by status |
| **Call Stats** | Today's call metrics |
| **Recent Activity** | Latest activities |

### Analytics Tab

| Metric | Description |
|--------|-------------|
| Lead Pipeline | Leads by status chart |
| Conversion Rate | Lead to customer rate |
| Call Volume | Calls over time |
| Account Status | Opened vs Activated |

![Dashboard](../assets/screenshots/dashboard.png)
<!-- UI File: frontend/src/pages/Dashboard.vue -->

![Dashboard KPI Cards](../assets/screenshots/dashboard-kpi-cards.png)
<!-- TODO: Capture KPI metric cards (leads count, calls, tasks) -->

![Dashboard Analytics Charts](../assets/screenshots/dashboard-charts.png)
<!-- TODO: Capture analytics charts section showing lead pipeline and conversion rates -->

---

## Navigation from Dashboard

### Click-through Navigation

Click any tile to view filtered data:

| Tile | Opens |
|------|-------|
| Today's Leads | Leads list filtered to today |
| Open Tickets | Tickets with status "Open" |
| Calls Today | Call logs for today |
| Overdue Tasks | Tasks past due date |

### Date Range

Select date range for analytics:
- Today
- This Week
- This Month
- Custom Range

![Dashboard Date Filters](../assets/screenshots/dashboard-filters.png)
<!-- TODO: Capture date range filter dropdown -->

---

## Analytics Drill-down

### Lead Analytics

Click lead status counts to see:
- All leads in that status
- Filtered by selected date range
- Quick actions available

### Call Analytics

Click call metrics to see:
- Call log list
- Filtered by type/status
- Export options

---

## Manager View

Managers see additional sections:

| Section | Data |
|---------|------|
| **Team Activity** | All team members' activity |
| **Assignment Requests** | Pending approvals |
| **Team Metrics** | Performance comparison |

---

## User Dashboard

The User Dashboard shows individual performance:

### Metrics Displayed

| Metric | Description |
|--------|-------------|
| My Leads | Leads assigned to you |
| My Tasks | Your task counts |
| My Calls | Your call activity |
| Conversion | Your conversion rate |

### Navigation

Click any metric to view details in respective module.

---

## Account Status Tiles

### Account Opened

Shows leads with accounts opened:
- Count of accounts opened
- Date range applied
- Click to see list

### Account Activated

Shows fully activated accounts:
- Activation count
- Conversion tracking
- Click for details

---

## Power User Tips

- **Customize View** - Drag widgets to reorder
- **Refresh** - Pull down to refresh data
- **Date Shortcuts** - Use keyboard shortcuts for dates
- **Pin Filters** - Save common filter combinations

---

## Related Guides

- [Leads](leads.md) - Lead management
- [Tasks](tasks.md) - Task management
- [Call Logs](call-logs.md) - Call tracking
