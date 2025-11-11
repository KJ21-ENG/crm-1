import frappe
from frappe import _


def _check_admin_role():
    # Allow only system/sales/crm managers to manage office hours
    # Allow Administrator user or users with one of the manager roles
    if frappe.session.user == 'Administrator':
        return True

    allowed = ("System Manager", "Sales Manager", "CRM Manager")
    for role in allowed:
        if frappe.has_role(role):
            return True

    frappe.throw(_("Insufficient permissions to access office hours"))


@frappe.whitelist()
def get_office_hours():
    """Return list of CRM Service Day rows ordered by weekday"""
    rows = frappe.get_all(
        "CRM Service Day",
        fields=["name", "workday", "start_time", "end_time", "office_open"],
        order_by="FIELD(workday, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')",
        ignore_permissions=True,
    )
    return rows


@frappe.whitelist()
def get_holidays(holiday_list_name=None):
    """Return holidays for given holiday list name (defaults to 'FCRM Holidays')."""
    try:
        if not holiday_list_name:
            holiday_list_name = 'FCRM Holidays'

        # Return list of dates and descriptions
        rows = frappe.get_all(
            'CRM Holiday',
            filters={"parent": holiday_list_name},
            fields=['name', 'date', 'description'],
            order_by='date desc',
            ignore_permissions=True,
        )
        return rows
    except Exception as e:
        frappe.log_error(e)
        return []


@frappe.whitelist()
def save_holidays(days, holiday_list_name=None):
    """Save holiday rows under the specified holiday list (create list if missing).

    days: list of {name?, date, description}
    """
    _check_admin_role()
    import json
    if not holiday_list_name:
        holiday_list_name = 'FCRM Holidays'

    # Ensure parent Holiday List exists
    if not frappe.db.exists('CRM Holiday List', holiday_list_name):
        hl = frappe.get_doc({'doctype': 'CRM Holiday List', 'holiday_list_name': holiday_list_name, 'from_date': '1970-01-01', 'to_date': '2099-12-31'})
        hl.insert(ignore_permissions=True)

    if isinstance(days, str):
        days = json.loads(days)

    results = []
    for d in days:
        name = d.get('name')
        date = d.get('date')
        description = d.get('description') or ''

        if not date:
            results.append({'error': 'date required', 'input': d})
            continue

        if name:
            try:
                frappe.db.set_value('CRM Holiday', name, {'date': date, 'description': description})
                results.append({'name': name, 'status': 'updated'})
            except Exception as e:
                frappe.log_error(e)
                results.append({'name': name, 'status': 'error', 'error': str(e)})
        else:
            try:
                child = {
                    'doctype': 'CRM Holiday',
                    'date': date,
                    'description': description,
                    'parent': holiday_list_name,
                    'parenttype': 'CRM Holiday List',
                    'parentfield': 'holidays'
                }
                doc = frappe.get_doc(child)
                doc.insert(ignore_permissions=True)
                results.append({'name': doc.name, 'status': 'created'})
            except Exception as e:
                frappe.log_error(e)
                results.append({'date': date, 'status': 'error', 'error': str(e)})

    frappe.db.commit()
    return results


@frappe.whitelist()
def save_office_hours(days):
    """Save multiple CRM Service Day rows.

    Expects `days` as JSON-serializable list of objects with keys:
    name (optional), workday, start_time, end_time
    """
    _check_admin_role()
    import json

    if isinstance(days, str):
        days = json.loads(days)

    results = []
    for d in days:
        name = d.get("name") or None
        workday = d.get("workday")
        start_time = d.get("start_time") or ""
        end_time = d.get("end_time") or ""

        # Normalize empty strings
        if not start_time:
            start_time = ""
        if not end_time:
            end_time = ""

        # If both times are empty, treat as 'closed' -> delete existing row or skip creating
        if not start_time and not end_time:
            if name:
                try:
                    frappe.delete_doc("CRM Service Day", name, force=True)
                    results.append({"name": name, "status": "deleted"})
                except Exception as e:
                    frappe.log_error(e)
                    results.append({"name": name, "status": "error", "error": str(e)})
            else:
                # nothing to create
                results.append({"workday": workday, "status": "skipped"})
            continue

        if name:
            try:
                frappe.db.set_value("CRM Service Day", name, {"start_time": start_time, "end_time": end_time, "office_open": bool(d.get("office_open"))})
                results.append({"name": name, "status": "updated"})
            except Exception as e:
                frappe.log_error(e)
                results.append({"name": name, "status": "error", "error": str(e)})
        else:
            try:
                # CRM Service Day is a child table of the single doc 'FCRM Settings'
                # When creating a new child row we must set parent/parenttype/parentfield
                child = {
                    "doctype": "CRM Service Day",
                    "workday": workday,
                    "start_time": start_time,
                    "end_time": end_time,
                    "office_open": bool(d.get("office_open")),
                    "parent": "FCRM Settings",
                    "parenttype": "FCRM Settings",
                    "parentfield": "office_hours",
                }
                doc = frappe.get_doc(child)
                doc.insert(ignore_permissions=True)
                results.append({"name": doc.name, "status": "created"})
            except Exception as e:
                frappe.log_error(e)
                results.append({"workday": workday, "status": "error", "error": str(e)})

    frappe.db.commit()
    return results


