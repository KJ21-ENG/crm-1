<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-lg font-semibold text-gray-900">Recent Activities</h3>
      <Button 
        variant="ghost" 
        size="sm"
        @click="$emit('refresh')"
        :loading="loading"
      >
        <FeatherIcon name="refresh-cw" class="w-4 h-4" />
      </Button>
    </div>
    
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="animate-pulse">
        <div class="flex items-center space-x-3">
          <div class="w-7 h-7 bg-gray-200 rounded-full"></div>
          <div class="flex-1">
            <div class="h-4 bg-gray-200 rounded w-3/4"></div>
            <div class="h-3 bg-gray-200 rounded w-1/2 mt-1"></div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="error" class="text-center py-6 text-red-600">
      <FeatherIcon name="alert-circle" class="w-8 h-8 mx-auto mb-2" />
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="!activities || activities.length === 0" class="text-center py-6 text-gray-500">
      <FeatherIcon name="activity" class="w-8 w-8 mx-auto mb-2" />
      <p>No recent activities</p>
    </div>
    
    <div v-else class="space-y-3">
      <div 
        v-for="activity in activities" 
        :key="activity.data.name"
        class="flex items-start space-x-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <div class="flex-shrink-0">
          <div 
            :class="[
              'w-7 h-7 rounded-full flex items-center justify-center',
              getActivityIconBg(activity.type)
            ]"
          >
            <FeatherIcon 
              :name="getActivityIcon(activity.type)" 
              :class="[
                'w-4 h-4',
                getActivityIconColor(activity.type)
              ]"
            />
          </div>
        </div>
        
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between">
            <p class="text-sm font-medium text-gray-900">
              {{ getActivityTitle(activity) }}
            </p>
            <span class="text-xs text-gray-500">
              {{ formatTime(activity.data.creation) }}
            </span>
          </div>
          <p class="text-sm text-gray-600 mt-1">
            {{ getActivityDescription(activity) }}
          </p>
          <div class="flex items-center mt-1">
            <Badge 
              :variant="getStatusVariant(activity.data.status)"
              size="sm"
            >
              {{ activity.data.status }}
            </Badge>
            <span v-if="activity.data.lead_owner || activity.data.assigned_to" class="text-xs text-gray-500 ml-2">
              • {{ activity.data.lead_owner || activity.data.assigned_to }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, FeatherIcon, Badge } from 'frappe-ui'

const props = defineProps({
  activities: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['refresh'])

const getActivityIcon = (type) => {
  const icons = {
    lead: 'user-plus',
    ticket: 'ticket',
    task: 'check-square',
    deal: 'briefcase'
  }
  return icons[type] || 'activity'
}

const getActivityIconBg = (type) => {
  const colors = {
    lead: 'bg-blue-100',
    ticket: 'bg-orange-100',
    task: 'bg-green-100',
    deal: 'bg-purple-100'
  }
  return colors[type] || 'bg-gray-100'
}

const getActivityIconColor = (type) => {
  const colors = {
    lead: 'text-blue-600',
    ticket: 'text-orange-600',
    task: 'text-green-600',
    deal: 'text-purple-600'
  }
  return colors[type] || 'text-gray-600'
}

const getActivityTitle = (activity) => {
  const titles = {
    lead: `${activity.data.display_name || 'Unknown Customer'} (${activity.data.status})`,
    ticket: `${activity.data.display_name || 'Unknown Customer'} (${activity.data.status})`,
    task: `${activity.data.subject || 'Unknown Task'} (${activity.data.status})`,
    deal: `${activity.data.organization || 'Unknown Deal'} (${activity.data.status})`
  }
  return titles[activity.type] || 'Unknown Activity'
}

const getActivityDescription = (activity) => {
  const descriptions = {
    lead: `Lead ${activity.data.name} was created`,
    ticket: `Ticket ${activity.data.name} was created`,
    task: `Task ${activity.data.name} was created`,
    deal: `Deal ${activity.data.name} was created`
  }
  return descriptions[activity.type] || 'Activity was created'
}

const getStatusVariant = (status) => {
  const variants = {
    'New': 'gray',
    'Open': 'blue',
    'In Progress': 'yellow',
    'Resolved': 'green',
    'Closed': 'gray',
    'Completed': 'green'
  }
  return variants[status] || 'gray'
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  const now = new Date()
  const diffInHours = (now - date) / (1000 * 60 * 60)
  
  if (diffInHours < 1) {
    return 'Just now'
  } else if (diffInHours < 24) {
    return `${Math.floor(diffInHours)}h ago`
  } else {
    return date.toLocaleDateString()
  }
}
</script> 