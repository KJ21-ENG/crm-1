<template>
  <div class="min-h-screen bg-white">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-4 py-3">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold text-gray-900">Dashboard</h1>
          <p class="text-sm text-gray-600 mt-1">
            Welcome back! Here's what's happening with your CRM.
          </p>
        </div>
        
        <div class="flex items-center space-x-3">
          <!-- View Selector -->
          <div class="flex items-center space-x-2">
            <span class="text-sm font-medium text-gray-700">View:</span>
            <div class="flex bg-gray-100 rounded-lg p-1">
              <button
                v-for="view in viewOptions"
                :key="view.value"
                @click="handleViewChange(view.value)"
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
            
            <!-- Custom Date Range Picker Button -->
            <button
              @click="openCustomDatePicker"
              class="ml-2 p-1.5 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors group relative"
              title="Select Custom Date Range"
            >
              <FeatherIcon name="edit-3" class="w-4 h-4" />
              <!-- Tooltip -->
              <div class="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-10">
                <span>Custom Date Range</span>
                <!-- Arrow -->
                <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-b-4 border-transparent border-b-gray-900"></div>
              </div>
            </button>
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

    <!-- Tab Navigation - Only show if user has access to multiple tabs -->
    <div v-if="availableTabs.length > 1" class="bg-white border-b border-gray-200">
      <div class="px-4">
        <nav class="flex space-x-8" role="tablist">
          <button
            v-for="(tab, index) in availableTabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            @keydown.enter="activeTab = tab.id"
            @keydown.space.prevent="activeTab = tab.id"
            :class="[
              'py-3 px-1 border-b-2 font-medium text-sm transition-all duration-200 relative focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
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

    <!-- Custom Date Range Picker Modal -->
    <div v-if="showCustomDatePicker" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="flex items-center justify-between p-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">Select Custom Date Range</h3>
          <button
            @click="showCustomDatePicker = false"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <FeatherIcon name="x" class="w-5 h-5" />
          </button>
        </div>
        
        <div class="p-4 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
              <input
                v-model="customStartDate"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">End Date</label>
              <input
                v-model="customEndDate"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          
          <div class="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              @click="showCustomDatePicker = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              @click="applyCustomDateRange"
              :disabled="!customStartDate || !customEndDate || customStartDate > customEndDate"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Apply
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="p-4">
      <!-- Loading State for User Role -->
      <div v-if="userRoleLoading" class="mb-4">
        <div class="flex items-center justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span class="ml-3 text-gray-600">Loading user permissions...</span>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="userRoleError" class="mb-4">
        <Alert variant="error">
          <div class="flex items-center">
            <FeatherIcon name="alert-circle" class="w-5 h-5 mr-2" />
            {{ userRoleError }}
          </div>
        </Alert>
      </div>

      <!-- Dashboard Content -->
      <div v-else>
        <!-- Error State -->
        <div v-if="error" class="mb-4">
          <Alert variant="error">
            <div class="flex items-center">
              <FeatherIcon name="alert-circle" class="w-5 h-5 mr-2" />
              {{ error }}
            </div>
          </Alert>
        </div>

        <!-- Tab Content Header -->
        <div class="mb-4">
          <div class="flex items-center space-x-2 text-sm text-gray-600">
            <FeatherIcon name="home" class="w-4 h-4" />
            <span>/</span>
            <span class="font-medium text-gray-900">{{ getActiveTabLabel() }}</span>
          </div>
        </div>

        <!-- Analytics Tab Content - Only show for admin users -->
        <div 
          v-if="activeTab === 'analytics' && isAdminUser"
          :id="`tab-panel-analytics`"
          role="tabpanel"
          :aria-labelledby="`tab-analytics`"
        >
          <!-- Stats Cards -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
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
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
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
          <div class="mb-6">
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
            <div class="space-y-4">
              <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <h3 class="text-lg font-semibold text-gray-900 mb-3">Top Performers</h3>
                
                <div v-if="loading" class="space-y-3">
                  <div v-for="i in 5" :key="i" class="animate-pulse">
                    <div class="flex items-center space-x-3">
                      <div class="w-8 h-8 bg-gray-200 rounded-full"></div>
                      <div class="flex-1">
                        <div class="h-4 bg-gray-200 rounded w-1/2"></div>
                        <div class="h-3 bg-gray-200 rounded w-1/3 mt-1"></div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div v-else-if="error" class="text-center py-6 text-red-600">
                  <FeatherIcon name="alert-circle" class="w-8 h-8 mx-auto mb-2" />
                  <p>{{ error }}</p>
                </div>
                
                <div v-else-if="!topPerformers || topPerformers.length === 0" class="text-center py-6 text-gray-500">
                  <FeatherIcon name="users" class="w-8 h-8 mx-auto mb-2" />
                  <p>No performance data available</p>
                </div>
                
                <div v-else class="space-y-3">
                  <div 
                    v-for="(performer, index) in topPerformers" 
                    :key="performer.user.name"
                    class="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div class="flex-shrink-0">
                      <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
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

        <!-- Referral Analytics Tab Content - Only show for admin users -->
        <div 
          v-if="activeTab === 'referral' && isAdminUser"
          :id="`tab-panel-referral`"
          role="tabpanel"
          :aria-labelledby="`tab-referral`"
        >
          <ReferralAnalyticsDashboard />
        </div>

        <!-- Call Log Analytics Tab Content - Show for all users with admin selector -->
        <div 
          v-if="activeTab === 'calllogs'"
          :id="`tab-panel-calllogs`"
          role="tabpanel"
          :aria-labelledby="`tab-calllogs`"
        >
          <!-- User Selector Header (Admin Only) -->
          <div v-if="isCallLogsSelectorVisible" class="mb-6 p-4 bg-white rounded-lg border border-gray-200 shadow-sm">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-4">
                <span class="text-sm font-medium text-gray-700">View Call Logs For:</span>
                <select
                  v-model="selectedCallLogsUserId"
                  @change="handleCallLogsUserChange"
                  class="px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                >
                  <option value="all">All Users</option>
                  <option value="">Current User</option>
                  <option v-for="user in availableUsers" :key="user.name" :value="user.name">
                    {{ user.full_name || user.name }}
                  </option>
                </select>
                <span class="text-xs text-gray-500">
                  {{ availableUsers.length }} users available
                </span>
              </div>
              <div class="flex items-center space-x-2">
                <span v-if="selectedCallLogsUserId" class="text-sm text-blue-600 font-medium">
                  Viewing: {{ getSelectedCallLogsUserName() }}
                </span>
                <button
                  v-if="selectedCallLogsUserId"
                  @click="selectedCallLogsUserId = ''; handleCallLogsUserChange()"
                  class="px-3 py-1.5 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 border border-gray-300 rounded-md transition-colors"
                  title="Reset to Current User"
                >
                  <FeatherIcon name="refresh-cw" class="w-4 h-4 mr-1" />
                  Reset
                </button>
              </div>
            </div>
          </div>

          <CallLogAnalytics
            :data="callLogsTabData"
            :current-view="currentView"
            :loading="loading"
            :error="error"
            @refresh="refreshDashboard"
          />
        </div>

        <!-- User Dashboard Tab Content - Show for all users -->
        <div 
          v-if="activeTab === 'user'"
          :id="`tab-panel-user`"
          role="tabpanel"
          :aria-labelledby="`tab-user`"
        >
          <!-- User Selector Header (Admin Only) -->
          <div v-if="isAdminUser" class="mb-6 p-4 bg-white rounded-lg border border-gray-200 shadow-sm">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-4">
                <span class="text-sm font-medium text-gray-700">View User Dashboard:</span>
                <select
                  v-model="selectedUserId"
                  @change="handleUserChange"
                  class="px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                >
                  <option value="">Current User</option>
                  <option v-for="user in availableUsers" :key="user.name" :value="user.name">
                    {{ user.full_name || user.name }}
                  </option>
                </select>
                <span class="text-xs text-gray-500">
                  {{ availableUsers.length }} users available
                </span>
              </div>
              <div class="flex items-center space-x-2">
                <span v-if="selectedUserId" class="text-sm text-blue-600 font-medium">
                  Viewing: {{ getSelectedUserName() }}
                </span>
                <button
                  v-if="selectedUserId"
                  @click="resetUserSelection"
                  class="px-3 py-1.5 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 border border-gray-300 rounded-md transition-colors transition-colors"
                  title="Reset to Current User"
                >
                  <FeatherIcon name="refresh-cw" class="w-4 h-4 mr-1" />
                  Reset
                </button>
              </div>
            </div>
          </div>
          
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
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, FeatherIcon, Alert, Badge } from 'frappe-ui'
import StatsCard from '@/components/Dashboard/StatsCard.vue'
import ReferralAnalyticsDashboard from '@/components/Dashboard/ReferralAnalyticsDashboard.vue'
import UserDashboard from '@/components/Dashboard/UserDashboard.vue'
import CallLogAnalytics from '@/components/Dashboard/CallLogAnalytics.vue'
import ChartCard from '@/components/Dashboard/ChartCard.vue'
import ActivityFeed from '@/components/Dashboard/ActivityFeed.vue'
import { useDashboard } from '@/stores/dashboard'
import { useUserRole } from '@/stores/userRole'