def is_office_open(dt=None):
    """Return True if current datetime (or provided dt) falls within today's CRM Service Day hours.

    dt may be a string or datetime; when None, uses current server time.
    """
    from frappe.utils import get_datetime, now
    from datetime import datetime

    try:
        if dt:
            current = get_datetime(dt)
        else:
            current = get_datetime(now())

        weekday = current.strftime('%A')

        rows = frappe.get_all(
            "CRM Service Day",
            filters={"workday": weekday},
            fields=["start_time", "end_time", "office_open"],
            limit=1,
            ignore_permissions=True,
        )

        # Check holidays first (use site/system timezone)
        try:
            # Use helpers from frappe.utils.data for timezone-aware datetime
            from frappe.utils.data import get_system_timezone, get_datetime_in_timezone, getdate

            site_tz = get_system_timezone()
            site_now_dt = get_datetime_in_timezone(site_tz)
            today_date = getdate(site_now_dt)

            # Look for a CRM Holiday under the central Holiday List
            holiday_list_name = 'FCRM Holidays'
            hl_exists = frappe.db.exists('CRM Holiday List', holiday_list_name)
            if hl_exists:
                # Compare using string ISO date to avoid type issues
                today_str = today_date.strftime('%Y-%m-%d')
                holidays = frappe.get_all('CRM Holiday', filters={"parent": holiday_list_name, "date": today_str}, fields=["name","date"], ignore_permissions=True)
                if holidays:
                    frappe.logger().info(f"OfficeHours: holiday match for {today_str}: {holidays}")
                    return False
        except Exception as e:
            frappe.log_error(e)
            # don't block reassignment if holiday check fails
            pass

        if not rows:
            return False

        row = rows[0]
        # Respect explicit office_open flag on the row
        if row.get("office_open") in (0, "0", False, "False"):
            return False

        start = row.get("start_time") or ""
        end = row.get("end_time") or ""
        if not start or not end:
            return False

        # start/end are strings like HH:MM:SS or HH:MM — normalize
        def to_seconds(val):
            # Accept string like HH:MM or HH:MM:SS, or datetime.time, datetime.timedelta, datetime.datetime
            from datetime import time, timedelta, datetime

            if val is None:
                return None

            # timedelta -> total seconds
            if isinstance(val, timedelta):
                return int(val.total_seconds()) % 86400

            # datetime -> take time part
            if isinstance(val, datetime):
                t = val.time()
                return t.hour * 3600 + t.minute * 60 + t.second

            # time object
            if isinstance(val, time):
                return val.hour * 3600 + val.minute * 60 + val.second

            # string
            try:
                parts = str(val).split(":")
                if len(parts) < 2:
                    return None
                h = int(parts[0])
                m = int(parts[1])
                s = int(parts[2]) if len(parts) > 2 else 0
                return h * 3600 + m * 60 + s
            except Exception:
                return None

        now_secs = current.hour * 3600 + current.minute * 60 + current.second
        start_secs = to_seconds(start)
        end_secs = to_seconds(end)
        if start_secs is None or end_secs is None:
            return False

        return start_secs <= now_secs <= end_secs
    except Exception as e:
        frappe.log_error(f"is_office_open failed: {str(e)}", "Office Hours Error")
        # If check fails, be conservative and allow processing
        return True


@frappe.whitelist()
def get_office_status(dt=None):
    """Diagnostic endpoint: return current server time, today's service day row and computed seconds.

    Useful for debugging why scheduler is skipping or not.
    """
    from frappe.utils import get_datetime, now
    try:
        current = get_datetime(dt) if dt else get_datetime(now())
        weekday = current.strftime('%A')
        rows = frappe.get_all(
            "CRM Service Day",
            filters={"workday": weekday},
            fields=["name", "workday", "start_time", "end_time", "office_open"],
            limit=1,
            ignore_permissions=True,
        )

        row = rows[0] if rows else None

        # reuse robust conversion used above
        def to_seconds(val):
            from datetime import time, timedelta, datetime

            if val is None:
                return None
            if isinstance(val, timedelta):
                return int(val.total_seconds()) % 86400
            if isinstance(val, datetime):
                t = val.time()
                return t.hour * 3600 + t.minute * 60 + t.second
            if isinstance(val, time):
                return val.hour * 3600 + val.minute * 60 + val.second
            try:
                parts = str(val).split(":")
                if len(parts) < 2:
                    return None
                h = int(parts[0])
                m = int(parts[1])
                s = int(parts[2]) if len(parts) > 2 else 0
                return h * 3600 + m * 60 + s
            except Exception:
                return None

        now_secs = current.hour * 3600 + current.minute * 60 + current.second
        start_secs = to_seconds(row.get('start_time')) if row else None
        end_secs = to_seconds(row.get('end_time')) if row else None

        return {
            "now": str(current),
            "weekday": weekday,
            "row": row,
            "now_secs": now_secs,
            "start_secs": start_secs,
            "end_secs": end_secs,
            "is_open": start_secs is not None and end_secs is not None and start_secs <= now_secs <= end_secs,
        }
    except Exception as e:
        frappe.log_error(f"get_office_status failed: {str(e)}", "Office Hours Error")
        return {"error": str(e)}


@frappe.whitelist()
def get_holiday_debug():
    """Debug helper: return site_now, today, and matching CRM Holiday rows for debugging."""
    try:
        from frappe.utils import get_site_timezone, now_datetime
        import pytz
        site_tz = pytz.timezone(get_site_timezone())
        site_now = now_datetime().astimezone(site_tz)
        today = site_now.date()
        holiday_list_name = 'FCRM Holidays'
        hl_exists = frappe.db.exists('CRM Holiday List', holiday_list_name)
        holidays = []
        if hl_exists:
            holidays = frappe.get_all('CRM Holiday', filters={"parent": holiday_list_name, "date": today}, fields=["name", "date", "description"], ignore_permissions=True)

        return {
            'site_now': str(site_now),
            'today': str(today),
            'holiday_list_exists': bool(hl_exists),
            'found': holidays
        }
    except Exception as e:
        frappe.log_error(e)
        return {'error': str(e)}


