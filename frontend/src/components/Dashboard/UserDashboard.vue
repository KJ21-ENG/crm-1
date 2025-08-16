<template>
  <div class="user-dashboard">
    <!-- User Profile Header -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <div class="flex items-center space-x-4">
        <div class="flex-shrink-0">
          <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <span class="text-2xl font-bold text-white">
              {{ userInitials }}
            </span>
          </div>
        </div>
        <div class="flex-1">
          <h2 class="text-2xl font-bold text-gray-900">{{ userInfo.full_name || userInfo.name }}</h2>
          <p class="text-gray-600">{{ userInfo.role }} • {{ userInfo.email }}</p>
          <div class="flex items-center space-x-4 mt-2 text-sm text-gray-500">
            <span>Member since {{ formatDate(userInfo.creation) }}</span>
            <span v-if="userInfo.last_login">Last login: {{ formatDate(userInfo.last_login) }}</span>
          </div>
        </div>
        <div class="flex-shrink-0">
          <div class="text-right">
            <div class="text-3xl font-bold text-blue-600">{{ performanceMetrics.efficiency_score || 0 }}</div>
            <div class="text-sm text-gray-600">Efficiency Score</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Overview Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Leads Assigned</p>
            <p class="text-2xl font-bold text-gray-900">{{ userOverview.leads_assigned || 0 }}</p>
            <div v-if="performanceMetrics.improvements?.leads" class="flex items-center mt-2">
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
          <div class="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
            <FeatherIcon name="user-plus" class="h-6 w-6 text-blue-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Tickets Assigned</p>
            <p class="text-2xl font-bold text-gray-900">{{ userOverview.tickets_assigned || 0 }}</p>
            <div v-if="performanceMetrics.improvements?.tickets" class="flex items-center mt-2">
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
          <div class="h-12 w-12 rounded-full bg-orange-100 flex items-center justify-center">
            <FeatherIcon name="ticket" class="h-6 w-6 text-orange-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Tasks Assigned</p>
            <p class="text-2xl font-bold text-gray-900">{{ userOverview.tasks_assigned || 0 }}</p>
            <div v-if="performanceMetrics.improvements?.tasks" class="flex items-center mt-2">
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
          <div class="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
            <FeatherIcon name="check-square" class="h-6 w-6 text-green-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Calls Made</p>
            <p class="text-2xl font-bold text-gray-900">{{ userOverview.calls_made || 0 }}</p>
            <p class="text-sm text-gray-500 mt-1">Total duration: {{ formatDuration(userOverview.total_duration || 0) }}</p>
          </div>
          <div class="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center">
            <FeatherIcon name="phone" class="h-6 w-6 text-purple-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Conversion Rates & Performance -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <!-- Lead Conversion Rate -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Lead Conversion</h3>
        <div class="text-center">
          <div class="text-4xl font-bold text-blue-600 mb-2">{{ userLeadAnalytics.conversion_rate || 0 }}%</div>
          <p class="text-sm text-gray-600">Conversion Rate</p>
          <div class="mt-4">
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
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Ticket Resolution</h3>
        <div class="text-center">
          <div class="text-4xl font-bold text-orange-600 mb-2">{{ userTicketAnalytics.resolution_rate || 0 }}%</div>
          <p class="text-sm text-gray-600">Resolution Rate</p>
          <div class="mt-4">
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
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Task Completion</h3>
        <div class="text-center">
          <div class="text-4xl font-bold text-green-600 mb-2">{{ userTaskAnalytics.completion_rate || 0 }}%</div>
          <p class="text-sm text-gray-600">Completion Rate</p>
          <div class="mt-4">
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-green-600 h-2 rounded-full transition-all duration-500"
                :style="{ width: `${Math.min(userTaskAnalytics.completion_rate || 0, 100)}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- User Trends Chart -->
      <ChartCard
        :title="`Your Activity Trends (${getViewContext()})`"
        :data="userTrendsChart"
        type="line"
        :loading="loading"
        :error="error"
        @refresh="$emit('refresh')"
      />

      <!-- Lead Status Distribution -->
      <ChartCard
        :title="`Your Lead Status (${getViewContext()})`"
        :data="userLeadStatusChart"
        type="doughnut"
        :loading="loading"
        :error="error"
        @refresh="$emit('refresh')"
      />
    </div>

    <!-- Achievements & Goals -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Achievements -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <FeatherIcon name="award" class="h-5 w-5 text-yellow-500 mr-2" />
          Your Achievements
        </h3>
        
        <div v-if="loading" class="space-y-3">
          <div v-for="i in 3" :key="i" class="animate-pulse">
            <div class="h-16 bg-gray-200 rounded-lg"></div>
          </div>
        </div>
        
        <div v-else-if="!userAchievements || userAchievements.length === 0" class="text-center py-8 text-gray-500">
          <FeatherIcon name="target" class="h-12 w-12 mx-auto mb-3 text-gray-300" />
          <p>No achievements yet this period</p>
          <p class="text-sm">Keep up the great work to earn achievements!</p>
        </div>
        
        <div v-else class="space-y-3">
          <div 
            v-for="achievement in userAchievements" 
            :key="achievement.title"
            class="flex items-center p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors"
          >
            <div class="flex-shrink-0 mr-3">
              <div class="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                <FeatherIcon :name="achievement.icon" class="h-5 w-5 text-green-600" />
              </div>
            </div>
            <div class="flex-1">
              <p class="font-medium text-gray-900">{{ achievement.title }}</p>
              <p class="text-sm text-gray-600">{{ achievement.description }}</p>
            </div>
            <div class="flex-shrink-0">
              <Badge variant="green" size="sm">{{ achievement.value }}</Badge>
            </div>
          </div>
        </div>
      </div>

      <!-- Goals -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <FeatherIcon name="target" class="h-5 w-5 text-blue-500 mr-2" />
          Your Goals
        </h3>
        
        <div v-if="loading" class="space-y-3">
          <div v-for="i in 3" :key="i" class="animate-pulse">
            <div class="h-16 bg-gray-200 rounded-lg"></div>
          </div>
        </div>
        
        <div v-else-if="!userGoals || userGoals.length === 0" class="text-center py-8 text-gray-500">
          <FeatherIcon name="flag" class="h-12 w-12 mx-auto mb-3 text-gray-300" />
          <p>No goals set for this period</p>
          <p class="text-sm">Set goals to track your progress!</p>
        </div>
        
        <div v-else class="space-y-3">
          <div 
            v-for="goal in userGoals" 
            :key="goal.title"
            class="p-3 rounded-lg border border-gray-100"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center">
                <FeatherIcon :name="goal.icon" class="h-4 w-4 text-blue-500 mr-2" />
                <span class="font-medium text-gray-900">{{ goal.title }}</span>
              </div>
              <span class="text-sm text-gray-600">{{ goal.current }}/{{ goal.target }}</span>
            </div>
            <p class="text-sm text-gray-600 mb-2">{{ goal.description }}</p>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-blue-600 h-2 rounded-full transition-all duration-500"
                :style="{ width: `${Math.min((goal.current / goal.target) * 100, 100)}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activities -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <FeatherIcon name="activity" class="h-5 w-5 text-purple-500 mr-2" />
        Recent Activities
      </h3>
      
      <div v-if="loading" class="space-y-4">
        <div v-for="i in 5" :key="i" class="animate-pulse">
          <div class="h-12 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
      
      <div v-else-if="!userRecentActivities || userRecentActivities.length === 0" class="text-center py-8 text-gray-500">
        <FeatherIcon name="clock" class="h-12 w-12 mx-auto mb-3 text-gray-300" />
        <p>No recent activities</p>
        <p class="text-sm">Start working to see your activities here!</p>
      </div>
      
      <div v-else class="space-y-3">
        <div 
          v-for="activity in userRecentActivities" 
          :key="`${activity.type}-${activity.data.name}`"
          class="flex items-center p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors"
        >
          <div class="flex-shrink-0 mr-3">
            <div class="h-8 w-8 rounded-full flex items-center justify-center"
                 :class="getActivityIconClass(activity.type)">
              <FeatherIcon :name="getActivityIcon(activity.type)" class="h-4 w-4 text-white" />
            </div>
          </div>
          <div class="flex-1">
            <p class="font-medium text-gray-900">
              {{ getActivityTitle(activity) }}
            </p>
            <p class="text-sm text-gray-600">
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

const emit = defineEmits(['refresh'])

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

// User initials for avatar
const userInitials = computed(() => {
  const fullName = userInfo.value.full_name || userInfo.value.name || ''
  return fullName.split(' ').map(n => n.charAt(0)).join('').toUpperCase().slice(0, 2)
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
    return date.toLocaleDateString()
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
    lead: `${activity.data.lead_name} (${activity.data.status})`,
    ticket: `${activity.data.customer_name} (${activity.data.status})`,
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
</style>