const route = useRoute()
const router = useRouter()

const {
  loading,
  error,
  lastUpdated,
  currentView,
  customDateRangeFormatted,
  statsCards,
  leadStatusChart,
  ticketStatusChart,
  callTypeChart,
  trendsChart,
  recentActivities,
  quickActions,
  topPerformers,
  dateRange,
  callLogAnalytics,
  userDashboardData,
  fetchDashboardData,
  fetchUserDashboardData,
  refreshDashboard,
  changeView,
  startAutoRefresh,
  stopAutoRefresh
  , lastFetchedUserId
} = useDashboard()

// User role management
const { isAdminUser, currentUserRole, initializeUserRole, userRoleLoading, userRoleError } = useUserRole()

// Tab system with role-based access control
const activeTab = ref('user') // Default to user dashboard for non-admin users

// Define all available tabs
const allTabs = [
  {
    id: 'analytics',
    label: 'Analytics',
    icon: 'bar-chart-2',
    badge: null,
    adminOnly: true
  },
  {
    id: 'referral',
    label: 'Referral Analytics',
    icon: 'users',
    badge: {
      text: 'New',
      variant: 'green'
    },
    adminOnly: true
  },
  {
    id: 'calllogs',
    label: 'Call Log Analytics',
    icon: 'phone',
    badge: null,
    adminOnly: false
  },
  {
    id: 'user',
    label: 'User Dashboard',
    icon: 'user',
    badge: null,
    adminOnly: false
  }
]

