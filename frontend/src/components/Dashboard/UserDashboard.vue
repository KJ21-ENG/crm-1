<template>
  <div class="user-dashboard">
    <!-- User Profile Header -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
      <div class="flex items-center space-x-4">
        <div class="flex-shrink-0">
          <div class="w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <span class="text-xl font-bold text-white">
              {{ userInitials }}
            </span>
          </div>
        </div>
        <div class="flex-1">
          <h2 class="text-xl font-bold text-gray-900">{{ userInfo.full_name || userInfo.name }}</h2>
          <p class="text-gray-600 text-sm">{{ userInfo.role }} • {{ userInfo.email }}</p>
          <div class="flex items-center space-x-4 mt-1 text-xs text-gray-500">
            <span>Member since {{ formatDate(userInfo.creation) }}</span>
            <span v-if="userInfo.last_login">Last login: {{ formatDate(userInfo.last_login) }}</span>
          </div>
          <!-- Admin viewing indicator -->
          <div v-if="isViewingOtherUser" class="mt-2">
            <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              <FeatherIcon name="eye" class="w-3 h-3 mr-1" />
              Admin View
            </span>
          </div>
        </div>
        <div class="flex-shrink-0">
          <!-- Efficiency Score -->
          <!-- <div class="text-2xl font-bold text-blue-600">{{ performanceMetrics.efficiency_score || 0 }}</div>
          <div class="text-sm text-gray-600">Efficiency Score</div> -->
        </div>
      </div>
    </div>

    <!-- Performance Overview Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      <!-- Leads tile: main = total (owner OR in _assign), support = created (owner) and assigned (_assign) -->
      <div
        class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 cursor-pointer hover:shadow-md transition"
        @click="navigateTo('leads')"
        @keydown.enter.prevent="navigateTo('leads')"
        @keydown.space.prevent="navigateTo('leads')"
        role="button"
        tabindex="0"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Leads</p>
            <p class="text-2xl font-bold text-gray-900">{{ userOverview.leads_total || 0 }}</p>
            <p class="text-sm text-gray-500 mt-1">Created: <strong>{{ userOverview.leads_created || 0 }}</strong> • Assigned: <strong>{{ userOverview.leads_assigned || 0 }}</strong></p>
            <div v-if="performanceMetrics.improvements?.leads" class="flex items-center mt-1">
              <span 
                :class="[
                  'text-sm font-medium',
                  performanceMetrics.improvements.leads >= 0 ? 'text-green-600' : 'text-red-600'
                ]"
              >
                {{ performanceMetrics.improvements.leads >= 0 ? '+' : '' }}{{ performanceMetrics.improvements.leads }}%
              </span>
              <span class="text-sm text-gray-500 ml-1">vs last period</span>
            </div>
          </div>
          <div class="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
            <FeatherIcon name="user-plus" class="h-5 w-5 text-blue-600" />
          </div>
        </div>
      </div>

      <!-- Tickets tile -->
      <div
        class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 cursor-pointer hover:shadow-md transition"
        @click="navigateTo('tickets')"
        @keydown.enter.prevent="navigateTo('tickets')"
        @keydown.space.prevent="navigateTo('tickets')"
        role="button"
        tabindex="0"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Tickets</p>
            <p class="text-2xl font-bold text-gray-900">{{ userOverview.tickets_total || 0 }}</p>
            <p class="text-sm text-gray-500 mt-1">Created: <strong>{{ userOverview.tickets_created || 0 }}</strong> • Assigned: <strong>{{ userOverview.tickets_assigned || 0 }}</strong></p>
            <div v-if="performanceMetrics.improvements?.tickets" class="flex items-center mt-1">
              <span 
                :class="[
                  'text-sm font-medium',
                  performanceMetrics.improvements.tickets >= 0 ? 'text-green-600' : 'text-red-600'
                ]"
              >
                {{ performanceMetrics.improvements.tickets >= 0 ? '+' : '' }}{{ performanceMetrics.improvements.tickets }}%
              </span>
              <span class="text-sm text-gray-500 ml-1">vs last period</span>
            </div>
          </div>
          <div class="h-10 w-10 rounded-full bg-orange-100 flex items-center justify-center">
            <FeatherIcon name="ticket" class="h-5 w-5 text-orange-600" />
          </div>
        </div>
      </div>

      <!-- Tasks tile -->
      <div
        class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 cursor-pointer hover:shadow-md transition"
        @click="navigateTo('tasks')"
        @keydown.enter.prevent="navigateTo('tasks')"
        @keydown.space.prevent="navigateTo('tasks')"
        role="button"
        tabindex="0"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Tasks</p>
            <p class="text-2xl font-bold text-gray-900">{{ userOverview.tasks_total || 0 }}</p>
            <p class="text-sm text-gray-500 mt-1">Created: <strong>{{ userOverview.tasks_created || 0 }}</strong> • Assigned: <strong>{{ userOverview.tasks_assigned || 0 }}</strong></p>
            <div v-if="performanceMetrics.improvements?.tasks" class="flex items-center mt-1">
              <span 
                :class="[
                  'text-sm font-medium',
                  performanceMetrics.improvements.tasks >= 0 ? 'text-green-600' : 'text-red-600'
                ]"
              >
                {{ performanceMetrics.improvements.tasks >= 0 ? '+' : '' }}{{ performanceMetrics.improvements.tasks }}%
              </span>
              <span class="text-sm text-gray-500 ml-1">vs last period</span>
            </div>
          </div>
          <div class="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
            <FeatherIcon name="check-square" class="h-5 w-5 text-green-600" />
          </div>
        </div>
      </div>

      <div
        class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 cursor-pointer hover:shadow-md transition"
        @click="navigateTo('calls')"
        @keydown.enter.prevent="navigateTo('calls')"
        @keydown.space.prevent="navigateTo('calls')"
        role="button"
        tabindex="0"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Calls Made</p>
            <p class="text-2xl font-bold text-gray-900">{{ userOverview.calls_made || 0 }}</p>
            <p class="text-sm text-gray-500 mt-1">Total duration: {{ formatDuration(userOverview.total_duration || 0) }}</p>
          </div>
          <div class="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center">
            <FeatherIcon name="phone" class="h-5 w-5 text-purple-600" />
          </div>
        </div>
      </div>

      <!-- Account Opened tile -->
      <div
        class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 cursor-pointer hover:shadow-md transition"
        @click="navigateTo('leads')"
        @keydown.enter.prevent="navigateTo('leads')"
        @keydown.space.prevent="navigateTo('leads')"
        role="button"
        tabindex="0"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Account Opened</p>
            <p class="text-2xl font-bold text-gray-900">{{ userLeadAnalytics.account_opened || 0 }}</p>
            <p class="text-sm text-gray-500 mt-1">Leads converted to accounts</p>
          </div>
          <div class="h-10 w-10 rounded-full bg-teal-100 flex items-center justify-center">
            <FeatherIcon name="user-check" class="h-5 w-5 text-teal-600" />
          </div>
        </div>
      </div>

      <!-- Account Activated tile -->
      <div
        class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 cursor-pointer hover:shadow-md transition"
        @click="navigateTo('leads')"
        @keydown.enter.prevent="navigateTo('leads')"
        @keydown.space.prevent="navigateTo('leads')"
        role="button"
        tabindex="0"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Account Activated</p>
            <p class="text-2xl font-bold text-gray-900">{{ userLeadAnalytics.account_activated || 0 }}</p>
            <p class="text-sm text-gray-500 mt-1">Active customer accounts</p>
          </div>
          <div class="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
            <FeatherIcon name="check-circle" class="h-5 w-5 text-indigo-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Conversion Rates & Performance -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
      <!-- Lead Conversion Rate -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-3">Lead Conversion</h3>
        <div class="text-center">
          <div class="text-3xl font-bold text-blue-600 mb-2">{{ userLeadAnalytics.conversion_rate || 0 }}%</div>
          <p class="text-sm text-gray-600">Conversion Rate</p>
          <div class="mt-3">
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-blue-600 h-2 rounded-full transition-all duration-500"
                :style="{ width: `${Math.min(userLeadAnalytics.conversion_rate || 0, 100)}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Ticket Resolution Rate -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-3">Ticket Resolution</h3>
        <div class="text-center">
          <div class="text-3xl font-bold text-orange-600 mb-2">{{ userTicketAnalytics.resolution_rate || 0 }}%</div>
          <p class="text-sm text-gray-600">Resolution Rate</p>
          <div class="mt-3">
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-orange-600 h-2 rounded-full transition-all duration-500"
                :style="{ width: `${Math.min(userTicketAnalytics.resolution_rate || 0, 100)}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Task Completion Rate -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-3">Task Completion</h3>
        <div class="text-center">
          <div class="text-3xl font-bold text-green-600 mb-2">{{ userTaskAnalytics.completion_rate || 0 }}%</div>
          <p class="text-sm text-gray-600">Completion Rate</p>
          <div class="mt-3">
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="h-2 rounded-full transition-all duration-500"
                :class="getGoalProgressColor(userTaskAnalytics.completion_rate || 0)"
                :style="{ width: `${Math.min(userTaskAnalytics.completion_rate || 0, 100)}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- Left Column: Activity Trends (Same width as Daily Activity Pattern) -->
      <div class="lg:col-span-1">
        <ChartCard
          :title="`Your Activity Trends (${getViewContext()})`"
          :data="userTrendsChart"
          type="line"
          :loading="loading"
          :error="error"
          @refresh="$emit('refresh')"
        />
      </div>

      <!-- Right Column: Lead Status + Ticket Status (Side by Side, Equal Widths) -->
      <div class="lg:col-span-1">
        <div class="grid grid-cols-2 gap-4">
          <!-- Lead Status Distribution (Left) -->
          <ChartCard
            :title="`Lead Status (${getViewContext()})`"
            :data="userLeadStatusChart"
            type="doughnut"
            :loading="loading"
            :error="error"
            @refresh="$emit('refresh')"
          />

          <!-- Ticket Status Distribution (Right) -->
          <ChartCard
            :title="`Ticket Status (${getViewContext()})`"
            :data="userTicketStatusChart"
            type="doughnut"
            :loading="loading"
            :error="error"
            @refresh="$emit('refresh')"
          />
        </div>
      </div>
    </div>

    <!-- Activity Pattern & Goals -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Left Column: Daily Activity Pattern + Recent Activities -->
      <div class="lg:col-span-1 flex flex-col">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <FeatherIcon name="clock" class="h-5 w-5 text-indigo-500 mr-2" />
            Your Daily Activity Pattern
          </h3>
          
          <div v-if="loading" class="space-y-3">
            <div class="animate-pulse">
              <div class="h-32 bg-gray-200 rounded-lg"></div>
            </div>
          </div>
          
          <div v-else-if="!userPeakHours || !userPeakHours.hourly_data" class="text-center py-6 text-gray-500">
            <FeatherIcon name="clock" class="h-10 w-10 mx-auto mb-2 text-gray-300" />
            <p class="text-sm">No activity data available</p>
          </div>
          
          <div v-else class="space-y-3">
            <!-- Compact Activity Timeline -->
            <div class="bg-gradient-to-r from-gray-50 to-gray-100 p-3 rounded-lg border border-gray-200">
              <h4 class="text-sm font-medium text-gray-700 mb-2 text-center">24-Hour Activity</h4>
              
              <!-- Timeline Chart -->
              <div class="relative">
                <!-- Time Labels -->
                <div class="flex justify-between text-xs text-gray-500 mb-2 px-1">
                  <span>6AM</span>
                  <span>12PM</span>
                  <span>6PM</span>
                  <span>12AM</span>
                </div>
                
                <!-- Activity Bars -->
                <div class="grid grid-cols-24 gap-0.5 items-end">
                  <div 
                    v-for="(hourData, index) in userPeakHours.hourly_data" 
                    :key="hourData.hour"
                    class="relative group flex items-end"
                  >
                    <!-- Activity Bar -->
                    <div 
                      class="w-full bg-gray-200 rounded-sm transition-all duration-300 hover:scale-105 cursor-pointer"
                      :style="{ 
                        height: `${Math.max(4, (hourData.total_activity / Math.max(userPeakHours.max_activity, 1)) * 30)}px`,
                        backgroundColor: hourData.total_activity > 0 ? getActivityBarColor(hourData.total_activity, userPeakHours.max_activity) : '#e5e7eb'
                      }"
                    ></div>
                    
                    <!-- Tooltip -->
                    <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-10">
                      <div class="text-center">
                        <div class="font-semibold">{{ hourData.hour }}</div>
                        <div class="text-gray-300">{{ hourData.total_activity }} activities</div>
                      </div>
                      <!-- Arrow -->
                      <div class="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-3 border-r-3 border-t-3 border-transparent border-t-gray-900"></div>
                    </div>
                  </div>
                </div>
                
                <!-- Peak Hours Highlight -->
                <div v-if="userPeakHours.peak_hours && userPeakHours.peak_hours.length > 0" class="mt-2 text-center">
                  <div class="inline-flex items-center px-2 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs font-medium">
                    <FeatherIcon name="star" class="h-3 w-3 mr-1 text-indigo-600" />
                    Peak: {{ formatPeakHours(userPeakHours.peak_hours) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activities (Below Daily Activity) -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mt-4 flex-1">
          <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <FeatherIcon name="activity" class="h-5 w-5 text-purple-500 mr-2" />
            Recent Activities
          </h3>
          
          <div v-if="loading" class="space-y-3">
            <div v-for="i in 4" :key="i" class="animate-pulse">
              <div class="h-10 bg-gray-200 rounded-lg"></div>
            </div>
          </div>
          
          <div v-else-if="!userRecentActivities || userRecentActivities.length === 0" class="text-center py-4 text-gray-500">
            <FeatherIcon name="clock" class="h-8 w-8 mx-auto mb-2 text-gray-300" />
            <p class="text-sm">No recent activities</p>
          </div>
          
          <div v-else class="space-y-2">
            <div 
              v-for="activity in userRecentActivities.slice(0, 4)" 
              :key="`${activity.type}-${activity.data.name}`"
              class="flex items-center p-2 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors"
            >
              <div class="flex-shrink-0 mr-2">
                <div class="h-6 w-6 rounded-full flex items-center justify-center"
                     :class="getActivityIconClass(activity.type)">
                  <FeatherIcon :name="getActivityIcon(activity.type)" class="h-3 w-3 text-white" />
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium text-gray-900 text-sm truncate">
                  {{ getActivityTitle(activity) }}
                </p>
                <p class="text-xs text-gray-600">
                  {{ formatTimeAgo(activity.data.creation) }}
                </p>
              </div>
              <div class="flex-shrink-0">
                <Badge :variant="getActivityBadgeVariant(activity.type)" size="sm">
                  {{ activity.type }}
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Goals & Progress (Equal Height) -->
      <div class="lg:col-span-1">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 h-full">
          <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <FeatherIcon name="target" class="h-5 w-5 text-blue-500 mr-2" />
            Your Goals & Progress
          </h3>
          
          <div v-if="loading" class="space-y-3">
            <div v-for="i in 4" :key="i" class="animate-pulse">
              <div class="h-16 bg-gray-200 rounded-lg"></div>
            </div>
          </div>
          
          <div v-else-if="!userGoals || userGoals.length === 0" class="text-center py-8 text-gray-500">
            <FeatherIcon name="flag" class="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>No goals set for this period</p>
            <p class="text-sm">Set goals to track your progress!</p>
          </div>
          
          <div v-else class="space-y-4">
            <div 
              v-for="goal in userGoals.filter(g => g.title !== 'Communication Goal')" 
              :key="goal.title"
              class="p-4 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors"
            >
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center">
                  <FeatherIcon :name="goal.icon" class="h-5 w-5 text-blue-500 mr-2" />
                  <span class="font-medium text-gray-900">{{ goal.title }}</span>
                </div>
                <div class="text-right">
                  <span class="text-lg font-bold text-blue-600">{{ goal.current }}/{{ goal.target }}</span>
                  <div class="text-sm text-gray-500">{{ goal.progress_percentage }}%</div>
                </div>
              </div>
              <p class="text-sm text-gray-600 mb-3">{{ goal.description }}</p>
              

              
              <div class="w-full bg-gray-200 rounded-full h-3 mb-2">
                <div 
                  class="h-3 rounded-full transition-all duration-500"
                  :class="getGoalProgressColor(goal.progress_percentage)"
                  :style="{ width: `${Math.min(goal.progress_percentage, 100)}%` }"
                ></div>
              </div>
              <div class="flex items-center justify-between text-xs text-gray-500">
                <span>Progress</span>
                <span>{{ goal.progress_percentage }}% Complete</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>




    <!-- Recent Activities -->
    <!-- Remove the old Recent Activities section since it's now in the left column -->
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { FeatherIcon, Badge } from 'frappe-ui'
import ChartCard from './ChartCard.vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  },
  userDashboardData: {
    type: Object,
    default: () => ({})
  },
  currentView: {
    type: String,
    default: 'daily'
  }
})

