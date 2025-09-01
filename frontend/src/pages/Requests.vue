<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Requests" />
      </template>
    </LayoutHeader>

    <ViewControls
      ref="viewControls"
      v-model="requests"
      v-model:loadMore="loadMore"
      v-model:resizeColumn="triggerResize"
      v-model:updatedPageCount="updatedPageCount"
      doctype="CRM Assignment Request"
      :options="{ allowedViews: ['list'] }"
    />

    <RequestsListView
      v-if="requests.data && rows.length"
      v-model="requests.data.page_length_count"
      v-model:list="requests"
      :rows="rows"
      :columns="enhancedColumns"
      :options="{
        showTooltip: false,
        resizeColumn: true,
        rowCount: requests.data.row_count,
        totalCount: requests.data.total_count,
      }"
      @loadMore="() => loadMore++"
      @columnWidthUpdated="() => triggerResize++"
      @updatePageCount="(count) => (updatedPageCount = count)"
      @pageChange="(page) => viewControls.goToPage(page)"
      @pageSizeChange="(pageSize) => viewControls.handlePageSizeChange(pageSize)"
      @applyFilter="(data) => viewControls.applyFilter(data)"
      @selectionsChanged="(selections) => viewControls.updateSelections(selections)"
    />
    <div v-else-if="requests.data" class="flex h-full items-center justify-center">
      <div class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4">
        <span>{{ __('No {0} Found', [__('Requests')]) }}</span>
      </div>
    </div>
  </div>
  
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewControls from '@/components/ViewControls.vue'
import RequestsListView from '@/components/ListViews/RequestsListView.vue'
import { usersStore } from '@/stores/users'
import { ref, computed } from 'vue'
import { formatDate, timeAgo } from '@/utils'
import { useRouter } from 'vue-router'

const { isAdmin, getUser } = usersStore()

if (!isAdmin()) {
  const r = useRouter()
  r.replace({ name: 'Dashboard' })
}

const requests = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)


const rows = computed(() => {
  if (!requests.value?.data?.data || !['list', 'group_by'].includes(requests.value.data.view_type)) return []
  return requests.value?.data.data.map((c) => {
    let _rows = {}
    requests.value?.data.rows.forEach((row) => {
      _rows[row] = c[row]
      const col = requests.value?.data.columns?.find((col) => (col.key || col.value) == row)
      const fieldType = col?.type
      if (fieldType && ['Date','Datetime'].includes(fieldType) && !['modified','creation'].includes(row)) {
        _rows[row] = new Date(c[row]).toLocaleString()
      }
      if (['modified','creation','approved_on'].includes(row)) {
        const label = formatDate(c[row])
        _rows[row] = { label, timeAgo: timeAgo(c[row]) }
      }
      if (['requested_user','requested_by'].includes(row)) {
        const user = getUser(c[row]) || {}
        const label = user.full_name || user.first_name || c[row]
        _rows[row] = { label, value: c[row] }
      }
    })
    _rows['name'] = c.name
    return _rows
  })
})

const enhancedColumns = computed(() => {
  const base = requests.value?.data?.columns || []
  // Append an Actions column for Accept/Reject controls (frontend-only)
  return [
    ...base,
  ]
})
</script>