// Computed property for available tabs based on user role
const availableTabs = computed(() => {
  if (isAdminUser.value) {
    return allTabs
  } else {
    return allTabs.filter(tab => !tab.adminOnly)
  }
})

// Initialize tab from URL query parameter or default based on role
const initializeTabFromURL = () => {
  const tabFromURL = route.query.tab
  
  if (tabFromURL && availableTabs.value.some(tab => tab.id === tabFromURL)) {
    activeTab.value = tabFromURL
  } else {
    // Set default tab based on user role
    if (isAdminUser.value) {
      activeTab.value = 'analytics'
    } else {
      activeTab.value = 'user'
    }
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
      // We're loading the current user's dashboard by default here — ensure the selector reflects that
      selectedUserId.value = ''
      fetchUserDashboardData(currentView.value)
    } else {
      console.log('🔍 DEBUG: User dashboard data already loaded:', userDashboardData)
    }
  }
  
  // If switching away from user dashboard and we're in custom view, clear custom date range
  if (newTab !== 'user' && currentView.value === 'custom') {
    console.log('🔍 DEBUG: Switching away from user dashboard in custom view, clearing custom date range')
    // This will be handled when the new tab data is fetched
  }
  // Ensure data for Call Logs tab
  if (newTab === 'calllogs') {
    if (selectedCallLogsUserId.value === 'all') {
      fetchDashboardData(currentView.value)
    } else if (selectedCallLogsUserId.value) {
      // Admin has selected a specific user for calllogs — load that user's data
      fetchUserDashboardData(currentView.value, null, null, selectedCallLogsUserId.value)
    } else {
      // No specific user selected: ensure selector shows "Current User" and load current user's data
      selectedCallLogsUserId.value = ''
      fetchUserDashboardData(currentView.value)
    }
  }
})

// Keep dropdown selectors in sync with what was last fetched
watch(lastFetchedUserId, (newVal) => {
  console.log('🔍 DEBUG: lastFetchedUserId changed:', newVal)
  // Sync the main user selector
  selectedUserId.value = newVal || ''
  // If calllogs selector is not specifically in use, also sync it
  if (!isCallLogsSelectorVisible.value || activeTab.value !== 'calllogs') {
    selectedCallLogsUserId.value = newVal || ''
  }
})

// Custom date range picker state
const showCustomDatePicker = ref(false)
const customStartDate = ref('')
const customEndDate = ref('')

