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
import { ref, onMounted, watch, nextTick, computed } from 'vue'
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

// Color palette for charts
const colors = [
  '#3B82F6', '#10B981', '#F59E0B', '#EF4444', 
  '#8B5CF6', '#06B6D4', '#84CC16', '#F97316',
  '#EC4899', '#8B5A2B', '#6366F1', '#14B8A6'
]

const getColorForIndex = (index) => {
  return colors[index % colors.length]
}



const isDistributionChart = computed(() => {
  return props.type === 'bar' || props.type === 'doughnut' || props.type === 'pie'
})

const isTrendsChart = computed(() => {
  return props.type === 'line' && props.data.length > 0 && props.data[0].hasOwnProperty('leads') && props.data[0].hasOwnProperty('tickets')
})

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
        borderColor: getColorForIndex(0),
        backgroundColor: getColorForIndex(0) + '20',
        tension: 0.4
      })
      datasets.push({
        label: 'Tickets',
        data: props.data.map(item => item.tickets),
        borderColor: getColorForIndex(1),
        backgroundColor: getColorForIndex(1) + '20',
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
          borderColor: getColorForIndex(0),
          backgroundColor: getColorForIndex(0) + '20',
          tension: 0.4
        }]
      }
    }
  } else {
    // Bar, doughnut, pie charts
    const backgroundColor = props.data.map((_, index) => getColorForIndex(index))
    const borderColor = props.data.map((_, index) => getColorForIndex(index))
    
    chartData = {
      labels: props.data.map(item => item.label || item.name),
      datasets: [{
        label: props.title,
        data: props.data.map(item => item.value || item.count),
        backgroundColor: backgroundColor,
        borderColor: borderColor,
        borderWidth: 1
      }]
    }
  }
  
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true, // Always show legend for all charts
        position: 'bottom',
        labels: {
          usePointStyle: true,
          padding: 15,
          font: {
            size: 12,
            weight: '500'
          },
          generateLabels: function(chart) {
            const datasets = chart.data.datasets;
            return datasets.map((dataset, index) => ({
              text: dataset.label,
              fillStyle: dataset.borderColor || dataset.backgroundColor,
              strokeStyle: dataset.borderColor || dataset.backgroundColor,
              lineWidth: 2,
              pointStyle: props.type === 'line' ? 'line' : 'circle',
              hidden: false,
              index: index
            }));
          }
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== undefined) {
              label += context.parsed.y;
            } else if (context.parsed !== undefined) {
              label += context.parsed;
            }
            return label;
          }
        }
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