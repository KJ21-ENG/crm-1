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

        <!-- Quick Actions and Top Performers -->
        <div class="space-y-6">
          <!-- Quick Actions -->
          <QuickActions :actions="quickActions" />
          
          <!-- Top Performers -->
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
                  <!-- Referral Analytics Dashboard Section -->
            <div class="mt-8">
              <ReferralAnalyticsDashboard />
            </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, computed } from 'vue'
import { Button, FeatherIcon, Alert, Badge } from 'frappe-ui'
import StatsCard from '@/components/Dashboard/StatsCard.vue'
import ReferralAnalyticsDashboard from '@/components/Dashboard/ReferralAnalyticsDashboard.vue'
import ChartCard from '@/components/Dashboard/ChartCard.vue'
import ActivityFeed from '@/components/Dashboard/ActivityFeed.vue'
import QuickActions from '@/components/Dashboard/QuickActions.vue'
import { useDashboard } from '@/stores/dashboard'

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
  fetchDashboardData,
  refreshDashboard,
  changeView,
  startAutoRefresh,
  stopAutoRefresh
} = useDashboard()

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

onMounted(() => {
  fetchDashboardData()
  // Auto-refresh disabled - removed startAutoRefresh() call
})

onUnmounted(() => {
  // Auto-refresh disabled - removed stopAutoRefresh() call
})
</script>
