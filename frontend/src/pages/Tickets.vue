<!-- Tickets.vue -->
<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Tickets" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="ticketsListView?.customListActions"
        :actions="ticketsListView.customListActions"
      />
        <Button
          variant="solid"
        :label="__('Create')"
          @click="showTicketModal = true"
        >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
      </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="tickets"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="CRM Ticket"
    :filters="{}"
    :options="{
      allowedViews: ['list', 'group_by', 'kanban'],
    }"
  />
  <KanbanView
    v-if="route.params.viewType == 'kanban'"
    v-model="tickets"
    :options="{
      getRoute: (row) => ({
        name: 'Ticket',
        params: { ticketId: row.name },
        query: { view: route.query.view, viewType: route.params.viewType },
      }),
      onNewClick: (column) => onNewClick(column),
    }"
    @update="(data) => viewControls.updateKanbanSettings(data)"
    @loadMore="(columnName) => viewControls.loadMoreKanban(columnName)"
  >
    <template #title="{ titleField, itemName }">
      <div class="flex items-center gap-2">
        <div v-if="titleField === 'status'">
          <IndicatorIcon :class="getRow(itemName, titleField).color" />
        </div>
        <div
          v-else-if="
            titleField === 'assigned_to' && getRow(itemName, titleField).full_name
          "
        >
          <Avatar
            class="flex items-center"
            :image="getRow(itemName, titleField).user_image"
            :label="getRow(itemName, titleField).full_name"
            size="sm"
          />
        </div>
        <div v-else-if="titleField === 'customer_name'">
          <Avatar
            v-if="getRow(itemName, titleField).label"
            class="flex items-center"
            :image="getRow(itemName, titleField).image"
            :label="getRow(itemName, titleField).image_label"
            size="sm"
          />
        </div>
        <div v-else-if="titleField === 'mobile_no'">
          <PhoneIcon class="h-4 w-4" />
        </div>
        <div
          v-if="
            [
              'modified',
              'creation',
              'first_response_time',
              'first_responded_on',
              'response_by',
              'resolved_on',
            ].includes(titleField)
          "
          class="truncate text-base"
        >
          <Tooltip :text="getRow(itemName, titleField).label">
            <div>{{ getRow(itemName, titleField).timeAgo }}</div>
          </Tooltip>
        </div>
        <div v-else-if="titleField === 'sla_status'" class="truncate text-base">
          <Badge
            v-if="getRow(itemName, titleField).value"
            :variant="'subtle'"
            :theme="getRow(itemName, titleField).color"
            size="md"
            :label="getRow(itemName, titleField).value"
          />
        </div>
        <div v-else-if="titleField === 'priority'" class="truncate text-base">
          <Badge
            v-if="getRow(itemName, titleField).value"
            :variant="'subtle'"
            :theme="getRow(itemName, titleField).color"
            size="md"
            :label="getRow(itemName, titleField).value"
          />
        </div>
        <div
          v-else-if="getRow(itemName, titleField).label"
          class="truncate text-base"
        >
          {{ getRow(itemName, titleField).label }}
      </div>
        <div class="text-ink-gray-4" v-else>{{ __('No Title') }}</div>
      </div>
    </template>
    <template #fields="{ fieldName, itemName }">
      <div
        v-if="getRow(itemName, fieldName).label"
        class="truncate flex items-center gap-2"
      >
        <div v-if="fieldName === 'status'">
          <IndicatorIcon :class="getRow(itemName, fieldName).color" />
        </div>
        <div v-else-if="fieldName === 'customer_name'">
          <Avatar
            v-if="getRow(itemName, fieldName).label"
            class="flex items-center"
            :image="getRow(itemName, fieldName).image"
            :label="getRow(itemName, fieldName).image_label"
            size="xs"
          />
              </div>
        <div v-else-if="fieldName === 'assigned_to'">
          <Avatar
            v-if="getRow(itemName, fieldName).full_name"
            class="flex items-center"
            :image="getRow(itemName, fieldName).user_image"
            :label="getRow(itemName, fieldName).full_name"
            size="xs"
          />
                </div>
        <div
          v-if="
            [
              'modified',
              'creation',
              'first_response_time',
              'first_responded_on',
              'response_by',
              'resolved_on',
            ].includes(fieldName)
          "
          class="truncate text-base"
        >
          <Tooltip :text="getRow(itemName, fieldName).label">
            <div>{{ getRow(itemName, fieldName).timeAgo }}</div>
          </Tooltip>
              </div>
        <div v-else-if="fieldName === 'sla_status'" class="truncate text-base">
          <Badge
            v-if="getRow(itemName, fieldName).value"
            :variant="'subtle'"
            :theme="getRow(itemName, fieldName).color"
            size="md"
            :label="getRow(itemName, fieldName).value"
          />
            </div>
        <div v-else-if="fieldName === 'priority'" class="truncate text-base">
          <Badge
            v-if="getRow(itemName, fieldName).value"
            :variant="'subtle'"
            :theme="getRow(itemName, fieldName).color"
            size="md"
            :label="getRow(itemName, fieldName).value"
          />
          </div>
        <div v-else-if="fieldName === '_assign'" class="flex items-center">
          <MultipleAvatar
            :avatars="getRow(itemName, fieldName).label"
            size="xs"
          />
        </div>
        <div v-else class="truncate text-base">
          {{ getRow(itemName, fieldName).label }}
        </div>
      </div>
    </template>
    <template #actions="{ itemName }">
      <div class="flex gap-2 items-center justify-between">
        <div class="text-ink-gray-5 flex items-center gap-1.5">
          <EmailAtIcon class="h-4 w-4" />
          <span v-if="getRow(itemName, '_email_count').label">
            {{ getRow(itemName, '_email_count').label }}
          </span>
          <span class="text-3xl leading-[0]"> &middot; </span>
          <NoteIcon class="h-4 w-4" />
          <span v-if="getRow(itemName, '_note_count').label">
            {{ getRow(itemName, '_note_count').label }}
          </span>
          <span class="text-3xl leading-[0]"> &middot; </span>
          <TaskIcon class="h-4 w-4" />
          <span v-if="getRow(itemName, '_task_count').label">
            {{ getRow(itemName, '_task_count').label }}
          </span>
          <span class="text-3xl leading-[0]"> &middot; </span>
          <CommentIcon class="h-4 w-4" />
          <span v-if="getRow(itemName, '_comment_count').label">
            {{ getRow(itemName, '_comment_count').label }}
          </span>
        </div>
        <Dropdown
          class="flex items-center gap-2"
          :options="actions(itemName)"
          variant="ghost"
          @click.stop.prevent
        >
          <Button icon="plus" variant="ghost" />
        </Dropdown>
      </div>
    </template>
  </KanbanView>
  <TicketsListView
    ref="ticketsListView"
    v-else-if="tickets.data && rows.length"
    v-model="tickets.data.page_length_count"
    v-model:list="tickets"
    :rows="rows"
    :columns="tickets.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: tickets.data.row_count,
      totalCount: tickets.data.total_count,
    }"
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
  <div v-else-if="tickets.data" class="flex h-full items-center justify-center">
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4"
    >
      <TicketIcon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Tickets')]) }}</span>
      <Button :label="__('Create')" @click="showTicketModal = true">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </div>
  </div>
    <TicketModal 
    v-if="showTicketModal"
      v-model="showTicketModal" 
    :defaults="defaults"
      @ticket-created="handleTicketCreated"
    />
  <NoteModal
    v-if="showNoteModal"
    v-model="showNoteModal"
    :note="note"
    doctype="CRM Ticket"
    :doc="docname"
  />
  <TaskModal
    v-if="showTaskModal"
    v-model="showTaskModal"
    :task="task"
    doctype="CRM Ticket"
    :doc="docname"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import MultipleAvatar from '@/components/MultipleAvatar.vue'
