# 08. Requests
Status: completed
## 1) What this module is
Requests is used for assignment approvals in CRM. It is a **two-sided process**:
- **User side**: Any employee can request that a specific Lead or Ticket be assigned to a particular employee. If the selected employee's role is not same as required role for the Lead/Ticket, the request goes to admin for approval.
- **Admin side**: Admins receive the request, review it, and either Approve or Decline it.

This keeps assignment changes controlled while still letting any team member suggest the right person for the job.

## 2) What staff can do here

### As a regular user (requester)
- Open a Lead or Ticket and click the **Assign** button
- Choose **"Request specific employee (admin approval)"** assignment type
- Select the employee they want to assign
- Provide a reason/note explaining why this employee should handle it
- Submit the request (it goes to admins for approval)
- Receive a notification when the request is approved or rejected

### As an admin (approver)
- Open **Requests** from the CRM menu to see all pending requests
- Filter requests by status (Pending, Approved, Rejected)
- Review the request details (who requested, which employee, which Lead/Ticket, reason)
- **Approve** the request to confirm the assignment
- **Decline** the request with a reason so the requester knows what to fix
- Open the related Lead or Ticket directly from the request

## 3) How to use (step-by-step)

### A) User side – Sending an assignment request
1. Open the **Lead** or **Ticket** you want to reassign.
![Screenshot](/docs/screenshots/08-requests/01-lead-detail-assign-button.png)
2. Click the **Assign** button on the Lead/Ticket detail page.
![Screenshot](/docs/screenshots/08-requests/02-assignment-modal.png)
3. In the Assignment modal, select **"Request specific employee (admin approval)"**.
![Screenshot](/docs/screenshots/08-requests/03-request-employee-option.png)
4. Choose the employee you want from the dropdown list.
5. Enter a **reason** explaining why this person should handle this Lead/Ticket.
![Screenshot](/docs/screenshots/08-requests/04-request-form-fields.png)
6. Click **Request** to submit.
7. You will see a confirmation: "Request submitted to admins for approval."
8. Wait for admin response – you will receive a **notification** when the request is approved or declined.

### B) Admin side – Reviewing and acting on requests
1. Open **Requests** from the CRM sidebar menu.
![Screenshot](/docs/screenshots/08-requests/05-requests-list-admin.png)
2. Use filters to see **Pending** requests that need action.
3. Review the request: check who requested it, which employee is being suggested, which Lead/Ticket it concerns, and the reason given.
4. Click **Approve** to confirm the assignment – the employee will be assigned automatically and both parties will be notified.
5. Or click **Decline** to reject – add a clear reason so the requester knows what to do next.
6. If needed, click the linked record name to jump directly to the related Lead or Ticket for more context.

## 4) Important buttons/options

### User side (on Lead/Ticket detail page)
- **Assign button**: Opens the assignment modal
- **"Request specific employee" option**: Switches to the request flow (visible to non-admin users)
- **Employee dropdown**: Lists all available employees to pick from
- **Reason field**: Required text note for the admin explaining the request
- **Request button**: Submits the request for admin approval

### Admin side (Requests list page)
- **Requests menu item**: Opens the full list of assignment requests
- **Pending filter**: Shows items waiting for action
- **Approve**: Accept request and automatically apply the assignment
- **Decline**: Reject request (add a reason)
- **Open Linked Record**: Jump to the related Lead/Ticket
- **Search/Filters**: Narrow requests by person, status, or date

## 5) Daily best practices
- **Users**: Always provide a clear, specific reason when requesting an assignment – vague reasons slow down approval
- **Users**: Only request reassignment when there is a genuine business reason
- **Admins**: Review pending requests at least twice a day to avoid delays
- **Admins**: Approve or decline quickly so work does not stall
- **Admins**: Always add a reason when declining so the requester can take corrective action
- **Admins**: Check the linked Lead/Ticket for context before making a decision

## 6) Common mistakes to avoid
- **Users**: Submitting requests without a reason (the system requires one for non-CRM-User employees)
- **Users**: Requesting an employee who is already assigned to the same Lead/Ticket
- **Users**: Not checking if the employee is the right fit before requesting
- **Admins**: Leaving requests in Pending status too long, causing work delays
- **Admins**: Approving without reviewing the workload or context of the target employee
- **Admins**: Declining without a reason, which leads to repeated requests
- **Admins**: Taking action on the wrong request due to not using filters
