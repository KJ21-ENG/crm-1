<template>
  <ListView
    :columns="columns"
    :rows="rows"
    :options="{
      getRowRoute: (row) => ({
        name: 'Customer',
        params: { customerId: row.name },
        query: { view: route.query.view, viewType: route.params.viewType },
      }),
      selectable: options.selectable,
      showTooltip: options.showTooltip,
      resizeColumn: options.resizeColumn,
    }"
    row-key="name"
    @update:selections="(selections) => emit('selectionsChanged', selections)"
  >
    <ListHeader class="mx-3 sm:mx-5" @columnWidthUpdated="emit('columnWidthUpdated')">
      <ListHeaderItem
        v-for="column in columns"
        :key="column.key"
        :item="column"
        @columnWidthUpdated="emit('columnWidthUpdated', column)"
      />
    </ListHeader>

    <ListRows class="mx-3 sm:mx-5" :rows="rows" v-slot="{ idx, column, item }" doctype="CRM Customer">
      <ListRowItem :item="item" :align="column.align">
        <template #prefix>
          <div v-if="['customer_name','full_name'].includes(column.key)">
            <Avatar v-if="item.label" class="flex items-center" :image="item.image" :label="item.image_label" size="sm" />
          </div>
        </template>
        <template #default="{ label }">
          <div
            v-if="['modified', 'creation'].includes(column.key)"
            class="truncate text-base"
            @click="(event) => emit('applyFilter', { event, idx, column, item, firstColumn: columns[0] })"
          >
            <Tooltip :text="item.label">
              <div>{{ item.timeAgo || item.label }}</div>
            </Tooltip>
          </div>
          <div v-else-if="column.type === 'Check'">
            <FormControl type="checkbox" :modelValue="item" :disabled="true" class="text-ink-gray-9" />
          </div>
          <div
            v-else
            class="truncate text-base"
            @click="(event) => emit('applyFilter', { event, idx, column, item, firstColumn: columns[0] })"
          >
            {{ label }}
          </div>
        </template>
      </ListRowItem>
    </ListRows>

    <ListSelectBanner />
  </ListView>
  <Pagination
    v-if="pageLengthCount && options.totalCount > 0"
    class="border-t px-3 py-2 sm:px-5"
    :current-page="currentPage"
    :page-size="pageLengthCount"
    :total-count="options.totalCount"
    @page-change="handlePageChange"
    @page-size-change="handlePageSizeChange"
  />
</template>

<script setup>
import ListRows from '@/components/ListViews/ListRows.vue'
import Pagination from '@/components/Pagination.vue'
import {
  Avatar,
  ListView,
  ListHeader,
  ListHeaderItem,
  ListSelectBanner,
  ListRowItem,
  Tooltip,
  FormControl,
} from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  rows: { type: Array, required: true },
  columns: { type: Array, required: true },
  options: {
    type: Object,
    default: () => ({ selectable: true, showTooltip: true, resizeColumn: false, totalCount: 0, rowCount: 0 }),
  },
})

const emit = defineEmits([
  'loadMore', 
  'updatePageCount', 
  'columnWidthUpdated', 
  'applyFilter', 
  'selectionsChanged',
  'pageChange',
  'pageSizeChange'
])
const route = useRoute()

const pageLengthCount = defineModel()
const list = defineModel('list')

watch(pageLengthCount, (val, oldVal) => {
  if (val === oldVal) return
  emit('updatePageCount', val)
})

// Add pagination computed properties
const currentPage = computed(() => {
  // Use the current page from the list data if available, otherwise fallback to 1
  if (!list.value?.data?.page_length) return 1
  const start = list.value.data.start || 0
  const pageLength = list.value.data.page_length
  const calculatedPage = Math.floor(start / pageLength) + 1
  
  console.log('🔍 CustomersListView Debug - Current page calculation:', {
    start,
    pageLength,
    calculatedPage,
    listData: list.value?.data
  })
  
  return calculatedPage
})

const totalPages = computed(() => {
  if (!list.value?.data?.total_count || !list.value?.data?.page_length) return 1
  return Math.ceil(list.value.data.total_count / list.value.data.page_length)
})

// Add pagination methods
function handlePageChange(page) {
  emit('pageChange', page)
}

function handlePageSizeChange(pageSize) {
  emit('pageSizeChange', pageSize)
}
</script>


