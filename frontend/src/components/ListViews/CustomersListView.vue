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
              <div>{{ item.timeAgo }}</div>
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
  <ListFooter
    class="border-t px-3 py-2 sm:px-5"
    v-model="pageLengthCount"
    :options="{ rowCount: options.rowCount, totalCount: options.totalCount }"
    @loadMore="emit('loadMore')"
  />
</template>

<script setup>
import ListRows from '@/components/ListViews/ListRows.vue'
import {
  Avatar,
  ListView,
  ListHeader,
  ListHeaderItem,
  ListSelectBanner,
  ListRowItem,
  ListFooter,
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

const emit = defineEmits(['loadMore', 'updatePageCount', 'columnWidthUpdated', 'applyFilter', 'selectionsChanged'])
const route = useRoute()

const pageLengthCount = defineModel()
const list = defineModel('list')

watch(pageLengthCount, (val, oldVal) => {
  if (val === oldVal) return
  emit('updatePageCount', val)
})
</script>


