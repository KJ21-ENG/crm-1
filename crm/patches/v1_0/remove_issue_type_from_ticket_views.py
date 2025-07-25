import frappe
import json

def execute():
    """Remove 'Issue Type' column from existing CRM Ticket view settings"""
    
    # Update list view settings
    view_settings = frappe.get_all(
        "CRM View Settings",
        filters={"dt": "CRM Ticket", "type": "list"},
        fields=["name", "columns", "rows"]
    )
    
    for view in view_settings:
        try:
            doc = frappe.get_doc("CRM View Settings", view.name)
            updated = False
            
            # Remove issue_type from columns
            if doc.columns:
                columns = frappe.parse_json(doc.columns)
                columns = [col for col in columns if col.get("key") != "issue_type"]
                doc.columns = json.dumps(columns, indent=2)
                updated = True
            
            # Remove issue_type from rows
            if doc.rows:
                rows = frappe.parse_json(doc.rows)
                if "issue_type" in rows:
                    rows.remove("issue_type")
                    doc.rows = json.dumps(rows, indent=2)
                    updated = True
            
            if updated:
                doc.save(ignore_permissions=True)
                print(f"✅ Updated list view setting: {doc.name}")
                
        except Exception as e:
            print(f"❌ Error updating list view {view.name}: {str(e)}")
    
    # Update kanban view settings
    kanban_views = frappe.get_all(
        "CRM View Settings",
        filters={"dt": "CRM Ticket", "type": "kanban"},
        fields=["name", "kanban_fields"]
    )
    
    for view in kanban_views:
        try:
            doc = frappe.get_doc("CRM View Settings", view.name)
            if doc.kanban_fields:
                kanban_fields = frappe.parse_json(doc.kanban_fields)
                if "issue_type" in kanban_fields:
                    kanban_fields.remove("issue_type")
                    doc.kanban_fields = json.dumps(kanban_fields, indent=2)
                    doc.save(ignore_permissions=True)
                    print(f"✅ Updated kanban view setting: {doc.name}")
                    
        except Exception as e:
            print(f"❌ Error updating kanban view {view.name}: {str(e)}")
    
    frappe.db.commit()
    print("✅ Successfully removed 'Issue Type' column from ticket view settings") 