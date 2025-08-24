import frappe


def execute():
    """Add Lead Expired statuses so frontend shows them with colors"""
    statuses = [
        {
            "name": "Lead Expired",
            "color": "slate",
            "position": 10,
        },
        {
            "name": "Lead Expired (Account Opened)",
            "color": "orange",
            "position": 11,
        },
    ]

    for s in statuses:
        try:
            if frappe.db.exists("CRM Lead Status", s["name"]):
                doc = frappe.get_doc("CRM Lead Status", s["name"])
                doc.color = s["color"]
                doc.position = s["position"]
                doc.save()
                frappe.logger().info(f"Updated existing lead status: {s['name']}")
            else:
                doc = frappe.new_doc("CRM Lead Status")
                doc.lead_status = s["name"]
                doc.color = s["color"]
                doc.position = s["position"]
                doc.insert()
                frappe.logger().info(f"Added lead status: {s['name']}")
        except Exception as e:
            frappe.log_error(f"Error adding/updating lead status {s['name']}: {e}")

    frappe.db.commit()


