<template>
  <div
    :class="[
      'rounded-lg border border-gray-200 bg-white p-3 transition-all',
      clickable ? 'cursor-pointer hover:border-blue-200 hover:shadow-sm' : 'hover:shadow-sm',
    ]"
    @click="handleClick"
    @keydown.enter.prevent="handleClick"
    @keydown.space.prevent="handleClick"
    :role="clickable ? 'button' : null"
    :tabindex="clickable ? 0 : null"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0 flex-1">
        <p class="min-h-[2rem] break-words whitespace-normal text-[11px] font-medium leading-4 text-gray-600">
          {{ title }}
        </p>
        <p class="mt-1 text-xl font-semibold text-gray-900">{{ value }}</p>
        <p v-if="subtitle" class="mt-1 line-clamp-2 min-h-[2rem] text-[11px] leading-4 text-gray-500">
          {{ subtitle }}
        </p>
        <div v-else class="min-h-[2rem]"></div>
      </div>

      <div class="flex shrink-0 items-center gap-2">
        <div v-if="tooltip?.enabled" class="relative">
          <button
            class="rounded-full p-1 transition-colors hover:bg-gray-100"
            @mouseenter="handleMouseEnter"
            @mouseleave="showTooltip = false"
            @click.stop="toggleTooltip"
          >
            <FeatherIcon name="info" class="h-4 w-4 text-gray-400 hover:text-gray-600" />
          </button>

          <div
            v-if="showTooltip && tooltipData"
            class="absolute right-0 top-full z-50 mt-2 w-80 rounded-lg border border-gray-200 bg-white p-3 text-sm text-gray-900 shadow-lg"
          >
            <div class="mb-2 flex items-center justify-between">
              <h4 class="font-medium text-gray-900">{{ tooltipData.metric_type }}</h4>
              <button class="text-gray-400 hover:text-gray-600" @click.stop="showTooltip = false">
                <FeatherIcon name="x" class="h-4 w-4" />
              </button>
            </div>

            <div v-if="tooltipLoading" class="py-4 text-center">
              <div class="mx-auto h-4 w-4 animate-spin rounded-full border-b-2 border-gray-600"></div>
              <p class="mt-2 text-gray-600">Loading...</p>
            </div>

            <div v-else-if="tooltipData.leads?.length">
              <p class="mb-2 text-gray-900">{{ tooltipData.total_count }} leads</p>
              <div class="max-h-40 space-y-2 overflow-y-auto">
                <div
                  v-for="lead in tooltipData.leads.slice(0, 10)"
                  :key="lead.name"
                  class="flex items-center justify-between border-b border-gray-200 py-1 last:border-b-0"
                >
                  <div>
                    <p class="font-medium text-gray-900">{{ lead.lead_name || lead.name }}</p>
                    <p class="text-xs text-gray-600">{{ lead.customer_id || 'No customer' }}</p>
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ formatDateTime(lead.account_opened_on || lead.account_activated_on) }}
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="py-4 text-center text-gray-500">
              No leads found
            </div>
          </div>
        </div>

        <div
          v-if="indicatorClass"
          class="flex h-8 w-8 items-center justify-center rounded-full bg-gray-50"
        >
          <IndicatorIcon :class="indicatorClass" class="h-4 w-4" />
        </div>
        <div
          v-else
          :class="['flex h-8 w-8 items-center justify-center rounded-full', iconBgColor]"
        >
          <FeatherIcon :name="icon" :class="['h-4 w-4', iconColor]" />
        </div>
      </div>
    </div>

    <div v-if="clickable" class="mt-2 flex justify-end">
      <FeatherIcon name="arrow-right" class="h-4 w-4 text-gray-300" />
    </div>
  </div>
</template>

<script setup>
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import { computed, ref } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  title: { type: String, required: true },
  value: { type: [String, Number], required: true },
  subtitle: { type: String, default: '' },
  icon: { type: String, default: 'bar-chart-2' },
  color: { type: String, default: 'blue' },
  indicatorClass: { type: String, default: '' },
  clickable: { type: Boolean, default: false },
  target: { type: String, default: '' },
  tooltip: { type: Object, default: null },
  filters: { type: Object, default: null },
})

const emit = defineEmits(['click'])

const showTooltip = ref(false)
const tooltipData = ref(null)
const tooltipLoading = ref(false)

function handleClick() {
  if (props.clickable && props.target) {
    emit('click', props.target, props.filters || {})
  }
}

async function handleMouseEnter() {
  if (props.tooltip?.fetchData && !tooltipData.value) {
    tooltipLoading.value = true
    try {
      const response = await props.tooltip.fetchData()
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

async function toggleTooltip() {
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
      tooltipData.value = { leads: [], total_count: 0, metric_type: '' }
    } finally {
      tooltipLoading.value = false
    }
  }
  showTooltip.value = true
}

function formatDateTime(dateTime) {
  if (!dateTime) return ''
  const date = new Date(dateTime)
  if (Number.isNaN(date.getTime())) return ''
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  const time = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  return `${day}/${month}/${year} ${time}`
}

const iconBgColor = computed(() => {
  const colors = {
    blue: 'bg-blue-100',
    green: 'bg-green-100',
    orange: 'bg-orange-100',
    purple: 'bg-purple-100',
    red: 'bg-red-100',
    yellow: 'bg-yellow-100',
    teal: 'bg-teal-100',
    indigo: 'bg-indigo-100',
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
    indigo: 'text-indigo-600',
  }
  return colors[props.color] || colors.blue
})
</script>
