# 21. Roles and Permissions
Status: completed
## 1) What this module is
Roles and Permissions controls who can see, edit, and manage information in the CRM. It helps protect sensitive data and keeps work aligned with office policy by ensuring team members only access what they need.

**Important: The Two-Layer Permission System**
In this CRM, access is determined by a strict two-layer check:
1. **Layer 1 (Role Level)**: Does the user’s assigned role allow them to read or write a particular type of document (like Leads or Tickets) in general?
2. **Layer 2 (Assignment Level)**: Even if their role allows read/write access to Tickets generally, is the user *actually assigned* to that specific Ticket? 
   - *Example:* If a user's role grants them read/write permissions for Tickets, but they have not been assigned to a ticket or they are not the owner of a particular ticket, they will **only be able to read** the details of that ticket. They will not be able to make any changes.

## 2) What staff can do here
- Create and manage system roles for different team positions.
- Adjust "Desk Access" and "Two Factor" authentication requirements per role.
- Configure granular action permissions (create, read, write, delete) for every document type.
- Support compliance by following least-access rules.

## 3) How to use (step-by-step)
1. Open the user dropdown menu in the top-left sidebar (under 'CRM').
2. Select **Settings** to open the Settings modal.
3. Click on the **Roles** tab on the left sidebar.
![Screenshot](/docs/screenshots/21-roles-and-permissions/01-roles-and-permissions.png)
4. To create a new role, type a name in the "New role name" field and click **+ Add**.
5. To edit an existing role's permissions, click the **Pencil (Edit)** icon next to that role.
6. Check or uncheck the specific allowed actions for each document type, keeping the Two-Layer Permission System in mind.
7. Click **Save** to confirm the access updates.

## 4) Important buttons/options
- **Search roles**: Quickly find a specific role by typing its name.
- **Desk Access toggle**: Determines if the role is permitted to log into the main CRM interface.
- **Edit (Pencil icon)**: Opens the detailed permission matrix for that specific role.
- **Bulk Actions**: Allows you to apply settings across multiple selected roles simultaneously.
- **Disabled toggle**: Temporarily suspends a role without deleting its configured permissions.

## 5) Daily best practices
- Give the minimum role access needed for each job function.
- Remember the Two-Layer rule: broadly granting "Write" access doesn't break assignment ownership.
- Apply the Two-Factor authentication requirement to roles with high-level access like Administrators.
- Review high-access roles on a regular schedule.

## 6) Common mistakes to avoid
- Assuming that a user can edit any ticket just because their role has "Write" access (forgetting they must also be assigned to it).
- Disabling "Desk Access" for users who genuinely need to log into the dashboard.
- Giving broad access “temporarily” and forgetting to remove it later.
- Deleting a role instead of using the "Disabled" toggle when you might need its configuration again.
