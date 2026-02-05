# API Reference

Whitelisted server-side methods available for API calls.

---

## Authentication

All API calls require authentication via:
- Session cookie (browser)
- API key/secret (programmatic access)

### Login

```bash
curl -X POST https://your-site.com/api/method/frappe.auth.login \
  -H "Content-Type: application/json" \
  -d '{"usr": "username", "pwd": "password"}'
```

---

## Lead APIs

### Get Leads

```python
# crm/api/doc.py
@frappe.whitelist()
def get_list(doctype, filters=None, fields=None, ...)
```

**Endpoint:** `POST /api/method/crm.api.doc.get_list`

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| doctype | string | Yes | "CRM Lead" |
| filters | object | No | Filter criteria |
| fields | array | No | Fields to return |
| page_length | int | No | Results per page |

**Example:**
```bash
curl -X POST https://your-site.com/api/method/crm.api.doc.get_list \
  -H "Cookie: sid=your-session-id" \
  -d '{
    "doctype": "CRM Lead",
    "filters": {"status": "New"},
    "fields": ["name", "first_name", "mobile_no"],
    "page_length": 20
  }'
```

---

### Get Lead Detail

```python
# crm/api/doc.py
@frappe.whitelist()
def get_doc(doctype, name)
```

**Endpoint:** `POST /api/method/crm.api.doc.get_doc`

**Parameters:**
| Name | Type | Required |
|------|------|----------|
| doctype | string | Yes |
| name | string | Yes |

---

### Create Lead

```python
# crm/api/lead_operations.py
@frappe.whitelist()
def create_lead(lead_data)
```

**Endpoint:** `POST /api/method/crm.api.lead_operations.create_lead`

---

## Ticket APIs

### Get Tickets

```python
# crm/api/ticket.py
@frappe.whitelist()
def get_tickets(filters=None, ...)
```

**Endpoint:** `POST /api/method/crm.api.ticket.get_tickets`

---

### Create Ticket

```python
# crm/api/ticket.py
@frappe.whitelist()
def create_ticket(ticket_data)
```

**Endpoint:** `POST /api/method/crm.api.ticket.create_ticket`

---

## Call Log APIs

### Sync Call Logs (Mobile)

```python
# crm/api/mobile_sync.py
@frappe.whitelist()
def sync_call_logs(call_logs)
```

**Endpoint:** `POST /api/method/crm.api.mobile_sync.sync_call_logs`

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| call_logs | array | Array of call log objects |

**Call Log Object:**
```json
{
  "device_call_id": "unique_id",
  "from_number": "+919876543210",
  "to_number": "+919876543211",
  "call_type": "Outgoing",
  "duration": 120,
  "start_time": "2026-02-02 10:00:00"
}
```

---

### Get User Call Logs

```python
# crm/api/mobile_sync.py
@frappe.whitelist()
def get_user_call_logs(page=1, page_size=20)
```

**Endpoint:** `POST /api/method/crm.api.mobile_sync.get_user_call_logs`

---

## Dashboard APIs

### Get Dashboard Data

```python
# crm/api/dashboard.py
@frappe.whitelist()
def get_dashboard_data(user=None, date_range=None)
```

**Endpoint:** `POST /api/method/crm.api.dashboard.get_dashboard_data`

---

### Get Lead Analytics

```python
# crm/api/dashboard.py
@frappe.whitelist()
def get_lead_analytics(filters=None)
```

---

## Search APIs

### Universal Search

```python
# crm/api/universal_search.py
@frappe.whitelist()
def search(query, doctypes=None, limit=10)
```

**Endpoint:** `POST /api/method/crm.api.universal_search.search`

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| query | string | Search term |
| doctypes | array | Optional: limit to specific doctypes |
| limit | int | Max results |

---

## Assignment APIs

### Create Assignment Request

```python
# crm/api/assignment_requests.py
@frappe.whitelist()
def create_assignment_request(doctype, docname, to_user, reason)
```

**Endpoint:** `POST /api/method/crm.api.assignment_requests.create_assignment_request`

---

### Approve/Reject Request

```python
# crm/api/assignment_requests.py
@frappe.whitelist()
def process_assignment_request(request_name, action, comment=None)
```

**Parameters:**
| Name | Type | Values |
|------|------|--------|
| action | string | "approve" or "reject" |

---

## WhatsApp APIs

### Send WhatsApp Message

```python
# crm/api/whatsapp_support.py
@frappe.whitelist()
def send_whatsapp_message(to_number, message, ...)
```

---

### Get WhatsApp Session Status

```python
# crm/api/whatsapp_setup.py
@frappe.whitelist()
def get_session_status()
```

---

## User APIs

### Get Current User

```python
# crm/api/user.py
@frappe.whitelist()
def get_current_user()
```

---

### Get Assignable Users

```python
# crm/api/role_assignment.py
@frappe.whitelist()
def get_assignable_users(doctype)
```

---

## Settings APIs

### Get CRM Settings

```python
# crm/api/settings.py
@frappe.whitelist()
def get_crm_settings()
```

---

### Trigger Manual Backup

```python
# crm/api/settings.py
@frappe.whitelist()
def trigger_backup()
```

---

## Error Responses

All APIs return standardized error format:

```json
{
  "exc_type": "ValidationError",
  "exception": "frappe.exceptions.ValidationError",
  "exc": "Error message details",
  "_server_messages": "[\"Error description\"]"
}
```

---

## Rate Limiting

Production environments should implement rate limiting at nginx level.
