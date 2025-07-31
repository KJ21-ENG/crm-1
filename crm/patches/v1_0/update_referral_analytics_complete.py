# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import os

def execute():
    """
    Complete update for referral analytics to include 'Account Activated' status
    This patch ensures that both 'Account Opened' and 'Account Activated' statuses 
    are properly handled in both backend calculations and frontend display.
    """
    
    # Log the patch execution
    frappe.logger().info("Executing patch: update_referral_analytics_complete")
    
    try:
        # Update backend API file
        update_backend_api()
        
        # Update frontend component
        update_frontend_component()
        
        # Clear cache to ensure changes take effect
        frappe.clear_cache()
        
        # Log completion
        frappe.logger().info("Patch update_referral_analytics_complete completed successfully")
        
    except Exception as e:
        frappe.logger().error(f"Error in patch update_referral_analytics_complete: {str(e)}")
        raise

def update_backend_api():
    """Update the backend referral analytics API file"""
    try:
        api_file_path = "crm/api/referral_analytics.py"
        
        # Check if the file exists
        if not os.path.exists(api_file_path):
            frappe.logger().warning(f"Backend API file not found: {api_file_path}")
            return
        
        # Read the current file content
        with open(api_file_path, 'r') as file:
            content = file.read()
        
        # Apply the necessary changes
        updated_content = content
        
        # Update all SQL queries to include Account Activated status
        replacements = [
            # get_top_referrers function
            (
                "COUNT(CASE WHEN l.status = 'Account Opened' THEN 1 END) as successful_referrals,",
                "COUNT(CASE WHEN l.status IN ('Account Opened', 'Account Activated') THEN 1 END) as successful_referrals,"
            ),
            # get_referral_source_table function
            (
                "COUNT(CASE WHEN l.status = 'Account Opened' THEN 1 END) as successful_referrals,",
                "COUNT(CASE WHEN l.status IN ('Account Opened', 'Account Activated') THEN 1 END) as successful_referrals,"
            ),
            # get_conversion_funnel function - converted_leads
            (
                "COUNT(CASE WHEN l.status = 'Account Opened' AND l.referral_through IS NOT NULL AND l.referral_through != '' THEN 1 END) as converted_leads,",
                "COUNT(CASE WHEN l.status IN ('Account Opened', 'Account Activated') AND l.referral_through IS NOT NULL AND l.referral_through != '' THEN 1 END) as converted_leads,"
            ),
            # get_conversion_funnel function - total_converted_leads
            (
                "COUNT(CASE WHEN l.status = 'Account Opened' THEN 1 END) as total_converted_leads,",
                "COUNT(CASE WHEN l.status IN ('Account Opened', 'Account Activated') THEN 1 END) as total_converted_leads,"
            ),
            # get_referral_trends function
            (
                'filters = "l.status = \'Account Opened\'"',
                'filters = "l.status IN (\'Account Opened\', \'Account Activated\')"'
            )
        ]
        
        for old_pattern, new_pattern in replacements:
            updated_content = updated_content.replace(old_pattern, new_pattern)
        
        # Write the updated content back to the file
        with open(api_file_path, 'w') as file:
            file.write(updated_content)
        
        frappe.logger().info("Successfully updated backend referral analytics API file")
        
    except Exception as e:
        frappe.logger().error(f"Error updating backend API: {str(e)}")
        raise

def update_frontend_component():
    """Update the frontend referral analytics component"""
    try:
        frontend_file_path = "frontend/src/components/Dashboard/ReferralAnalyticsDashboard.vue"
        
        # Check if the file exists
        if not os.path.exists(frontend_file_path):
            frappe.logger().warning(f"Frontend file not found: {frontend_file_path}")
            return
        
        # Read the current file content
        with open(frontend_file_path, 'r') as file:
            content = file.read()
        
        # Apply the necessary changes
        updated_content = content
        
        # Update the getStatusBadgeClass function to include Account Activated
        # Look for the status map and add Account Activated if it doesn't exist
        if "'Account Activated': 'bg-green-100 text-green-800'," not in updated_content:
            # Find the line after Account Opened and add Account Activated
            old_pattern = "'Account Opened': 'bg-green-100 text-green-800',"
            new_pattern = "'Account Opened': 'bg-green-100 text-green-800',\n    'Account Activated': 'bg-green-100 text-green-800',"
            updated_content = updated_content.replace(old_pattern, new_pattern)
        
        # Write the updated content back to the file
        with open(frontend_file_path, 'w') as file:
            file.write(updated_content)
        
        frappe.logger().info("Successfully updated frontend referral analytics component")
        
    except Exception as e:
        frappe.logger().error(f"Error updating frontend component: {str(e)}")
        raise 