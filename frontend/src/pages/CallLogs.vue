<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Call Logs" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="callLogsListView?.customListActions"
        :actions="callLogsListView.customListActions"
      />
      <Button v-if="canWriteCallLogs" variant="solid" :label="__('Create')" @click="createCallLog">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="callLogs"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="CRM Call Log"
    :filters="userOwnerFilter"
  />
  <CallLogsListView
    ref="callLogsListView"
    v-if="callLogs.data && filteredRows.length"
    v-model="callLogs.data.page_length_count"
    v-model:list="callLogs"
    :rows="filteredRows"
    :columns="callLogs.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: callLogs.data.row_count,
      totalCount: callLogs.data.total_count,
    }"
    @showCallLog="showCallLog"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @pageChange="(page) => viewControls.goToPage(page)"
    @pageSizeChange="(pageSize) => viewControls.handlePageSizeChange(pageSize)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
    @toggleColdCall="handleToggleColdCall"
    @selectionsChanged="
      (selections) => viewControls.updateSelections(selections)
    "
  />
  <div
    v-else-if="callLogs.data"
    class="flex h-full items-center justify-center"
  >
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4"
    >
      <PhoneIcon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Logs')]) }}</span>
    </div>
  </div>
  <CallLogDetailModal
    v-model="showCallLogDetailModal"
    v-model:callLogModal="showCallLogModal"
    v-model:callLog="callLog"
  />
  <CallLogModal
    v-if="showCallLogModal"
    v-model="showCallLogModal"
    :data="callLog.data"
    :options="{ afterInsert: () => callLogs.reload() }"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewControls from '@/components/ViewControls.vue'
import CallLogsListView from '@/components/ListViews/CallLogsListView.vue'
import CallLogDetailModal from '@/components/Modals/CallLogDetailModal.vue'
import CallLogModal from '@/components/Modals/CallLogModal.vue'
import { getCallLogDetail } from '@/utils/callLog'
import { call, createResource, toast } from 'frappe-ui'
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { sessionStore } from '@/stores/session'
import { permissionsStore } from '@/stores/permissions'

const callLogsListView = ref(null)
const showCallLogModal = ref(false)

// Get session store instance
const session = sessionStore()

// callLogs data is loaded in the ViewControls component
const callLogs = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Permissions
const { canWrite } = permissionsStore()
const canWriteCallLogs = computed(() => canWrite('Call Logs'))

const route = useRoute()
const router = useRouter()

// Create a more robust user filter that waits for session
const userOwnerFilter = computed(() => {
  if (!session.isLoggedIn || !session.user) return {}
  if (session.user === 'Administrator') return {}
  return { owner: session.user }
})

// Watch for session changes
watch(() => session.user, (newUser) => {
  if (newUser && viewControls.value) {
    setTimeout(() => {
      viewControls.value.reload?.()
    }, 100)
  }
}, { immediate: true })

// Ensure employee column uses display name for header filters/search (map backend employee_display)
watch(
  () => callLogs.value?.data,
  (data) => {
    if (!data || !data.data) return
    try {
      data.data = data.data.map((row) => {
        // If backend provided employee_display, use it for the employee column so header filters/search show names
        if (row && row.employee_display) {
          return { ...row, employee: row.employee_display }
        }
        return row
      })
    } catch (e) {
      // swallow
    }
  },
  { immediate: true },
)

// Watch for login state changes
watch(() => session.isLoggedIn, (isLoggedIn) => {
  if (isLoggedIn && viewControls.value) {
    setTimeout(() => {
      viewControls.value.reload?.()
    }, 200)
  }
}, { immediate: true })

