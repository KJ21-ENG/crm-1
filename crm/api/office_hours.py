import json
import frappe
from frappe import _


def _to_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return default


def _parse_json(value, default=None):
    if value is None:
        return default
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return default


@frappe.whitelist()
def get_settings():
    """Return a concise view of Office Hours settings for the CRM UI."""
    doc = frappe.get_single("FCRM Settings")
    office_hours = []
    for row in (doc.get("office_hours") or []):
        office_hours.append({
            "workday": row.workday,
            "start_time": str(row.start_time) if row.start_time else None,
            "end_time": str(row.end_time) if row.end_time else None,
        })
    return {
        "enforce_office_hours": int(doc.enforce_office_hours or 0),
        "enforce_on_manual_assignment": int(doc.enforce_on_manual_assignment or 0),
        "holiday_list": doc.holiday_list or "",
        "office_hours": office_hours,
    }


@frappe.whitelist()
def set_settings(enforce_office_hours=None, enforce_on_manual_assignment=None, holiday_list=None, office_hours=None):
    """Update FCRM Settings fields and office hours child table.

    Args can be primitives or JSON strings. `office_hours` is list of {workday, start_time, end_time}.
    """
    doc = frappe.get_single("FCRM Settings")

    if enforce_office_hours is not None:
        doc.enforce_office_hours = 1 if _to_bool(enforce_office_hours) else 0

    if enforce_on_manual_assignment is not None:
        doc.enforce_on_manual_assignment = 1 if _to_bool(enforce_on_manual_assignment) else 0

    if holiday_list is not None:
        doc.holiday_list = holiday_list or None

    hours = _parse_json(office_hours, default=None)
    if hours is not None:
        # Reset and repopulate
        doc.set("office_hours", [])
        for item in hours:
            workday = (item or {}).get("workday")
            start_time = (item or {}).get("start_time")
            end_time = (item or {}).get("end_time")
            if not workday or not start_time or not end_time:
                # Skip incomplete rows
                continue
            doc.append("office_hours", {
                "workday": workday,
                "start_time": start_time,
                "end_time": end_time,
            })

    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True}


@frappe.whitelist()
def seed_default_hours():
    """Seed Mon–Fri 10:00–18:00 and Sat 10:00–15:00 into FCRM Settings."""
    doc = frappe.get_single("FCRM Settings")
    doc.set("office_hours", [])
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        doc.append("office_hours", {"workday": day, "start_time": "10:00:00", "end_time": "18:00:00"})
    doc.append("office_hours", {"workday": "Saturday", "start_time": "10:00:00", "end_time": "15:00:00"})
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True}


@frappe.whitelist()
def list_holiday_lists(search=None, start=0, page_length=50):
    filters = {}
    if search:
        filters["name"] = ["like", f"%{search}%"]
    rows = frappe.get_all(
        "CRM Holiday List",
        filters=filters,
        fields=["name", "from_date", "to_date", "total_holidays"],
        start=int(start or 0),
        page_length=int(page_length or 50),
        order_by="modified desc",
    )
    return rows


@frappe.whitelist()
def upsert_holiday_list(name, dates=None, from_date=None, to_date=None):
    """Create/update a CRM Holiday List with provided additional holiday dates.

    - dates: list or JSON list of 'YYYY-MM-DD' strings.
    """
    name = (name or "").strip()
    if not name:
        frappe.throw(_("Holiday List Name is required"))

    dates = _parse_json(dates, default=[]) or []

    if frappe.db.exists("CRM Holiday List", name):
        doc = frappe.get_doc("CRM Holiday List", name)
        # Clear current holidays; keep weekly_off as-is
        doc.set("holidays", [])
    else:
        doc = frappe.get_doc({
            "doctype": "CRM Holiday List",
            "holiday_list_name": name,
            "from_date": from_date,
            "to_date": to_date,
        })

    for d in dates:
        if not d:
            continue
        doc.append("holidays", {"date": d, "weekly_off": 0, "description": "Additional Holiday"})

    doc.total_holidays = len(doc.get("holidays") or [])
    if doc.name:
        doc.save(ignore_permissions=True)
    else:
        doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {"success": True, "name": doc.name}



