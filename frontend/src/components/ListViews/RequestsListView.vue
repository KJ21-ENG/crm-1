<template>
  <ListView
    :columns="columns"
    :rows="rows"
    :options="{
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

    <ListRows
      class="mx-3 sm:mx-5"
      :rows="rows"
      v-slot="{ idx, column, item, row }"
      doctype="CRM Assignment Request"
    >
      <div v-if="column.key === '_actions'" class="flex items-center justify-end gap-2">
        <Button
          v-if="isAdmin() && row.status === 'Pending'"
          size="sm"
          variant="solid"
          @click.stop.prevent="approve(row)"
        >
          {{ __('Accept') }}
        </Button>
        <Button
          v-if="isAdmin() && row.status === 'Pending'"
          size="sm"
          variant="subtle"
          theme="red"
          @click.stop.prevent="reject(row)"
        >
          {{ __('Reject') }}
        </Button>
      </div>
      <div
        v-if="column.key === 'reason'"
        class="truncate text-base"
        @click="(event) => emit('applyFilter', { event, idx, column, item, firstColumn: columns[0] })"
      >
        <Tooltip :text="item">
          <div>{{ item }}</div>
        </Tooltip>
      </div>
      <ListRowItem v-else :item="item" :align="column.align">
        <template #default="{ label }">
          <div
            v-if="['modified','creation','approved_on'].includes(column.key)"
            class="truncate text-base"
            @click="(event) => emit('applyFilter', { event, idx, column, item, firstColumn: columns[0] })"
          >
            <Tooltip :text="item && item.label ? item.label : ''">
              <div>{{ item && item.timeAgo ? item.timeAgo : '' }}</div>
            </Tooltip>
          </div>
          <div v-else-if="column.key === 'reference_name'" class="flex items-center gap-2 min-w-0">
            <RouterLink :to="getDocRoute(row)" class="min-w-0 flex-1">
              <span class="block truncate whitespace-nowrap text-primary-600 hover:underline">{{ label }}</span>
            </RouterLink>
            <Popover trigger="hover" placement="top" class="flex-shrink-0">
              <template #target>
                <span class="inline-flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 text-ink-gray-6 cursor-help hover:text-ink-gray-8">
                    <path fill-rule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25Zm.75 6a.75.75 0 1 0-1.5 0v.008a.75.75 0 0 0 1.5 0V8.25ZM12 10.5a.75.75 0 0 0-.75.75v5.25a.75.75 0 0 0 1.5 0v-5.25a.75.75 0 0 0-.75-.75Z" clip-rule="evenodd" />
                  </svg>
                </span>
              </template>
              <template #body-main>
                <div class="p-3 text-sm leading-6 max-w-sm whitespace-pre-line">
                  {{ getInfoTooltip(row) }}
                </div>
              </template>
            </Popover>
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
  ListView,
  ListHeader,
  ListHeaderItem,
  ListSelectBanner,
  ListRowItem,
  Tooltip,
  FormControl,
  Popover,
} from 'frappe-ui'
import { computed, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { usersStore } from '@/stores/users'
import { call, toast, Button } from 'frappe-ui'
import { globalStore } from '@/stores/global'

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
  'pageSizeChange',
])

const route = useRoute()
const { isAdmin } = usersStore()
const { $dialog } = globalStore()

const pageLengthCount = defineModel()
const list = defineModel('list')

watch(pageLengthCount, (val, oldVal) => {
  if (val === oldVal) return
  emit('updatePageCount', val)
})

const currentPage = computed(() => {
  if (!list.value?.data?.page_length) return 1
  const start = list.value.data.start || 0
  const pageLength = list.value.data.page_length
  const calculatedPage = Math.floor(start / pageLength) + 1
  return calculatedPage
})

const totalPages = computed(() => {
  if (!list.value?.data?.total_count || !list.value?.data?.page_length) return 1
  return Math.ceil(list.value.data.total_count / list.value.data.page_length)
})

function handlePageChange(page) {
  emit('pageChange', page)
}

function handlePageSizeChange(pageSize) {
  emit('pageSizeChange', pageSize)
}

function getDocRoute(row) {
  const doctype = row?.reference_doctype?.value || row?.reference_doctype || ''
  const name = row?.reference_name?.value || row?.reference_name?.label || row?.reference_name || ''
  if (doctype === 'CRM Lead') {
    return { name: 'Lead', params: { leadId: name } }
  }
  if (doctype === 'CRM Ticket') {
    return { name: 'Ticket', params: { ticketId: name } }
  }
  return { name: route.name }
}

function formatInfo(summary) {
  if (!summary) return ''
  const lines = []
  if (summary.customer_name) lines.push(`${__('Customer')}: ${summary.customer_name}`)
  if (summary.mobile_no) lines.push(`${__('Contact')}: ${summary.mobile_no}`)
  if (summary.extra_label && summary.extra_value) lines.push(`${summary.extra_label}: ${summary.extra_value}`)
  return lines.join('\n')
}

function getInfoTooltip(row) {
  const cacheKey = `${row.reference_doctype}|${row.reference_name?.label || row.reference_name}`
  const existing = infoCache[cacheKey]
  if (existing) return existing
  // Return placeholder while we fetch; Tooltip will update when cache fills
  fetchInfo(row)
  return __('Loading...')
}

const infoCache = {}

async function fetchInfo(row) {
  try {
    const doctype = row?.reference_doctype?.value || row?.reference_doctype || ''
    const name = row?.reference_name?.value || row?.reference_name?.label || row?.reference_name || ''
    if (!doctype || !name) return
    const res = await call('crm.api.assignment_requests.get_reference_summary', {
      reference_doctype: doctype,
      reference_name: name,
    })
    const text = formatInfo(res)
    infoCache[`${doctype}|${name}`] = text
  } catch (e) {
    console.log(e);
  }
}

async function approve(row) {
  try {
    await call('crm.api.assignment_requests.approve_assignment_request', { name: row.name })
    toast.success(__('Request approved'))
    list.value?.reload?.()
  } catch (e) {
    toast.error(e?.message || __('Failed to approve'))
  }
}

async function reject(row) {
  $dialog({
    title: __('Reject Request'),
    html: `
      <div class="space-y-2">
        <p class="text-p-base text-ink-gray-7">${__('Are you sure you want to reject this request?')}</p>
        <label class="block text-sm text-ink-gray-6 mb-1">${__('Rejection Reason (optional)')}</label>
        <textarea id="reject-reason" class="form-control w-full" rows="3" placeholder="${__('Enter reason')}"></textarea>
      </div>
    `,
    actions: [
      {
        label: __('Reject'),
        variant: 'solid',
        theme: 'red',
        onClick: async (close) => {
          try {
            const reason = document.getElementById('reject-reason')?.value || ''
            await call('crm.api.assignment_requests.reject_assignment_request', {
              name: row.name,
              reason,
            })
            toast.success(__('Request rejected'))
            list.value?.reload?.()
            close()
          } catch (e) {
            toast.error(e?.message || __('Failed to reject'))
          }
        },
      },
    ],
  })
}
</script>


