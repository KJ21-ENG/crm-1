<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p class="text-sm text-gray-600 mt-1">
            Welcome back! Here's what's happening with your CRM.
          </p>
        </div>
        
        <div class="flex items-center space-x-4">
          <!-- View Selector -->
          <div class="flex items-center space-x-2">
            <span class="text-sm font-medium text-gray-700">View:</span>
            <div class="flex bg-gray-100 rounded-lg p-1">
              <button
                v-for="view in viewOptions"
                :key="view.value"
                @click="changeView(view.value)"
                :class="[
                  'px-3 py-1 text-sm font-medium rounded-md transition-colors relative group',
                  currentView === view.value
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                ]"

              >
                {{ view.label }}
                <!-- Tooltip -->
                <div class="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-10">
                  <div class="flex items-center space-x-1">
                    <FeatherIcon name="calendar" class="w-3 h-3" />
                    <span>{{ getViewTooltip(view.value) }}</span>
                    <span v-if="view.value === currentView && dateRange.formatted_range" class="text-green-300">✓</span>
                  </div>
                  <!-- Arrow -->
                  <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-b-4 border-transparent border-b-gray-900"></div>
                </div>
              </button>
            </div>
          </div>
          
          <div v-if="lastUpdated" class="text-sm text-gray-500">
            Last updated: {{ formatTime(lastUpdated) }}
          </div>
          
          <Button 
            variant="outline" 
            size="sm"
            @click="refreshDashboard"
            :loading="loading"
          >
            <FeatherIcon name="refresh-cw" class="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>
    </div>

    <!-- Tab Navigation -->
    <div class="bg-white border-b border-gray-200">
      <div class="px-6">
        <nav class="flex space-x-8" role="tablist">
          <button
            v-for="(tab, index) in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            @keydown.enter="activeTab = tab.id"
            @keydown.space.prevent="activeTab = tab.id"
            :class="[
              'py-4 px-1 border-b-2 font-medium text-sm transition-all duration-200 relative focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
            :role="'tab'"
            :aria-selected="activeTab === tab.id"
            :aria-controls="`tab-panel-${tab.id}`"
            :tabindex="activeTab === tab.id ? 0 : -1"
          >
            <div class="flex items-center space-x-2">
              <FeatherIcon :name="tab.icon" class="w-4 h-4" />
              <span>{{ tab.label }}</span>
              <Badge v-if="tab.badge" :variant="tab.badge.variant" size="sm">
                {{ tab.badge.text }}
              </Badge>
            </div>
            <!-- Active indicator -->
            <div 
              v-if="activeTab === tab.id"
              class="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500 rounded-t"
            ></div>
          </button>
        </nav>
      </div>
    </div>

    <!-- Main Content -->
    <div class="p-6">
      <!-- Error State -->
      <div v-if="error" class="mb-6">
        <Alert variant="error">
          <div class="flex items-center">
            <FeatherIcon name="alert-circle" class="w-5 h-5 mr-2" />
            {{ error }}
          </div>
        </Alert>
      </div>

      <!-- Tab Content Header -->
      <div class="mb-6">
        <div class="flex items-center space-x-2 text-sm text-gray-600">
          <FeatherIcon name="home" class="w-4 h-4" />
          <span>/</span>
          <span class="font-medium text-gray-900">{{ getActiveTabLabel() }}</span>
        </div>
      </div>

      <!-- Analytics Tab Content -->
      <div 
        v-if="activeTab === 'analytics'"
        :id="`tab-panel-analytics`"
        role="tabpanel"
        :aria-labelledby="`tab-analytics`"
      >
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <StatsCard
            v-for="card in statsCards"
            :key="card.title"
            :title="card.title"
            :value="card.value"
            :subtitle="card.subtitle"
            :icon="card.icon"
            :color="card.color"
            :change="card.change"
          />
        </div>

        <!-- Charts and Analytics -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <!-- Lead Status Distribution -->
          <ChartCard
            :title="`Lead Status Distribution (${getViewContext()})`"
            :data="leadStatusChart"
            type="doughnut"
            :loading="loading"
            :error="error"
            @refresh="refreshDashboard"
          />

          <!-- Ticket Status Distribution -->
          <ChartCard
            :title="`Ticket Status Distribution (${getViewContext()})`"
            :data="ticketStatusChart"
            type="doughnut"
            :loading="loading"
            :error="error"
            @refresh="refreshDashboard"
          />
        </div>

        <!-- Trends Chart -->
        <div class="mb-8">
          <ChartCard
            :title="trendsChartTitle"
            :data="trendsChart"
            type="line"
            :loading="loading"
            :error="error"
            @refresh="refreshDashboard"
          />
        </div>

        <!-- Bottom Section -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Recent Activities -->
          <div class="lg:col-span-2">
            <ActivityFeed
              :activities="recentActivities"
              :loading="loading"
              :error="error"
              @refresh="refreshDashboard"
            />
          </div>

          <!-- Top Performers -->
          <div class="space-y-6">
            <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">Top Performers</h3>
              
              <div v-if="loading" class="space-y-4">
                <div v-for="i in 5" :key="i" class="animate-pulse">
                  <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 bg-gray-200 rounded-full"></div>
                    <div class="flex-1">
                      <div class="h-4 bg-gray-200 rounded w-1/2"></div>
                      <div class="h-3 bg-gray-200 rounded w-1/3 mt-2"></div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-else-if="error" class="text-center py-8 text-red-600">
                <FeatherIcon name="alert-circle" class="w-8 h-8 mx-auto mb-2" />
                <p>{{ error }}</p>
              </div>
              
              <div v-else-if="!topPerformers || topPerformers.length === 0" class="text-center py-8 text-gray-500">
                <FeatherIcon name="users" class="w-8 h-8 mx-auto mb-2" />
                <p>No performance data available</p>
              </div>
              
              <div v-else class="space-y-4">
                <div 
                  v-for="(performer, index) in topPerformers" 
                  :key="performer.user.name"
                  class="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div class="flex-shrink-0">
                    <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <span class="text-sm font-medium text-blue-600">
                        {{ performer.user.full_name?.charAt(0) || performer.user.name?.charAt(0) }}
                      </span>
                    </div>
                  </div>
                  
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900">
                      {{ performer.user.full_name || performer.user.name }}
                    </p>
                    <p class="text-sm text-gray-600">
                      {{ performer.leads_assigned }} leads • {{ performer.tickets_assigned }} tickets
                    </p>
                  </div>
                  
                  <div class="flex-shrink-0">
                    <Badge variant="blue" size="sm">
                      #{{ index + 1 }}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Referral Analytics Tab Content -->
      <div 
        v-if="activeTab === 'referral'"
        :id="`tab-panel-referral`"
        role="tabpanel"
        :aria-labelledby="`tab-referral`"
      >
        <ReferralAnalyticsDashboard />
      </div>

      <!-- User Dashboard Tab Content -->
      <div 
        v-if="activeTab === 'user'"
        :id="`tab-panel-user`"
        role="tabpanel"
        :aria-labelledby="`tab-user`"
      >
        <UserDashboard
          :loading="loading"
          :error="error"
          :user-dashboard-data="userDashboardData"
          :current-view="currentView"
          @refresh="refreshDashboard"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, FeatherIcon, Alert, Badge } from 'frappe-ui'