import CustomActions from '@/components/CustomActions.vue'
import EmailAtIcon from '@/components/Icons/EmailAtIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import TicketIcon from '@/components/Icons/TicketIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import TicketsListView from '@/components/ListViews/TicketsListView.vue'
import KanbanView from '@/components/Kanban/KanbanView.vue'
import TicketModal from '@/components/Modals/TicketModal.vue'
import NoteModal from '@/components/Modals/NoteModal.vue'
import TaskModal from '@/components/Modals/TaskModal.vue'
import ViewControls from '@/components/ViewControls.vue'
import { getMeta } from '@/stores/meta'
import { globalStore } from '@/stores/global'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { callEnabled } from '@/composables/settings'
import { formatDate, timeAgo, website, formatTime } from '@/utils'
import { Avatar, Tooltip, Dropdown, Badge, Button, FeatherIcon } from 'frappe-ui'
import { useRoute, useRouter } from 'vue-router'
import { ref, computed, reactive, watch, onMounted, h } from 'vue'

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta('CRM Ticket')
const { makeCall } = globalStore()
const { getUser } = usersStore()

const route = useRoute()
const router = useRouter()

const ticketsListView = ref(null)
const showTicketModal = ref(false)

const defaults = reactive({
  mobile_no: route.query.mobile_no || '',
  priority: route.query.priority || 'Medium',
})

// Watch for query parameter to open ticket modal
watch(() => route.query.showTicketModal, (value) => {
  if (value === 'true') {
    if (route.query.mobile_no) {
      defaults.mobile_no = route.query.mobile_no
    }
    showTicketModal.value = true
    router.replace({ query: {} })
  }
})

// Check on mount in case user refreshes the page
onMounted(() => {
  if (route.query.showTicketModal === 'true') {
    if (route.query.mobile_no) {
      defaults.mobile_no = route.query.mobile_no
    }
    showTicketModal.value = true
    router.replace({ query: {} })
  }
})

