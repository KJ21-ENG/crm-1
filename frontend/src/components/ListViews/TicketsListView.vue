<!-- TicketsListView.vue -->
<template>
  <div class="flex flex-1 flex-col">
    <ListView
      v-bind="$attrs"
      :rows="rows"
      :columns="columns"
      :options="{
        showTooltip: false,
        resizeColumn: true,
        rowCount: rowCount,
        totalCount: totalCount,
      }"
      @loadMore="$emit('loadMore')"
      @columnWidthUpdated="$emit('columnWidthUpdated')"
      @view="$emit('view', $event)"
    >
      <template #cell-status="{ row }">
        <StatusBadge :status="row.status" />
      </template>

      <template #cell-priority="{ row }">
        <PriorityBadge :priority="row.priority" />
      </template>

      <template #cell-creation="{ row }">
        {{ formatDate(row.creation) }}
      </template>

      <template #cell-assigned_to="{ row }">
        <div v-if="row.assigned_to" class="flex items-center gap-2">
          <Avatar
            :image="getUser(row.assigned_to)?.user_image"
            :label="getUser(row.assigned_to)?.full_name"
            size="sm"
          />
          <span>{{ getUser(row.assigned_to)?.full_name }}</span>
        </div>
      </template>
    </ListView>
  </div>
</template>

<script setup>
import { ListView, Avatar } from 'frappe-ui'
import { usersStore } from '@/stores/users'
import { formatDate } from '@/utils'
import StatusBadge from '@/components/Badges/StatusBadge.vue'
import PriorityBadge from '@/components/Badges/PriorityBadge.vue'

const { getUser } = usersStore()

defineProps({
  rows: {
    type: Array,
    default: () => [],
  },
  columns: {
    type: Array,
    default: () => [],
  },
  rowCount: {
    type: Number,
    default: 0,
  },
  totalCount: {
    type: Number,
    default: 0,
  },
})

defineEmits(['loadMore', 'columnWidthUpdated', 'view'])
</script> 