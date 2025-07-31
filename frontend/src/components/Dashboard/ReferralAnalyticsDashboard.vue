<template>
  <div class="referral-analytics-dashboard">
    <!-- Compact Filters -->
    <div class="bg-white rounded-lg p-4 border border-gray-200 mb-6">
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-xs font-medium text-ink-gray-7 mb-1">Date From</label>
          <input
            v-model="filters.dateFrom"
            type="date"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-ink-gray-7 mb-1">Date To</label>
          <input
            v-model="filters.dateTo"
            type="date"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-ink-gray-7 mb-1">Account Type</label>
          <select
            v-model="filters.accountType"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
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
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
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

    <!-- Conversion Funnel -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-lg p-4 border border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs text-ink-gray-6">Total Leads with Referral</p>
            <p class="text-lg font-bold text-ink-gray-9">{{ conversionFunnel.total_leads_with_referral || 0 }}</p>
          </div>
          <div class="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
            <ArrowUpRightIcon class="h-4 w-4 text-blue-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg p-4 border border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs text-ink-gray-6">Converted Leads</p>
            <p class="text-lg font-bold text-ink-gray-9">{{ conversionFunnel.converted_leads || 0 }}</p>
          </div>
          <div class="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
            <CheckIcon class="h-4 w-4 text-green-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg p-4 border border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs text-ink-gray-6">Referral Conversion Rate</p>
            <p class="text-lg font-bold text-ink-gray-9">{{ conversionFunnel.conversion_rate || 0 }}%</p>
          </div>
          <div class="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center">
            <ActivityIcon class="h-4 w-4 text-purple-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg p-4 border border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs text-ink-gray-6">Overall Conversion Rate</p>
            <p class="text-lg font-bold text-ink-gray-9">{{ conversionFunnel.overall_conversion_rate || 0 }}%</p>
          </div>
          <div class="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center">
            <ConvertIcon class="h-4 w-4 text-orange-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Top Referrers and Source Table Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Top Referrers -->
      <div class="bg-white rounded-lg border border-gray-200">
        <div class="p-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold text-ink-gray-9">Top Referrers</h3>
              <p class="text-sm text-ink-gray-6">Customers with the most successful referrals</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              @click="refreshData"
              :loading="loading"
            >
              <RefreshIcon class="w-4 h-4" />
            </Button>
          </div>
        </div>
        <div class="p-4">
          <div v-if="loading" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          </div>
          <div v-else-if="topReferrers.length === 0" class="text-center py-8">
            <ArrowUpRightIcon class="h-12 w-12 text-gray-300 mx-auto mb-3" />
            <p class="text-sm text-ink-gray-6">No referral data available</p>
          </div>
          <div v-else>
            <div class="space-y-3">
              <div
                v-for="referrer in paginatedTopReferrers"
                :key="`${referrer.referrer_name}-${referrer.referral_code}`"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div class="flex-1">
                  <p class="text-sm font-medium text-ink-gray-9">{{ referrer.referrer_name || 'Unknown' }}</p>
                  <p class="text-xs text-ink-gray-6">{{ referrer.referrer_mobile || 'No mobile' }}</p>
                </div>
                <div class="text-right">
                  <p class="text-sm font-medium text-ink-gray-9">{{ referrer.referral_code }}</p>
                  <p class="text-xs text-ink-gray-6">{{ referrer.total_referrals }} referrals</p>
                </div>
              </div>
            </div>
            
            <!-- Top Referrers Pagination -->
            <div v-if="topReferrers.length > itemsPerPage" class="mt-4 flex items-center justify-between">
              <div class="flex items-center space-x-4">
                <div class="text-sm text-gray-600">
                  Showing {{ (topReferrersCurrentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(topReferrersCurrentPage * itemsPerPage, topReferrers.length) }} of {{ topReferrers.length }} results
                </div>
                <div class="flex items-center space-x-2">
                  <span class="text-sm text-gray-600">Show:</span>
                  <select 
                    v-model="itemsPerPage" 
                    class="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    @change="topReferrersCurrentPage = 1"
                  >
                    <option value="5">5</option>
                    <option value="10">10</option>
                    <option value="20">20</option>
                    <option :value="topReferrers.length">All</option>
                  </select>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  @click="topReferrersCurrentPage--"
                  :disabled="topReferrersCurrentPage === 1"
                >
                  Previous
                </Button>
                
                <!-- Page Numbers -->
                <div class="flex items-center space-x-1">
                  <button
                    v-for="page in topReferrersPageNumbers"
                    :key="page"
                    @click="page !== '...' ? topReferrersCurrentPage = page : null"
                    :class="[
                      'px-2 py-1 text-sm rounded border transition-colors',
                      page === topReferrersCurrentPage
                        ? 'bg-blue-500 text-white border-blue-500'
                        : page === '...'
                        ? 'text-gray-400 cursor-default'
                        : 'text-gray-600 border-gray-300 hover:bg-gray-50'
                    ]"
                    :disabled="page === '...'"
                  >
                    {{ page }}
                  </button>
                </div>
                
                <Button
                  variant="outline"
                  size="sm"
                  @click="topReferrersCurrentPage++"
                  :disabled="topReferrersCurrentPage === topReferrersTotalPages"
                >
                  Next
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Referral Source Table -->
      <div class="bg-white rounded-lg border border-gray-200">
        <div class="p-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold text-ink-gray-9">Referral Source Table</h3>
              <p class="text-sm text-ink-gray-6">Detailed referral source information</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              @click="exportData"
              :loading="exporting"
            >
              <ExportIcon class="w-4 h-4" />
            </Button>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-ink-gray-6 uppercase tracking-wider">
                  Referrer Name
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-ink-gray-6 uppercase tracking-wider">
                  Referral Code
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-ink-gray-6 uppercase tracking-wider">
                  Account Type
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-ink-gray-6 uppercase tracking-wider">
                  Total Referrals
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-ink-gray-6 uppercase tracking-wider">
                  Success Rate
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-ink-gray-6 uppercase tracking-wider">
                  Last Referral
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-ink-gray-6 uppercase tracking-wider">
                  Details
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-if="loading">
                <td colspan="7" class="px-4 py-6 text-center">
                  <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                </td>
              </tr>
              <tr v-else-if="sourceTable.length === 0">
                <td colspan="7" class="px-4 py-6 text-center text-ink-gray-6">
                  No referral source data available
                </td>
              </tr>
              <template v-for="source in paginatedSourceTable" :key="`${source.referrer_name}-${source.referral_code}`">
                <tr class="hover:bg-gray-50">
                  <td class="px-4 py-3 whitespace-nowrap">
                    <div>
                      <p class="text-sm font-medium text-ink-gray-9">{{ source.referrer_name || 'Unknown' }}</p>
                      <p class="text-xs text-ink-gray-6">{{ source.referrer_mobile || 'No mobile' }}</p>
                    </div>
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-ink-gray-9">
                    {{ source.referral_code }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap">
                    <span class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                      {{ source.account_type }}
                    </span>
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-ink-gray-9">
                    {{ source.total_referrals }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-ink-gray-9">
                    {{ source.total_referrals > 0 ? Math.round((source.successful_referrals / source.total_referrals) * 100) : 0 }}%
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-xs text-ink-gray-6">
                    {{ formatDate(source.last_referral_date) }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap">
                    <button
                      @click="toggleReferralDetails(source.referral_code)"
                      class="text-gray-400 hover:text-gray-600 transition-colors"
                      :title="expandedReferrals.includes(source.referral_code) ? 'Hide details' : 'Show details'"
                    >
                      <svg 
                        class="w-4 h-4 transition-transform duration-200"
                        :class="{ 'rotate-180': expandedReferrals.includes(source.referral_code) }"
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                  </td>
                </tr>
                
                <!-- Expanded Referral Details -->
                <tr v-if="expandedReferrals.includes(source.referral_code)">
                  <td colspan="7" class="px-4 py-0 bg-gray-50">
                    <div class="py-4">
                      <div v-if="loadingReferralDetails" class="text-center py-4">
                        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                        <p class="text-sm text-gray-600 mt-2">Loading referral details...</p>
                      </div>
                      <div v-else-if="referralDetails[source.referral_code] && referralDetails[source.referral_code].length > 0" class="space-y-3">
                        <h4 class="text-sm font-medium text-gray-900 mb-3">Referral Details for {{ source.referral_code }}</h4>
                        
                        <!-- Referral Details Table -->
                        <div class="overflow-x-auto">
                          <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                              <tr>
                                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Lead Name
                                </th>
                                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Contact
                                </th>
                                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Status
                                </th>
                                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Account Type
                                </th>
                                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Lead Category
                                </th>
                                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Client ID
                                </th>
                                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Assigned To
                                </th>
                                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Created
                                </th>
                                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Modified
                                </th>
                              </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-200">
                              <tr 
                                v-for="referral in referralDetails[source.referral_code]" 
                                :key="referral.name"
                                class="hover:bg-gray-50"
                              >
                                <td class="px-3 py-2 whitespace-nowrap">
                                  <div>
                                    <p class="text-sm font-medium text-gray-900">{{ referral.lead_name || 'Unnamed Lead' }}</p>
                                    <p class="text-xs text-gray-500">{{ referral.job_title || 'No job title' }}</p>
                                  </div>
                                </td>
                                <td class="px-3 py-2 whitespace-nowrap">
                                  <div>
                                    <p class="text-sm text-gray-900">{{ referral.mobile_no || 'No mobile' }}</p>
                                    <p class="text-xs text-gray-500">{{ referral.email || 'No email' }}</p>
                                  </div>
                                </td>
                                <td class="px-3 py-2 whitespace-nowrap">
                                  <span 
                                    :class="[
                                      'px-2 py-1 text-xs font-medium rounded-full',
                                      getStatusBadgeClass(referral.status)
                                    ]"
                                  >
                                    {{ referral.status }}
                                  </span>
                                </td>
                                <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900">
                                  {{ referral.account_type || 'N/A' }}
                                </td>
                                <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900">
                                  {{ referral.lead_category || 'N/A' }}
                                </td>
                                <td class="px-3 py-2 whitespace-nowrap">
                                  <span v-if="referral.client_id" class="text-sm font-medium text-green-600">
                                    {{ referral.client_id }}
                                  </span>
                                  <span v-else class="text-sm text-gray-400">Not assigned</span>
                                </td>
                                <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900">
                                  {{ referral.lead_owner || 'Unassigned' }}
                                </td>
                                <td class="px-3 py-2 whitespace-nowrap text-xs text-gray-500">
                                  {{ formatDate(referral.creation) }}
                                </td>
                                <td class="px-3 py-2 whitespace-nowrap text-xs text-gray-500">
                                  {{ formatDate(referral.modified) }}
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
          
          <!-- Source Table Pagination -->
          <div v-if="sourceTable.length > itemsPerPage" class="px-4 py-3 border-t border-gray-200">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-4">
                <div class="text-sm text-gray-600">
                  Showing {{ (sourceTableCurrentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(sourceTableCurrentPage * itemsPerPage, sourceTable.length) }} of {{ sourceTable.length }} results
                </div>
                <div class="flex items-center space-x-2">
                  <span class="text-sm text-gray-600">Show:</span>
                  <select 
                    v-model="itemsPerPage" 
                    class="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    @change="sourceTableCurrentPage = 1"
                  >
                    <option value="5">5</option>
                    <option value="10">10</option>
                    <option value="20">20</option>
                    <option :value="sourceTable.length">All</option>
                  </select>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  @click="sourceTableCurrentPage--"
                  :disabled="sourceTableCurrentPage === 1"
                >
                  Previous
                </Button>
                
                <!-- Page Numbers -->
                <div class="flex items-center space-x-1">
                  <button
                    v-for="page in sourceTablePageNumbers"
                    :key="page"
                    @click="page !== '...' ? sourceTableCurrentPage = page : null"
                    :class="[
                      'px-2 py-1 text-sm rounded border transition-colors',
                      page === sourceTableCurrentPage
                        ? 'bg-blue-500 text-white border-blue-500'
                        : page === '...'
                        ? 'text-gray-400 cursor-default'
                        : 'text-gray-600 border-gray-300 hover:bg-gray-50'
                    ]"
                    :disabled="page === '...'"
                  >
                    {{ page }}
                  </button>
                </div>
                
                <Button
                  variant="outline"
                  size="sm"
                  @click="sourceTableCurrentPage++"
                  :disabled="sourceTableCurrentPage === sourceTableTotalPages"
                >
                  Next
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
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

// Pagination state
const itemsPerPage = ref(5)
const topReferrersCurrentPage = ref(1)
const sourceTableCurrentPage = ref(1)

// Expandable details state
const expandedReferrals = ref([])
const referralDetails = ref({})
const loadingReferralDetails = ref(false)

const filters = ref({
  dateFrom: '',
  dateTo: '',
  accountType: '',
  leadCategory: ''
})

// Computed properties for pagination
const topReferrersTotalPages = computed(() => {
  if (!topReferrers.value || !Array.isArray(topReferrers.value) || itemsPerPage.value <= 0) {
    return 1
  }
  return Math.ceil(topReferrers.value.length / itemsPerPage.value)
})

const sourceTableTotalPages = computed(() => {
  if (!sourceTable.value || !Array.isArray(sourceTable.value) || itemsPerPage.value <= 0) {
    return 1
  }
  return Math.ceil(sourceTable.value.length / itemsPerPage.value)
})

const paginatedTopReferrers = computed(() => {
  if (!topReferrers.value || !Array.isArray(topReferrers.value)) {
    return []
  }
  const start = (topReferrersCurrentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return topReferrers.value.slice(start, end)
})

const paginatedSourceTable = computed(() => {
  if (!sourceTable.value || !Array.isArray(sourceTable.value)) {
    return []
  }
  const start = (sourceTableCurrentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return sourceTable.value.slice(start, end)
})

// Generate page numbers for pagination
const topReferrersPageNumbers = computed(() => {
  const pages = []
  const total = topReferrersTotalPages.value
  const current = topReferrersCurrentPage.value
  
  if (total <= 0) {
    return [1]
  }
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 3) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1)
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    }
  }
  return pages
})

