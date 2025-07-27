# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, getdate
import json

@frappe.whitelist()
def get_top_referrers(limit=10, date_from=None, date_to=None, account_type=None, lead_category=None, branch=None):
    """Get top referrers with most successful referrals"""
    try:
        # Build filters - show all referrals, not just Account Opened
        filters = "1=1"
        params = []
        
        if date_from:
            filters += " AND l.modified >= %s"
            params.append(date_from)
        
        if date_to:
            filters += " AND l.modified <= %s"
            params.append(date_to)
        
        if account_type:
            filters += " AND l.account_type = %s"
            params.append(account_type)
            
        if lead_category:
            filters += " AND l.lead_category = %s"
            params.append(lead_category)
            
        if branch:
            filters += " AND l.branch = %s"
            params.append(branch)
        
        # Simpler query that works reliably
        query = f"""
            SELECT 
                c.customer_name as referrer_name,
                c.name as customer_id,
                c.mobile_no as referrer_mobile,
                l.referral_through as client_id,
                l.account_type,
                COUNT(l.name) as total_referrals,
                COUNT(CASE WHEN l.status = 'Account Opened' THEN 1 END) as successful_referrals,
                MAX(l.modified) as last_referral_date
            FROM `tabCRM Lead` l
            LEFT JOIN `tabCRM Customer` c ON c.mobile_no = l.mobile_no
            WHERE {filters} AND l.referral_through IS NOT NULL AND l.referral_through != ''
            GROUP BY l.referral_through
            ORDER BY total_referrals DESC, last_referral_date DESC
            LIMIT %s
        """
        params.append(limit)
        
        results = frappe.db.sql(query, params, as_dict=True)
        
        return results
        
    except Exception as e:
        frappe.log_error(f"Error in get_top_referrers: {str(e)}")
        return []

@frappe.whitelist()
def get_referral_source_table(date_from=None, date_to=None, account_type=None, lead_category=None, branch=None):
    """Get referral source table with detailed information"""
    try:
        # Build filters - show all referrals, not just Account Opened
        filters = "1=1"
        params = []
        
        if date_from:
            filters += " AND l.modified >= %s"
            params.append(date_from)
        
        if date_to:
            filters += " AND l.modified <= %s"
            params.append(date_to)
        
        if account_type:
            filters += " AND l.account_type = %s"
            params.append(account_type)
            
        if lead_category:
            filters += " AND l.lead_category = %s"
            params.append(lead_category)
            
        if branch:
            filters += " AND l.branch = %s"
            params.append(branch)
        
        # Simpler query that works reliably
        query = f"""
            SELECT 
                c.customer_name as referrer_name,
                c.mobile_no as referrer_mobile,
                l.referral_through as client_id,
                l.account_type,
                COUNT(l.name) as total_referrals,
                COUNT(CASE WHEN l.status = 'Account Opened' THEN 1 END) as successful_referrals,
                COUNT(DISTINCT l.name) as total_leads_referred,
                MAX(l.modified) as last_referral_date,
                MIN(l.modified) as first_referral_date
            FROM `tabCRM Lead` l
            LEFT JOIN `tabCRM Customer` c ON c.mobile_no = l.mobile_no
            WHERE {filters} AND l.referral_through IS NOT NULL AND l.referral_through != ''
            GROUP BY l.referral_through
            ORDER BY total_referrals DESC, last_referral_date DESC
        """
        
        results = frappe.db.sql(query, params, as_dict=True)
        
        return results
        
    except Exception as e:
        frappe.log_error(f"Error in get_referral_source_table: {str(e)}")
        return []

@frappe.whitelist()
def get_conversion_funnel(date_from=None, date_to=None, account_type=None, lead_category=None, branch=None):
    """Get conversion funnel data"""
    try:
        # Build filters
        filters = "1=1"
        params = []
        
        if date_from:
            filters += " AND l.modified >= %s"
            params.append(date_from)
        
        if date_to:
            filters += " AND l.modified <= %s"
            params.append(date_to)
        
        if account_type:
            filters += " AND l.account_type = %s"
            params.append(account_type)
            
        if lead_category:
            filters += " AND l.lead_category = %s"
            params.append(lead_category)
            
        if branch:
            filters += " AND l.branch = %s"
            params.append(branch)
        
        # Query for conversion funnel - include all leads with referrals
        query = f"""
            SELECT 
                COUNT(CASE WHEN l.referral_through IS NOT NULL AND l.referral_through != '' THEN 1 END) as total_leads_with_referral,
                COUNT(CASE WHEN l.status = 'Account Opened' AND l.referral_through IS NOT NULL AND l.referral_through != '' THEN 1 END) as converted_leads,
                COUNT(CASE WHEN l.status = 'Account Opened' THEN 1 END) as total_converted_leads,
                COUNT(*) as total_leads,
                COUNT(CASE WHEN l.lead_category = 'Direct' THEN 1 END) as direct_leads,
                COUNT(CASE WHEN l.lead_category = 'Indirect' THEN 1 END) as indirect_leads
            FROM `tabCRM Lead` l
            WHERE {filters}
        """
        
        result = frappe.db.sql(query, params, as_dict=True)
        
        if result:
            data = result[0]
            data['conversion_rate'] = round((data['converted_leads'] / data['total_leads_with_referral'] * 100) if data['total_leads_with_referral'] > 0 else 0, 2)
            data['overall_conversion_rate'] = round((data['total_converted_leads'] / data['total_leads'] * 100) if data['total_leads'] > 0 else 0, 2)
            return data
        
        return {}
        
    except Exception as e:
        frappe.log_error(f"Error in get_conversion_funnel: {str(e)}")
        return {}