const emit = defineEmits(['refresh', 'navigate'])

// Computed properties for user data
const userInfo = computed(() => {
  const info = props.userDashboardData.user_info || {}
  console.log('🔍 DEBUG: UserDashboard - userInfo computed:', info)
  return info
})

const userOverview = computed(() => {
  const overview = props.userDashboardData.overview || {}
  console.log('🔍 DEBUG: UserDashboard - userOverview computed:', overview)
  return overview
})

const userLeadAnalytics = computed(() => {
  const analytics = props.userDashboardData.lead_analytics || {}
  console.log('🔍 DEBUG: UserDashboard - userLeadAnalytics computed:', analytics)
  return analytics
})

const userTicketAnalytics = computed(() => {
  const analytics = props.userDashboardData.ticket_analytics || {}
  console.log('🔍 DEBUG: UserDashboard - userTicketAnalytics computed:', analytics)
  return analytics
})

const userTaskAnalytics = computed(() => {
  const analytics = props.userDashboardData.task_analytics || {}
  console.log('🔍 DEBUG: UserDashboard - userTaskAnalytics computed:', analytics)
  return analytics
})

const userCallLogAnalytics = computed(() => {
  const analytics = props.userDashboardData.call_log_analytics || {}
  console.log('🔍 DEBUG: UserDashboard - userCallLogAnalytics computed:', analytics)
  return analytics
})

