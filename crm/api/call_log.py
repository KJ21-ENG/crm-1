"""Call log specific API helpers."""

import frappe
from frappe import _
from frappe.utils import cint
from frappe.utils.csvutils import build_csv_response
from frappe.utils.xlsxutils import make_xlsx
from frappe.utils.data import getdate, formatdate
from crm.utils import seconds_to_duration
from crm.api.doc import convert_filter_to_tuple
import json
from collections import defaultdict


@frappe.whitelist()
def set_cold_call(call_log: str, cold_call: int | str | bool = 1):
    """Mark or unmark a call log as a cold call.

    Args:
        call_log: Name of the ``CRM Call Log`` document to update.
        cold_call: Truthy value marks as cold, falsy removes the flag.
    """
    if not call_log:
        frappe.throw(_("Call log name is required"))

    doc = frappe.get_doc("CRM Call Log", call_log)
    if not doc.has_permission("write"):
        frappe.throw(_("Not permitted to update this call log"), frappe.PermissionError)

    flag = 1 if cint(cold_call) else 0
    # set_value can raise QueryDeadlockError (Record has changed since last read).
    # Retry a couple of times to handle transient snapshot isolation / deadlock errors.
    from time import sleep

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            frappe.db.set_value(
                "CRM Call Log",
                call_log,
                "is_cold_call",
                flag,
                update_modified=True,
            )
            break
        except frappe.QueryDeadlockError:
            if attempt == max_retries:
                raise
            # small backoff before retrying
            sleep(0.1 * attempt)

    return {"name": doc.name, "is_cold_call": flag}


