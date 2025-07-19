<template>
  <div
    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
    :class="statusClass"
  >
    {{ status }}
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { statusesStore } from '@/stores/statuses'

const props = defineProps({
  status: {
    type: String,
    required: true,
  },
})

const statusClass = computed(() => {
  // Get ticket statuses from the store
  const { ticketStatuses } = statusesStore()
  
  // Find the status in the database
  const statusData = ticketStatuses.data?.find(s => s.name === props.status)
  
  if (statusData && statusData.color) {
    // Convert color to badge class
    const colorMap = {
      'blue': 'bg-blue-50 text-blue-700',
      'orange': 'bg-orange-50 text-orange-700',
      'yellow': 'bg-yellow-50 text-yellow-700',
      'cyan': 'bg-cyan-50 text-cyan-700',
      'teal': 'bg-teal-50 text-teal-700',
      'green': 'bg-green-50 text-green-700',
      'gray': 'bg-gray-50 text-gray-700',
      'red': 'bg-red-50 text-red-700',
      'purple': 'bg-purple-50 text-purple-700',
      'violet': 'bg-violet-50 text-violet-700',
      'amber': 'bg-amber-50 text-amber-700',
      'pink': 'bg-pink-50 text-pink-700',
      'black': 'bg-black-50 text-black-700'
    }
    return colorMap[statusData.color] || 'bg-gray-50 text-gray-700'
  }
  
  return 'bg-gray-50 text-gray-700'
})
</script> 