const performanceMetrics = computed(() => {
  const metrics = props.userDashboardData.performance_metrics || {}
  console.log('🔍 DEBUG: UserDashboard - performanceMetrics computed:', metrics)
  return metrics
})

const userRecentActivities = computed(() => {
  const activities = props.userDashboardData.recent_activities || []
  console.log('🔍 DEBUG: UserDashboard - userRecentActivities computed:', activities)
  return activities
})

const userTrends = computed(() => {
  const trends = props.userDashboardData.trends || {}
  console.log('🔍 DEBUG: UserDashboard - userTrends computed:', trends)
  return trends
})

const userAchievements = computed(() => {
  const achievements = props.userDashboardData.achievements || []
  console.log('🔍 DEBUG: UserDashboard - userAchievements computed:', achievements)
  return achievements
})

const userGoals = computed(() => {
  const goals = props.userDashboardData.goals || []
  console.log('🔍 DEBUG: UserDashboard - userGoals computed:', goals)
  return goals
})

const userPeakHours = computed(() => {
  const peakHours = props.userDashboardData.peak_hours || {}
  console.log('🔍 DEBUG: UserDashboard - userPeakHours computed:', peakHours)
  return peakHours
})

// User initials for avatar
const userInitials = computed(() => {
  const fullName = userInfo.value.full_name || userInfo.value.name || ''
  return fullName.split(' ').map(n => n.charAt(0)).join('').toUpperCase().slice(0, 2)
})

