<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
      <div v-if="showRefresh" class="flex items-center space-x-2">
        <Button 
          variant="ghost" 
          size="sm"
          @click="$emit('refresh')"
          :loading="loading"
        >
          <FeatherIcon name="refresh-cw" class="w-4 h-4" />
        </Button>
      </div>
    </div>
    
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>
    
    <div v-else-if="error" class="flex items-center justify-center h-64 text-red-600">
      <div class="text-center">
        <FeatherIcon name="alert-circle" class="w-8 h-8 mx-auto mb-2" />
        <p>{{ error }}</p>
      </div>
    </div>
    
    <div v-else-if="!data || data.length === 0" class="flex items-center justify-center h-64 text-gray-500">
      <div class="text-center">
        <FeatherIcon name="bar-chart-2" class="w-8 h-8 mx-auto mb-2" />
        <p>No data available</p>
      </div>
    </div>
    
    <div v-else class="h-64">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { Button, FeatherIcon } from 'frappe-ui'
import Chart from 'chart.js/auto'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  data: {
    type: Array,
    default: () => []
  },
  type: {
    type: String,
    default: 'bar'
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  },
  showRefresh: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['refresh'])

const chartCanvas = ref(null)
let chart = null

const createChart = () => {
  if (!chartCanvas.value) return
  
  const ctx = chartCanvas.value.getContext('2d')
  
  if (chart) {
    chart.destroy()
  }
  
  let chartData = {}
  
  if (props.type === 'line') {
    // Handle line chart with multiple datasets
    const datasets = []
    
    // Check if data has leads and tickets properties (trends data)
    if (props.data.length > 0 && props.data[0].hasOwnProperty('leads')) {
      datasets.push({
        label: 'Leads',
        data: props.data.map(item => item.leads),
        borderColor: '#3B82F6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4
      })
      datasets.push({
        label: 'Tickets',
        data: props.data.map(item => item.tickets),
        borderColor: '#F59E0B',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        tension: 0.4
      })
      
      chartData = {
        labels: props.data.map(item => item.label),
        datasets
      }
    } else {
      // Single dataset line chart
      chartData = {
        labels: props.data.map(item => item.label || item.name),
        datasets: [{
          label: props.title,
          data: props.data.map(item => item.value || item.count),
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4
        }]
      }
    }
  } else {
    // Bar, doughnut, pie charts
    chartData = {
      labels: props.data.map(item => item.label || item.name),
      datasets: [{
        label: props.title,
        data: props.data.map(item => item.value || item.count),
        backgroundColor: [
          '#3B82F6', '#10B981', '#F59E0B', '#EF4444', 
          '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'
        ],
        borderColor: [
          '#2563EB', '#059669', '#D97706', '#DC2626',
          '#7C3AED', '#0891B2', '#65A30D', '#EA580C'
        ],
        borderWidth: 1
      }]
    }
  }
  
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: props.type !== 'doughnut' && props.type !== 'pie'
      }
    }
  }
  
  if (props.type === 'line') {
    options.scales = {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1
        }
      }
    }
  } else if (props.type === 'bar') {
    options.scales = {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1
        }
      }
    }
  }
  
  chart = new Chart(ctx, {
    type: props.type,
    data: chartData,
    options
  })
}

onMounted(() => {
  nextTick(() => {
    if (props.data && props.data.length > 0) {
      createChart()
    }
  })
})

watch(() => props.data, () => {
  nextTick(() => {
    if (props.data && props.data.length > 0) {
      createChart()
    }
  }, { deep: true })
})

watch(() => props.loading, (newVal) => {
  if (!newVal && props.data && props.data.length > 0) {
    nextTick(() => {
      createChart()
    })
  }
})
</script> 