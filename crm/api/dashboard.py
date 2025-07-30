import frappe
from frappe import _
from frappe.utils import getdate, add_days, get_datetime
from datetime import datetime, timedelta
import json


@frappe.whitelist()
def get_dashboard_data(view='daily', _refresh=None):
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
        start_date, end_date = get_date_range(view)
        
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
                "overview": get_overview_stats(view),
                "lead_analytics": get_lead_analytics(view),
                "ticket_analytics": get_ticket_analytics(view),
                "task_analytics": get_task_analytics(view),
                "call_log_analytics": get_call_log_analytics(view),
                "user_performance": get_user_performance(view),
                "recent_activities": get_recent_activities(view),
                "trends": get_trends_data(view),
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


def get_date_range(view):
    """Get date range based on view type"""
    from frappe.utils import getdate, now_datetime, add_days, add_to_date, get_datetime
    from datetime import datetime, timedelta
    
    today = getdate()
    now = now_datetime()
    
    if view == 'daily':
        # For daily view, use the entire day from 00:00:00 to 23:59:59
        # Fix: Use explicit datetime objects to avoid timezone issues
        start_date = datetime.combine(today, datetime.min.time())  # Start of day (00:00:00)
        end_date = datetime.combine(today, datetime.max.time())    # End of day (23:59:59.999999)
    elif view == 'weekly':
        start_date = get_datetime(add_days(today, -7))
        end_date = now
    elif view == 'monthly':
        start_date = get_datetime(add_days(today, -30))
        end_date = now
    else:
        start_date = get_datetime(today)
        end_date = now
    
    return start_date, end_date


def get_overview_stats(view='daily'):
    """Get high-level overview statistics"""
    start_date, end_date = get_date_range(view)
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
        "avg_response_time": get_avg_response_time(view)
    }


def get_lead_analytics(view='daily'):
    """Get lead-related analytics"""
    start_date, end_date = get_date_range(view)
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


def get_ticket_analytics(view='daily'):
    """Get ticket-related analytics"""
    start_date, end_date = get_date_range(view)
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


def get_task_analytics(view='daily'):
    """Get task-related analytics"""
    start_date, end_date = get_date_range(view)
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


def get_call_log_analytics(view='daily'):
    """Get call log analytics"""
    start_date, end_date = get_date_range(view)
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


def get_user_performance(view='daily'):
    """Get user performance metrics"""
    start_date, end_date = get_date_range(view)
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
            "recent_activity": get_user_recent_activity(user.name, view)
        }
        performance_data.append(user_data)
    
    return performance_data


def get_user_recent_activity(user, view='daily'):
    """Get recent activity for a specific user"""
    start_date, end_date = get_date_range(view)
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


def get_recent_activities(view='daily'):
    """Get recent activities across all modules"""
    start_date, end_date = get_date_range(view)
    date_filter = {"creation": ["between", [start_date, end_date]]}
    
    activities = []
    
    # Recent leads
    recent_leads = frappe.db.get_list("CRM Lead",
        fields=["name", "lead_name", "status", "lead_owner", "creation"],
        filters=date_filter,
        order_by="creation desc",
        limit=3
    )
    activities.extend([{"type": "lead", "data": lead} for lead in recent_leads])
    
    # Recent tickets
    recent_tickets = frappe.db.get_list("CRM Ticket",
        fields=["name", "customer_name", "status", "assigned_to", "creation"],
        filters=date_filter,
        order_by="creation desc",
        limit=3
    )
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


def get_trends_data(view='daily'):
    """Get trends data for charts"""
    from frappe.utils import getdate, now_datetime, add_days
    from datetime import datetime, timedelta
    
    today = getdate()
    now = now_datetime()
    dates = []
    lead_counts = []
    ticket_counts = []
    
    if view == 'daily':
        # Show last 24 hours (hourly data points)
        for i in range(24):
            # Fix: Use proper datetime objects for hourly calculations
            hour_start = datetime.combine(today, datetime.min.time()) + timedelta(hours=i)
            hour_end = hour_start + timedelta(hours=1) if i < 23 else datetime.combine(today, datetime.max.time())
            
            dates.insert(0, hour_start.strftime("%H:00"))
            
            lead_count = frappe.db.count("CRM Lead", filters={
                "creation": ["between", [hour_start, hour_end]]
            })
            lead_counts.insert(0, lead_count)
            
            ticket_count = frappe.db.count("CRM Ticket", filters={
                "creation": ["between", [hour_start, hour_end]]
            })
            ticket_counts.insert(0, ticket_count)
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
        # Show last 30 days (daily data points)
        for i in range(30):
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
    
    return {
        "dates": dates,
        "lead_trends": lead_counts,
        "ticket_trends": ticket_counts
    }


def get_avg_response_time(view='daily'):
    """Calculate average response time for tickets"""
    start_date, end_date = get_date_range(view)
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