// User selection state (Admin only)
const selectedUserId = ref('')
const selectedCallLogsUserId = ref('')
const availableUsers = ref([])
const isUserSelectorVisible = computed(() => isAdminUser.value && activeTab.value === 'user')
const isCallLogsSelectorVisible = computed(() => isAdminUser.value && activeTab.value === 'calllogs')

// View options
const viewOptions = [
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Monthly', value: 'monthly' },
  { label: 'Custom', value: 'custom' }
]

// Computed property for trends chart title
const trendsChartTitle = computed(() => {
  switch (currentView.value) {
    case 'daily':
      return '24-Hour Trends'
    case 'weekly':
      return '7-Day Trends'
    case 'monthly':
      return 'Current Month Trends'
    case 'custom':
      return 'Custom Range Trends'
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
    case 'custom':
      return 'Custom Range'
    default:
      return 'All Time'
  }
}

const getViewTooltip = (viewType) => {
  if (loading.value) return 'Loading...'
  
  // For custom view, show the actual custom date range
  if (viewType === 'custom' && customDateRangeFormatted.value) {
    return customDateRangeFormatted.value
  }
  
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
      // Show current month instead of past 30 days
      const currentMonth = today.getMonth()
      const currentYear = today.getFullYear()
      const firstDay = new Date(currentYear, currentMonth, 1)
      const lastDay = new Date(currentYear, currentMonth + 1, 0)
      return `${formatDate(firstDay)} - ${formatDate(lastDay)}`
    case 'custom':
      return customDateRangeFormatted.value || 'Custom Range'
    default:
      return 'Custom Range'
  }
}

// Custom date range methods
const applyCustomDateRange = async () => {
  if (!customStartDate.value || !customStartDate.value > customEndDate.value) {
    return
  }
  
  try {
    // Set custom view
    currentView.value = 'custom'
    
    // Fetch data with custom date range
    if (activeTab.value === 'user') {
      await fetchUserDashboardData('custom', customStartDate.value, customEndDate.value)
    } else if (activeTab.value === 'calllogs') {
      // If admin has selected a specific user in Call Logs, fetch user-specific data
      if (selectedCallLogsUserId.value && selectedCallLogsUserId.value !== 'all') {
        await fetchUserDashboardData('custom', customStartDate.value, customEndDate.value, selectedCallLogsUserId.value)
      } else {
        await fetchDashboardData('custom', customStartDate.value, customEndDate.value)
      }
    } else {
      await fetchDashboardData('custom', customStartDate.value, customEndDate.value)
    }
    
    // Close modal
    showCustomDatePicker.value = false
    
    // Reset custom dates
    customStartDate.value = ''
    customEndDate.value = ''
  } catch (error) {
    console.error('Error applying custom date range:', error)
  }
}

// Function to handle view changes and clear custom date range when needed
const handleViewChange = async (view) => {
  // If switching away from custom view, clear custom date range
  if (currentView.value === 'custom' && view !== 'custom') {
    // Clear custom date range by fetching data for the new view
    if (activeTab.value === 'user') {
      const targetUser = selectedUserId.value || null
      await fetchUserDashboardData(view, null, null, targetUser)
    } else if (activeTab.value === 'calllogs' && selectedCallLogsUserId.value && selectedCallLogsUserId.value !== 'all') {
      await fetchUserDashboardData(view, null, null, selectedCallLogsUserId.value)
    } else {
      await fetchDashboardData(view)
    }
  }
  
  // Change the view
  // Pass selectedCallLogsUserId when switching views so user-specific data continues to load
  if (activeTab.value === 'calllogs' && selectedCallLogsUserId.value && selectedCallLogsUserId.value !== 'all') {
    await changeView(view, selectedCallLogsUserId.value)
  } else if (activeTab.value === 'user') {
    const targetUser = selectedUserId.value || null
    await changeView(view, targetUser)
  } else {
    await changeView(view)
  }
}

const openCustomDatePicker = () => {
  // Set default dates to current month
  const today = new Date()
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
  const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0)
  
  customStartDate.value = firstDay.toISOString().split('T')[0]
  customEndDate.value = lastDay.toISOString().split('T')[0]
  
  showCustomDatePicker.value = true
}

