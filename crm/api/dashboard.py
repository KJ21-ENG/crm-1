import frappe
from frappe import _
from frappe.utils import getdate, add_days, get_datetime
from datetime import datetime, timedelta
import json


@frappe.whitelist()
def get_dashboard_data():
    """Get comprehensive dashboard data for CRM"""
    try:
        return {
            "overview": get_overview_stats(),
            "lead_analytics": get_lead_analytics(),
            "ticket_analytics": get_ticket_analytics(),
            "task_analytics": get_task_analytics(),
            "call_log_analytics": get_call_log_analytics(),
            "user_performance": get_user_performance(),
            "recent_activities": get_recent_activities(),
            "trends": get_trends_data(),
            "quick_actions": get_quick_actions()
        }
    except Exception as e:
        frappe.log_error(f"Dashboard API Error: {str(e)}")
        return {"error": str(e)}


def get_overview_stats():
    """Get high-level overview statistics"""
    today = getdate()
    week_start = add_days(today, -7)
    month_start = add_days(today, -30)
    
    return {
        "total_leads": frappe.db.count("CRM Lead"),
        "total_tickets": frappe.db.count("CRM Ticket"),
        "total_deals": frappe.db.count("CRM Deal"),
        "total_tasks": frappe.db.count("CRM Task"),
        "total_call_logs": frappe.db.count("CRM Call Log"),
        "new_leads_this_week": frappe.db.count("CRM Lead", filters={
            "creation": [">=", week_start]
        }),
        "new_tickets_this_week": frappe.db.count("CRM Ticket", filters={
            "creation": [">=", week_start]
        }),
        "resolved_tickets_this_week": frappe.db.count("CRM Ticket", filters={
            "status": ["in", ["Resolved", "Closed"]],
            "modified": [">=", week_start]
        }),
        "conversion_rate": get_conversion_rate(),
        "avg_response_time": get_avg_response_time()
    }


def get_lead_analytics():
    """Get lead-related analytics"""
    return {
        "status_distribution": frappe.db.get_list("CRM Lead", 
            fields=["status", "count(name) as count"],
            group_by="status",
            order_by="count desc"
        ),
        "lead_type_distribution": frappe.db.get_list("CRM Lead",
            fields=["lead_type", "count(name) as count"],
            filters={"lead_type": ["is", "set"]},
            group_by="lead_type"
        ),
        "lead_owner_performance": frappe.db.get_list("CRM Lead",
            fields=["lead_owner", "count(name) as count"],
            filters={"lead_owner": ["is", "set"]},
            group_by="lead_owner",
            order_by="count desc",
            limit=10
        ),
        "recent_leads": frappe.db.get_list("CRM Lead",
            fields=["name", "lead_name", "status", "lead_owner", "creation"],
            order_by="creation desc",
            limit=5
        )
    }


def get_ticket_analytics():
    """Get ticket-related analytics"""
    return {
        "status_distribution": frappe.db.get_list("CRM Ticket",
            fields=["status", "count(name) as count"],
            group_by="status",
            order_by="count desc"
        ),
        "priority_distribution": frappe.db.get_list("CRM Ticket",
            fields=["priority", "count(name) as count"],
            group_by="priority",
            order_by="count desc"
        ),
        "issue_type_distribution": frappe.db.get_list("CRM Ticket",
            fields=["issue_type", "count(name) as count"],
            filters={"issue_type": ["is", "set"]},
            group_by="issue_type"
        ),
        "assigned_to_performance": frappe.db.get_list("CRM Ticket",
            fields=["assigned_to", "count(name) as count"],
            filters={"assigned_to": ["is", "set"]},
            group_by="assigned_to",
            order_by="count desc",
            limit=10
        ),
        "recent_tickets": frappe.db.get_list("CRM Ticket",
            fields=["name", "customer_name", "status", "priority", "assigned_to", "creation"],
            order_by="creation desc",
            limit=5
        )
    }


def get_task_analytics():
    """Get task-related analytics"""
    return {
        "status_distribution": frappe.db.get_list("CRM Task",
            fields=["status", "count(name) as count"],
            group_by="status",
            order_by="count desc"
        ),
        "recent_tasks": frappe.db.get_list("CRM Task",
            fields=["name", "subject", "status", "assigned_to", "creation"],
            order_by="creation desc",
            limit=5
        )
    }


