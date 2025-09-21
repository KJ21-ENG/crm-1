import { ref, computed } from 'vue'
import { frappeRequest } from 'frappe-ui'

export function useDashboard() {
  const loading = ref(false)
  const error = ref(null)
  const dashboardData = ref(null)
  const userDashboardData = ref(null)
  const lastUpdated = ref(null)
  const currentView = ref('daily') // 'daily', 'weekly', 'monthly', 'custom'
  const customDateRange = ref({ start: null, end: null })
  const autoRefreshInterval = ref(null)
  // Track which user id the latest user-specific fetch returned for ('' = current user)
  const lastFetchedUserId = ref('')

  const fetchDashboardData = async (view = 'daily', customStartDate = null, customEndDate = null) => {
    loading.value = true
    error.value = null
    
    try {
      // Clear any existing data first
      dashboardData.value = null
      
      const params = { 
        view,
        _t: Date.now(), // Cache busting parameter
        _refresh: 'true' // Force refresh flag
      }
      
      // Add custom date parameters if provided
      if (view === 'custom' && customStartDate && customEndDate) {
        params.custom_start_date = customStartDate
        params.custom_end_date = customEndDate
        // Store custom date range for tooltip display
        customDateRange.value = { start: customStartDate, end: customEndDate }
      }
      
      const response = await frappeRequest({ 
        url: '/api/method/crm.api.dashboard.get_dashboard_data',
        params,
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      })
      
      // Log debug information if available
      if (response._debug) {
        console.log('Dashboard Debug Info:', response._debug)
      }
      
      // Log the entire response for debugging
      console.log('Dashboard API Response:', response)
      console.log('Overview data:', response.overview)
      
      // FIX: Use response.message if present (Frappe API compatibility)
      dashboardData.value = response.message || response
      lastUpdated.value = new Date()
    } catch (err) {
      error.value = err.message || 'Failed to load dashboard data'
      console.error('Dashboard API Error:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchUserDashboardData = async (view = 'daily', customStartDate = null, customEndDate = null, targetUserId = null) => {
    console.log('🔍 DEBUG: fetchUserDashboardData called with view:', view, 'customStartDate:', customStartDate, 'customEndDate:', customEndDate, 'targetUserId:', targetUserId)
    loading.value = true
    error.value = null
    
    try {
      // Clear any existing user data first
      userDashboardData.value = null
      console.log('🔍 DEBUG: Cleared existing user dashboard data')
      
      const requestParams = { 
        view,
        _t: Date.now(), // Cache busting parameter
        _refresh: 'true' // Force refresh flag
      }
      
      // Add custom date parameters if provided
      if (view === 'custom' && customStartDate && customEndDate) {
        requestParams.custom_start_date = customStartDate
        requestParams.custom_end_date = customEndDate
        // Store custom date range for tooltip display
        customDateRange.value = { start: customStartDate, end: customEndDate }
      }
      
      // Add target user ID if provided (for admin viewing other users)
      if (targetUserId) {
        requestParams.target_user_id = targetUserId
      }
      
      console.log('🔍 DEBUG: Request params:', requestParams)
      console.log('🔍 DEBUG: Making request to /api/method/crm.api.dashboard.get_user_dashboard_data')
      
      const response = await frappeRequest({ 
        url: '/api/method/crm.api.dashboard.get_user_dashboard_data',
        params: requestParams,
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      })
      
      console.log('🔍 DEBUG: Raw response received:', response)
      console.log('🔍 DEBUG: Response type:', typeof response)
      console.log('🔍 DEBUG: Response keys:', Object.keys(response))
      
      // Log debug information if available
      if (response._debug) {
        console.log('🔍 DEBUG: User Dashboard Debug Info:', response._debug)
      }
      
      // Check for error responses
      if (response.error) {
        console.error('❌ ERROR: API returned error:', response.error)
        throw new Error(response.error)
      }
      
      if (response.exc_type) {
        console.error('❌ ERROR: API exception:', response.exc_type, response._server_messages)
        throw new Error(`API Exception: ${response.exc_type}`)
      }
      
      console.log('🔍 DEBUG: Processing successful response')
      
      // FIX: Use response.message if present (Frappe API compatibility)
      const processedData = response.message || response
      console.log('🔍 DEBUG: Processed data:', processedData)
      
      userDashboardData.value = processedData
      lastUpdated.value = new Date()
      // Record which user the backend responded with (empty => current user)
      lastFetchedUserId.value = targetUserId || ''
      
      console.log('✅ SUCCESS: User dashboard data loaded successfully')
      console.log('🔍 DEBUG: Final userDashboardData:', userDashboardData.value)
      
    } catch (err) {
      console.error('❌ ERROR: User Dashboard API Error:', err)
      console.error('🔍 DEBUG: Error details:', {
        message: err.message,
        stack: err.stack,
        name: err.name
      })
      
      error.value = err.message || 'Failed to load user dashboard data'
    } finally {
      loading.value = false
      console.log('🔍 DEBUG: fetchUserDashboardData completed, loading set to false')
      // Ensure UI selector sync even if fetch failed
      lastFetchedUserId.value = targetUserId || ''
    }
  }

  const refreshData = () => {
    return fetchDashboardData(currentView.value)
  }

  const refreshUserData = () => {
    return fetchUserDashboardData(currentView.value)
  }

  const refreshDashboard = () => {
    // Force a complete refresh by clearing cache and refetching
    dashboardData.value = null
    userDashboardData.value = null
    lastUpdated.value = null
    error.value = null
    
    // Add a small delay to ensure cache is cleared
    setTimeout(() => {
      Promise.all([
        fetchDashboardData(currentView.value),
        fetchUserDashboardData(currentView.value)
      ])
    }, 100)
  }

  const changeView = (view, targetUserId = null) => {
    console.log('🔍 DEBUG: changeView called with:', view)
    console.log('🔍 DEBUG: Previous currentView:', currentView.value)
    currentView.value = view
    console.log('🔍 DEBUG: New currentView:', currentView.value)

    // Don't fetch data for custom view - it will be handled by custom date picker
    if (view === 'custom') {
      console.log('🔍 DEBUG: Custom view selected, waiting for date selection')
      return Promise.resolve()
    }

    // Return the Promise so callers can await view change completion and data loading
    return Promise.all([
      fetchDashboardData(view),
      fetchUserDashboardData(view, null, null, targetUserId)
    ])
  }

  const startAutoRefresh = () => {
    // Auto-refresh disabled - function kept for compatibility but does nothing
    console.log('Auto-refresh is disabled')
  }

  const stopAutoRefresh = () => {
    // Auto-refresh disabled - function kept for compatibility but does nothing
    if (autoRefreshInterval.value) {
      clearInterval(autoRefreshInterval.value)
      autoRefreshInterval.value = null
    }
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
  const dateRange = computed(() => dashboardData.value?.date_range || {})

  // User dashboard computed properties
  const userInfo = computed(() => userDashboardData.value?.user_info || {})
  const userOverview = computed(() => userDashboardData.value?.overview || {})
  const userLeadAnalytics = computed(() => userDashboardData.value?.lead_analytics || {})
  const userTicketAnalytics = computed(() => userDashboardData.value?.ticket_analytics || {})
  const userTaskAnalytics = computed(() => userDashboardData.value?.task_analytics || {})
  const userCallLogAnalytics = computed(() => userDashboardData.value?.call_log_analytics || {})
  const userPerformanceMetrics = computed(() => userDashboardData.value?.performance_metrics || {})
  const userRecentActivities = computed(() => userDashboardData.value?.recent_activities || [])
  const userTrends = computed(() => userDashboardData.value?.trends || {})
  const userAchievements = computed(() => userDashboardData.value?.achievements || [])
  const userGoals = computed(() => userDashboardData.value?.goals || [])
  const userPeakHours = computed(() => userDashboardData.value?.peak_hours || {})

  // Custom date range formatting
  const customDateRangeFormatted = computed(() => {
    if (currentView.value === 'custom' && customDateRange.value.start && customDateRange.value.end) {
      const startDate = new Date(customDateRange.value.start)
      const endDate = new Date(customDateRange.value.end)
      const formatDate = (date) => date.toLocaleDateString('en-GB', { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric' 
      })
      return `${formatDate(startDate)} - ${formatDate(endDate)}`
    }
    return null
  })

  // Stats cards data - removed specified cards
  const statsCards = computed(() => {
    console.log('StatsCards computed - overview.value:', overview.value)
    console.log('StatsCards computed - total_leads:', overview.value.total_leads)
    console.log('StatsCards computed - total_tickets:', overview.value.total_tickets)
    
    return [
      { title: 'Total Leads', value: overview.value.total_leads || 0, icon: 'user-plus', color: 'blue', change: null, clickable: true, target: 'leads' },
      { title: 'Total Tickets', value: overview.value.total_tickets || 0, icon: 'ticket', color: 'orange', change: null, clickable: true, target: 'tickets' },
      { title: 'Total Tasks', value: overview.value.total_tasks || 0, icon: 'check-square', color: 'green', change: null, clickable: true, target: 'tasks' },
      { 
        title: 'Call Logs', 
        value: overview.value.total_call_logs || 0, 
        subtitle: overview.value.missed_calls > 0 ? `${overview.value.missed_calls} missed calls` : null,
        icon: 'phone', 
        color: 'purple', 
        change: null,
        clickable: true,
        target: 'calls'
      }
    ]
  })

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

  // User dashboard chart data
  const userTrendsChart = computed(() => {
    if (!userTrends.value.dates || !userTrends.value.lead_trends) return []
    
    return userTrends.value.dates.map((date, index) => ({
      label: date,
      leads: userTrends.value.lead_trends[index] || 0,
      tickets: userTrends.value.ticket_trends[index] || 0,
      tasks: userTrends.value.task_trends[index] || 0
    }))
  })

  const userLeadStatusChart = computed(() => 
    userLeadAnalytics.value.status_distribution?.map(item => ({
      label: item.status,
      value: item.count
    })) || []
  )

  return {
    // State
    loading,
    error,
    dashboardData,
    userDashboardData,
    lastUpdated,
    currentView,
    customDateRangeFormatted,
    
    // Actions
    fetchDashboardData,
    fetchUserDashboardData,
    refreshData,
    refreshUserData,
    refreshDashboard,
    changeView,
    startAutoRefresh,
    stopAutoRefresh,
    
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
    
    // User dashboard computed
    userInfo,
    userOverview,
    userLeadAnalytics,
    userTicketAnalytics,
    userTaskAnalytics,
    userCallLogAnalytics,
    userPerformanceMetrics,
    userRecentActivities,
    userTrends,
    userAchievements,
    userGoals,
    
    // Chart data
    statsCards,
    leadStatusChart,
    ticketStatusChart,
    callTypeChart,
    trendsChart,
    topPerformers,
    dateRange,
    
    // User dashboard chart data
    userTrendsChart,
    userLeadStatusChart,
    
    // User dashboard additional data
    userPeakHours
    ,
    lastFetchedUserId
  }
} 