const applyCallLogFiltersFromRoute = () => {
  const payload = route.query.calllogFilters
  if (!payload || !viewControls.value?.updateFilter) return

  try {
    const raw = Array.isArray(payload) ? payload[0] : payload
    const parsed = raw ? JSON.parse(raw) : null
    if (!parsed || typeof parsed !== 'object') return

    const baseFilters = { ...(userOwnerFilter.value || {}) }
    const normalized = { ...baseFilters }

    Object.entries(parsed).forEach(([field, value]) => {
      if (field === 'owner') {
        if (value === '__all__') {
          delete normalized.owner
        } else if (value === '__current__') {
          if (session.user) normalized.owner = session.user
          else delete normalized.owner
        } else if (value) {
          normalized.owner = value
        } else {
          delete normalized.owner
        }
      } else if (value === null || value === undefined || value === '__unset__') {
        delete normalized[field]
      } else {
        normalized[field] = value
      }
    })

    viewControls.value.updateFilter(normalized)
  } catch (error) {
    console.error('Failed to apply call log filters from route', error)
  } finally {
    if (route.query.calllogFilters !== undefined) {
      const newQuery = { ...route.query }
      delete newQuery.calllogFilters
      router.replace({ query: newQuery })
    }
  }
}

watch(
  () => [route.query.calllogFilters, viewControls.value],
  ([filtersParam, vc]) => {
    if (filtersParam && vc) {
      // Delay to ensure ViewControls settled before applying filters
      setTimeout(() => applyCallLogFiltersFromRoute())
    }
  },
  { immediate: true },
)

// Enhanced filtering with manual data filtering as fallback
const filteredRows = computed(() => {
  const data = callLogs.value?.data?.data
  if (!data || !session.user) return []
  const rowKeys = callLogs.value?.data?.rows || []
  const columns = callLogs.value?.data?.columns || []

  // Rely on backend filtering; just format current page
  return data.map((callLog) => {
    const _rows = {}
    rowKeys.forEach((row) => {
      _rows[row] = getCallLogDetail(row, callLog, columns)
    })
    _rows.__doc = callLog
    _rows.__isColdCall = Boolean(callLog.is_cold_call)
    return _rows
  })
})

const showCallLogDetailModal = ref(false)
const callLog = ref({})
const togglingColdCalls = new Set()

function showCallLog(name) {
  showCallLogDetailModal.value = true
  callLog.value = createResource({
    url: 'crm.fcrm.doctype.crm_call_log.crm_call_log.get_call_log',
    params: { name },
    cache: ['call_log', name],
    auto: true,
  })
}

function createCallLog() {
  callLog.value = {}
  showCallLogModal.value = true
}

function handleToggleColdCall({ name, nextValue }) {
  if (!name || togglingColdCalls.has(name)) return

  togglingColdCalls.add(name)

  call('crm.api.call_log.set_cold_call', {
    call_log: name,
    cold_call: nextValue ? 1 : 0,
  })
    .then(() => {
      const message = nextValue ? __('Marked as cold call') : __('Cold call removed')
      const toastFn = nextValue ? toast.success : toast.info
      toastFn(message)

      const rawList = callLogs.value?.data?.data
      if (Array.isArray(rawList)) {
        const idx = rawList.findIndex((entry) => entry.name === name)
        if (idx !== -1) {
          const updated = {
            ...rawList[idx],
            is_cold_call: nextValue ? 1 : 0,
          }
          rawList.splice(idx, 1, updated)
          // Trigger computed consumers
          callLogs.value.data.data = [...rawList]
        }
      }

      viewControls.value?.reload?.()
    })
    .catch((error) => {
      const message = error?.messages?.[0] || error?.message || __('Failed to update cold call flag')
      toast.error(message)
    })
    .finally(() => {
      togglingColdCalls.delete(name)
    })
}

const openCallLogFromURL = () => {
  const searchParams = new URLSearchParams(window.location.search)
  const callLogName = searchParams.get('open')

  if (callLogName) {
    showCallLog(callLogName)
    searchParams.delete('open')
    window.history.replaceState(null, '', window.location.pathname)
  }
}

onMounted(() => {
  openCallLogFromURL()
  
  // Ensure we reload data after component is mounted with proper session
  if (session.isLoggedIn && session.user) {
    setTimeout(() => {
      if (viewControls.value?.reload) {
        // Force a sane default page length on first load to avoid huge data pulls
        try {
          if (typeof viewControls.value.updatePageLength === 'function') {
            viewControls.value.updatePageLength(20)
          }
        } catch (e) {}
        viewControls.value.reload()
      }
    }, 500) // Longer delay to ensure everything is initialized
  }
})
</script>