// tickets data is loaded in the ViewControls component
const tickets = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

function getRow(name, field) {
  function getValue(value) {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      return value
    }
    return { label: value }
  }
  return getValue(rows.value?.find((row) => row.name == name)[field])
}

// Rows
const rows = computed(() => {
  if (!tickets.value?.data?.data) return []
  if (tickets.value.data.view_type === 'group_by') {
    if (!tickets.value?.data.group_by_field?.fieldname) return []
    return getGroupedByRows(
      tickets.value?.data.data,
      tickets.value?.data.group_by_field,
      tickets.value.data.columns,
    )
  } else if (tickets.value.data.view_type === 'kanban') {
    return getKanbanRows(tickets.value.data.data, tickets.value.data.fields)
  } else {
    return parseRows(tickets.value?.data.data, tickets.value.data.columns)
  }
})

function getGroupedByRows(listRows, groupByField, columns) {
  let groupedRows = []

  groupByField.options?.forEach((option) => {
    let filteredRows = []

    if (!option) {
      filteredRows = listRows.filter((row) => !row[groupByField.fieldname])
    } else {
      filteredRows = listRows.filter((row) => row[groupByField.fieldname] === option)
    }

    if (filteredRows.length > 0) {
      groupedRows.push({
        label: option || __('No {0}', [groupByField.label]),
        group: option,
        collapsed: false,
        rows: parseRows(filteredRows, columns),
      })
    }
  })

  return groupedRows
}

function getKanbanRows(listRows, columns) {
  return parseRows(listRows, columns)
}

function parseRows(rows, columns) {
  return rows.map((row) => {
    let _row = {}
    columns.forEach((column) => {
      _row[column.key] = parseValue(row[column.key], column)
    })
    _row['name'] = row.name
    return _row
  })
}

function parseValue(value, column) {
  if (!value) return null

  if (column.type === 'Date') {
    return {
      label: formatDate(value),
      timeAgo: timeAgo(value),
    }
  }
  if (column.type === 'Datetime') {
    return {
      label: formatTime(value),
      timeAgo: timeAgo(value),
    }
  }
  if (column.type === 'Check') {
    return {
      label: value ? __('Yes') : __('No'),
      value: Boolean(value),
    }
  }
  if (column.type === 'Int' || column.type === 'Float') {
    return {
      label: value,
      value: value,
    }
  }
  if (column.type === 'Currency') {
    return {
      label: getFormattedCurrency(value),
      value: value,
    }
  }
  if (column.key === 'sla_status') {
    let colors = {
      'First Response Due': 'orange',
      'Failed': 'red',
      'Fulfilled': 'green',
    }
    return {
      label: value,
      value: value,
      color: colors[value] || 'gray',
    }
  }
  if (column.key === 'priority') {
    let colors = {
      'Low': 'blue',
      'Medium': 'orange',
      'High': 'red',
      'Urgent': 'purple',
    }
    return {
      label: value,
      value: value,
      color: colors[value] || 'gray',
    }
  }
  if (column.key === 'status') {
    // Get ticket statuses from the store
    const { ticketStatuses } = statusesStore()
    
    // Find the status in the database
    const statusData = ticketStatuses.data?.find(s => s.name === value)
    
    return {
      label: value,
      value: value,
      color: statusData?.color || 'gray',
    }
  }

  return {
    label: value,
    value: value,
  }
}

function onNewClick(column) {
  let column_field = tickets.value.params.column_field

  if (column_field) {
    defaults[column_field] = column.column.name
  }

  showTicketModal.value = true
}

function actions(itemName) {
  let mobile_no = getRow(itemName, 'mobile_no')?.label || ''
  let actions = [
    {
      icon: h(PhoneIcon, { class: 'h-4 w-4' }),
      label: __('Make a Call'),
      onClick: () => makeCall(mobile_no),
      condition: () => mobile_no && callEnabled.value,
    },
    {
      icon: h(NoteIcon, { class: 'h-4 w-4' }),
      label: __('New Note'),
      onClick: () => showNote(itemName),
    },
    {
      icon: h(TaskIcon, { class: 'h-4 w-4' }),
      label: __('New Task'),
      onClick: () => showTask(itemName),
    },
  ]
  return actions.filter((action) =>
    action.condition ? action.condition() : true,
  )
}

const docname = ref('')
const showNoteModal = ref(false)
const note = ref({
  title: '',
  content: '',
})

function showNote(name) {
  docname.value = name
  showNoteModal.value = true
}

const showTaskModal = ref(false)
const task = ref({
  title: '',
  description: '',
  assigned_to: '',
  due_date: '',
  priority: 'Low',
  status: 'Todo',
})

function showTask(name) {
  docname.value = name
  showTaskModal.value = true
}

function handleTicketCreated() {
  console.log('Ticket created, refreshing list...')
  tickets.value?.reload?.()
}
</script> 