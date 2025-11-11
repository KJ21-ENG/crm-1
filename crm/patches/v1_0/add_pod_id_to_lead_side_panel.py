import json
import frappe


def execute():
    """
    Ensure the `pod_id` field appears in the default Side Panel layout for `CRM Lead`.
    Adds it to the `lead_info_section` (first column) if not already present.
    Safe to re-run.
    """
    try:
        layout_name = "CRM Lead-Side Panel"

        if not frappe.db.exists("CRM Fields Layout", layout_name):
            # Nothing to do if side panel layout doesn't exist yet
            return

        layout_doc = frappe.get_doc("CRM Fields Layout", layout_name)
        layout_data = []
        if layout_doc.layout:
            try:
                layout_data = json.loads(layout_doc.layout)
            except Exception:
                layout_data = []

        if not isinstance(layout_data, list):
            layout_data = []

        # Check if pod_id already present anywhere
        def has_pod_id(layout):
            for section in layout:
                for column in section.get("columns", []) or []:
                    fields = column.get("fields", []) or []
                    if "pod_id" in fields:
                        return True
            return False

        if has_pod_id(layout_data):
            return

        # Prefer adding to lead_info_section if exists; otherwise, first section/column
        target_section = None
        for section in layout_data:
            if section.get("name") in ("lead_info_section", "lead_info", "lead_details"):
                target_section = section
                break

        if not target_section and layout_data:
            target_section = layout_data[0]

        if not target_section:
            # If no sections, create a minimal one
            target_section = {
                "label": "Lead Info",
                "name": "lead_info_section",
                "opened": True,
                "columns": [{"name": "column_lead_info", "fields": []}],
            }
            layout_data.append(target_section)

        if not target_section.get("columns"):
            target_section["columns"] = [{"name": "column_lead_info", "fields": []}]

        # Use the first column by default
        first_col = target_section["columns"][0]
        fields = first_col.get("fields") or []

        # Place pod_id after account_type if present; else append at end
        try:
            idx = fields.index("account_type")
            insert_pos = idx + 1
        except ValueError:
            insert_pos = len(fields)

        fields.insert(insert_pos, "pod_id")
        first_col["fields"] = fields

        # Save layout
        layout_doc.layout = json.dumps(layout_data, indent=2)
        layout_doc.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"add_pod_id_to_lead_side_panel patch failed: {str(e)}")
        # Let it bubble to fail migration if critical parsing/storage errors
        raise


