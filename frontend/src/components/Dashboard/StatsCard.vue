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
      <div class="flex-shrink-0 flex items-center space-x-2">
        <!-- Tooltip button -->
        <div v-if="tooltip?.enabled" class="relative">
          <button
            ref="tooltipButton"
            class="p-1 rounded-full hover:bg-gray-100 transition-colors"
            @mouseenter="handleMouseEnter"
            @mouseleave="showTooltip = false"
            @click="toggleTooltip"
          >
            <FeatherIcon name="info" class="w-4 h-4 text-gray-400 hover:text-gray-600" />
          </button>

          <!-- Tooltip -->
          <div
            v-if="showTooltip && tooltipData"
            ref="tooltip"
            class="absolute bottom-full right-0 mb-2 z-50 w-80 bg-white border border-gray-200 text-gray-900 text-sm rounded-lg shadow-lg p-3"
          >
            <div class="flex items-center justify-between mb-2">
              <h4 class="font-medium text-gray-900">{{ tooltipData.metric_type }}</h4>
              <button
                class="text-gray-400 hover:text-gray-600"
                @click="showTooltip = false"
              >
                <FeatherIcon name="x" class="w-4 h-4" />
              </button>
            </div>

            <div v-if="tooltipLoading" class="text-center py-4">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mx-auto"></div>
              <p class="mt-2 text-gray-600">Loading...</p>
            </div>

            <div v-else-if="tooltipData.leads?.length">
              <p class="mb-2 text-gray-900">{{ tooltipData.total_count }} leads</p>
              <div class="max-h-40 overflow-y-auto space-y-2">
                <div
                  v-for="lead in tooltipData.leads.slice(0, 10)"
                  :key="lead.name"
                  class="flex justify-between items-center py-1 border-b border-gray-200 last:border-b-0"
                >
                  <div>
                    <p class="font-medium text-gray-900">{{ lead.lead_name || lead.name }}</p>
                    <p class="text-xs text-gray-600">{{ lead.customer_id || 'No customer' }}</p>
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ formatDateTime(lead.account_opened_on || lead.account_activated_on) }}
                  </div>
                </div>
                <div v-if="tooltipData.total_count > 10" class="text-center py-1 text-gray-500 text-xs">
                  ... and {{ tooltipData.total_count - 10 }} more
                </div>
              </div>
            </div>

            <div v-else class="text-center py-4 text-gray-500">
              No leads found
            </div>
          </div>
        </div>

        <!-- Clickable arrow -->
        <div v-if="clickable">
          <FeatherIcon name="arrow-right" class="w-4 h-4 text-gray-400" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
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
  },
  tooltip: {
    type: Object,
    default: null
  },
  filters: {
    type: Object,
    default: null
  }
})

// Tooltip functionality
const showTooltip = ref(false)
const tooltipData = ref(null)
const tooltipLoading = ref(false)

const emit = defineEmits(['click'])

const handleClick = () => {
  if (props.clickable && props.target) {
    emit('click', props.target, props.filters || {})
  }
}

const handleMouseEnter = async () => {
  if (props.tooltip?.fetchData && !tooltipData.value) {
    tooltipLoading.value = true
    try {
      const response = await props.tooltip.fetchData()
      // unwrap frappe response if needed
      tooltipData.value = response?.message ?? response
    } catch (error) {
      console.error('Error fetching tooltip data:', error)
      tooltipData.value = { leads: [], total_count: 0, metric_type: '' }
    } finally {
      tooltipLoading.value = false
    }
  }
  showTooltip.value = true
}

const toggleTooltip = async () => {
  if (showTooltip.value) {
    showTooltip.value = false
    return
  }

  if (props.tooltip?.fetchData && !tooltipData.value) {
    tooltipLoading.value = true
    try {
      const response = await props.tooltip.fetchData()
      tooltipData.value = response?.message ?? response
    } catch (error) {
      console.error('Error fetching tooltip data:', error)
    } finally {
      tooltipLoading.value = false
    }
  }
  showTooltip.value = true
}

const formatDateTime = (dateTime) => {
  if (!dateTime) return ''
  const date = new Date(dateTime)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  const time = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  return `${day}/${month}/${year} ${time}`
}

// Close tooltip when clicking outside
const handleClickOutside = (event) => {
  const tooltipButton = event.target.closest('[ref="tooltipButton"]')
  const tooltip = event.target.closest('[ref="tooltip"]')

  if (!tooltipButton && !tooltip) {
    showTooltip.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const iconBgColor = computed(() => {
  const colors = {
    blue: 'bg-blue-100',
    green: 'bg-green-100',
    orange: 'bg-orange-100',
    purple: 'bg-purple-100',
    red: 'bg-red-100',
    yellow: 'bg-yellow-100',
    teal: 'bg-teal-100',
    indigo: 'bg-indigo-100'
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
    yellow: 'text-yellow-600',
    teal: 'text-teal-600',
    indigo: 'text-indigo-600'
  }
  return colors[props.color] || colors.blue
})
</script> 
