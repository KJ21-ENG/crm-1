<template>
  <Dialog
    v-model="isOpen"
    :options="{
      size: '3xl',
      position: 'top'
    }"
  >
    <template #body>
      <div class="universal-search-modal">
        <!-- Search Input -->
        <div class="search-input-wrapper sticky top-0 bg-white z-10 pb-4">
          <div class="relative">
            <FeatherIcon
              name="search"
              class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 w-5 h-5"
            />
            <input
              ref="searchInput"
              v-model="searchQuery"
              type="text"
              placeholder="Search for leads, customers, tickets, tasks, notes, and more..."
              class="w-full pl-11 pr-4 py-3 text-base border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:ring-0 focus:outline-none"
              @input="onSearchInput"
              @keydown="handleKeyDown"
            />
            <div class="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center gap-2">
              <span v-if="searching" class="text-sm text-gray-400">
                Searching...
              </span>
              <button
                v-if="searchQuery"
                @click="clearSearch"
                class="text-gray-400 hover:text-gray-600"
              >
                <FeatherIcon name="x" class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <!-- Search Results -->
        <div class="search-results-wrapper max-h-[60vh] overflow-y-auto">
          <!-- Loading State -->
          <div v-if="searching" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <p class="mt-2 text-sm text-gray-500">Searching across CRM...</p>
          </div>

          <!-- No Results -->
          <div v-else-if="searchQuery && results.length === 0 && !searching" class="text-center py-12">
            <FeatherIcon name="search" class="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <h3 class="text-lg font-medium text-gray-700 mb-1">No results found</h3>
            <p class="text-sm text-gray-500">
              Try searching with different keywords or check spelling
            </p>
          </div>

          <!-- Results List -->
          <div v-else-if="results.length > 0" class="divide-y divide-gray-100">
            <div
              v-for="(result, index) in results"
              :key="`${result.doctype}-${result.name}`"
              :class="[
                'search-result-item p-3 cursor-pointer transition-colors duration-150',
                selectedIndex === index
                  ? 'bg-blue-50 border-l-4 border-blue-500'
                  : 'hover:bg-gray-50 border-l-4 border-transparent'
              ]"
              @click="openResult(result)"
              @mouseenter="selectedIndex = index"
            >
              <div class="flex items-start gap-3">
                <!-- Icon -->
                <div class="flex-shrink-0 mt-1">
                  <div
                    class="w-8 h-8 rounded-lg flex items-center justify-center"
                    :class="getIconColorClass(result.doctype)"
                  >
                    <FeatherIcon :name="result.icon" class="w-4 h-4" />
                  </div>
                </div>

                <!-- Content -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between gap-2">
                    <div class="flex-1 min-w-0">
                      <h4 class="text-sm font-medium text-gray-900 truncate">
                        {{ result.title || result.name }}
                      </h4>
                      <p v-if="result.subtitle" class="text-xs text-gray-500 truncate mt-0.5">
                        {{ result.subtitle }}
                      </p>
                    </div>
                    <div class="flex-shrink-0 flex items-center gap-2">
                      <!-- Status Badge -->
                      <span
                        v-if="result.status"
                        class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                        :class="getStatusClass(result.status)"
                      >
                        {{ result.status }}
                      </span>
                    </div>
                  </div>
                  
                  <!-- DocType Label -->
                  <div class="flex items-center gap-2 mt-2">
                    <span class="text-xs text-gray-400">
                      {{ result.label }}
                    </span>
                    <span v-if="result.matched_field" class="text-xs text-gray-400">
                      • Matched in {{ formatFieldName(result.matched_field) }}
                    </span>
                  </div>
                </div>

                <!-- Arrow Icon -->
                <div class="flex-shrink-0">
                  <FeatherIcon name="arrow-right" class="w-4 h-4 text-gray-400" />
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State (No search yet) -->
          <div v-else-if="!searchQuery" class="py-8">
            <div class="text-center mb-8">
              <FeatherIcon name="zap" class="w-10 h-10 text-gray-300 mx-auto mb-3" />
              <h3 class="text-base font-medium text-gray-700 mb-1">Universal Search</h3>
              <p class="text-sm text-gray-500">
                Search across leads, customers, tickets, tasks, and more
              </p>
            </div>

            <!-- Quick Tips -->
            <div class="max-w-md mx-auto space-y-2 text-sm">
              <div class="flex items-start gap-2 text-gray-600">
                <FeatherIcon name="info" class="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>Type to search across all CRM data</span>
              </div>
              <div class="flex items-start gap-2 text-gray-600">
                <FeatherIcon name="arrow-up" class="w-4 h-4 mt-0.5 flex-shrink-0" />
                <FeatherIcon name="arrow-down" class="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>Use arrow keys to navigate results</span>
              </div>
              <div class="flex items-start gap-2 text-gray-600">
                <FeatherIcon name="corner-down-left" class="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>Press Enter to open selected result</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="search-footer sticky bottom-0 bg-gray-50 border-t border-gray-200 px-4 py-2 flex items-center justify-between text-xs text-gray-500 mt-4">
          <div class="flex items-center gap-4">
            <span v-if="results.length > 0">
              {{ results.length }} result{{ results.length !== 1 ? 's' : '' }} found
            </span>
            <span v-if="searchQuery && totalSearchTime">
              Search completed in {{ totalSearchTime }}ms
            </span>
          </div>
          <div class="flex items-center gap-2">
            <KeyboardShortcut :meta="true">K</KeyboardShortcut>
            <span>to toggle search</span>
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Dialog, FeatherIcon } from 'frappe-ui'
import { call } from 'frappe-ui'
import KeyboardShortcut from '@/components/KeyboardShortcut.vue'