@frappe.whitelist()
@frappe.read_only()
def export_call_log_monthly_summary(filters=None, file_format_type="Excel"):
    """Export monthly summary of call logs grouped by employee and call direction.

    Admin/System Manager: all employees. Everyone else: only their own call logs.
    """
    translate = frappe._
    # Parse filters from query string
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
    except Exception:
        filters = {}

    filters = filters or {}

    if not frappe.has_permission("CRM Call Log", ptype="export"):
        frappe.throw(_("Not permitted to export call logs"), frappe.PermissionError)

    # Respect simple date-only filters on start_time (align with list filtering)
    if isinstance(filters.get("start_time"), str):
        val = filters["start_time"]
        if len(val) >= 10 and val[4] == "-" and val[7] == "-":
            day = val[:10]
            filters["start_time"] = ["between", [f"{day} 00:00:00", f"{day} 23:59:59"]]

    user = frappe.session.user
    roles = set(frappe.get_roles(user))
    is_admin = user == "Administrator" or "System Manager" in roles

    # Admins should see all data by default; drop the auto-applied owner filter if it matches themselves
    if is_admin and filters.get("owner") == user:
        filters.pop("owner", None)

    # Non-admins must only export their own data
    if not is_admin:
        filters = {**filters, "owner": user}

    # Build tuple filters for frappe ORM
    try:
        tuple_filters = convert_filter_to_tuple("CRM Call Log", filters)
    except Exception:
        tuple_filters = []

    # Translate filters to SQL conditions (allow functions in SELECT safely)
    conditions = []
    values = []
    for _filter in tuple_filters:
        # Expected tuple: (doctype, field, operator, value) or (field, operator, value)
        if len(_filter) == 4:
            _, fieldname, operator, value = _filter
        elif len(_filter) == 3:
            fieldname, operator, value = _filter
        else:
            continue

        column = f"`tabCRM Call Log`.`{fieldname}`"
        op = (operator or "=").lower()

        if op == "between" and isinstance(value, (list, tuple)) and len(value) == 2:
            conditions.append(f"{column} BETWEEN %s AND %s")
            values.extend(value)
        elif op in ("in", "not in") and isinstance(value, (list, tuple)):
            placeholders = ", ".join(["%s"] * len(value))
            conditions.append(f"{column} {operator} ({placeholders})")
            values.extend(value)
        elif op == "like":
            conditions.append(f"{column} LIKE %s")
            values.append(value)
        else:
            conditions.append(f"{column} {operator} %s")
            values.append(value)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    sql = f"""
        SELECT
            DATE_FORMAT(COALESCE(start_time, creation), '%%Y-%%m-01') AS month_start,
            employee,
            SUM(CASE WHEN type='Incoming' THEN 1 ELSE 0 END) AS incoming_calls,
            SUM(CASE WHEN type='Incoming' THEN COALESCE(duration, 0) ELSE 0 END) AS incoming_duration,
            SUM(CASE WHEN type='Outgoing' THEN 1 ELSE 0 END) AS outgoing_calls,
            SUM(CASE WHEN type='Outgoing' THEN COALESCE(duration, 0) ELSE 0 END) AS outgoing_duration,
            COUNT(*) AS total_calls,
            SUM(COALESCE(duration, 0)) AS total_duration
        FROM `tabCRM Call Log`
        {where_clause}
        GROUP BY month_start, employee
        ORDER BY month_start ASC, employee ASC
    """

    rows = frappe.db.sql(sql, values, as_dict=True)

    if not rows:
        frappe.throw(translate("No call logs found for the selected filters"))

    # Resolve employee display names
    employees = {r.employee for r in rows if r.employee}
    full_names = {}
    if employees:
        for user_row in frappe.get_all(
            "User",
            filters={"name": ["in", list(employees)]},
            fields=["name", "full_name"],
        ):
            full_names[user_row.name] = user_row.full_name or user_row.name

    grouped = defaultdict(list)
    for r in rows:
        month_key = getdate(r.month_start)
        employee_label = full_names.get(r.employee) if r.employee else translate("Unknown")
        grouped[month_key].append(
            {
                "employee": employee_label,
                "incoming_calls": int(r.incoming_calls or 0),
                "incoming_duration": int(r.incoming_duration or 0),
                "outgoing_calls": int(r.outgoing_calls or 0),
                "outgoing_duration": int(r.outgoing_duration or 0),
                "total_calls": int(r.total_calls or 0),
                "total_duration": int(r.total_duration or 0),
            }
        )

    export_data = []

    for month in sorted(grouped.keys()):
        export_data.append([formatdate(month, "MMM yyyy")])
        export_data.append(
            [
                translate("Caller Name"),
                translate("Incoming Calls"),
                translate("Call Duration"),
                translate("Outgoing Calls"),
                translate("Call Duration"),
                translate("Total Calls"),
                translate("Call Duration"),
            ]
        )

        month_totals = {
            "incoming_calls": 0,
            "incoming_duration": 0,
            "outgoing_calls": 0,
            "outgoing_duration": 0,
            "total_calls": 0,
            "total_duration": 0,
        }

        for entry in grouped[month]:
            export_data.append(
                [
                    entry["employee"],
                    entry["incoming_calls"],
                    seconds_to_duration(entry["incoming_duration"]),
                    entry["outgoing_calls"],
                    seconds_to_duration(entry["outgoing_duration"]),
                    entry["total_calls"],
                    seconds_to_duration(entry["total_duration"]),
                ]
            )
            for k in month_totals:
                month_totals[k] += entry[k]

        export_data.append(
            [
                translate("Total"),
                month_totals["incoming_calls"],
                seconds_to_duration(month_totals["incoming_duration"]),
                month_totals["outgoing_calls"],
                seconds_to_duration(month_totals["outgoing_duration"]),
                month_totals["total_calls"],
                seconds_to_duration(month_totals["total_duration"]),
            ]
        )
        export_data.append([])

    filename_base = "Call_Log_Monthly_Summary"

    if file_format_type == "CSV":
        build_csv_response(export_data, filename_base)
        return

    # Default to Excel
    content = make_xlsx(export_data, filename_base).getvalue()
    frappe.response["filename"] = f"{filename_base}.xlsx"
    frappe.response["filecontent"] = content
    frappe.response["type"] = "binary"
    frappe.response["doctype"] = "CRM Call Log"
