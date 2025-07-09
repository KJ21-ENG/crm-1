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
      <Button variant="solid" :label="__('Create')" @click="createCallLog">
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

// Create a more robust user filter that waits for session
const userOwnerFilter = computed(() => {
  // Only apply filter if user is logged in and session is available
  if (!session.isLoggedIn || !session.user) {
    console.log('🔍 Call Logs Debug - No user session, returning empty filters')
    return {}
  }
  
  // If user is Administrator, don't apply owner filter
  if (session.user === 'Administrator') {
    console.log('🔍 Call Logs Debug - Administrator user, showing all logs')
    return {}
  }
  
  const filters = { owner: session.user }
  console.log('🔍 Call Logs Debug - Regular user, applying owner filter:', filters)
  return filters
})

// Watch for session changes
watch(() => session.user, (newUser, oldUser) => {
  console.log('🔍 Session User Changed:', { oldUser, newUser })
  if (newUser && viewControls.value) {
    console.log('🔍 Reloading call logs due to user change')
    setTimeout(() => {
      viewControls.value.reload?.()
    }, 100) // Small delay to ensure session is fully updated
  }
}, { immediate: true })

// Watch for login state changes
watch(() => session.isLoggedIn, (isLoggedIn) => {
  console.log('🔍 Login state changed:', isLoggedIn)
  if (isLoggedIn && viewControls.value) {
    console.log('🔍 User logged in, reloading call logs')
    setTimeout(() => {
      viewControls.value.reload?.()
    }, 200)
  }
}, { immediate: true })

// Enhanced filtering with manual data filtering as fallback
const filteredRows = computed(() => {
  if (!callLogs.value?.data?.data || !session.user) {
    return []
  }
  
  // Skip filtering for Administrator
  if (session.user === 'Administrator') {
    console.log('🔍 Administrator: Showing all logs without filtering')
    return callLogs.value.data.data.map((callLog) => {
      let _rows = {}
      callLogs.value?.data.rows.forEach((row) => {
        _rows[row] = getCallLogDetail(row, callLog, callLogs.value?.data.columns)
      })
      return _rows
    })
  }
  
  // Manual client-side filtering as backup for regular users
  const userCallLogs = callLogs.value.data.data.filter(log => {
    const isUserLog = log.owner === session.user || log._owner === session.user
    if (!isUserLog) {
      console.log('🔍 Filtering out log owned by:', log.owner || log._owner, 'Current user:', session.user)
    }
    return isUserLog
  })
  
  console.log('🔍 Total logs:', callLogs.value.data.data.length, 'User logs:', userCallLogs.length)
  
  return userCallLogs.map((callLog) => {
    let _rows = {}
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
  
  // Debug session state on mount
  console.log('🔍 CallLogs mounted - Session state:', {
    user: session.user,
    isLoggedIn: session.isLoggedIn,
    userFilter: userOwnerFilter.value
  })
  
  // Ensure we reload data after component is mounted with proper session
  if (session.isLoggedIn && session.user) {
    console.log('🔍 Session ready on mount, triggering reload')
    setTimeout(() => {
      if (viewControls.value?.reload) {
        viewControls.value.reload()
      }
    }, 500) // Longer delay to ensure everything is initialized
  }
})
</script>
