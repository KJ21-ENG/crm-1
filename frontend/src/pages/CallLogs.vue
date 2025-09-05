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
import { createResource } from 'frappe-ui'
import { computed, ref, onMounted, watch } from 'vue'
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

// Enhanced filtering with manual data filtering as fallback
const filteredRows = computed(() => {
  const data = callLogs.value?.data?.data
  if (!data || !session.user) return []
  // Rely on backend filtering; just format current page
  return data.map((callLog) => {
    const _rows = {}
    callLogs.value?.data.rows.forEach((row) => {
      _rows[row] = getCallLogDetail(row, callLog, callLogs.value?.data.columns)
    })
    return _rows
  })
})

const showCallLogDetailModal = ref(false)
const callLog = ref({})

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
