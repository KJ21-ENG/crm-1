# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import os

def execute():
    """
    Update frontend referral analytics status badge styling to include 'Account Activated' status
    This patch ensures that 'Account Activated' status displays with the same green styling as 'Account Opened'.
    """
    
    # Log the patch execution
    frappe.logger().info("Executing patch: update_referral_analytics_frontend_status")
    
    try:
        # Update the frontend component file
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
        old_pattern = """function getStatusBadgeClass(status) {
  const statusMap = {
    'New': 'bg-gray-100 text-gray-800',
    'Open': 'bg-blue-100 text-blue-800',
    'In Progress': 'bg-yellow-100 text-yellow-800',
    'Qualified': 'bg-green-100 text-green-800',
    'Converted': 'bg-green-100 text-green-800',
    'Account Opened': 'bg-green-100 text-green-800',
    'Lost': 'bg-red-100 text-red-800',
    'Rejected': 'bg-red-100 text-red-800',
    'Closed': 'bg-gray-100 text-gray-800',
    'Completed': 'bg-green-100 text-green-800',
    'Pending': 'bg-orange-100 text-orange-800',
    'On Hold': 'bg-yellow-100 text-yellow-800'
  }
  
  return statusMap[status] || 'bg-gray-100 text-gray-800'
}"""
        
        new_pattern = """function getStatusBadgeClass(status) {
  const statusMap = {
    'New': 'bg-gray-100 text-gray-800',
    'Open': 'bg-blue-100 text-blue-800',
    'In Progress': 'bg-yellow-100 text-yellow-800',
    'Qualified': 'bg-green-100 text-green-800',
    'Converted': 'bg-green-100 text-green-800',
    'Account Opened': 'bg-green-100 text-green-800',
    'Account Activated': 'bg-green-100 text-green-800',
    'Lost': 'bg-red-100 text-red-800',
    'Rejected': 'bg-red-100 text-red-800',
    'Closed': 'bg-gray-100 text-gray-800',
    'Completed': 'bg-green-100 text-green-800',
    'Pending': 'bg-orange-100 text-orange-800',
    'On Hold': 'bg-yellow-100 text-yellow-800'
  }
  
  return statusMap[status] || 'bg-gray-100 text-gray-800'
}"""
        
        updated_content = updated_content.replace(old_pattern, new_pattern)
        
        # Write the updated content back to the file
        with open(frontend_file_path, 'w') as file:
            file.write(updated_content)
        
        frappe.logger().info("Successfully updated frontend referral analytics component")
        
        # Log completion
        frappe.logger().info("Patch update_referral_analytics_frontend_status completed successfully")
        
    except Exception as e:
        frappe.logger().error(f"Error in patch update_referral_analytics_frontend_status: {str(e)}")
        raise 