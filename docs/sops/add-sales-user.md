# SOP: Add Sales User

| Field | Value |
|-------|-------|
| **Purpose** | Create new user account with sales role and permissions |
| **Scope** | User creation, role assignment, module access |
| **Role** | System Administrator, Manager |
| **Frequency** | As needed |

---

## Prerequisites

- [ ] Admin or Manager access to CRM
- [ ] New user's email address
- [ ] Assigned manager/supervisor information
- [ ] Initial role determination (Sales User, Support User)

---

## Procedure

### Step 1: Access User Management

1. Login to CRM as Administrator
2. Click **Settings** in sidebar
3. Navigate to **Users**

![User List](../assets/screenshots/user-list.png)
<!-- TODO: Capture user list showing existing users -->

---

### Step 2: Create New User

1. Click **+ Add User**
2. Fill in user details:

| Field | Value |
|-------|-------|
| Email | user@company.com |
| First Name | [User's first name] |
| Last Name | [User's last name] |
| Send Welcome Email | ✅ Checked |

![Add User Modal](../assets/screenshots/add-user-modal.png)
<!-- TODO: Capture new user creation form -->

---

### Step 3: Assign Roles

Select appropriate roles:

| Role | Use Case |
|------|----------|
| **Sales User** | Lead and customer management |
| **Support User** | Ticket management |
| **Sales Manager** | Team oversight, reports |

Enable checkbox for selected role.

![Role Checkboxes](../assets/screenshots/role-checkboxes.png)
<!-- TODO: Capture role assignment checkboxes -->

---

### Step 4: Configure Module Access

In CRM Role Module Permission (if applicable):

1. Go to Settings → Permissions
2. Enable modules for the role:
   - Leads ✅
   - Tickets ✅ (if support role)
   - Customers ✅
   - Call Logs ✅
   - Tasks ✅
   - Dashboard ✅

![Module Permissions](../assets/screenshots/module-permissions.png)
<!-- TODO: Capture module access checkboxes -->

---

### Step 5: Save User

1. Click **Save**
2. Welcome email sent automatically

---

### Step 6: Verify User Setup

1. Ask user to check email for welcome/password reset link
2. Have user login and verify access
3. Verify user can see assigned modules

---

## Verification Checklist

- [ ] User can login
- [ ] Correct role assigned
- [ ] Can access Leads module
- [ ] Can create new lead
- [ ] Cannot access Admin settings (unless Manager)
- [ ] Appears in assignable users list

---

## Rollback / Undo

To remove user:

1. Go to Settings → Users
2. Find the user
3. Click **Disable** or **Delete**

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Welcome email not received | Check spam, resend from User form |
| Can't see modules | Check Role Module Permission |
| Can't be assigned leads | Verify role in assignable users |
| Login fails | Reset password from User form |

---

## Related Documents

- [Resolve Permission Issues](resolve-permission-issues.md)
- [Security Checklist](../admin-guide/security-checklist.md)