def get_call_log_analytics():
    """Get call log analytics"""
    return {
        "call_type_distribution": frappe.db.get_list("CRM Call Log",
            fields=["type", "count(name) as count"],
            group_by="type",
            order_by="count desc"
        ),
        "call_status_distribution": frappe.db.get_list("CRM Call Log",
            fields=["status", "count(name) as count"],
            group_by="status",
            order_by="count desc"
        ),
        "recent_calls": frappe.db.get_list("CRM Call Log",
            fields=["name", "from", "to", "type", "status", "duration", "start_time"],
            order_by="start_time desc",
            limit=5
        )
    }


def get_user_performance():
    """Get user performance metrics"""
    users = frappe.db.get_list("User", 
        filters={"enabled": 1},
        fields=["name", "full_name", "email"]
    )
    
    performance_data = []
    for user in users:
        user_data = {
            "user": user,
            "leads_assigned": frappe.db.count("CRM Lead", filters={"lead_owner": user.name}),
            "tickets_assigned": frappe.db.count("CRM Ticket", filters={"assigned_to": user.name}),
            "tasks_assigned": frappe.db.count("CRM Task", filters={"assigned_to": user.name}),
            "recent_activity": get_user_recent_activity(user.name)
        }
        performance_data.append(user_data)
    
    return performance_data


def get_user_recent_activity(user):
    """Get recent activity for a specific user"""
    activities = []
    
    # Recent leads created
    recent_leads = frappe.db.get_list("CRM Lead",
        filters={"owner": user},
        fields=["name", "lead_name", "creation"],
        order_by="creation desc",
        limit=3
    )
    activities.extend([{"type": "lead", "data": lead} for lead in recent_leads])
    
    # Recent tickets created
    recent_tickets = frappe.db.get_list("CRM Ticket",
        filters={"owner": user},
        fields=["name", "customer_name", "creation"],
        order_by="creation desc",
        limit=3
    )
    activities.extend([{"type": "ticket", "data": ticket} for ticket in recent_tickets])
    
    return sorted(activities, key=lambda x: x["data"]["creation"], reverse=True)[:5]


def get_recent_activities():
    """Get recent activities across all modules"""
    activities = []
    
    # Recent leads
    recent_leads = frappe.db.get_list("CRM Lead",
        fields=["name", "lead_name", "status", "lead_owner", "creation"],
        order_by="creation desc",
        limit=3
    )
    activities.extend([{"type": "lead", "data": lead} for lead in recent_leads])
    
    # Recent tickets
    recent_tickets = frappe.db.get_list("CRM Ticket",
        fields=["name", "customer_name", "status", "assigned_to", "creation"],
        order_by="creation desc",
        limit=3
    )
    activities.extend([{"type": "ticket", "data": ticket} for ticket in recent_tickets])
    
    # Recent tasks
    recent_tasks = frappe.db.get_list("CRM Task",
        fields=["name", "subject", "status", "assigned_to", "creation"],
        order_by="creation desc",
        limit=3
    )
    activities.extend([{"type": "task", "data": task} for task in recent_tasks])
    
    return sorted(activities, key=lambda x: x["data"]["creation"], reverse=True)[:10]


def get_trends_data():
    """Get trends data for charts"""
    today = getdate()
    dates = []
    lead_counts = []
    ticket_counts = []
    
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


def get_conversion_rate():
    """Calculate lead conversion rate"""
    total_leads = frappe.db.count("CRM Lead")
    converted_leads = frappe.db.count("CRM Lead", filters={"converted": 1})
    
    if total_leads > 0:
        return round((converted_leads / total_leads) * 100, 2)
    return 0


def get_avg_response_time():
    """Calculate average response time for tickets"""
    tickets_with_response = frappe.db.get_list("CRM Ticket",
        fields=["first_response_time"],
        filters={"first_response_time": ["is", "set"]}
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
        },
        {
            "title": "New Task",
            "icon": "check-square",
            "route": "/tasks/new", 
            "color": "green"
        },
        {
            "title": "New Deal",
            "icon": "briefcase",
            "route": "/deals/new",
            "color": "purple"
        }
    ] 