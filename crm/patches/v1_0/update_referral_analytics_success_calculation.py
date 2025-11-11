# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute():
    """
    Update referral analytics success calculation to include 'Account Activated' status
    This patch ensures that both 'Account Opened' and 'Account Activated' statuses 
    are counted as successful referrals in the analytics calculations.
    """
    
    # Log the patch execution
    frappe.logger().info("Executing patch: update_referral_analytics_success_calculation")
    
    try:
        # Update the referral analytics API file
        api_file_path = "crm/api/referral_analytics.py"
        
        # Read the current file content
        with open(api_file_path, 'r') as file:
            content = file.read()
        
        # Apply the necessary changes
        updated_content = content
        
        # Update get_top_referrers function
        old_pattern_1 = "COUNT(CASE WHEN l.status = 'Account Opened' THEN 1 END) as successful_referrals,"
        new_pattern_1 = "COUNT(CASE WHEN l.status IN ('Account Opened', 'Account Activated') THEN 1 END) as successful_referrals,"
        updated_content = updated_content.replace(old_pattern_1, new_pattern_1)
        
        # Update get_referral_source_table function
        old_pattern_2 = "COUNT(CASE WHEN l.status = 'Account Opened' THEN 1 END) as successful_referrals,"
        new_pattern_2 = "COUNT(CASE WHEN l.status IN ('Account Opened', 'Account Activated') THEN 1 END) as successful_referrals,"
        updated_content = updated_content.replace(old_pattern_2, new_pattern_2)
        
        # Update get_conversion_funnel function
        old_pattern_3 = "COUNT(CASE WHEN l.status = 'Account Opened' AND l.referral_through IS NOT NULL AND l.referral_through != '' THEN 1 END) as converted_leads,"
        new_pattern_3 = "COUNT(CASE WHEN l.status IN ('Account Opened', 'Account Activated') AND l.referral_through IS NOT NULL AND l.referral_through != '' THEN 1 END) as converted_leads,"
        updated_content = updated_content.replace(old_pattern_3, new_pattern_3)
        
        old_pattern_4 = "COUNT(CASE WHEN l.status = 'Account Opened' THEN 1 END) as total_converted_leads,"
        new_pattern_4 = "COUNT(CASE WHEN l.status IN ('Account Opened', 'Account Activated') THEN 1 END) as total_converted_leads,"
        updated_content = updated_content.replace(old_pattern_4, new_pattern_4)
        
        # Update get_referral_trends function
        old_pattern_5 = "filters = \"l.status = 'Account Opened'\""
        new_pattern_5 = "filters = \"l.status IN ('Account Opened', 'Account Activated')\""
        updated_content = updated_content.replace(old_pattern_5, new_pattern_5)
        
        # Write the updated content back to the file
        with open(api_file_path, 'w') as file:
            file.write(updated_content)
        
        frappe.logger().info("Successfully updated referral analytics API file")
        
        # Clear cache to ensure changes take effect
        frappe.clear_cache()
        
        # Log completion
        frappe.logger().info("Patch update_referral_analytics_success_calculation completed successfully")
        
    except Exception as e:
        frappe.logger().error(f"Error in patch update_referral_analytics_success_calculation: {str(e)}")
        raise 