@frappe.whitelist()
def get_referral_trends(date_from=None, date_to=None, account_type=None):
    """Get referral trends over time"""
    try:
        # Build filters
        filters = "l.status = 'Account Opened'"
        params = []
        
        if date_from:
            filters += " AND l.modified >= %s"
            params.append(date_from)
        
        if date_to:
            filters += " AND l.modified <= %s"
            params.append(date_to)
        
        if account_type:
            filters += " AND l.account_type = %s"
            params.append(account_type)
        
        # Query for trends
        query = f"""
            SELECT 
                DATE(l.modified) as date,
                COUNT(l.name) as referrals_count,
                COUNT(DISTINCT c.name) as unique_referrers
            FROM `tabCRM Lead` l
            JOIN `tabCRM Customer` c ON JSON_CONTAINS(c.accounts, JSON_OBJECT('client_id', l.referral_through))
            WHERE {filters}
            GROUP BY DATE(l.modified)
            ORDER BY date DESC
            LIMIT 30
        """
        
        results = frappe.db.sql(query, params, as_dict=True)
        
        return results
        
    except Exception as e:
        frappe.log_error(f"Error in get_referral_trends: {str(e)}")
        return []

@frappe.whitelist()
def update_customer_accounts(customer_name, client_id, account_type):
    """Update customer accounts when account is opened/activated"""
    try:
        customer = frappe.get_doc("CRM Customer", customer_name)
        
        # Initialize accounts if not exists
        if not customer.accounts:
            customer.accounts = []
        elif isinstance(customer.accounts, str):
            customer.accounts = json.loads(customer.accounts)
        
        # Check if account already exists
        account_exists = False
        for account in customer.accounts:
            if account.get('client_id') == client_id:
                account_exists = True
                break
        
        # Add new account if not exists
        if not account_exists:
            customer.accounts.append({
                "account_type": account_type,
                "client_id": client_id,
                "created_date": today()
            })
            
            customer.save(ignore_permissions=True)
            
            # Update referral count
            update_referral_count(customer_name)
            
            return {"success": True, "message": "Account added successfully"}
        
        return {"success": True, "message": "Account already exists"}
        
    except Exception as e:
        frappe.log_error(f"Error in update_customer_accounts: {str(e)}")
        return {"success": False, "message": str(e)}

def update_referral_count(customer_name):
    """Update referral count for a customer"""
    try:
        customer = frappe.get_doc("CRM Customer", customer_name)
        
        if not customer.accounts:
            customer.referral_count = 0
        else:
            # Count successful referrals
            client_ids = []
            if isinstance(customer.accounts, str):
                accounts = json.loads(customer.accounts)
            else:
                accounts = customer.accounts
                
            for account in accounts:
                if account.get('client_id'):
                    client_ids.append(account['client_id'])
            
            if client_ids:
                successful_referrals = frappe.db.count("CRM Lead", {
                    "referral_through": ["in", client_ids],
                    "status": "Account Opened"
                })
                customer.referral_count = successful_referrals
            else:
                customer.referral_count = 0
        
        customer.save(ignore_permissions=True)
        
    except Exception as e:
        frappe.log_error(f"Error updating referral count: {str(e)}")

@frappe.whitelist()
def get_default_referral_code():
    """Get default referral code from FCRM Settings"""
    try:
        settings = frappe.get_single('FCRM Settings')
        return settings.default_referral_code or ''
    except Exception as e:
        frappe.log_error(f"Error getting default referral code: {str(e)}")
        return ''

@frappe.whitelist()
def get_branch_list():
    """Get list of available branches for filtering"""
    try:
        branches = frappe.db.sql("""
            SELECT DISTINCT branch 
            FROM `tabCRM Lead` 
            WHERE branch IS NOT NULL AND branch != ''
            ORDER BY branch
        """, as_dict=True)
        return [branch.branch for branch in branches]
    except Exception as e:
        frappe.log_error(f"Error getting branch list: {str(e)}")
        return []

@frappe.whitelist()
def export_referral_analytics(date_from=None, date_to=None, account_type=None, lead_category=None, branch=None, format='csv'):
    """Export referral analytics data"""
    try:
        # Get all data with new filters
        top_referrers = get_top_referrers(1000, date_from, date_to, account_type, lead_category, branch)
        source_table = get_referral_source_table(date_from, date_to, account_type, lead_category, branch)
        conversion_funnel = get_conversion_funnel(date_from, date_to, account_type, lead_category, branch)
        
        # Combine data for export
        export_data = {
            "top_referrers": top_referrers,
            "source_table": source_table,
            "conversion_funnel": conversion_funnel,
            "export_date": today(),
            "filters": {
                "date_from": date_from,
                "date_to": date_to,
                "account_type": account_type,
                "lead_category": lead_category,
                "branch": branch
            }
        }
        
        return export_data
        
    except Exception as e:
        frappe.log_error(f"Error in export_referral_analytics: {str(e)}")
        return {"error": str(e)} 