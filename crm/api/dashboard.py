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
    from frappe.utils import getdate, now_datetime, add_days, add_to_date
    from datetime import datetime, timedelta
    
    today = getdate()
    now = now_datetime()
    
    if view == 'daily':
        # For daily view, use the entire day from 00:00:00 to 23:59:59
        start_date = get_datetime(today)  # Start of day
        end_date = get_datetime(add_to_date(today, days=1))  # Start of next day as datetime
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
    today = getdate()
    dates = []
    lead_counts = []
    ticket_counts = []
    
    if view == 'daily':
        # Show last 24 hours (hourly data points)
        for i in range(24):
            hour_start = add_days(today, 0)  # Today
            hour_start = hour_start.replace(hour=i, minute=0, second=0, microsecond=0)
            hour_end = hour_start.replace(hour=i+1, minute=0, second=0, microsecond=0) if i < 23 else today.replace(hour=23, minute=59, second=59, microsecond=999999)
            
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