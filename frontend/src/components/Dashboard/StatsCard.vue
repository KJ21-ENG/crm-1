<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-gray-600">{{ title }}</p>
        <p class="text-3xl font-bold text-gray-900 mt-2">{{ value }}</p>
        <div v-if="change" class="flex items-center mt-2">
          <span 
            :class="[
              'text-sm font-medium',
              change > 0 ? 'text-green-600' : 'text-red-600'
            ]"
          >
            {{ change > 0 ? '+' : '' }}{{ change }}%
          </span>
          <span class="text-sm text-gray-500 ml-1">vs last week</span>
        </div>
      </div>
      <div 
        :class="[
          'p-3 rounded-full',
          iconBgColor
        ]"
      >
        <FeatherIcon 
          :name="icon" 
          :class="[
            'w-6 h-6',
            iconColor
          ]"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  change: {
    type: Number,
    default: null
  },
  color: {
    type: String,
    default: 'blue'
  }
})

const iconBgColor = computed(() => {
  const colors = {
    blue: 'bg-blue-100',
    green: 'bg-green-100',
    orange: 'bg-orange-100',
    purple: 'bg-purple-100',
    red: 'bg-red-100',
    yellow: 'bg-yellow-100'
  }
  return colors[props.color] || colors.blue
})

const iconColor = computed(() => {
  const colors = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    orange: 'text-orange-600',
    purple: 'text-purple-600',
    red: 'text-red-600',
    yellow: 'text-yellow-600'
  }
  return colors[props.color] || colors.blue
})
</script> 