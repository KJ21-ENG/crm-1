<template>
  <div 
    :class="[
      'bg-white rounded-lg shadow-sm border border-gray-200 p-4 transition-shadow',
      clickable ? 'cursor-pointer hover:shadow-md hover:border-blue-300' : 'hover:shadow-md'
    ]"
    @click="handleClick"
    @keydown.enter.prevent="handleClick"
    @keydown.space.prevent="handleClick"
    :role="clickable ? 'button' : null"
    :tabindex="clickable ? 0 : null"
  >
    <div class="flex items-center space-x-3">
      <div 
        :class="[
          'p-2 rounded-full flex-shrink-0',
          iconBgColor
        ]"
      >
        <FeatherIcon 
          :name="icon" 
          :class="[
            'w-5 h-5',
            iconColor
          ]"
        />
      </div>
      <div class="flex-1">
        <p class="text-sm font-medium text-gray-600">{{ title }}</p>
        <p class="text-2xl font-bold text-gray-900 mt-1">{{ value }}</p>
        <p v-if="subtitle" class="text-sm text-gray-500 mt-1">{{ subtitle }}</p>
        <div v-if="change" class="flex items-center mt-1">
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
      <div v-if="clickable" class="flex-shrink-0">
        <FeatherIcon name="arrow-right" class="w-4 h-4 text-gray-400" />
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
  subtitle: {
    type: String,
    default: null
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
  },
  clickable: {
    type: Boolean,
    default: false
  },
  target: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['click'])

const handleClick = () => {
  if (props.clickable && props.target) {
    emit('click', props.target)
  }
}

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