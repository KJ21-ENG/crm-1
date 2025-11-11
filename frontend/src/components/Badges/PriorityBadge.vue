<template>
  <div
    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
    :class="priorityClass"
  >
    {{ priority }}
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  priority: {
    type: String,
    required: true,
  },
})

const priorityClass = computed(() => {
  const classes = {
    'Low': 'bg-gray-50 text-gray-700',
    'Medium': 'bg-blue-50 text-blue-700',
    'High': 'bg-orange-50 text-orange-700',
    'Urgent': 'bg-red-50 text-red-700',
  }
  return classes[props.priority] || 'bg-gray-50 text-gray-700'
})
</script> 