// Check if admin is viewing another user's data
const isViewingOtherUser = computed(() => {
  // This will be true when the dashboard data is for a different user than the current session user
  // We can determine this by checking if the user info in the dashboard data matches the current session
  // For now, we'll use a simple check - if this component is being used in admin mode
  return props.userDashboardData._debug?.requested_by !== props.userDashboardData._debug?.target_user
})

// Chart data
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

const userTicketStatusChart = computed(() => 
  userTicketAnalytics.value.status_distribution?.map(item => ({
    label: item.status,
    value: item.count
  })) || []
)

// Helper functions
const getViewContext = () => {
  switch (props.currentView) {
    case 'daily': return 'Today'
    case 'weekly': return 'This Week'
    case 'monthly': return 'This Month'
    default: return 'All Time'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    const dd = String(date.getDate()).padStart(2, '0')
    const mm = String(date.getMonth() + 1).padStart(2, '0')
    const yyyy = date.getFullYear()
    return `${dd}/${mm}/${yyyy}`
  } catch {
    return 'N/A'
  }
}

const formatTimeAgo = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    const now = new Date()
    const diffInMinutes = (now - date) / (1000 * 60)
    
    if (diffInMinutes < 1) return 'Just now'
    if (diffInMinutes < 60) return `${Math.floor(diffInMinutes)}m ago`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
    return `${Math.floor(diffInMinutes / 1440)}d ago`
  } catch {
    return 'N/A'
  }
}

