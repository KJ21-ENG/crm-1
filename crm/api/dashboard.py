import frappe
from frappe import _
from frappe.utils import getdate, add_days, get_datetime
from datetime import datetime, timedelta
import json


@frappe.whitelist()
def get_dashboard_data(view='daily', custom_start_date=None, custom_end_date=None, _refresh=None):
    """Get comprehensive dashboard data for CRM"""
    try:
        # Force fresh data by clearing any potential cache
        frappe.cache.delete_keys("dashboard_data*")
        
        # If refresh flag is set, also clear any other potential caches
        if _refresh:
            frappe.cache.delete_keys("crm_dashboard*")
            frappe.cache.delete_keys("dashboard*")
            # Clear all cache for this user
            frappe.clear_cache()
        
        # Get date range for debugging
        start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
        
        # Debug: Log the date range being used
        print(f"Dashboard Debug - View: {view}, Start Date: {start_date}, End Date: {end_date}")
        
        # Debug: Get recent leads to verify data
        recent_leads = frappe.db.get_list("CRM Lead",
            fields=["name", "lead_name", "creation"],
            filters={"creation": ["between", [start_date, end_date]]},
            order_by="creation desc",
            limit=5
        )
        
        # Get total count for debugging
        total_leads_in_range = frappe.db.count("CRM Lead", filters={
            "creation": ["between", [start_date, end_date]]
        })
        
        print(f"Dashboard Debug - Total leads in range: {total_leads_in_range}")
        print(f"Dashboard Debug - Recent leads: {recent_leads}")
        
        try:
            result = {
                "overview": get_overview_stats(view, custom_start_date, custom_end_date),
                "lead_analytics": get_lead_analytics(view, custom_start_date, custom_end_date),
                "ticket_analytics": get_ticket_analytics(view, custom_start_date, custom_end_date),
                "task_analytics": get_task_analytics(view, custom_start_date, custom_end_date),
                "call_log_analytics": get_call_log_analytics(view, custom_start_date, custom_end_date),
                "user_performance": get_user_performance(view, custom_start_date, custom_end_date),
                "recent_activities": get_recent_activities(view, custom_start_date, custom_end_date),
                "trends": get_trends_data(view, custom_start_date, custom_end_date),
                "quick_actions": get_quick_actions(),
                "date_range": {
                    "view": view,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "formatted_range": get_formatted_date_range(start_date, end_date, view)
                },
                "_debug": {
                    "view": view,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "total_leads_in_range": total_leads_in_range,
                    "recent_leads_count": len(recent_leads),
                    "recent_leads": recent_leads
                }
            }
            
            print(f"Dashboard API Success - Overview: {result['overview']}")
            return result
            
        except Exception as e:
            print(f"Dashboard API Error in result creation: {str(e)}")
            frappe.log_error(f"Dashboard API Error in result creation: {str(e)}")
            return {"error": str(e)}
    except Exception as e:
        frappe.log_error(f"Dashboard API Error: {str(e)}")
        return {"error": str(e)}