import StatsCard from '@/components/Dashboard/StatsCard.vue'
import ReferralAnalyticsDashboard from '@/components/Dashboard/ReferralAnalyticsDashboard.vue'
import UserDashboard from '@/components/Dashboard/UserDashboard.vue'
import ChartCard from '@/components/Dashboard/ChartCard.vue'
import ActivityFeed from '@/components/Dashboard/ActivityFeed.vue'
import { useDashboard } from '@/stores/dashboard'

const route = useRoute()
const router = useRouter()

const {
  loading,
  error,
  lastUpdated,
  currentView,
  statsCards,
  leadStatusChart,
  ticketStatusChart,
  callTypeChart,
  trendsChart,
  recentActivities,
  quickActions,
  topPerformers,
  dateRange,
  userDashboardData,
  fetchDashboardData,
  fetchUserDashboardData,
  refreshDashboard,
  changeView,
  startAutoRefresh,
  stopAutoRefresh
} = useDashboard()

// Tab system with URL routing
const activeTab = ref('analytics')

// Initialize tab from URL query parameter
const initializeTabFromURL = () => {
  const tabFromURL = route.query.tab
  if (tabFromURL && ['analytics', 'referral', 'user'].includes(tabFromURL)) {
    activeTab.value = tabFromURL
  }
}

