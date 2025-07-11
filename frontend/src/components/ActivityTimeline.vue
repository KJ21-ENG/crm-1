<template>
  <div class="space-y-6">
    <div v-for="activity in activities" :key="activity.name" class="relative">
      <!-- Timeline line -->
      <div class="absolute left-0 top-0 ml-2.5 h-full w-px bg-gray-200"></div>

      <div class="relative flex gap-x-4">
        <!-- Timeline dot -->
        <div class="absolute left-0 top-2 -ml-1">
          <div class="h-2 w-2 rounded-full ring-4 ring-white" :class="getActivityColor(activity.type)"></div>
        </div>

        <div class="flex-auto py-0.5 text-sm leading-5">
          <div class="font-medium text-gray-900">
            {{ activity.title }}
          </div>
          <p v-if="activity.description" class="text-gray-500">{{ activity.description }}</p>
          <p class="mt-1 text-xs text-gray-500">
            {{ formatDate(activity.creation) }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { format } from 'date-fns'

const props = defineProps({
  activities: {
    type: Array,
    required: true,
    validator: (activities) => {
      return activities.every(activity => 
        typeof activity === 'object' && 
        'name' in activity &&
        'title' in activity &&
        'type' in activity &&
        'creation' in activity
      )
    }
  }
})

function getActivityColor(type) {
  const colors = {
    status: 'bg-blue-500',
    comment: 'bg-gray-500',
    assignment: 'bg-purple-500',
    creation: 'bg-green-500',
    default: 'bg-gray-500'
  }
  return colors[type] || colors.default
}

function formatDate(date) {
  return format(new Date(date), 'MMM d, yyyy h:mm a')
}
</script> 