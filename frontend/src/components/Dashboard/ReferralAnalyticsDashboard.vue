<template>
  <div class="referral-analytics-dashboard">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold text-ink-gray-9">
        Referral Analytics Dashboard
      </h2>
      <div class="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          @click="refreshData"
          :loading="loading"
        >
          <RefreshIcon class="w-4 h-4 mr-2" />
          Refresh
        </Button>
        <Button
          variant="outline"
          size="sm"
          @click="exportData"
          :loading="exporting"
        >
          <ExportIcon class="w-4 h-4 mr-2" />
          Export
        </Button>
      </div>
    </div>

    <!-- Compact Filters -->
    <div class="bg-white rounded-lg p-3 border border-gray-200 mb-4">
      <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div>
          <label class="block text-xs font-medium text-ink-gray-7 mb-1">Date From</label>
          <input
            v-model="filters.dateFrom"
            type="date"
            class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-ink-gray-7 mb-1">Date To</label>
          <input
            v-model="filters.dateTo"
            type="date"
            class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-ink-gray-7 mb-1">Account Type</label>
          <select
            v-model="filters.accountType"
            class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All Types</option>
            <option value="Individual">Individual</option>
            <option value="HUF">HUF</option>
            <option value="Corporate">Corporate</option>
            <option value="NRI">NRI</option>
            <option value="LLP">LLP</option>
            <option value="Minor">Minor</option>
            <option value="Partnership">Partnership</option>
            <option value="Others">Others</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-ink-gray-7 mb-1">Lead Category</label>
          <select
            v-model="filters.leadCategory"
            class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All Categories</option>
            <option value="Direct">Direct</option>
            <option value="Indirect">Indirect</option>
          </select>
        </div>
        <div class="flex items-end gap-2">
          <Button
            @click="applyFilters"
            :loading="loading"
            size="sm"
            class="flex-1"
          >
            Apply
          </Button>
          <Button
            @click="clearFilters"
            variant="outline"
            size="sm"
          >
            Clear
          </Button>
        </div>
      </div>
    </div>

    <!-- Compact Conversion Funnel -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
      <div class="bg-white rounded-lg p-3 border border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs text-ink-gray-6">Total Leads with Referral</p>
            <p class="text-lg font-bold text-ink-gray-9">{{ conversionFunnel.total_leads_with_referral || 0 }}</p>
          </div>
          <div class="h-6 w-6 rounded-full bg-blue-100 flex items-center justify-center">
            <ArrowUpRightIcon class="h-3 w-3 text-blue-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg p-3 border border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs text-ink-gray-6">Converted Leads</p>
            <p class="text-lg font-bold text-ink-gray-9">{{ conversionFunnel.converted_leads || 0 }}</p>
          </div>
          <div class="h-6 w-6 rounded-full bg-green-100 flex items-center justify-center">
            <CheckIcon class="h-3 w-3 text-green-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg p-3 border border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs text-ink-gray-6">Referral Conversion Rate</p>
            <p class="text-lg font-bold text-ink-gray-9">{{ conversionFunnel.conversion_rate || 0 }}%</p>
          </div>
          <div class="h-6 w-6 rounded-full bg-purple-100 flex items-center justify-center">
            <ActivityIcon class="h-3 w-3 text-purple-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg p-3 border border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs text-ink-gray-6">Overall Conversion Rate</p>
            <p class="text-lg font-bold text-ink-gray-9">{{ conversionFunnel.overall_conversion_rate || 0 }}%</p>
          </div>
          <div class="h-6 w-6 rounded-full bg-orange-100 flex items-center justify-center">
            <ConvertIcon class="h-3 w-3 text-orange-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Compact Top Referrers -->
    <div class="bg-white rounded-lg border border-gray-200 mb-4">
      <div class="p-3 border-b border-gray-200">
        <h3 class="text-sm font-medium text-ink-gray-9">Top Referrers</h3>
        <p class="text-xs text-ink-gray-6">Customers with the most successful referrals</p>
      </div>
      <div class="p-3">
        <div v-if="loading" class="text-center py-4">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
        </div>
        <div v-else-if="topReferrers.length === 0" class="text-center py-4">
          <ArrowUpRightIcon class="h-8 w-8 text-gray-300 mx-auto mb-2" />
          <p class="text-sm text-ink-gray-6">No referral data available</p>
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="referrer in topReferrers.slice(0, 5)"
            :key="`${referrer.referrer_name}-${referrer.client_id}`"
            class="flex items-center justify-between p-2 bg-gray-50 rounded"
          >
            <div class="flex-1">
              <p class="text-sm font-medium text-ink-gray-9">{{ referrer.referrer_name || 'Unknown' }}</p>
              <p class="text-xs text-ink-gray-6">{{ referrer.referrer_mobile || 'No mobile' }}</p>
            </div>
            <div class="text-right">
              <p class="text-sm font-medium text-ink-gray-9">{{ referrer.client_id }}</p>
              <p class="text-xs text-ink-gray-6">{{ referrer.total_referrals }} referrals</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Compact Referral Source Table -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div class="p-3 border-b border-gray-200">
        <h3 class="text-sm font-medium text-ink-gray-9">Referral Source Table</h3>
        <p class="text-xs text-ink-gray-6">Detailed referral source information</p>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-ink-gray-6 uppercase tracking-wider">
                Referrer Name
              </th>
              <th class="px-3 py-2 text-left text-xs font-medium text-ink-gray-6 uppercase tracking-wider">
                Client ID
              </th>
              <th class="px-3 py-2 text-left text-xs font-medium text-ink-gray-6 uppercase tracking-wider">
                Account Type
              </th>
              <th class="px-3 py-2 text-left text-xs font-medium text-ink-gray-6 uppercase tracking-wider">
                Total Referrals
              </th>
              <th class="px-3 py-2 text-left text-xs font-medium text-ink-gray-6 uppercase tracking-wider">
                Success Rate
              </th>
              <th class="px-3 py-2 text-left text-xs font-medium text-ink-gray-6 uppercase tracking-wider">
                Last Referral
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="loading">
              <td colspan="6" class="px-3 py-4 text-center">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
              </td>
            </tr>
            <tr v-else-if="sourceTable.length === 0">
              <td colspan="6" class="px-3 py-4 text-center text-ink-gray-6">
                No referral source data available
              </td>
            </tr>
            <tr
              v-for="source in sourceTable.slice(0, 10)"
              :key="`${source.referrer_name}-${source.client_id}`"
              class="hover:bg-gray-50"
            >
              <td class="px-3 py-2 whitespace-nowrap">
                <div>
                  <p class="text-sm font-medium text-ink-gray-9">{{ source.referrer_name || 'Unknown' }}</p>
                  <p class="text-xs text-ink-gray-6">{{ source.referrer_mobile || 'No mobile' }}</p>
                </div>
              </td>
              <td class="px-3 py-2 whitespace-nowrap text-sm text-ink-gray-9">
                {{ source.client_id }}
              </td>
              <td class="px-3 py-2 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                  {{ source.account_type }}
                </span>
              </td>
              <td class="px-3 py-2 whitespace-nowrap text-sm text-ink-gray-9">
                {{ source.total_referrals }}
              </td>
              <td class="px-3 py-2 whitespace-nowrap text-sm text-ink-gray-9">
                {{ source.total_referrals > 0 ? Math.round((source.successful_referrals / source.total_referrals) * 100) : 0 }}%
              </td>
              <td class="px-3 py-2 whitespace-nowrap text-xs text-ink-gray-6">
                {{ formatDate(source.last_referral_date) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import { Button } from 'frappe-ui'
import ArrowUpRightIcon from '@/components/Icons/ArrowUpRightIcon.vue'
import CheckIcon from '@/components/Icons/CheckIcon.vue'
import ActivityIcon from '@/components/Icons/ActivityIcon.vue'
import ConvertIcon from '@/components/Icons/ConvertIcon.vue'
import RefreshIcon from '@/components/Icons/RefreshIcon.vue'
import ExportIcon from '@/components/Icons/ExportIcon.vue'

const loading = ref(false)
const exporting = ref(false)
const topReferrers = ref([])
const sourceTable = ref([])
const conversionFunnel = ref({})

const filters = ref({
  dateFrom: '',
  dateTo: '',
  accountType: '',
  leadCategory: ''
})

// Create resources for API calls
const topReferrersResource = createResource({
  url: 'crm.api.referral_analytics.get_top_referrers',
  auto: false,
})

const sourceTableResource = createResource({
  url: 'crm.api.referral_analytics.get_referral_source_table',
  auto: false,
})

const conversionFunnelResource = createResource({
  url: 'crm.api.referral_analytics.get_conversion_funnel',
  auto: false,
})

const exportResource = createResource({
  url: 'crm.api.referral_analytics.export_referral_analytics',
  auto: false,
})

async function loadData() {
  loading.value = true
  try {
    const params = {
      date_from: filters.value.dateFrom || undefined,
      date_to: filters.value.dateTo || undefined,
      account_type: filters.value.accountType || undefined,
      lead_category: filters.value.leadCategory || undefined
    }
    
    // Load all data with filters
    const [referrersData, sourceData, funnelData] = await Promise.all([
      topReferrersResource.submit(params),
      sourceTableResource.submit(params),
      conversionFunnelResource.submit(params)
    ])
    
    topReferrers.value = referrersData || []
    sourceTable.value = sourceData || []
    conversionFunnel.value = funnelData || {}
    
    console.log('Referral Analytics Data Loaded:', {
      referrers: topReferrers.value.length,
      sources: sourceTable.value.length,
      funnel: conversionFunnel.value
    })
    
  } catch (error) {
    console.error('Error loading referral analytics data:', error)
  } finally {
    loading.value = false
  }
}

async function refreshData() {
  await loadData()
}

async function applyFilters() {
  await loadData()
}

async function clearFilters() {
  filters.value = {
    dateFrom: '',
    dateTo: '',
    accountType: '',
    leadCategory: ''
  }
  await loadData()
}

async function exportData() {
  exporting.value = true
  try {
    const params = {
      date_from: filters.value.dateFrom || undefined,
      date_to: filters.value.dateTo || undefined,
      account_type: filters.value.accountType || undefined,
      lead_category: filters.value.leadCategory || undefined,
      format: 'csv'
    }
    
    const exportData = await exportResource.submit(params)
    
    // Create and download CSV file
    if (exportData && !exportData.error) {
      const csvContent = generateCSV(exportData)
      downloadCSV(csvContent, `referral_analytics_${new Date().toISOString().split('T')[0]}.csv`)
    }
    
  } catch (error) {
    console.error('Error exporting data:', error)
  } finally {
    exporting.value = false
  }
}

function generateCSV(data) {
  // Generate CSV content from the data
  let csv = 'Referral Analytics Report\n\n'
  
  // Top Referrers
  csv += 'Top Referrers\n'
  csv += 'Referrer Name,Client ID,Total Referrals,Last Referral Date\n'
  data.top_referrers?.forEach(referrer => {
    csv += `"${referrer.referrer_name}","${referrer.client_id}",${referrer.total_referrals},"${referrer.last_referral_date}"\n`
  })
  
  csv += '\n'
  
  // Source Table
  csv += 'Referral Source Table\n'
  csv += 'Referrer Name,Client ID,Account Type,Total Referrals,Total Leads,Last Referral Date\n'
  data.source_table?.forEach(source => {
    csv += `"${source.referrer_name}","${source.client_id}","${source.account_type}",${source.total_referrals},${source.total_leads_referred},"${source.last_referral_date}"\n`
  })
  
  csv += '\n'
  
  // Conversion Funnel
  csv += 'Conversion Funnel\n'
  csv += 'Metric,Value\n'
  csv += `Total Leads with Referral,${data.conversion_funnel?.total_leads_with_referral || 0}\n`
  csv += `Converted Leads,${data.conversion_funnel?.converted_leads || 0}\n`
  csv += `Referral Conversion Rate,${data.conversion_funnel?.conversion_rate || 0}%\n`
  csv += `Overall Conversion Rate,${data.conversion_funnel?.overall_conversion_rate || 0}%\n`
  
  return csv
}

function downloadCSV(content, filename) {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', filename)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.referral-analytics-dashboard {
  @apply space-y-6;
}
</style> 