<template>
  <ListView
    :columns="columns"
    :rows="rows"
    :options="{
      onRowClick: (row) => emit('showCallLog', row.name),
      selectable: options.selectable,
      showTooltip: options.showTooltip,
      resizeColumn: options.resizeColumn,
    }"
    row-key="name"
    v-bind="$attrs"
    @update:selections="(selections) => emit('selectionsChanged', selections)"
  >
    <ListHeader
      class="sm:mx-5 mx-3"
      @columnWidthUpdated="emit('columnWidthUpdated')"
    >
      <ListHeaderItem
        v-for="column in columns"
        :key="column.key"
        :item="column"
        @columnWidthUpdated="emit('columnWidthUpdated', column)"
      >
        <Button
          v-if="column.key == '_liked_by'"
          variant="ghosted"
          class="!h-4"
          :class="isLikeFilterApplied ? 'fill-red-500' : 'fill-white'"
          @click="() => emit('applyLikeFilter')"
        >
          <HeartIcon class="h-4 w-4" />
        </Button>
      </ListHeaderItem>
    </ListHeader>
    <ListRows
      class="mx-3 sm:mx-5"
      :rows="rows"
      v-slot="{ idx, column, item, row }"
      doctype="CRM Call Log"
    >
      <ListRowItem :item="item" :align="column.align">
        <template #prefix>
          <div v-if="['caller', 'receiver', 'employee'].includes(column.key)">
            <Avatar
              v-if="item.label"
              class="flex items-center"
              :image="item.image"
              :label="item.label"
              size="sm"
            />
          </div>
          <div v-else-if="['type', 'duration'].includes(column.key)">
            <FeatherIcon :name="item.icon" class="h-3 w-3" />
          </div>
        </template>
        <template #default="{ label }">
          <div
            v-if="['modified', 'creation', 'start_time'].includes(column.key)"
            class="truncate text-base"
            @click="
              (event) =>
                emit('applyFilter', {
                  event,
                  idx,
                  column,
                  item,
                  firstColumn: columns[0],
                })
            "
          >
            <Tooltip :text="item.label">
              <div>{{ item.timeAgo }}</div>
            </Tooltip>
          </div>
          <div v-else-if="column.key === 'status'" class="truncate text-base">
            <div class="inline-flex items-center gap-1">
              <Badge
                :variant="'subtle'"
                :theme="item.color"
                size="md"
                :label="__(item.label)"
                @click="
                  (event) =>
                    emit('applyFilter', {
                      event,
                      idx,
                      column,
                      item,
                      firstColumn: columns[0],
                    })
                "
              />
              <Tooltip :text="__('Original status: {0}', [item.raw || item.name || __('Unknown')])">
                <FeatherIcon name="info" class="h-3.5 w-3.5 text-ink-gray-5" />
              </Tooltip>
            </div>
          </div>
          <div v-else-if="column.type === 'Check'">
            <FormControl
              type="checkbox"
              :modelValue="item"
              :disabled="true"
              class="text-ink-gray-9"
            />
          </div>
          <div v-else-if="column.key === '_liked_by'">
            <Button
              v-if="column.key == '_liked_by'"
              variant="ghosted"
              :class="isLiked(item) ? 'fill-red-500' : 'fill-white'"
              @click.stop.prevent="
                () => emit('likeDoc', { name: row.name, liked: isLiked(item) })
              "
            >
              <HeartIcon class="h-4 w-4" />
            </Button>
          </div>
          <div
            v-else
            class="flex items-center gap-2 truncate text-base"
            @click="
              (event) =>
                emit('applyFilter', {
                  event,
                  idx,
                  column,
                  item,
                  firstColumn: columns[0],
                })
            "
          >
            <span class="flex-1 truncate">{{ label }}</span>
            <Tooltip
              v-if="idx === 0"
              :text="row?.__isColdCall ? __('Unmark cold call') : __('Mark as cold call')"
            >
              <Button
                variant="ghost"
                size="sm"
                class="!p-1"
                @click.stop="toggleColdCall(row)"
              >
                <FeatherIcon
                  name="flag"
                  class="h-4 w-4 transition-colors"
                  :class="row?.__isColdCall ? 'text-blue-600' : 'text-ink-gray-4'"
                />
              </Button>
            </Tooltip>
          </div>
        </template>
      </ListRowItem>
    </ListRows>
    <ListSelectBanner>
      <template #actions="{ selections, unselectAll }">
        <Dropdown
          :options="listBulkActionsRef.bulkActions(selections, unselectAll)"
        >
          <Button icon="more-horizontal" variant="ghost" />
        </Dropdown>
      </template>
    </ListSelectBanner>
  </ListView>
  <Pagination
    v-if="pageLengthCount && options.totalCount > 0"
    class="border-t sm:px-5 px-3 py-2"
    :current-page="currentPage"
    :page-size="pageLengthCount"
    :total-count="options.totalCount"
    @page-change="handlePageChange"
    @page-size-change="handlePageSizeChange"
  />
  <ListBulkActions
    ref="listBulkActionsRef"
    v-model="list"
    doctype="CRM Call Log"
    :options="{
      hideEdit: true,
      hideAssign: true,
    }"
  />
</template>
<script setup>
import HeartIcon from '@/components/Icons/HeartIcon.vue'
import ListBulkActions from '@/components/ListBulkActions.vue'
import ListRows from '@/components/ListViews/ListRows.vue'
import Pagination from '@/components/Pagination.vue'
import {
  Avatar,
  Button,
  FeatherIcon,
  ListView,
  ListHeader,
  ListHeaderItem,
  ListSelectBanner,
  ListRowItem,
  Tooltip,
  Dropdown,
} from 'frappe-ui'
import { sessionStore } from '@/stores/session'
import { ref, computed, watch } from 'vue'

const props = defineProps({
  rows: {
    type: Array,
    required: true,
  },
  columns: {
    type: Array,
    required: true,
  },
  options: {
    type: Object,
    default: () => ({
      selectable: true,
      showTooltip: true,
      resizeColumn: false,
      totalCount: 0,
      rowCount: 0,
    }),
  },
})

const emit = defineEmits([
  'showCallLog',
  'loadMore',
  'updatePageCount',
  'columnWidthUpdated',
  'applyFilter',
  'applyLikeFilter',
  'likeDoc',
  'toggleColdCall',
  'selectionsChanged',
  'pageChange',
  'pageSizeChange',
])

const pageLengthCount = defineModel()
const list = defineModel('list')

const isLikeFilterApplied = computed(() => {
  return list.value.params?.filters?._liked_by ? true : false
})

const { user } = sessionStore()

function isLiked(item) {
  if (item) {
    let likedByMe = JSON.parse(item)
    return likedByMe.includes(user)
  }
}

function toggleColdCall(row) {
  if (!row) return
  const name = row.__doc?.name || row.name
  if (!name) return
  emit('toggleColdCall', { name, nextValue: !row.__isColdCall })
}

watch(pageLengthCount, (val, old_value) => {
  if (val === old_value) return
  emit('updatePageCount', val)
})

const listBulkActionsRef = ref(null)

defineExpose({
  customListActions: computed(
    () => listBulkActionsRef.value?.customListActions,
  ),
})

// Add pagination computed properties
const currentPage = computed(() => {
  // Use the current page from the list data if available, otherwise fallback to 1
  if (!list.value?.data?.page_length) return 1
  const start = list.value.data.start || 0
  const pageLength = list.value.data.page_length
  const calculatedPage = Math.floor(start / pageLength) + 1
  
  console.log('🔍 CallLogsListView Debug - Current page calculation:', {
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

<style scoped>
</style>