const formatDuration = (minutes) => {
  if (!minutes || minutes === 0) return '0m'
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (hours > 0) {
    return `${hours}h ${mins}m`
  }
  return `${mins}m`
}

const getActivityIcon = (type) => {
  const icons = {
    lead: 'user-plus',
    ticket: 'ticket',
    task: 'check-square'
  }
  return icons[type] || 'circle'
}

const getActivityIconClass = (type) => {
  const classes = {
    lead: 'bg-blue-500',
    ticket: 'bg-orange-500',
    task: 'bg-green-500'
  }
  return classes[type] || 'bg-gray-500'
}

const getActivityTitle = (activity) => {
  const titles = {
    lead: `${activity.data.display_name || 'Unknown Customer'} (${activity.data.status})`,
    ticket: `${activity.data.display_name || 'Unknown Customer'} (${activity.data.status})`,
    task: `${activity.data.title} (${activity.data.status})`
  }
  return titles[activity.type] || 'Unknown Activity'
}

const getActivityBadgeVariant = (type) => {
  const variants = {
    lead: 'blue',
    ticket: 'orange',
    task: 'green'
  }
  return variants[type] || 'gray'
}

const getGoalProgressColor = (percentage) => {
  if (percentage >= 80) return 'bg-green-500'
  if (percentage >= 60) return 'bg-blue-500'
  if (percentage >= 40) return 'bg-yellow-500'
  if (percentage >= 20) return 'bg-orange-500'
  return 'bg-red-500'
}



