<template>
  <div class="calllog-analytics">
    <!-- Stats Row -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Calls</p>
            <p class="text-2xl font-bold text-gray-900">{{ totalCalls }}</p>
            <p class="text-sm text-gray-500 mt-1">{{ getViewContext() }}</p>
          </div>
          <div class="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center">
            <FeatherIcon name="phone" class="h-5 w-5 text-purple-600" />
          </div>
        </div>
      </div>

      <!-- New: Unique Calls -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Unique Calls</p>
            <p class="text-2xl font-bold text-gray-900">{{ uniqueCallers }}</p>
            <p class="text-sm text-gray-500 mt-1">New customers contacted</p>
          </div>
          <div class="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
            <FeatherIcon name="users" class="h-5 w-5 text-indigo-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Completed</p>
            <p class="text-2xl font-bold text-gray-900">{{ completedCalls }}</p>
            <p class="text-sm text-gray-500 mt-1">Completed calls</p>
          </div>
          <div class="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
            <FeatherIcon name="check-circle" class="h-5 w-5 text-green-600" />
          </div>
        </div>
      </div>

      
      <!-- New: Incoming Calls -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Incoming Calls</p>
            <p class="text-2xl font-bold text-gray-900">{{ incomingCalls }}</p>
            <p class="text-sm text-gray-500 mt-1">Total incoming calls</p>
          </div>
          <div class="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
            <FeatherIcon name="phone-incoming" class="h-5 w-5 text-blue-600" />
          </div>
        </div>
      </div>

      <!-- New: Outgoing Calls -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Outgoing Calls</p>
            <p class="text-2xl font-bold text-gray-900">{{ outgoingCalls }}</p>
            <p class="text-sm text-gray-500 mt-1">Total outgoing calls</p>
          </div>
          <div class="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center">
            <FeatherIcon name="phone-outgoing" class="h-5 w-5 text-purple-600" />
          </div>
        </div>
      </div>

      <!-- New: Missed Calls (duration 0 for incoming) -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Missed Calls</p>
            <p class="text-2xl font-bold text-gray-900">{{ missedIncomingDuration0 }}</p>
            <p class="text-sm text-gray-500 mt-1">Incoming calls with duration 0</p>
          </div>
          <div class="h-10 w-10 rounded-full bg-red-100 flex items-center justify-center">
            <FeatherIcon name="phone-off" class="h-5 w-5 text-red-600" />
          </div>
        </div>
      </div>

      <!-- New: Did Not Picked (outgoing with duration 0) -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Did Not Pick</p>
            <p class="text-2xl font-bold text-gray-900">{{ didNotPickedOutgoingDuration0 }}</p>
            <p class="text-sm text-gray-500 mt-1">Outgoing calls with duration 0</p>
          </div>
          <div class="h-10 w-10 rounded-full bg-yellow-100 flex items-center justify-center">
            <FeatherIcon name="x" class="h-5 w-5 text-yellow-600" />
          </div>
        </div>
      </div>

    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <ChartCard
        :title="`Call Type Distribution (${getViewContext()})`"
        :data="typeChart"
        type="doughnut"
        :loading="loading"
        :error="error"
        @refresh="$emit('refresh')"
      />

      <ChartCard
        :title="`Call Status Distribution (${getViewContext()})`"
        :data="statusChart"
        type="doughnut"
        :loading="loading"
        :error="error"
        @refresh="$emit('refresh')"
      />
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- Left: Calling Pattern (same width as Call Type Distribution) -->
      <div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 h-full">
          <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <FeatherIcon name="clock" class="h-5 w-5 text-indigo-500 mr-2" />
            Calling Pattern
          </h3>

          <div v-if="loading" class="space-y-3">
            <div class="animate-pulse">
              <div class="h-32 bg-gray-200 rounded-lg"></div>
            </div>
          </div>

          <div v-else-if="!callActivity || !callActivity.hourly_data || callActivity.hourly_data.length === 0" class="text-center py-6 text-gray-500">
            <FeatherIcon name="clock" class="h-10 w-10 mx-auto mb-2 text-gray-300" />
            <p class="text-sm">No calling activity</p>
          </div>

          <div v-else class="space-y-3">
            <div class="bg-gradient-to-r from-gray-50 to-gray-100 p-3 rounded-lg border border-gray-200">
              <h4 class="text-sm font-medium text-gray-700 mb-2 text-center">24-Hour Activity</h4>

              <div class="relative">
                <div class="flex justify-between text-xs text-gray-500 mb-2 px-1">
                  <span>6AM</span>
                  <span>12PM</span>
                  <span>6PM</span>
                  <span>12AM</span>
                </div>

                <div class="grid grid-cols-24 gap-0.5 items-end">
                  <div 
                    v-for="(hourData, index) in callActivity.hourly_data" 
                    :key="hourData.hour"
                    class="relative group flex items-end"
                  >
                    <div 
                      class="w-full bg-gray-200 rounded-sm transition-all duration-300 hover:scale-105 cursor-pointer"
                      :style="{ 
                        height: `${Math.max(4, (hourData.total_activity / Math.max(callActivity.max_activity, 1)) * 30)}px`,
                        backgroundColor: getActivityBarColor(hourData.total_activity, callActivity.max_activity)
                      }"
                    ></div>

                    <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-10">
                      <div class="text-center">
                        <div class="font-semibold">{{ hourData.hour }}</div>
                        <div class="text-gray-300">{{ hourData.calls }} calls</div>
                      </div>
                      <div class="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-3 border-r-3 border-t-3 border-transparent border-t-gray-900"></div>
                    </div>
                  </div>
                </div>

                <div v-if="callActivity.peak_hours && callActivity.peak_hours.length > 0" class="mt-2 text-center">
                  <div class="inline-flex items-center px-2 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs font-medium">
                    <FeatherIcon name="star" class="h-3 w-3 mr-1 text-indigo-600" />
                    Peak: {{ formatPeakHours(callActivity.peak_hours) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Recent Calls (reduced width to remaining area) -->
      <div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 h-full">
          <h3 class="text-lg font-semibold text-gray-900 mb-3">Recent Calls</h3>

          <div v-if="loading" class="space-y-3">
            <div v-for="i in 5" :key="i" class="animate-pulse">
              <div class="h-10 bg-gray-200 rounded-lg"></div>
            </div>
          </div>

          <div v-else-if="!recentCalls || recentCalls.length === 0" class="text-center py-6 text-gray-500">
            <FeatherIcon name="clock" class="w-8 h-8 mx-auto mb-2 text-gray-300" />
            <p>No recent calls</p>
          </div>

          <div v-else class="space-y-2">
            <div
              v-for="call in recentCalls"
              :key="call.name"
              class="flex items-center p-2 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors"
            >
              <div class="flex-shrink-0 mr-3">
                <div class="h-8 w-8 rounded-full flex items-center justify-center"
                     :class="getTypeClass(call.type)">
                  <FeatherIcon :name="getTypeIcon(call.type)" class="h-4 w-4 text-white" />
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium text-gray-900 text-sm truncate">
                  {{ call.from || 'Unknown' }} → {{ call.to || 'Unknown' }}
                </p>
                <p class="text-xs text-gray-600">
                  {{ call.type }} • {{ call.status }} • {{ call.start_time }}
                </p>
              </div>
              <div class="flex-shrink-0 text-sm text-gray-700">
                {{ formatDuration(call.duration || 0) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import ChartCard from './ChartCard.vue'

const props = defineProps({
  data: { type: Object, default: () => ({}) },
  currentView: { type: String, default: 'daily' },
  loading: { type: Boolean, default: false },
  error: { type: String, default: null }
})

defineEmits(['refresh'])

const typeChart = computed(() =>
  (props.data.call_type_distribution || []).map(i => ({ label: i.type, value: i.count }))
)

const statusChart = computed(() =>
  (props.data.call_status_distribution || []).map(i => ({ label: i.status, value: i.count }))
)

const recentCalls = computed(() => props.data.recent_calls || [])

const totalCalls = computed(() =>
  (props.data.call_type_distribution || []).reduce((sum, i) => sum + (i.count || 0), 0)
)

const completedCalls = computed(() =>
  (props.data.call_status_distribution || [])
    .filter(i => String(i.status).toLowerCase() === 'completed')
    .reduce((sum, i) => sum + (i.count || 0), 0)
)

const missedCalls = computed(() =>
  (props.data.call_status_distribution || [])
    .filter(i => ['no answer', 'missed'].includes(String(i.status).toLowerCase()))
    .reduce((sum, i) => sum + (i.count || 0), 0)
)

// New metrics
const incomingCalls = computed(() => props.data.incoming_calls || 0)
const outgoingCalls = computed(() => props.data.outgoing_calls || 0)
const missedIncomingDuration0 = computed(() => props.data.missed_incoming_duration0 || 0)
const didNotPickedOutgoingDuration0 = computed(() => props.data.did_not_picked_outgoing_duration0 || 0)
const uniqueCallers = computed(() => props.data.unique_callers || 0)
const callActivity = computed(() => props.data.call_activity_pattern || { hourly_data: [] })

const getViewContext = () => {
  switch (props.currentView) {
    case 'daily': return 'Today'
    case 'weekly': return 'This Week'
    case 'monthly': return 'This Month'
    default: return 'All Time'
  }
}

const formatDuration = (minutes) => {
  if (!minutes || minutes === 0) return '0m'
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (hours > 0) return `${hours}h ${mins}m`
  return `${mins}m`
}

const getTypeIcon = (type) => {
  const map = { Incoming: 'phone-incoming', Outgoing: 'phone-outgoing', Missed: 'phone-off' }
  return map[type] || 'phone'
}

const getTypeClass = (type) => {
  const map = { Incoming: 'bg-blue-500', Outgoing: 'bg-purple-500', Missed: 'bg-red-500' }
  return map[type] || 'bg-gray-500'
}

const getActivityBarColor = (activity, maxActivity) => {
  if (!maxActivity || maxActivity === 0) return '#e5e7eb'
  const ratio = activity / maxActivity
  if (ratio >= 0.8) return '#7c3aed'
  if (ratio >= 0.6) return '#3b82f6'
  if (ratio >= 0.4) return '#10b981'
  if (ratio >= 0.2) return '#f59e0b'
  return '#6b7280'
}

const formatPeakHours = (peakHours) => {
  if (!peakHours || peakHours.length === 0) return 'None'
  const formatted = peakHours.map(h => {
    const hr = parseInt(h)
    if (hr === 0) return '12:00 AM'
    if (hr < 12) return `${hr}:00 AM`
    if (hr === 12) return '12:00 PM'
    return `${hr - 12}:00 PM`
  })
  if (formatted.length === 1) return formatted[0]
  if (formatted.length === 2) return `${formatted[0]} and ${formatted[1]}`
  const last = formatted.pop()
  return `${formatted.join(', ')}, and ${last}`
}
</script>

<style scoped>
.calllog-analytics {
  animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 24-column grid for timeline */
.grid-cols-24 {
  grid-template-columns: repeat(24, minmax(0, 1fr));
}

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