@frappe.whitelist()
def get_user_dashboard_data(view='daily', custom_start_date=None, custom_end_date=None, target_user_id=None, _refresh=None):
    """Get user-specific dashboard data for the current user or target user (admin only)"""
    try:
        # Debug: Log function entry
        print(f"🔍 DEBUG: get_user_dashboard_data called with view={view}, custom_start_date={custom_start_date}, custom_end_date={custom_end_date}, target_user_id={target_user_id}, _refresh={_refresh}")
        
        # Get current user
        current_user = frappe.session.user
        print(f"🔍 DEBUG: Current user from session: {current_user}")
        
        # Check if user is authenticated
        if not current_user or current_user == 'Guest':
            print(f"❌ ERROR: User not authenticated: {current_user}")
            return {"error": "User not authenticated", "debug": {"user": current_user}}
        
        # Determine which user's data to fetch
        target_user = target_user_id if target_user_id else current_user
        print(f"🔍 DEBUG: Target user for data: {target_user}")
        
        # If admin is viewing another user's data, check permissions
        if target_user != current_user:
            if not frappe.has_permission("User", "read"):
                print(f"❌ ERROR: User {current_user} doesn't have permission to view other users' data")
                return {"error": "Insufficient permissions to view other users' data"}
            
            # Verify target user exists and is enabled
            target_user_exists = frappe.db.exists("User", {"name": target_user, "enabled": 1})
            if not target_user_exists:
                print(f"❌ ERROR: Target user {target_user} not found or disabled")
                return {"error": f"Target user {target_user} not found or disabled"}
        
        # Force fresh data by clearing any potential cache
        try:
            frappe.cache.delete_keys(f"user_dashboard_data_{target_user}*")
            print(f"🔍 DEBUG: Cleared cache keys for user: {target_user}")
        except Exception as cache_error:
            print(f"⚠️ WARNING: Cache clearing failed: {cache_error}")
        
        # If refresh flag is set, also clear any other potential caches
        if _refresh:
            try:
                frappe.cache.delete_keys(f"user_dashboard_{target_user}*")
                frappe.cache.delete_keys(f"dashboard*")
                print(f"🔍 DEBUG: Cleared additional cache keys for refresh")
            except Exception as cache_error:
                print(f"⚠️ WARNING: Additional cache clearing failed: {cache_error}")
        
        # Get date range for debugging
        try:
            start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
            print(f"🔍 DEBUG: Date range - Start: {start_date}, End: {end_date}")
        except Exception as date_error:
            print(f"❌ ERROR: Failed to get date range: {date_error}")
            return {"error": f"Date range error: {date_error}", "debug": {"view": view}}
        
        # Debug: Log the date range being used
        print(f"🔍 DEBUG: User Dashboard Debug - Target User: {target_user}, View: {view}, Start Date: {start_date}, End Date: {end_date}")
        
        try:
            # Test basic database connectivity
            test_count = frappe.db.count("User", filters={"name": target_user})
            print(f"🔍 DEBUG: Database connectivity test - User count: {test_count}")
            
            if test_count == 0:
                print(f"❌ ERROR: Target user {target_user} not found in database")
                return {"error": f"Target user {target_user} not found", "debug": {"user": target_user}}
            
        except Exception as db_error:
            print(f"❌ ERROR: Database connectivity test failed: {db_error}")
            return {"error": f"Database error: {db_error}", "debug": {"user": target_user}}
        
        try:
            result = {
                "user_info": get_user_info(target_user),
                "overview": get_user_overview_stats(target_user, view, custom_start_date, custom_end_date),
                "lead_analytics": get_user_lead_analytics(target_user, view, custom_start_date, custom_end_date),
                "ticket_analytics": get_user_ticket_analytics(target_user, view, custom_start_date, custom_end_date),
                "task_analytics": get_user_task_analytics(target_user, view, custom_start_date, custom_end_date),
                "call_log_analytics": get_user_call_log_analytics(target_user, view, custom_start_date, custom_end_date),
                "performance_metrics": get_user_performance_metrics(target_user, view, custom_start_date, custom_end_date),
                "recent_activities": get_user_recent_activities(target_user, view, custom_start_date, custom_end_date),
                "trends": get_user_trends_data(target_user, view, custom_start_date, custom_end_date),
                "achievements": get_user_achievements(target_user, view, custom_start_date, custom_end_date),
                "goals": get_user_goals(target_user, view, custom_start_date, custom_end_date),
                "peak_hours": get_user_peak_hours(target_user, view, custom_start_date, custom_end_date),
                "date_range": {
                    "view": view,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "formatted_range": get_formatted_date_range(start_date, end_date, view)
                },
                "_debug": {
                    "target_user": target_user,
                    "requested_by": current_user,
                    "view": view,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "function": "get_user_dashboard_data",
                    "debug": "get_user_dashboard_data",
                    "timestamp": str(frappe.utils.now()),
                    "session_id": frappe.session.sid if hasattr(frappe.session, 'sid') else 'N/A'
                }
            }
            
            print(f"✅ SUCCESS: User Dashboard API Success - Target User: {target_user}, Requested by: {current_user}")
            print(f"🔍 DEBUG: Result keys: {list(result.keys())}")
            print(f"🔍 DEBUG: User info keys: {list(result.get('user_info', {}).keys())}")
            print(f"🔍 DEBUG: Overview keys: {list(result.get('overview', {}).keys())}")
            
            return result
            
        except Exception as e:
            print(f"❌ ERROR: Dashboard API Error in result creation: {str(e)}")
            print(f"🔍 DEBUG: Exception type: {type(e).__name__}")
            print(f"🔍 DEBUG: Exception args: {e.args}")
            import traceback
            print(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
            frappe.log_error(f"Dashboard API Error in result creation: {str(e)}")
            return {"error": str(e), "debug": {"target_user": target_user, "exception_type": type(e).__name__}}
            
    except Exception as e:
        print(f"❌ ERROR: User Dashboard API Error: {str(e)}")
        print(f"🔍 DEBUG: Exception type: {type(e).__name__}")
        print(f"🔍 DEBUG: Exception args: {e.args}")
        import traceback
        print(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
        frappe.log_error(f"Dashboard API Error: {str(e)}")
        return {"error": str(e), "debug": {"exception_type": type(e).__name__}}


@frappe.whitelist()
def test_user_dashboard_api():
    """Simple test endpoint to verify API accessibility"""
    try:
        print("🔍 DEBUG: test_user_dashboard_api called")
        
        current_user = frappe.session.user
        print(f"🔍 DEBUG: Current user: {current_user}")
        
        return {
            "status": "success",
            "message": "User Dashboard API is working",
            "user": current_user,
            "timestamp": str(frappe.utils.now()),
            "debug": {
                "function": "test_user_dashboard_api",
                "session_active": bool(current_user and current_user != 'Guest')
            }
        }
    except Exception as e:
        print(f"❌ ERROR: Test API failed: {str(e)}")
        import traceback
        print(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
        return {"error": str(e), "status": "error"}


@frappe.whitelist()
def get_available_users():
    """Get list of available users for admin dashboard viewing"""
    try:
        print("🔍 DEBUG: get_available_users called")
        
        current_user = frappe.session.user
        print(f"🔍 DEBUG: Current user: {current_user}")
        
        # Check if user is admin
        if not frappe.has_permission("User", "read"):
            print(f"❌ ERROR: User {current_user} doesn't have permission to read users")
            return {"error": "Insufficient permissions"}
        
        # Get all enabled users
        users = frappe.db.get_list("User",
            filters={"enabled": 1},
            fields=["name", "full_name", "email", "last_login", "creation"],
            order_by="full_name asc"
        )
        
        print(f"✅ SUCCESS: Found {len(users)} available users")
        return {"message": users}
        
    except Exception as e:
        print(f"❌ ERROR: get_available_users failed: {str(e)}")
        import traceback
        print(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
        return {"error": str(e), "status": "error"}


@frappe.whitelist()
def get_user_roles():
    """Get current user's roles for frontend role-based access control"""
    try:
        print(f"🔍 DEBUG: get_user_roles called")
        
        # Get current user
        current_user = frappe.session.user
        print(f"🔍 DEBUG: Current user: {current_user}")
        
        # Check if user is authenticated
        if not current_user or current_user == 'Guest':
            print(f"❌ ERROR: User not authenticated: {current_user}")
            return {"error": "User not authenticated", "debug": {"user": current_user}}
        
        try:
            # Get user roles
            user_roles = frappe.get_roles(current_user)
            print(f"🔍 DEBUG: User roles: {user_roles}")
            
            # Get primary role (first non-system role)
            primary_role = get_user_role(current_user)
            print(f"🔍 DEBUG: Primary role: {primary_role}")
            
            result = {
                "user": current_user,
                "roles": user_roles,
                "primary_role": primary_role,
                "is_admin": any(role in ['Administrator', 'System Manager', 'CRM Manager', 'Dashboard Manager'] for role in user_roles),
                "timestamp": str(frappe.utils.now())
            }
            
            print(f"✅ SUCCESS: User roles fetched successfully")
            print(f"🔍 DEBUG: Result: {result}")
            
            return result
            
        except Exception as e:
            print(f"❌ ERROR: Error getting user roles: {str(e)}")
            print(f"🔍 DEBUG: Exception type: {type(e).__name__}")
            import traceback
            print(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
            frappe.log_error(f"Error getting user roles: {str(e)}")
            return {"error": str(e), "debug": {"user": current_user}}
            
    except Exception as e:
        print(f"❌ ERROR: get_user_roles API Error: {str(e)}")
        print(f"🔍 DEBUG: Exception type: {type(e).__name__}")
        import traceback
        print(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
        frappe.log_error(f"get_user_roles API Error: {str(e)}")
        return {"error": str(e), "debug": {"exception_type": type(e).__name__}}


def get_date_range(view, custom_start_date=None, custom_end_date=None):
    """Get date range based on view type"""
    from frappe.utils import getdate, now_datetime, add_days, add_to_date, get_datetime
    from datetime import datetime, timedelta
    
    today = getdate()
    now = now_datetime()
    
    if view == 'custom' and custom_start_date and custom_end_date:
        # Handle custom date range
        try:
            if isinstance(custom_start_date, str):
                start_date = datetime.strptime(custom_start_date, '%Y-%m-%d')
            else:
                start_date = custom_start_date
            
            if isinstance(custom_end_date, str):
                end_date = datetime.strptime(custom_end_date, '%Y-%m-%d')
                # Set end time to end of day
                end_date = datetime.combine(end_date.date(), datetime.max.time())
            else:
                end_date = custom_end_date
                
            return start_date, end_date
        except Exception as e:
            print(f"Error parsing custom dates: {e}")
            # Fallback to monthly view if custom dates fail
            pass
    
    if view == 'daily':
        # For daily view, use the entire day from 00:00:00 to 23:59:59
        # Fix: Use explicit datetime objects to avoid timezone issues
        start_date = datetime.combine(today, datetime.min.time())  # Start of day (00:00:00)
        end_date = datetime.combine(today, datetime.max.time())    # End of day (23:59:59.999999)
    elif view == 'weekly':
        start_date = get_datetime(add_days(today, -7))
        end_date = now
    elif view == 'monthly':
        # For monthly view, show current month (1st day to last day of current month)
        current_month = today.month
        current_year = today.year
        start_date = datetime(current_year, current_month, 1)  # First day of current month
        # Get last day of current month
        if current_month == 12:
            end_date = datetime(current_year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(current_year, current_month + 1, 1) - timedelta(days=1)
        # Set end time to end of day
        end_date = datetime.combine(end_date.date(), datetime.max.time())
    else:
        start_date = get_datetime(today)
        end_date = now
    
    return start_date, end_date


def get_overview_stats(view='daily', custom_start_date=None, custom_end_date=None):
    """Get high-level overview statistics"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    # Get total call logs
    total_call_logs = frappe.db.count("CRM Call Log", filters=date_filter)
    
    # Get missed calls count
    missed_calls = frappe.db.count("CRM Call Log", filters={
        **date_filter,
        "status": ["in", ["No Answer", "Missed"]]
    })
    
    return {
        "total_leads": frappe.db.count("CRM Lead", filters={
            "creation": ["between", [start_date, end_date]]
        }),
        "total_tickets": frappe.db.count("CRM Ticket", filters={
            "creation": ["between", [start_date, end_date]]
        }),
        "total_deals": frappe.db.count("CRM Deal", filters={
            "creation": ["between", [start_date, end_date]]
        }),
        "total_tasks": frappe.db.count("CRM Task", filters={
            "creation": ["between", [start_date, end_date]]
        }),
        "total_call_logs": total_call_logs,
        "missed_calls": missed_calls,
        "avg_response_time": get_avg_response_time(view, custom_start_date, custom_end_date)
    }


def get_lead_analytics(view='daily', custom_start_date=None, custom_end_date=None):
    """Get lead-related analytics"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    return {
        "status_distribution": frappe.db.get_list("CRM Lead", 
            fields=["status", "count(name) as count"],
            filters=date_filter,
            group_by="status",
            order_by="count desc"
        ),
        "lead_owner_performance": frappe.db.get_list("CRM Lead",
            fields=["lead_owner", "count(name) as count"],
            filters={**date_filter, "lead_owner": ["is", "set"]},
            group_by="lead_owner",
            order_by="count desc",
            limit=10
        ),
        "recent_leads": frappe.db.get_list("CRM Lead",
            fields=["name", "lead_name", "status", "lead_owner", "creation"],
            filters=date_filter,
            order_by="creation desc",
            limit=5
        )
    }


def get_ticket_analytics(view='daily', custom_start_date=None, custom_end_date=None):
    """Get ticket-related analytics"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    return {
        "status_distribution": frappe.db.get_list("CRM Ticket",
            fields=["status", "count(name) as count"],
            filters=date_filter,
            group_by="status",
            order_by="count desc"
        ),
        "issue_type_distribution": frappe.db.get_list("CRM Ticket",
            fields=["issue_type", "count(name) as count"],
            filters={**date_filter, "issue_type": ["is", "set"]},
            group_by="issue_type"
        ),
        "assigned_to_performance": frappe.db.get_list("CRM Ticket",
            fields=["assigned_to", "count(name) as count"],
            filters={**date_filter, "assigned_to": ["is", "set"]},
            group_by="assigned_to",
            order_by="count desc",
            limit=10
        ),
        "recent_tickets": frappe.db.get_list("CRM Ticket",
            fields=["name", "customer_name", "status", "priority", "assigned_to", "creation"],
            filters=date_filter,
            order_by="creation desc",
            limit=5
        )
    }


def get_task_analytics(view='daily', custom_start_date=None, custom_end_date=None):
    """Get task-related analytics"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    return {
        "status_distribution": frappe.db.get_list("CRM Task",
            fields=["status", "count(name) as count"],
            filters=date_filter,
            group_by="status",
            order_by="count desc"
        ),
        "recent_tasks": frappe.db.get_list("CRM Task",
            fields=["name", "subject", "status", "assigned_to", "creation"],
            filters=date_filter,
            order_by="creation desc",
            limit=5
        )
    }


def get_call_log_analytics(view='daily', custom_start_date=None, custom_end_date=None):
    """Get call log analytics"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    return {
        "call_type_distribution": frappe.db.get_list("CRM Call Log",
            fields=["type", "count(name) as count"],
            filters=date_filter,
            group_by="type",
            order_by="count desc"
        ),
        "call_status_distribution": frappe.db.get_list("CRM Call Log",
            fields=["status", "count(name) as count"],
            filters=date_filter,
            group_by="status",
            order_by="count desc"
        ),
        "recent_calls": frappe.db.get_list("CRM Call Log",
            fields=["name", "from", "to", "type", "status", "duration", "start_time"],
            filters=date_filter,
            order_by="start_time desc",
            limit=5
        )
    }


def get_user_performance(view='daily', custom_start_date=None, custom_end_date=None):
    """Get user performance metrics"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    users = frappe.db.get_list("User", 
        filters={"enabled": 1},
        fields=["name", "full_name", "email"]
    )
    
    performance_data = []
    for user in users:
        user_data = {
            "user": user,
            "leads_assigned": frappe.db.count("CRM Lead", filters={
                **date_filter, "lead_owner": user.name
            }),
            "tickets_assigned": frappe.db.count("CRM Ticket", filters={
                **date_filter, "assigned_to": user.name
            }),
            "tasks_assigned": frappe.db.count("CRM Task", filters={
                **date_filter, "assigned_to": user.name
            }),
            "recent_activity": get_user_recent_activity(user.name, view, custom_start_date, custom_end_date)
        }
        performance_data.append(user_data)
    
    return performance_data


def get_user_recent_activity(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Get recent activity for a specific user"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    activities = []
    
    # Recent leads created
    recent_leads = frappe.db.get_list("CRM Lead",
        filters={**date_filter, "owner": user},
        fields=["name", "lead_name", "creation"],
        order_by="creation desc",
        limit=3
    )
    activities.extend([{"type": "lead", "data": lead} for lead in recent_leads])
    
    # Recent tickets created
    recent_tickets = frappe.db.get_list("CRM Ticket",
        filters={**date_filter, "owner": user},
        fields=["name", "customer_name", "creation"],
        order_by="creation desc",
        limit=3
    )
    activities.extend([{"type": "ticket", "data": ticket} for ticket in recent_tickets])
    
    return sorted(activities, key=lambda x: x["data"]["creation"], reverse=True)[:5]


def get_recent_activities(view='daily', custom_start_date=None, custom_end_date=None):
    """Get recent activities across all modules"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    activities = []
    
    # Recent leads with proper customer name lookup
    recent_leads = frappe.db.sql("""
        SELECT 
            l.name, 
            l.status, 
            l.lead_owner, 
            l.creation,
            l.customer_id,
            COALESCE(c.customer_name, c.full_name, l.lead_name, 'Unknown Customer') as display_name
        FROM `tabCRM Lead` l
        LEFT JOIN `tabCRM Customer` c ON l.customer_id = c.name
        WHERE l.creation BETWEEN %s AND %s
        ORDER BY l.creation DESC
        LIMIT 3
    """, (start_date, end_date), as_dict=True)
    activities.extend([{"type": "lead", "data": lead} for lead in recent_leads])
    
    # Recent tickets with proper customer name lookup
    recent_tickets = frappe.db.sql("""
        SELECT 
            t.name, 
            t.status, 
            t.assigned_to, 
            t.creation,
            t.customer_id,
            COALESCE(c.customer_name, c.full_name, t.customer_name, 'Unknown Customer') as display_name
        FROM `tabCRM Ticket` t
        LEFT JOIN `tabCRM Customer` c ON t.customer_id = c.name
        WHERE t.creation BETWEEN %s AND %s
        ORDER BY t.creation DESC
        LIMIT 3
    """, (start_date, end_date), as_dict=True)
    activities.extend([{"type": "ticket", "data": ticket} for ticket in recent_tickets])
    
    # Recent tasks
    recent_tasks = frappe.db.get_list("CRM Task",
        fields=["name", "subject", "status", "assigned_to", "creation"],
        filters=date_filter,
        order_by="creation desc",
        limit=3
    )
    activities.extend([{"type": "task", "data": task} for task in recent_tasks])
    
    return sorted(activities, key=lambda x: x["data"]["creation"], reverse=True)[:10]


def get_trends_data(view='daily', custom_start_date=None, custom_end_date=None):
    """Get trends data for charts"""
    from frappe.utils import getdate, now_datetime, add_days
    from datetime import datetime, timedelta
    
    today = getdate()
    now = now_datetime()
    dates = []
    lead_counts = []
    ticket_counts = []
    
    if view == 'daily':
        # Show 24 hours (hourly data points) from 00:00 to 23:00
        for i in range(24):
            # Use proper datetime objects for hourly calculations
            hour_start = datetime.combine(today, datetime.min.time()) + timedelta(hours=i)
            hour_end = hour_start + timedelta(hours=1) if i < 23 else datetime.combine(today, datetime.max.time())
            
            dates.append(hour_start.strftime("%H:00"))
            
            lead_count = frappe.db.count("CRM Lead", filters={
                "creation": ["between", [hour_start, hour_end]]
            })
            lead_counts.append(lead_count)
            
            ticket_count = frappe.db.count("CRM Ticket", filters={
                "creation": ["between", [hour_start, hour_end]]
            })
            ticket_counts.append(ticket_count)
    elif view == 'weekly':
        # Show last 7 days (daily data points)
        for i in range(7):
            date = add_days(today, -i)
            dates.insert(0, date.strftime("%Y-%m-%d"))
            
            lead_count = frappe.db.count("CRM Lead", filters={
                "creation": ["between", [date, add_days(date, 1)]]
            })
            lead_counts.insert(0, lead_count)
            
            ticket_count = frappe.db.count("CRM Ticket", filters={
                "creation": ["between", [date, add_days(date, 1)]]
            })
            ticket_counts.insert(0, ticket_count)
    else:  # monthly
        # Show current month (daily data points from 1st to last day of current month)
        current_month = today.month
        current_year = today.year
        
        # Get first and last day of current month
        first_day = datetime(current_year, current_month, 1).date()
        if current_month == 12:
            last_day = (datetime(current_year + 1, 1, 1) - timedelta(days=1)).date()
        else:
            last_day = (datetime(current_year, current_month + 1, 1) - timedelta(days=1)).date()
        
        # Generate dates for each day of the current month
        current_date = first_day
        while current_date <= last_day:
            dates.append(current_date.strftime("%Y-%m-%d"))
            
            lead_count = frappe.db.count("CRM Lead", filters={
                "creation": ["between", [current_date, add_days(current_date, 1)]]
            })
            lead_counts.append(lead_count)
            
            ticket_count = frappe.db.count("CRM Ticket", filters={
                "creation": ["between", [current_date, add_days(current_date, 1)]]
            })
            ticket_counts.append(ticket_count)
            
            current_date = add_days(current_date, 1)
    
    return {
        "dates": dates,
        "lead_trends": lead_counts,
        "ticket_trends": ticket_counts
    }


def get_avg_response_time(view='daily', custom_start_date=None, custom_end_date=None):
    """Calculate average response time for tickets"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    tickets_with_response = frappe.db.get_list("CRM Ticket",
        fields=["first_response_time"],
        filters={**date_filter, "first_response_time": ["is", "set"]}
    )
    
    if tickets_with_response:
        total_time = sum(ticket.first_response_time or 0 for ticket in tickets_with_response)
        return round(total_time / len(tickets_with_response), 2)
    return 0


def get_formatted_date_range(start_date, end_date, view):
    """Get formatted date range string for display"""
    from frappe.utils import getdate, formatdate
    from datetime import datetime
    
    try:
        # Handle different date formats
        if isinstance(start_date, str):
            start_dt = datetime.fromisoformat(str(start_date).replace('Z', '+00:00'))
        else:
            start_dt = start_date
            
        if isinstance(end_date, str):
            end_dt = datetime.fromisoformat(str(end_date).replace('Z', '+00:00'))
        else:
            end_dt = end_date
        
        if view == 'daily':
            return f"Today ({formatdate(start_dt.date())})"
        elif view == 'weekly':
            start_formatted = formatdate(start_dt.date())
            end_formatted = formatdate(end_dt.date())
            return f"{start_formatted} - {end_formatted}"
        elif view == 'monthly':
            start_formatted = formatdate(start_dt.date())
            end_formatted = formatdate(end_dt.date())
            return f"{start_formatted} - {end_formatted}"
        else:
            return f"{formatdate(start_dt.date())} - {formatdate(end_dt.date())}"
    except Exception as e:
        # Fallback formatting
        try:
            if view == 'daily':
                return f"Today ({start_date.strftime('%Y-%m-%d') if hasattr(start_date, 'strftime') else str(start_date)})"
            else:
                start_str = start_date.strftime('%Y-%m-%d') if hasattr(start_date, 'strftime') else str(start_date)
                end_str = end_date.strftime('%Y-%m-%d') if hasattr(end_date, 'strftime') else str(end_date)
                return f"{start_str} - {end_str}"
        except:
            return f"Date Range: {view.title()}"


def get_quick_actions():
    """Get quick action buttons for dashboard"""
    return [
        {
            "title": "New Lead",
            "icon": "user-plus",
            "route": "/leads/new",
            "color": "blue"
        },
        {
            "title": "New Ticket", 
            "icon": "ticket",
            "route": "/tickets/new",
            "color": "orange"
        }
    ] 


def get_user_info(user):
    """Get basic user information"""
    try:
        print(f"🔍 DEBUG: get_user_info called for user: {user}")
        
        user_doc = frappe.get_doc("User", user)
        print(f"🔍 DEBUG: User doc retrieved successfully: {user_doc.name}")
        
        user_roles = frappe.get_roles(user)
        print(f"🔍 DEBUG: User roles: {user_roles}")
        
        primary_role = get_user_role(user)
        print(f"🔍 DEBUG: Primary role: {primary_role}")
        
        result = {
            "name": user_doc.name,
            "full_name": user_doc.full_name,
            "email": user_doc.email,
            "image": user_doc.user_image,
            "role": primary_role,
            "last_login": user_doc.last_login,
            "creation": user_doc.creation
        }
        
        print(f"🔍 DEBUG: User info result: {result}")
        return result
        
    except Exception as e:
        print(f"❌ ERROR: Error getting user info: {str(e)}")
        print(f"🔍 DEBUG: Exception type: {type(e).__name__}")
        import traceback
        print(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
        frappe.log_error(f"Error getting user info: {str(e)}")
        return {"name": user, "full_name": user, "email": "", "image": "", "role": "", "last_login": None, "creation": None}


def get_user_role(user):
    """Get user's primary role"""
    try:
        user_roles = frappe.get_roles(user)
        # Return the first non-system role
        system_roles = ['Guest', 'Administrator', 'System Manager', 'All']
        for role in user_roles:
            if role not in system_roles:
                return role
        return user_roles[0] if user_roles else "User"
    except:
        return "User"


def get_user_overview_stats(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Get user-specific overview statistics"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    return {
        "leads_assigned": frappe.db.count("CRM Lead", filters={
            **date_filter, "lead_owner": user
        }),
        "leads_created": frappe.db.count("CRM Lead", filters={
            **date_filter, "owner": user
        }),
        "tickets_assigned": frappe.db.count("CRM Ticket", filters={
            **date_filter, "assigned_to": user
        }),
        "tickets_created": frappe.db.count("CRM Ticket", filters={
            **date_filter, "owner": user
        }),
        "tasks_assigned": frappe.db.count("CRM Task", filters={
            **date_filter, "assigned_to": user
        }),
        "tasks_created": frappe.db.count("CRM Task", filters={
            **date_filter, "owner": user
        }),
        "calls_made": frappe.db.count("CRM Call Log", filters={
            **date_filter, "employee": user
        }),
        "total_duration": get_user_total_call_duration(user, view, custom_start_date, custom_end_date),
        "avg_response_time": get_user_avg_response_time(user, view, custom_start_date, custom_end_date)
    }


def get_user_lead_analytics(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Get user-specific lead analytics"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    return {
        "status_distribution": frappe.db.get_list("CRM Lead", 
            fields=["status", "count(name) as count"],
            filters={**date_filter, "lead_owner": user},
            group_by="status",
            order_by="count desc"
        ),
        "conversion_rate": get_user_lead_conversion_rate(user, view, custom_start_date, custom_end_date),
        "recent_leads": frappe.db.get_list("CRM Lead",
            fields=["name", "lead_name", "status", "creation", "follow_up_date"],
            filters={**date_filter, "lead_owner": user},
            order_by="creation desc",
            limit=5
        ),
        "leads_by_source": frappe.db.get_list("CRM Lead",
            fields=["source", "count(name) as count"],
            filters={**date_filter, "lead_owner": user},
            group_by="source",
            order_by="count desc"
        )
    }


def get_user_ticket_analytics(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Get user-specific ticket analytics"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    return {
        "status_distribution": frappe.db.get_list("CRM Ticket",
            fields=["status", "count(name) as count"],
            filters={**date_filter, "assigned_to": user},
            group_by="status",
            order_by="count desc"
        ),
        "priority_distribution": frappe.db.get_list("CRM Ticket",
            fields=["priority", "count(name) as count"],
            filters={**date_filter, "assigned_to": user},
            group_by="priority",
            order_by="count desc"
        ),
        "recent_tickets": frappe.db.get_list("CRM Ticket",
            fields=["name", "customer_name", "status", "priority", "creation"],
            filters={**date_filter, "assigned_to": user},
            order_by="creation desc",
            limit=5
        ),
        "resolution_rate": get_user_ticket_resolution_rate(user, view, custom_start_date, custom_end_date)
    }


def get_user_task_analytics(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Get user-specific task analytics"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    return {
        "status_distribution": frappe.db.get_list("CRM Task",
            fields=["status", "count(name) as count"],
            filters={**date_filter, "assigned_to": user},
            group_by="status",
            order_by="count desc"
        ),
        "priority_distribution": frappe.db.get_list("CRM Task",
            fields=["priority", "count(name) as count"],
            filters={**date_filter, "assigned_to": user},
            group_by="priority",
            order_by="count desc"
        ),
        "recent_tasks": frappe.db.get_list("CRM Task",
            fields=["name", "title", "status", "priority", "due_date", "creation"],
            filters={**date_filter, "assigned_to": user},
            order_by="creation desc",
            limit=5
        ),
        "completion_rate": get_user_task_completion_rate(user, view, custom_start_date, custom_end_date)
    }


def get_user_call_log_analytics(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Get user-specific call log analytics"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    return {
        "call_type_distribution": frappe.db.get_list("CRM Call Log",
            fields=["type", "count(name) as count"],
            filters={**date_filter, "employee": user},
            group_by="type",
            order_by="count desc"
        ),
        "call_status_distribution": frappe.db.get_list("CRM Call Log",
            fields=["status", "count(name) as count"],
            filters={**date_filter, "employee": user},
            group_by="status",
            order_by="count desc"
        ),
        "total_duration": get_user_total_call_duration(user, view, custom_start_date, custom_end_date),
        "recent_calls": frappe.db.get_list("CRM Call Log",
            fields=["name", "from", "to", "type", "status", "duration", "start_time"],
            filters={**date_filter, "employee": user},
            order_by="start_time desc",
            limit=5
        )
    }


def get_user_performance_metrics(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Get comprehensive user performance metrics"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    # Get previous period for comparison
    if view == 'daily':
        prev_start = start_date - timedelta(days=1)
        prev_end = start_date
    elif view == 'weekly':
        prev_start = start_date - timedelta(days=7)
        prev_end = start_date
    else:  # monthly
        prev_start = start_date - timedelta(days=30)
        prev_end = start_date
    
    prev_date_filter = {"creation": ["between", [prev_start, prev_end]]}
    
    # Current period metrics
    current_leads = frappe.db.count("CRM Lead", filters={**date_filter, "lead_owner": user})
    current_tickets = frappe.db.count("CRM Ticket", filters={**date_filter, "assigned_to": user})
    current_tasks = frappe.db.count("CRM Task", filters={**date_filter, "assigned_to": user})
    
    # Previous period metrics
    prev_leads = frappe.db.count("CRM Lead", filters={**prev_date_filter, "lead_owner": user})
    prev_tickets = frappe.db.count("CRM Ticket", filters={**prev_date_filter, "assigned_to": user})
    prev_tasks = frappe.db.count("CRM Task", filters={**prev_date_filter, "assigned_to": user})
    
    # Calculate improvements
    lead_improvement = calculate_improvement(current_leads, prev_leads)
    ticket_improvement = calculate_improvement(current_tickets, prev_tickets)
    task_improvement = calculate_improvement(current_tasks, prev_tasks)
    
    return {
        "current_period": {
            "leads": current_leads,
            "tickets": current_tickets,
            "tasks": current_tasks
        },
        "previous_period": {
            "leads": prev_leads,
            "tickets": prev_tickets,
            "tasks": prev_tasks
        },
        "improvements": {
            "leads": lead_improvement,
            "tickets": ticket_improvement,
            "tasks": task_improvement
        },
        "efficiency_score": calculate_efficiency_score(user, view, custom_start_date, custom_end_date)
    }


def get_user_recent_activities(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Get user-specific recent activities"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    activities = []
    
    # Recent leads with proper customer name lookup
    recent_leads = frappe.db.sql("""
        SELECT 
            l.name, 
            l.status, 
            l.creation,
            l.customer_id,
            COALESCE(c.customer_name, c.full_name, l.lead_name, 'Unknown Customer') as display_name
        FROM `tabCRM Lead` l
        LEFT JOIN `tabCRM Customer` c ON l.customer_id = c.name
        WHERE l.creation BETWEEN %s AND %s 
        AND l.lead_owner = %s
        ORDER BY l.creation DESC
        LIMIT 3
    """, (start_date, end_date, user), as_dict=True)
    
    activities.extend([{"type": "lead", "data": lead, "action": "assigned"} for lead in recent_leads])
    
    # Recent tickets with proper customer name lookup
    recent_tickets = frappe.db.sql("""
        SELECT 
            t.name, 
            t.status, 
            t.creation,
            t.customer_id,
            COALESCE(c.customer_name, c.full_name, t.customer_name, 'Unknown Customer') as display_name
        FROM `tabCRM Ticket` t
        LEFT JOIN `tabCRM Customer` c ON t.customer_id = c.name
        WHERE t.creation BETWEEN %s AND %s 
        AND t.assigned_to = %s
        ORDER BY t.creation DESC
        LIMIT 3
    """, (start_date, end_date, user), as_dict=True)
    
    activities.extend([{"type": "ticket", "data": ticket, "action": "assigned"} for ticket in recent_tickets])
    
    return sorted(activities, key=lambda x: x["data"]["creation"], reverse=True)[:10]


def get_user_trends_data(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Get user-specific trends data"""
    from frappe.utils import getdate, now_datetime, add_days
    from datetime import datetime, timedelta
    
    today = getdate()
    now = now_datetime()
    dates = []
    lead_counts = []
    ticket_counts = []
    task_counts = []
    
    if view == 'daily':
        # Show 24 hours (hourly data points) from 00:00 to 23:00
        for i in range(24):
            hour_start = datetime.combine(today, datetime.min.time()) + timedelta(hours=i)
            hour_end = hour_start + timedelta(hours=1) if i < 23 else datetime.combine(today, datetime.max.time())
            
            dates.append(hour_start.strftime("%H:00"))
            
            lead_count = frappe.db.count("CRM Lead", filters={
                "creation": ["between", [hour_start, hour_end]],
                "lead_owner": user
            })
            lead_counts.append(lead_count)
            
            ticket_count = frappe.db.count("CRM Ticket", filters={
                "creation": ["between", [hour_start, hour_end]],
                "assigned_to": user
            })
            ticket_counts.append(ticket_count)
            
            task_count = frappe.db.count("CRM Task", filters={
                "creation": ["between", [hour_start, hour_end]],
                "assigned_to": user
            })
            task_counts.append(task_count)
    elif view == 'weekly':
        # Show last 7 days (daily data points)
        for i in range(7):
            date = add_days(today, -i)
            dates.insert(0, date.strftime("%Y-%m-%d"))
            
            lead_count = frappe.db.count("CRM Lead", filters={
                "creation": ["between", [date, add_days(date, 1)]],
                "lead_owner": user
            })
            lead_counts.insert(0, lead_count)
            
            ticket_count = frappe.db.count("CRM Ticket", filters={
                "creation": ["between", [date, add_days(date, 1)]],
                "assigned_to": user
            })
            ticket_counts.insert(0, ticket_count)
            
            task_count = frappe.db.count("CRM Task", filters={
                "creation": ["between", [date, add_days(date, 1)]],
                "assigned_to": user
            })
            task_counts.insert(0, task_count)
    else:  # monthly
        # Show current month (daily data points from 1st to last day of current month)
        current_month = today.month
        current_year = today.year
        
        # Get first and last day of current month
        first_day = datetime(current_year, current_month, 1).date()
        if current_month == 12:
            last_day = (datetime(current_year + 1, 1, 1) - timedelta(days=1)).date()
        else:
            last_day = (datetime(current_year, current_month + 1, 1) - timedelta(days=1)).date()
        
        # Generate dates for each day of the current month
        current_date = first_day
        while current_date <= last_day:
            dates.append(current_date.strftime("%Y-%m-%d"))
            
            lead_count = frappe.db.count("CRM Lead", filters={
                "creation": ["between", [current_date, add_days(current_date, 1)]],
                "lead_owner": user
            })
            lead_counts.append(lead_count)
            
            ticket_count = frappe.db.count("CRM Ticket", filters={
                "creation": ["between", [current_date, add_days(current_date, 1)]],
                "assigned_to": user
            })
            ticket_counts.append(ticket_count)
            
            task_count = frappe.db.count("CRM Task", filters={
                "creation": ["between", [current_date, add_days(current_date, 1)]],
                "assigned_to": user
            })
            task_counts.append(task_count)
            
            current_date = add_days(current_date, 1)
    
    return {
        "dates": dates,
        "lead_trends": lead_counts,
        "ticket_trends": ticket_counts,
        "task_trends": task_counts
    }


def get_user_achievements(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Get user achievements and milestones"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    achievements = []
    
    # Lead conversion achievements
    converted_leads = frappe.db.count("CRM Lead", filters={
        **date_filter, "lead_owner": user, "status": "Account Opened"
    })
    if converted_leads > 0:
        achievements.append({
            "type": "success",
            "title": f"Converted {converted_leads} Lead(s)",
            "description": "Great job converting leads to customers!",
            "icon": "check-circle",
            "value": converted_leads
        })
    
    # Ticket resolution achievements
    resolved_tickets = frappe.db.count("CRM Ticket", filters={
        **date_filter, "assigned_to": user, "status": "Resolved"
    })
    if resolved_tickets > 0:
        achievements.append({
            "type": "success",
            "title": f"Resolved {resolved_tickets} Ticket(s)",
            "description": "Excellent customer support work!",
            "icon": "award",
            "value": resolved_tickets
        })
    
    # Task completion achievements
    completed_tasks = frappe.db.count("CRM Task", filters={
        **date_filter, "assigned_to": user, "status": "Completed"
    })
    if completed_tasks > 0:
        achievements.append({
            "type": "success",
            "title": f"Completed {completed_tasks} Task(s)",
            "description": "Outstanding task management!",
            "icon": "check-square",
            "value": completed_tasks
        })
    
    # Call volume achievements
    total_calls = frappe.db.count("CRM Call Log", filters={
        **date_filter, "employee": user
    })
    if total_calls >= 10:
        achievements.append({
            "type": "info",
            "title": f"Made {total_calls} Calls",
            "description": "Excellent communication activity!",
            "icon": "phone",
            "value": total_calls
        })
    
    return achievements


def get_user_goals(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Get user goals and targets with actual progress data"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    # Calculate actual progress from database
    leads_assigned = frappe.db.count("CRM Lead", filters={
        **date_filter, "lead_owner": user
    })
    leads_converted = frappe.db.count("CRM Lead", filters={
        **date_filter, "lead_owner": user, "status": "Account Opened"
    })
    
    tickets_assigned = frappe.db.count("CRM Ticket", filters={
        **date_filter, "assigned_to": user
    })
    tickets_resolved = frappe.db.count("CRM Ticket", filters={
        **date_filter, "assigned_to": user, "status": "Resolved"
    })
    
    tasks_assigned = frappe.db.count("CRM Task", filters={
        **date_filter, "assigned_to": user
    })
    tasks_completed = frappe.db.count("CRM Task", filters={
        **date_filter, "assigned_to": user, "status": "Done"
    })
    
    calls_made = frappe.db.count("CRM Call Log", filters={
        **date_filter, "employee": user
    })
    
    # Dynamic goal calculation based on actual assigned/created items
    # For leads: Goal is to convert ALL assigned leads to accounts
    lead_goal = leads_assigned if leads_assigned > 0 else 1
    
    # For tickets: Goal is to resolve ALL assigned tickets
    ticket_goal = tickets_assigned if tickets_assigned > 0 else 1
    
    # For tasks: Goal is to complete ALL assigned tasks
    task_goal = tasks_assigned if tasks_assigned > 0 else 1
    
    # For calls: Goal is to maintain activity (minimum 5 calls, or 20% more than current)
    call_goal = max(5, int(calls_made * 1.2)) if calls_made > 0 else 5
    
    return [
        {
            "title": "Lead Conversion Goal",
            "target": lead_goal,
            "current": leads_converted,
            "description": f"Convert {lead_goal} leads to customers (Currently {leads_converted}/{leads_assigned} assigned)",
            "icon": "target",
            "type": "leads",
            "progress_percentage": round((leads_converted / max(lead_goal, 1)) * 100, 1),
            "assigned_count": leads_assigned,
            "goal_type": "conversion"
        },
        {
            "title": "Ticket Resolution Goal",
            "target": ticket_goal,
            "current": tickets_resolved,
            "description": f"Resolve {ticket_goal} support tickets (Currently {tickets_resolved}/{tickets_assigned} assigned)",
            "icon": "check-circle",
            "type": "tickets",
            "progress_percentage": round((tickets_resolved / max(ticket_goal, 1)) * 100, 1),
            "assigned_count": tickets_assigned,
            "goal_type": "resolution"
        },
        {
            "title": "Task Completion Goal",
            "target": task_goal,
            "current": tasks_completed,
            "description": f"Complete {task_goal} assigned tasks (Currently {tasks_completed}/{tasks_assigned} assigned)",
            "icon": "list",
            "type": "tasks",
            "progress_percentage": round((tasks_completed / max(task_goal, 1)) * 100, 1),
            "assigned_count": tasks_assigned,
            "goal_type": "completion"
        },
        {
            "title": "Communication Goal",
            "target": call_goal,
            "current": calls_made,
            "description": f"Make {call_goal} customer calls (Currently {calls_made} calls made)",
            "icon": "phone",
            "type": "calls",
            "progress_percentage": round((calls_made / max(call_goal, 1)) * 100, 1),
            "goal_type": "activity"
        }
    ]


def get_user_peak_hours(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Get user's peak activity hours based on call logs and activities"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    # Get call log data for peak hours analysis
    call_logs = frappe.db.get_list("CRM Call Log",
        fields=["start_time", "duration", "type", "status"],
        filters={**date_filter, "employee": user, "status": "Completed"}
    )
    
    # Initialize hourly data
    hourly_data = {i: {"calls": 0, "total_duration": 0, "activities": 0} for i in range(24)}
    
    # Process call logs
    for call in call_logs:
        if call.start_time:
            try:
                hour = int(str(call.start_time).split(' ')[1].split(':')[0])
                hourly_data[hour]["calls"] += 1
                hourly_data[hour]["total_duration"] += call.duration or 0
            except:
                continue
    
    # Get other activities for comprehensive analysis
    leads_created = frappe.db.get_list("CRM Lead",
        fields=["creation"],
        filters={**date_filter, "owner": user}
    )
    
    tickets_created = frappe.db.get_list("CRM Ticket",
        fields=["creation"],
        filters={**date_filter, "owner": user}
    )
    
    tasks_created = frappe.db.get_list("CRM Task",
        fields=["creation"],
        filters={**date_filter, "owner": user}
    )
    
    # Process activity timestamps
    for activity in leads_created + tickets_created + tasks_created:
        if activity.creation:
            try:
                hour = int(str(activity.creation).split(' ')[1].split(':')[0])
                hourly_data[hour]["activities"] += 1
            except:
                continue
    
    # Find peak hours
    peak_hours = []
    max_activity = 0
    
    for hour, data in hourly_data.items():
        total_activity = data["calls"] + data["activities"]
        if total_activity > max_activity:
            max_activity = total_activity
            peak_hours = [hour]
        elif total_activity == max_activity and total_activity > 0:
            peak_hours.append(hour)
    
    # Format hourly data for charts
    hourly_chart_data = []
    for hour in range(24):
        data = hourly_data[hour]
        hourly_chart_data.append({
            "hour": f"{hour:02d}:00",
            "calls": data["calls"],
            "duration": round(data["total_duration"], 2),
            "activities": data["activities"],
            "total_activity": data["calls"] + data["activities"]
        })
    
    return {
        "peak_hours": peak_hours,
        "max_activity": max_activity,
        "hourly_data": hourly_chart_data,
        "total_calls": sum(data["calls"] for data in hourly_data.values()),
        "total_duration": sum(data["total_duration"] for data in hourly_data.values()),
        "total_activities": sum(data["activities"] for data in hourly_data.values())
    }


# Helper functions
def get_user_avg_response_time(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Calculate average response time for user's tickets"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    tickets_with_response = frappe.db.get_list("CRM Ticket",
        fields=["first_response_time"],
        filters={**date_filter, "assigned_to": user, "first_response_time": ["is", "set"]}
    )
    
    if tickets_with_response:
        total_time = sum(ticket.first_response_time or 0 for ticket in tickets_with_response)
        return round(total_time / len(tickets_with_response), 2)
    return 0


def get_user_lead_conversion_rate(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Calculate user's lead conversion rate"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    total_leads = frappe.db.count("CRM Lead", filters={**date_filter, "lead_owner": user})
    converted_leads = frappe.db.count("CRM Lead", filters={
        **date_filter, "lead_owner": user, "status": "Account Opened"
    })
    
    if total_leads > 0:
        return round((converted_leads / total_leads) * 100, 1)
    return 0


def get_user_ticket_resolution_rate(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Calculate user's ticket resolution rate"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    total_tickets = frappe.db.count("CRM Ticket", filters={**date_filter, "assigned_to": user})
    resolved_tickets = frappe.db.count("CRM Ticket", filters={
        **date_filter, "assigned_to": user, "status": "Resolved"
    })
    
    if total_tickets > 0:
        return round((resolved_tickets / total_tickets) * 100, 1)
    return 0


def get_user_task_completion_rate(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Calculate user's task completion rate"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    total_tasks = frappe.db.count("CRM Task", filters={**date_filter, "assigned_to": user})
    completed_tasks = frappe.db.count("CRM Task", filters={
        **date_filter, "assigned_to": user, "status": "Completed"
    })
    
    if total_tasks > 0:
        return round((completed_tasks / total_tasks) * 100, 1)
    return 0


def get_user_total_call_duration(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Calculate total call duration for user"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    call_logs = frappe.db.get_list("CRM Call Log",
        fields=["duration"],
        filters={**date_filter, "employee": user, "duration": ["is", "set"]}
    )
    
    total_duration = sum(call.duration or 0 for call in call_logs)
    return round(total_duration, 2)


def calculate_improvement(current, previous):
    """Calculate improvement percentage"""
    if previous == 0:
        return 100 if current > 0 else 0
    return round(((current - previous) / previous) * 100, 1)


def calculate_efficiency_score(user, view='daily', custom_start_date=None, custom_end_date=None):
    """Calculate overall efficiency score for user"""
    start_date, end_date = get_date_range(view, custom_start_date, custom_end_date)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    # Get various metrics
    lead_conversion_rate = get_user_lead_conversion_rate(user, view, custom_start_date, custom_end_date)
    ticket_resolution_rate = get_user_ticket_resolution_rate(user, view, custom_start_date, custom_end_date)
    task_completion_rate = get_user_task_completion_rate(user, view, custom_start_date, custom_end_date)
    avg_response_time = get_user_avg_response_time(user, view, custom_start_date, custom_end_date)
    
    # Calculate efficiency score (0-100)
    # Higher conversion rates and completion rates = higher score
    # Lower response time = higher score
    score = 0
    
    # Lead conversion (30% weight)
    score += (lead_conversion_rate / 100) * 30
    
    # Ticket resolution (30% weight)
    score += (ticket_resolution_rate / 100) * 30
    
    # Task completion (25% weight)
    score += (task_completion_rate / 100) * 25
    
    # Response time (15% weight) - inverse relationship
    if avg_response_time > 0:
        # Lower response time = higher score
        response_score = max(0, 15 - (avg_response_time / 2))
        score += response_score
    
    return round(score, 1) 