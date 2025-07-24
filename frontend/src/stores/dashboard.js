import { ref, computed } from 'vue'
import { frappeRequest } from 'frappe-ui'

export function useDashboard() {
  const loading = ref(false)
  const error = ref(null)
  const dashboardData = ref(null)
  const lastUpdated = ref(null)

  const fetchDashboardData = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await frappeRequest({ 
        url: '/api/method/crm.api.dashboard.get_dashboard_data' 
      })
      dashboardData.value = response
      lastUpdated.value = new Date()
    } catch (err) {
      error.value = err.message || 'Failed to load dashboard data'
      console.error('Dashboard API Error:', err)
    } finally {
      loading.value = false
    }
  }

  const refreshData = () => {
    return fetchDashboardData()
  }

  // Computed properties for different dashboard sections
  const overview = computed(() => dashboardData.value?.overview || {})
  const leadAnalytics = computed(() => dashboardData.value?.lead_analytics || {})
  const ticketAnalytics = computed(() => dashboardData.value?.ticket_analytics || {})
  const taskAnalytics = computed(() => dashboardData.value?.task_analytics || {})
  const callLogAnalytics = computed(() => dashboardData.value?.call_log_analytics || {})
  const userPerformance = computed(() => dashboardData.value?.user_performance || [])
  const recentActivities = computed(() => dashboardData.value?.recent_activities || [])
  const trends = computed(() => dashboardData.value?.trends || {})
  const quickActions = computed(() => dashboardData.value?.quick_actions || [])

  // Stats cards data
  const statsCards = computed(() => [
    {
      title: 'Total Leads',
      value: overview.value.total_leads || 0,
      icon: 'user-plus',
      color: 'blue',
      change: null
    },
    {
      title: 'Total Tickets',
      value: overview.value.total_tickets || 0,
      icon: 'ticket',
      color: 'orange',
      change: null
    },
    {
      title: 'Total Tasks',
      value: overview.value.total_tasks || 0,
      icon: 'check-square',
      color: 'green',
      change: null
    },
    {
      title: 'Call Logs',
      value: overview.value.total_call_logs || 0,
      icon: 'phone',
      color: 'purple',
      change: null
    },
    {
      title: 'New Leads (Week)',
      value: overview.value.new_leads_this_week || 0,
      icon: 'trending-up',
      color: 'blue',
      change: null
    },
    {
      title: 'Resolved Tickets (Week)',
      value: overview.value.resolved_tickets_this_week || 0,
      icon: 'check-circle',
      color: 'green',
      change: null
    },
    {
      title: 'Conversion Rate',
      value: `${overview.value.conversion_rate || 0}%`,
      icon: 'percent',
      color: 'yellow',
      change: null
    },
    {
      title: 'Avg Response Time',
      value: `${overview.value.avg_response_time || 0}h`,
      icon: 'clock',
      color: 'red',
      change: null
    }
  ])

  // Chart data
  const leadStatusChart = computed(() => 
    leadAnalytics.value.status_distribution?.map(item => ({
      label: item.status,
      value: item.count
    })) || []
  )

  const ticketStatusChart = computed(() => 
    ticketAnalytics.value.status_distribution?.map(item => ({
      label: item.status,
      value: item.count
    })) || []
  )

  const ticketPriorityChart = computed(() => 
    ticketAnalytics.value.priority_distribution?.map(item => ({
      label: item.priority,
      value: item.count
    })) || []
  )

  const leadTypeChart = computed(() => 
    leadAnalytics.value.lead_type_distribution?.map(item => ({
      label: item.lead_type,
      value: item.count
    })) || []
  )

  const callTypeChart = computed(() => 
    callLogAnalytics.value.call_type_distribution?.map(item => ({
      label: item.type,
      value: item.count
    })) || []
  )

  const trendsChart = computed(() => {
    if (!trends.value.dates || !trends.value.lead_trends) return []
    
    return trends.value.dates.map((date, index) => ({
      label: date,
      leads: trends.value.lead_trends[index] || 0,
      tickets: trends.value.ticket_trends[index] || 0
    }))
  })

  // User performance data
  const topPerformers = computed(() => {
    return userPerformance.value
      .filter(user => user.leads_assigned > 0 || user.tickets_assigned > 0)
      .sort((a, b) => (b.leads_assigned + b.tickets_assigned) - (a.leads_assigned + a.tickets_assigned))
      .slice(0, 5)
  })

  return {
    // State
    loading,
    error,
    dashboardData,
    lastUpdated,
    
    // Actions
    fetchDashboardData,
    refreshData,
    
    // Computed
    overview,
    leadAnalytics,
    ticketAnalytics,
    taskAnalytics,
    callLogAnalytics,
    userPerformance,
    recentActivities,
    trends,
    quickActions,
    
    // Chart data
    statsCards,
    leadStatusChart,
    ticketStatusChart,
    ticketPriorityChart,
    leadTypeChart,
    callTypeChart,
    trendsChart,
    topPerformers
  }
} 