const formatPeakHours = (peakHours) => {
  if (!peakHours || peakHours.length === 0) return 'None'
  
  const formattedHours = peakHours.map(hour => {
    const hourNum = parseInt(hour)
    if (hourNum === 0) return '12:00 AM'
    if (hourNum < 12) return `${hourNum}:00 AM`
    if (hourNum === 12) return '12:00 PM'
    return `${hourNum - 12}:00 PM`
  })
  
  if (formattedHours.length === 1) {
    return formattedHours[0]
  } else if (formattedHours.length === 2) {
    return `${formattedHours[0]} and ${formattedHours[1]}`
  } else {
    const last = formattedHours.pop()
    return `${formattedHours.join(', ')}, and ${last}`
  }
}

const getActivityBarColor = (activity, maxActivity) => {
  if (maxActivity === 0) return '#e5e7eb'
  const ratio = activity / maxActivity
  
  if (ratio >= 0.8) return '#7c3aed' // Purple for peak
  if (ratio >= 0.6) return '#3b82f6' // Blue for high
  if (ratio >= 0.4) return '#10b981' // Green for medium
  if (ratio >= 0.2) return '#f59e0b' // Yellow for low
  return '#6b7280' // Gray for minimal
}

const getBestCallTime = (hourlyData) => {
  if (!hourlyData || hourlyData.length === 0) return 'No data available'
  
  let bestHour = 0
  let maxCalls = 0
  
  hourlyData.forEach(hourData => {
    if (hourData.calls > maxCalls) {
      maxCalls = hourData.calls
      bestHour = parseInt(hourData.hour.split(':')[0])
    }
  })
  
  if (maxCalls === 0) return 'No calls made yet'
  
  const timeLabel = bestHour < 12 ? `${bestHour}:00 AM` : 
                   bestHour === 12 ? '12:00 PM' : 
                   `${bestHour - 12}:00 PM`
  
  return `${timeLabel} (${maxCalls} calls)`
}

