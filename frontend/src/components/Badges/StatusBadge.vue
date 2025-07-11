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

const props = defineProps({
  status: {
    type: String,
    required: true,
  },
})

const statusClass = computed(() => {
  const classes = {
    'New': 'bg-blue-50 text-blue-700',
    'Open': 'bg-yellow-50 text-yellow-700',
    'In Progress': 'bg-purple-50 text-purple-700',
    'Pending Customer': 'bg-orange-50 text-orange-700',
    'Resolved': 'bg-green-50 text-green-700',
    'Closed': 'bg-gray-50 text-gray-700',
  }
  return classes[props.status] || 'bg-gray-50 text-gray-700'
})
</script> 