const router = useRouter()

const isOpen = ref(false)
const searchQuery = ref('')
const results = ref([])
const searching = ref(false)
const selectedIndex = ref(0)
const searchInput = ref(null)
const totalSearchTime = ref(0)

let searchTimeout = null

// Expose methods to parent
defineExpose({
  open: openSearch,
  close: closeSearch,
  toggle: toggleSearch
})

function openSearch() {
  isOpen.value = true
  nextTick(() => {
    searchInput.value?.focus()
  })
}

function closeSearch() {
  isOpen.value = false
  searchQuery.value = ''
  results.value = []
  selectedIndex.value = 0
  totalSearchTime.value = 0
}

function toggleSearch() {
  if (isOpen.value) {
    closeSearch()
  } else {
    openSearch()
  }
}

function clearSearch() {
  searchQuery.value = ''
  results.value = []
  selectedIndex.value = 0
  totalSearchTime.value = 0
}

function onSearchInput() {
  // Debounce search
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  
  if (!searchQuery.value || searchQuery.value.trim().length < 2) {
    results.value = []
    return
  }
  
  searchTimeout = setTimeout(() => {
    performSearch()
  }, 300)
}

async function performSearch() {
  if (!searchQuery.value || searchQuery.value.trim().length < 2) {
    return
  }
  
  searching.value = true
  const startTime = Date.now()
  
  try {
    const response = await call('crm.api.search.universal_search', {
      query: searchQuery.value.trim(),
      limit: 20
    })
    
    totalSearchTime.value = Date.now() - startTime
    results.value = response.results || []
    selectedIndex.value = 0
  } catch (error) {
    console.error('Search error:', error)
    results.value = []
  } finally {
    searching.value = false
  }
}

function handleKeyDown(event) {
  if (event.key === 'ArrowDown') {
    event.preventDefault()
    selectedIndex.value = Math.min(selectedIndex.value + 1, results.value.length - 1)
    scrollToSelected()
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    selectedIndex.value = Math.max(selectedIndex.value - 1, 0)
    scrollToSelected()
  } else if (event.key === 'Enter') {
    event.preventDefault()
    if (results.value.length > 0 && selectedIndex.value >= 0) {
      openResult(results.value[selectedIndex.value])
    }
  } else if (event.key === 'Escape') {
    event.preventDefault()
    closeSearch()
  }
}

function scrollToSelected() {
  nextTick(() => {
    const selectedElement = document.querySelectorAll('.search-result-item')[selectedIndex.value]
    if (selectedElement) {
      selectedElement.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
    }
  })
}

function openResult(result) {
  closeSearch()
  
  // Navigate to the result
  if (result.route) {
    router.push(result.route)
  }
}

function getIconColorClass(doctype) {
  const colorMap = {
    'CRM Lead': 'bg-blue-100 text-blue-600',
    'CRM Customer': 'bg-green-100 text-green-600',
    'CRM Ticket': 'bg-red-100 text-red-600',
    'CRM Task': 'bg-purple-100 text-purple-600',
    'CRM Call Log': 'bg-yellow-100 text-yellow-600',
    'FCRM Note': 'bg-indigo-100 text-indigo-600',
    'CRM Support Pages': 'bg-pink-100 text-pink-600'
  }
  return colorMap[doctype] || 'bg-gray-100 text-gray-600'
}

function getStatusClass(status) {
  if (!status) return ''
  
  const statusLower = status.toLowerCase()
  
  if (statusLower.includes('open') || statusLower.includes('new')) {
    return 'bg-blue-100 text-blue-800'
  } else if (statusLower.includes('progress') || statusLower.includes('working')) {
    return 'bg-yellow-100 text-yellow-800'
  } else if (statusLower.includes('closed') || statusLower.includes('completed') || statusLower.includes('won')) {
    return 'bg-green-100 text-green-800'
  } else if (statusLower.includes('lost') || statusLower.includes('cancelled')) {
    return 'bg-red-100 text-red-800'
  }
  
  return 'bg-gray-100 text-gray-800'
}

function formatFieldName(fieldname) {
  if (!fieldname) return ''
  
  // Convert snake_case to Title Case
  return fieldname
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

// Keyboard shortcut listener
function handleGlobalKeyDown(event) {
  // Cmd+K or Ctrl+K to toggle search
  if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
    event.preventDefault()
    toggleSearch()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeyDown)
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
})

// Watch for dialog close
watch(isOpen, (newValue) => {
  if (!newValue) {
    // Clean up when dialog closes
    searchQuery.value = ''
    results.value = []
    selectedIndex.value = 0
    totalSearchTime.value = 0
  } else {
    // Focus input when dialog opens
    nextTick(() => {
      searchInput.value?.focus()
    })
  }
})
</script>

<style scoped>
.universal-search-modal {
  @apply py-2;
}

.search-input-wrapper input:focus {
  outline: none;
  box-shadow: none;
}

.search-results-wrapper::-webkit-scrollbar {
  width: 6px;
}

.search-results-wrapper::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.search-results-wrapper::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.search-results-wrapper::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