const getMostProductivePeriod = (hourlyData) => {
  if (!hourlyData || hourlyData.length === 0) return 'No data available'
  
  // Group hours into periods
  const periods = {
    'Early Morning (6-9 AM)': 0,
    'Morning (9 AM-12 PM)': 0,
    'Afternoon (12-3 PM)': 0,
    'Late Afternoon (3-6 PM)': 0,
    'Evening (6-9 PM)': 0,
    'Night (9 PM-12 AM)': 0,
    'Late Night (12-6 AM)': 0
  }
  
  hourlyData.forEach(hourData => {
    const hour = parseInt(hourData.hour.split(':')[0])
    const activity = hourData.total_activity
    
    if (hour >= 6 && hour < 9) periods['Early Morning (6-9 AM)'] += activity
    else if (hour >= 9 && hour < 12) periods['Morning (9 AM-12 PM)'] += activity
    else if (hour >= 12 && hour < 15) periods['Afternoon (12-3 PM)'] += activity
    else if (hour >= 15 && hour < 18) periods['Late Afternoon (3-6 PM)'] += activity
    else if (hour >= 18 && hour < 21) periods['Evening (6-9 PM)'] += activity
    else if (hour >= 21 && hour < 24) periods['Night (9 PM-12 AM)'] += activity
    else periods['Late Night (12-6 AM)'] += activity
  })
  
  let bestPeriod = 'No data'
  let maxActivity = 0
  
  Object.entries(periods).forEach(([period, activity]) => {
    if (activity > maxActivity) {
      maxActivity = activity
      bestPeriod = period
    }
  })
  
  if (maxActivity === 0) return 'No activity recorded'
  
  return `${bestPeriod} (${maxActivity} activities)`
}

const navigateTo = (target) => {
  if (!target) return
  emit('navigate', target)
}

onMounted(() => {
  console.log('🔍 DEBUG: UserDashboard component mounted')
  console.log('🔍 DEBUG: Props received:', props)
  console.log('🔍 DEBUG: userDashboardData:', props.userDashboardData)
  console.log('🔍 DEBUG: loading:', props.loading)
  console.log('🔍 DEBUG: error:', props.error)
})
</script>

<style scoped>
.user-dashboard {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 24-column grid for timeline */
.grid-cols-24 {
  grid-template-columns: repeat(24, minmax(0, 1fr));
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .grid-cols-24 {
    grid-template-columns: repeat(12, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .grid-cols-24 {
    grid-template-columns: repeat(6, minmax(0, 1fr));
  }
}
</style>
