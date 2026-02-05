# Customer Management

Customers represent fully onboarded clients who have opened accounts with Eshin Broking. This guide covers viewing, managing, and tracking customer information.

---

## Purpose

The Customers module helps you:
- View converted customer details
- Track customer activity history
- Access linked leads and tickets
- Manage customer relationships

**Typical Users:** Sales Users, Support Users, Managers

---

## Customer vs Lead

| Aspect | Lead | Customer |
|--------|------|----------|
| Stage | Prospect | Converted |
| Account | Not opened | Active account |
| Client ID | May not have | Always has |
| Origin | Created manually | Converted from Lead |

---

## Viewing Customers

### Customer List

1. Click **Customers** in sidebar
2. View list with:
   - Customer name
   - Client ID
   - Mobile number
   - Last activity date

![Customer List](../assets/screenshots/customer-list.png)
<!-- UI File: frontend/src/pages/Customers.vue -->

### Search and Filter

- **Search** - Type name, mobile, or Client ID
- **Filter by date** - Use date range filter
- **Sort** - Click column headers

---

## Customer Details

Click a customer to view full profile:

### Information Tabs

| Tab | Contents |
|-----|----------|
| **Overview** | Contact info, Client ID, account status |
| **Activities** | All logged activities |
| **Tickets** | Support tickets for this customer |
| **Calls** | Call history |

### Key Fields

| Field | Description |
|-------|-------------|
| **Client ID** | Unique identifier in system |
| **Mobile** | Primary contact |
| **Alternative Mobile** | Secondary contact |
| **Email** | Email address |
| **Account Opened** | Date account was created |
| **Account Activated** | Date account went live |

![Customer Detail](../assets/screenshots/customer-detail.png)
<!-- UI File: frontend/src/pages/Customer.vue -->

---

## Customer Activities

### View Activity Timeline

All customer interactions are logged:

- Notes added
- Calls made/received
- WhatsApp messages
- Status changes
- Ticket updates

### Add Activity

1. Open customer profile
2. Click **+ Activity**
3. Select activity type
4. Add details and save

---

## Linked Records

### View Original Lead

If customer was converted from a lead:

1. Open customer profile
2. Click **View Lead** link
3. Original lead opens with full history

![Linked Leads Section](../assets/screenshots/customer-linked-leads.png)
<!-- TODO: Capture linked leads section in customer profile -->

### View Tickets

1. In customer profile, click **Tickets** tab
2. All related tickets displayed
3. Click any ticket to open

![Linked Tickets Section](../assets/screenshots/customer-linked-tickets.png)
<!-- TODO: Capture tickets tab showing linked support tickets -->

---

## Customer Search

Use the global search or dedicated search features:

### Quick Search

1. Press `Ctrl+K` (universal search)
2. Type customer name or Client ID
3. Click result to open

### Advanced Search

1. Go to Customers page
2. Click **Filters**
3. Add filter criteria:
   - Date range
   - Account status
   - Assigned user

---

## Personal Information Fields

Customers include personal details for KYC:

| Field | Description |
|-------|-------------|
| Date of Birth | Customer's birth date |
| Gender | Male/Female/Other |
| Marital Status | Single/Married/etc. |
| PAN Number | Tax ID (masked display) |
| Aadhar | ID number (masked display) |

> **Note:** Sensitive fields are masked for privacy. Full values visible only to authorized users.

---

## Date Tracking

Key dates tracked for each customer:

| Date | Description |
|------|-------------|
| Created | When lead was first created |
| Account Opened | When account became active |
| Account Activated | When account was fully activated |
| Last Activity | Most recent interaction |

---

## SOP: Reviewing Customer Profile

### Purpose
Complete review of customer relationship status.

### Steps

1. **Open Customer Profile**
   - Search by name or Client ID
   - Click to open

2. **Review Contact Info**
   - Verify mobile numbers current
   - Check email address

3. **Check Activity History**
   - Review recent communications
   - Note any pending issues

4. **Review Tickets**
   - Check for open tickets
   - Verify all resolved

5. **Update if Needed**
   - Edit contact information
   - Add notes for team

### Verification
- [ ] Contact info verified
- [ ] No pending tickets
- [ ] Recent activity logged

---

## Power User Tips

- **Client ID Search** - Fastest way to find a specific customer
- **Activity Date Filter** - Find customers with recent/no activity
- **Export** - Export customer list for reports
- **Quick Actions** - Call/WhatsApp directly from profile

---

## Related Guides

- [Leads](leads.md) - Lead to customer conversion
- [Tickets](tickets.md) - Create tickets for customers
- [Call Logs](call-logs.md) - View call history