// User management functions
const fetchAvailableUsers = async () => {
  try {
    const response = await fetch('/api/method/crm.api.dashboard.get_available_users')
    
    if (response.ok) {
      const data = await response.json()
      
      if (data.message && Array.isArray(data.message)) {
        // Direct array format
        availableUsers.value = data.message
      } else if (data.message && typeof data.message === 'object' && data.message.users) {
        // Nested object format with users property
        availableUsers.value = data.message.users
      } else if (data.message && typeof data.message === 'object') {
        // Try to extract users from the message object
        const users = Object.values(data.message).find(val => Array.isArray(val))
        if (users) {
          availableUsers.value = users
        } else {
          availableUsers.value = []
        }
      } else {
        availableUsers.value = []
      }
    } else {
      availableUsers.value = []
    }
  } catch (error) {
    console.error('Error fetching available users:', error)
    availableUsers.value = []
  }
}

const handleUserChange = async () => {
  if (!selectedUserId.value) {
    // If no user selected, fetch current user's data
    await fetchUserDashboardData(currentView.value)
    return
  }
  
  // Fetch data for selected user
  if (currentView.value === 'custom' && customStartDate.value && customEndDate.value) {
    await fetchUserDashboardData('custom', customStartDate.value, customEndDate.value, selectedUserId.value)
  } else {
    await fetchUserDashboardData(currentView.value, null, null, selectedUserId.value)
  }
}

const handleCallLogsUserChange = async () => {
  console.log('🔍 DEBUG: handleCallLogsUserChange selectedCallLogsUserId=', selectedCallLogsUserId.value, 'availableUsers=', availableUsers.value)
  if (selectedCallLogsUserId.value === 'all') {
    await fetchDashboardData(currentView.value)
    return
  }
  if (!selectedCallLogsUserId.value) {
    await fetchUserDashboardData(currentView.value)
    console.log('🔍 DEBUG: callLogs - userDashboardData after fetch (current user):', userDashboardData.value)
    return
  }
  if (currentView.value === 'custom' && customStartDate.value && customEndDate.value) {
    await fetchUserDashboardData('custom', customStartDate.value, customEndDate.value, selectedCallLogsUserId.value)
    console.log('🔍 DEBUG: callLogs - userDashboardData after fetch (custom range):', userDashboardData.value)
  } else {
    await fetchUserDashboardData(currentView.value, null, null, selectedCallLogsUserId.value)
    console.log('🔍 DEBUG: callLogs - userDashboardData after fetch (selected user):', userDashboardData.value)
  }
}

const callLogsTabData = computed(() => {
  if (isAdminUser.value && selectedCallLogsUserId.value === 'all') {
    return callLogAnalytics.value || {}
  }
  return (userDashboardData.value && userDashboardData.value.call_log_analytics) || {}
})

const getSelectedCallLogsUserName = () => {
  if (!selectedCallLogsUserId.value) return 'Current User'
  if (selectedCallLogsUserId.value === 'all') return 'All Users'
  const user = availableUsers.value.find(u => u.name === selectedCallLogsUserId.value)
  return user ? (user.full_name || user.name) : selectedCallLogsUserId.value
}

const getSelectedUserName = () => {
  if (!selectedUserId.value) return 'Current User'
  const user = availableUsers.value.find(u => u.name === selectedUserId.value)
  return user ? (user.full_name || user.name) : selectedUserId.value
}

const resetUserSelection = () => {
  selectedUserId.value = ''
  // Fetch current user's data
  fetchUserDashboardData(currentView.value)
}

const getActiveTabLabel = () => {
  const tab = availableTabs.value.find(t => t.id === activeTab.value)
  return tab ? tab.label : 'Dashboard'
}

onMounted(async () => {
  // Initialize user role information first
  await initializeUserRole()
  
  // Set default view to daily BEFORE initializing tabs
  currentView.value = 'daily'

  // Ensure changeView returns a promise and await fetching data once
  await changeView('daily')

  initializeTabFromURL()

  // Remove duplicate immediate fetches; changeView already triggered data fetch
  // but ensure we have data by awaiting the store fetch promises if needed
  await Promise.all([
    // If store fetches did not run for some reason, call them explicitly
    fetchDashboardData(currentView.value),
    fetchUserDashboardData(currentView.value)
  ])
  
  // Fetch available users if admin
  if (isAdminUser.value) {
    await fetchAvailableUsers()
  }
  
  // Auto-refresh disabled - removed startAutoRefresh() call
})

onUnmounted(() => {
  // Auto-refresh disabled - removed stopAutoRefresh() call
})
</script>
