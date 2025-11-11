import frappe
import json

def execute():
    """Update CRM Ticket list view to use 'subject' field instead of 'ticket_subject'"""
    
    # Update existing view settings in CRM View Settings
    view_settings = frappe.get_all(
        "CRM View Settings",
        filters={"dt": "CRM Ticket", "type": "list"},
        fields=["name", "columns", "rows"]
    )
    
    for view in view_settings:
        try:
            doc = frappe.get_doc("CRM View Settings", view.name)
            updated = False
            
            # Update columns
            if doc.columns:
                columns = frappe.parse_json(doc.columns)
                for column in columns:
                    if column.get("key") == "ticket_subject":
                        column["key"] = "subject"
                        updated = True
            
            # Update rows
            if doc.rows:
                rows = frappe.parse_json(doc.rows)
                if "ticket_subject" in rows:
                    rows.remove("ticket_subject")
                if "subject" not in rows:
                    rows.append("subject")
                    updated = True
            
            if updated:
                doc.save(ignore_permissions=True)
                print(f"✅ Updated view setting: {doc.name}")
                
        except Exception as e:
            print(f"❌ Error updating view {view.name}: {str(e)}")
    
    # Update kanban settings if any
    kanban_views = frappe.get_all(
        "CRM View Settings",
        filters={"dt": "CRM Ticket", "type": "kanban"},
        fields=["name", "title_field"]
    )
    
    for view in kanban_views:
        try:
            doc = frappe.get_doc("CRM View Settings", view.name)
            if doc.title_field == "ticket_subject":
                doc.title_field = "subject"
                doc.save(ignore_permissions=True)
                print(f"✅ Updated kanban view: {doc.name}")
                
        except Exception as e:
            print(f"❌ Error updating kanban view {view.name}: {str(e)}")
    
    frappe.db.commit()
    print("✅ Successfully updated ticket list views to use 'subject' field") 