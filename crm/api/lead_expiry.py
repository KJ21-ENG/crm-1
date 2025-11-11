import frappe
from frappe.utils import nowdate, add_days


@frappe.whitelist()
def daily_mark_expired_leads():
    """
    Daily cron job to mark expired leads:
    - Leads created > 60 days ago and not 'Account Opened' => 'Lead Expired'
    - Leads with account_open_date > 30 days ago and status not 'Account Activated' => 'Lead Expired (Account Opened)'
    """
    try:
        today = nowdate()

        # Case 1: created > 60 days and not Account Opened
        cutoff_60 = add_days(today, -60)
        leads_case1 = frappe.db.sql(
            """
            SELECT name FROM `tabCRM Lead`
            WHERE DATE(creation) <= %s
            AND IFNULL(status, '') NOT IN ('Account Opened', 'Account Activated', 'Lead Expired', 'Lead Expired (Account Opened)')
            """,
            (cutoff_60,),
            as_dict=True,
        )

        # Update statuses for case1
        updated_case1 = 0
        for r in leads_case1:
            try:
                frappe.db.set_value('CRM Lead', r.name, 'status', 'Lead Expired', update_modified=False)
                updated_case1 += 1
            except Exception:
                pass

        # Case 2: account_open_date > 30 days and not Account Activated
        cutoff_30 = add_days(today, -30)
        leads_case2 = frappe.db.sql(
            """
            SELECT name FROM `tabCRM Lead`
            WHERE account_open_date IS NOT NULL
            AND DATE(account_open_date) <= %s
            AND IFNULL(status, '') NOT IN ('Account Activated', 'Lead Expired (Account Opened)', 'Lead Expired')
            """,
            (cutoff_30,),
            as_dict=True,
        )

        updated_case2 = 0
        for r in leads_case2:
            try:
                frappe.db.set_value('CRM Lead', r.name, 'status', 'Lead Expired (Account Opened)', update_modified=False)
                updated_case2 += 1
            except Exception:
                pass

        frappe.db.commit()
        return {"success": True, "updated_case1": updated_case1, "updated_case2": updated_case2}
    except Exception as e:
        frappe.log_error(f"Error in daily_mark_expired_leads: {str(e)}")
        return {"success": False, "error": str(e)}