const sourceTablePageNumbers = computed(() => {
  const pages = []
  const total = sourceTableTotalPages.value
  const current = sourceTableCurrentPage.value
  
  if (total <= 0) {
    return [1]
  }
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 3) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1)
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    }
  }
  return pages
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

const referralDetailsResource = createResource({
  url: 'crm.api.referral_analytics.get_referral_details',
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
    
    // Reset pagination when data changes
    topReferrersCurrentPage.value = 1
    sourceTableCurrentPage.value = 1
    
    // Clear expanded details when data changes
    expandedReferrals.value = []
    referralDetails.value = {}
    
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
  csv += 'Referrer Name,Referral Code,Total Referrals,Last Referral Date\n'
  data.top_referrers?.forEach(referrer => {
    csv += `"${referrer.referrer_name}","${referrer.referral_code}",${referrer.total_referrals},"${referrer.last_referral_date}"\n`
  })
  
  csv += '\n'
  
  // Source Table
  csv += 'Referral Source Table\n'
  csv += 'Referrer Name,Referral Code,Account Type,Total Referrals,Total Leads,Last Referral Date\n'
  data.source_table?.forEach(source => {
    csv += `"${source.referrer_name}","${source.referral_code}","${source.account_type}",${source.total_referrals},${source.total_leads_referred},"${source.last_referral_date}"\n`
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

function getStatusBadgeClass(status) {
  const statusMap = {
    'New': 'bg-gray-100 text-gray-800',
    'Open': 'bg-blue-100 text-blue-800',
    'In Progress': 'bg-yellow-100 text-yellow-800',
    'Qualified': 'bg-green-100 text-green-800',
    'Converted': 'bg-green-100 text-green-800',
    'Account Opened': 'bg-green-100 text-green-800',
    'Account Activated': 'bg-green-100 text-green-800',
    'Lost': 'bg-red-100 text-red-800',
    'Rejected': 'bg-red-100 text-red-800',
    'Closed': 'bg-gray-100 text-gray-800',
    'Completed': 'bg-green-100 text-green-800',
    'Pending': 'bg-orange-100 text-orange-800',
    'On Hold': 'bg-yellow-100 text-yellow-800'
  }
  
  return statusMap[status] || 'bg-gray-100 text-gray-800'
}

async function toggleReferralDetails(referralCode) {
  if (!referralCode) {
    console.warn('No referral code provided to toggleReferralDetails')
    return
  }
  
  if (expandedReferrals.value.includes(referralCode)) {
    expandedReferrals.value = expandedReferrals.value.filter(code => code !== referralCode)
    referralDetails.value[referralCode] = null // Clear details when hiding
  } else {
    expandedReferrals.value.push(referralCode)
    loadingReferralDetails.value = true
    try {
      const details = await referralDetailsResource.submit({
        referral_code: referralCode,
        date_from: filters.value.dateFrom || undefined,
        date_to: filters.value.dateTo || undefined,
        account_type: filters.value.accountType || undefined,
        lead_category: filters.value.leadCategory || undefined
      })
      referralDetails.value[referralCode] = details || []
    } catch (error) {
      console.error('Error loading referral details:', error)
      referralDetails.value[referralCode] = []
    } finally {
      loadingReferralDetails.value = false
    }
  }
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