// Update URL when tab changes
const updateURLForTab = (tabId) => {
  router.replace({
    query: {
      ...route.query,
      tab: tabId
    }
  })
}

// Watch for tab changes and update URL
watch(activeTab, (newTab) => {
  console.log('🔍 DEBUG: Tab changed to:', newTab)
  updateURLForTab(newTab)
  
  // If switching to user dashboard, ensure data is loaded
  if (newTab === 'user') {
    console.log('🔍 DEBUG: User Dashboard tab activated, checking data')
    if (!userDashboardData || Object.keys(userDashboardData).length === 0) {
      console.log('🔍 DEBUG: User dashboard data empty, fetching...')
      fetchUserDashboardData()
    } else {
      console.log('🔍 DEBUG: User dashboard data already loaded:', userDashboardData)
    }
  }
})

const tabs = [
  {
    id: 'analytics',
    label: 'Analytics',
    icon: 'bar-chart-2',
    badge: null
  },
  {
    id: 'referral',
    label: 'Referral Analytics',
    icon: 'users',
    badge: {
      text: 'New',
      variant: 'green'
    }
  },
  {
    id: 'user',
    label: 'User Dashboard',
    icon: 'user',
    badge: null
  }
]

// View options
const viewOptions = [
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Monthly', value: 'monthly' }
]

// Computed property for trends chart title
const trendsChartTitle = computed(() => {
  switch (currentView.value) {
    case 'daily':
      return '24-Hour Trends'
    case 'weekly':
      return '7-Day Trends'
    case 'monthly':
      return '30-Day Trends'
    default:
      return 'Trends'
  }
})

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  const now = new Date()
  const diffInMinutes = (now - date) / (1000 * 60)
  
  if (diffInMinutes < 1) {
    return 'Just now'
  } else if (diffInMinutes < 60) {
    return `${Math.floor(diffInMinutes)}m ago`
  } else {
    return date.toLocaleTimeString()
  }
}

const getViewContext = () => {
  switch (currentView.value) {
    case 'daily':
      return 'Today'
    case 'weekly':
      return 'This Week'
    case 'monthly':
      return 'This Month'
    default:
      return 'All Time'
  }
}

const getViewTooltip = (viewType) => {
  if (loading.value) return 'Loading...'
  
  // For the current view, show the actual date range
  if (viewType === currentView.value && dateRange.value.formatted_range) {
    return dateRange.value.formatted_range
  }
  
  // For other views, show what the range would be
  const today = new Date()
  const formatDate = (date) => date.toISOString().split('T')[0]
  
  switch (viewType) {
    case 'daily':
      return `Today (${formatDate(today)})`
    case 'weekly':
      const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
      return `${formatDate(weekAgo)} - ${formatDate(today)}`
    case 'monthly':
      const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
      return `${formatDate(monthAgo)} - ${formatDate(today)}`
    default:
      return 'Date range'
  }
}

const getActiveTabLabel = () => {
  const tab = tabs.find(t => t.id === activeTab.value)
  return tab ? tab.label : 'Dashboard'
}

onMounted(() => {
  console.log('🔍 DEBUG: Dashboard.vue mounted')
  initializeTabFromURL()
  console.log('🔍 DEBUG: Initializing dashboard data')
  fetchDashboardData()
  console.log('🔍 DEBUG: Initializing user dashboard data')
  fetchUserDashboardData()
  // Auto-refresh disabled - removed startAutoRefresh() call
})

onUnmounted(() => {
  // Auto-refresh disabled - removed stopAutoRefresh() call
})
</script>
