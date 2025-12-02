<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Tasks" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="tasksListView?.customListActions"
        :actions="tasksListView.customListActions"
      />
      <Button 
        variant="secondary" 
        :label="showWeeklyTasks ? 'Show All Tasks' : 'Show Weekly Tasks'"
        @click="toggleWeeklyTasks"
      >
        <template #prefix><FeatherIcon name="calendar" class="h-4" /></template>
      </Button>
      <!-- <Button variant="solid" :label="__('Create')" @click="createTask">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button> -->
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="tasks"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="CRM Task"
    :filters="defaultFilters"
    :options="{
      allowedViews: ['list', 'kanban'],
    }"
  />
  <KanbanView
    v-if="$route.params.viewType == 'kanban' && rows.length"
    v-model="tasks"
    :options="{
      onClick: (row) => showTask(row.name),
      onNewClick: canWriteTasks ? (column) => createTask(column) : undefined,
    }"
    @update="(data) => viewControls.updateKanbanSettings(data)"
    @loadMore="(columnName) => viewControls.loadMoreKanban(columnName)"
  >
    <template #title="{ titleField, itemName }">
      <div class="flex items-center gap-2">
        <div v-if="titleField === 'status'">
          <TaskStatusIcon :status="getRow(itemName, titleField).label" />
        </div>
        <div v-else-if="titleField === 'priority'">
          <TaskPriorityIcon :priority="getRow(itemName, titleField).label" />
        </div>
        <div v-else-if="titleField === 'assigned_to'">
          <Avatar
            v-if="getRow(itemName, titleField).full_name"
            class="flex items-center"
            :image="getRow(itemName, titleField).user_image"
            :label="getRow(itemName, titleField).full_name"
            size="sm"
          />
        </div>
        <div
          v-if="['modified', 'creation'].includes(titleField)"
          class="truncate text-base"
        >
          <Tooltip :text="getRow(itemName, titleField).label">
            <div>{{ getRow(itemName, titleField).timeAgo }}</div>
          </Tooltip>
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
          <TaskStatusIcon
            class="size-3"
            :status="getRow(itemName, fieldName).label"
          />
        </div>
        <div v-else-if="fieldName === 'priority'">
          <TaskPriorityIcon :priority="getRow(itemName, fieldName).label" />
        </div>
        <div v-else-if="fieldName === 'assigned_to'">
          <Avatar
            v-if="getRow(itemName, fieldName).full_name"
            class="flex items-center"
            :image="getRow(itemName, fieldName).user_image"
            :label="getRow(itemName, fieldName).full_name"
            size="sm"
          />
        </div>
        <div
          v-if="['modified', 'creation'].includes(fieldName)"
          class="truncate text-base"
        >
          <Tooltip :text="getRow(itemName, fieldName).label">
            <div>{{ getRow(itemName, fieldName).timeAgo }}</div>
          </Tooltip>
        </div>
        <div
          v-else-if="fieldName == 'description'"
          class="truncate text-base max-h-44"
        >
          <TextEditor
            v-if="getRow(itemName, fieldName).label"
            :content="getRow(itemName, fieldName).label"
            :editable="false"
            editor-class="!prose-sm max-w-none focus:outline-none"
            class="flex-1 overflow-hidden"
          />
        </div>
        <div v-else class="truncate text-base">
          {{ getRow(itemName, fieldName).label }}
        </div>
      </div>
    </template>
    <template #actions="{ itemName }">
      <div class="flex gap-2 items-center justify-between">
        <div>
          <Button
            class="-ml-2"
            v-if="getRow(itemName, 'reference_docname').label"
            variant="ghost"
            size="sm"
            :label="
              getRow(itemName, 'reference_doctype').label == 'CRM Deal'
                ? __('Deal')
                : __('Lead')
            "
            @click.stop="
              redirect(
                getRow(itemName, 'reference_doctype').label,
                getRow(itemName, 'reference_docname').label,
              )
            "
          >
            <template #suffix>
              <ArrowUpRightIcon class="h-4 w-4" />
            </template>
          </Button>
        </div>
        <Dropdown
          class="flex items-center gap-2"
          :options="actions(itemName)"
          variant="ghost"
          @click.stop.prevent
        >
          <Button icon="more-horizontal" variant="ghost" />
        </Dropdown>
      </div>
    </template>
  </KanbanView>
  <TasksListView
    ref="tasksListView"
    v-else-if="tasks.data && rows.length"
    v-model="tasks.data.page_length_count"
    v-model:list="tasks"
    :rows="rows"
    :columns="tasks.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: tasks.data.row_count,
      totalCount: tasks.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @pageChange="(page) => viewControls.goToPage(page)"
    @pageSizeChange="(pageSize) => viewControls.handlePageSizeChange(pageSize)"
    @showTask="showTask"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
    @selectionsChanged="
      (selections) => viewControls.updateSelections(selections)
    "
  />
  <div v-else-if="tasks.data" class="flex h-full items-center justify-center">
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4"
    >
      <Email2Icon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Tasks')]) }}</span>
      <!-- <Button :label="__('Create')" @click="showTaskModal = true">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button> -->
    </div>
  </div>
  <TaskModal
    v-if="showTaskModal"
    v-model="showTaskModal"
    v-model:reloadTasks="tasks"
    :task="task"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import ArrowUpRightIcon from '@/components/Icons/ArrowUpRightIcon.vue'
import TaskStatusIcon from '@/components/Icons/TaskStatusIcon.vue'
import TaskPriorityIcon from '@/components/Icons/TaskPriorityIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewControls from '@/components/ViewControls.vue'
import TasksListView from '@/components/ListViews/TasksListView.vue'
import KanbanView from '@/components/Kanban/KanbanView.vue'
import TaskModal from '@/components/Modals/TaskModal.vue'
import { getMeta } from '@/stores/meta'
import { usersStore } from '@/stores/users'
import { formatDate, timeAgo } from '@/utils'
import { Tooltip, Avatar, TextEditor, Dropdown, call } from 'frappe-ui'
import { computed, ref, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { permissionsStore } from '@/stores/permissions'
import { sessionStore } from '@/stores/session'
import { dayjs } from 'frappe-ui'

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta('CRM Task')
const { getUser } = usersStore()

const route = useRoute()
const router = useRouter()
const session = sessionStore()
const tasksListView = ref(null)

// tasks data is loaded in the ViewControls component
const tasks = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

const applyTaskFiltersFromRoute = () => {
  const payload = route.query.taskFilters
  if (!payload || !viewControls.value?.updateFilter) return

  try {
    const raw = Array.isArray(payload) ? payload[0] : payload
    const parsed = raw ? JSON.parse(raw) : null
    if (!parsed || typeof parsed !== 'object') return

    const normalized = { ...(defaultFilters.value || {}) }

    Object.entries(parsed).forEach(([field, value]) => {
      let resolved = value

      if (resolved === '__current__') {
        resolved = session.user || ''
      }

      if (
        resolved === null ||
        resolved === undefined ||
        resolved === '__unset__' ||
        (typeof resolved === 'string' && resolved.trim() === '')
      ) {
        delete normalized[field]
        return
      }

      if (Array.isArray(resolved)) {
        normalized[field] = resolved
        return
      }

      if (typeof resolved === 'object') {
        normalized[field] = resolved
        return
      }

      if (field === '_assign') {
        normalized[field] = ['LIKE', `%${resolved}%`]
      } else {
        normalized[field] = resolved
      }
    })

    viewControls.value.updateFilter(normalized)
  } catch (error) {
    console.error('Failed to apply task filters from route', error)
  } finally {
    if (route.query.taskFilters !== undefined) {
      const newQuery = { ...route.query }
      delete newQuery.taskFilters
      router.replace({ query: newQuery })
    }
  }
}

watch(
  () => [route.query.taskFilters, viewControls.value],
  ([filtersParam, vc]) => {
    if (filtersParam && vc) {
      setTimeout(() => applyTaskFiltersFromRoute())
    }
  },
  { immediate: true },
)

// Permissions
const { canWrite } = permissionsStore()
const canWriteTasks = computed(() => canWrite('Tasks'))

// Track if showing today's tasks
const showWeeklyTasks = ref(true)

// Default filters including today's tasks filter
const defaultFilters = computed(() => {
  if (!showWeeklyTasks.value) return {}
  
  const today = dayjs()
  // Start of the week (Monday)
  let startOfWeek = today.startOf('week') // dayjs default start of week is Sunday
  if (startOfWeek.day() === 0) { // If it's Sunday, move to Monday
    startOfWeek = startOfWeek.add(1, 1, 'day')
  }
  // End of the week (Sunday)
  const endOfWeek = today.endOf('week').add(1, 'day')

  // Only show tasks from today onwards
  const startDate = today.format('YYYY-MM-DD HH:mm:ss')
  const endDate = endOfWeek.format('YYYY-MM-DD HH:mm:ss')
  
  return {
    due_date: ['between', [startDate, endDate]]
  }
})

// Toggle today's tasks filter
async function toggleWeeklyTasks() {
  showWeeklyTasks.value = !showWeeklyTasks.value
  // Wait for props (:filters) to propagate to ViewControls before applying
  await nextTick()
  // Preserve existing filters and only toggle the due_date constraint
  const currentFilters = (tasks.value?.params?.filters && { ...tasks.value.params.filters }) || {}
  
  if (showWeeklyTasks.value) {
    const today = dayjs()
    // Start of the week (Monday)
    let startOfWeek = today.startOf('week') // dayjs default start of week is Sunday
    if (startOfWeek.day() === 0) { // If it's Sunday, move to Monday
      startOfWeek = startOfWeek.add(1, 'day')
    }
    // End of the week (Sunday)
    const endOfWeek = today.endOf('week').add(1, 'day')

    // Only show tasks from today onwards
    const startDate = today.format('YYYY-MM-DD HH:mm:ss')
    const endDate = endOfWeek.format('YYYY-MM-DD HH:mm:ss')

    currentFilters.due_date = ['between', [startDate, endDate]]
  } else {
    if (currentFilters.due_date) delete currentFilters.due_date
  }
  if (viewControls.value) {
    viewControls.value.updateFilter(currentFilters)
  }
}

// Add quick filter button in the header
const quickActions = [
  {
    label: computed(() => showWeeklyTasks.value ? 'Show All Tasks' : "Show Weekly Tasks"),
    icon: 'calendar',
    onClick: toggleWeeklyTasks,
  }
]

function getRow(name, field) {
  function getValue(value) {
    if (value && typeof value === 'object') {
      return value
    }
    return { label: value }
  }
  return getValue(rows.value?.find((row) => row.name == name)[field])
}

const rows = computed(() => {
  if (!tasks.value?.data?.data) return []

  if (tasks.value.data.view_type === 'kanban') {
    return getKanbanRows(tasks.value.data.data, tasks.value.data.fields)
  }

  openTaskFromURL()
  return parseRows(tasks.value?.data.data, tasks.value?.data.columns)
})

function getKanbanRows(data, columns) {
  let _rows = []
  data.forEach((column) => {
    column.data?.forEach((row) => {
      _rows.push(row)
    })
  })
  return parseRows(_rows, columns)
}

function parseRows(rows, columns = []) {
  let view_type = tasks.value.data.view_type
  let key = view_type === 'kanban' ? 'fieldname' : 'key'
  let type = view_type === 'kanban' ? 'fieldtype' : 'type'

  return rows.map((task) => {
    let _rows = {}
    tasks.value?.data.rows.forEach((row) => {
      _rows[row] = task[row]

      let fieldType = columns?.find((col) => (col[key] || col.value) == row)?.[
        type
      ]

      if (
        fieldType &&
        ['Date', 'Datetime'].includes(fieldType) &&
        !['modified', 'creation'].includes(row)
      ) {
        _rows[row] = formatDate(task[row], '', true, fieldType == 'Datetime')
      }

      if (fieldType && fieldType == 'Currency') {
        _rows[row] = getFormattedCurrency(row, task)
      }

      if (fieldType && fieldType == 'Float') {
        _rows[row] = getFormattedFloat(row, task)
      }

      if (fieldType && fieldType == 'Percent') {
        _rows[row] = getFormattedPercent(row, task)
      }

      if (['modified', 'creation'].includes(row)) {
        _rows[row] = {
          label: formatDate(task[row]),
          timeAgo: __(timeAgo(task[row])),
        }
      } else if (row == 'assigned_to') {
        // Backwards-compatible single-assignee support for assigned_to
        _rows[row] = {
          label: task.assigned_to && getUser(task.assigned_to).full_name,
          ...(task.assigned_to && getUser(task.assigned_to)),
        }
      } else if (row == '_assign') {
        // Parse _assign JSON to expose multiple assignees similar to Leads/Tickets
        try {
          const assignees = JSON.parse(task._assign || '[]')
          _rows[row] = assignees.map((user) => ({
            name: user,
            image: getUser(user).user_image,
            label: getUser(user).full_name,
          }))
        } catch (e) {
          _rows[row] = []
        }
      } else if (row == 'due_date') {
        // Store both original date and formatted display string
        _rows[row] = task[row] ? {
          original: task[row],
          display: formatDate(task[row], 'D MMM, hh:mm a')
        } : null;
      }
    })
    return _rows
  })
}

const showTaskModal = ref(false)

const task = ref({
  name: '',
  title: '',
  description: '',
  assigned_to: '',
  due_date: '',
  status: 'Todo',
  priority: 'Low',
  reference_doctype: 'CRM Lead',
  reference_docname: '',
})

function showTask(name) {
  let t = rows.value?.find((row) => row.name === name)
  task.value = {
    name: t.name,
    title: t.title,
    description: t.description,
    assigned_to: t.assigned_to?.email || '',
    due_date: t.due_date,
    status: t.status,
    priority: t.priority,
    reference_doctype: t.reference_doctype,
    reference_docname: t.reference_docname,
  }
  showTaskModal.value = true
}

function createTask(column) {
  task.value = {
    name: '',
    title: '',
    description: '',
    assigned_to: '',
    due_date: '',
    status: 'Todo',
    priority: 'Low',
    reference_doctype: 'CRM Lead',
    reference_docname: '',
  }

  if (column.column?.name) {
    let column_field = tasks.value.params.column_field
    if (column_field) {
      task.value[column_field] = column.column.name
    }
  }

  showTaskModal.value = true
}

function actions(name) {
  return [
    {
      label: __('Delete'),
      icon: 'trash-2',
      onClick: () => {
        deletetask(name)
        tasks.value.reload()
      },
    },
  ]
}

async function deletetask(name) {
  await call('frappe.client.delete', {
    doctype: 'CRM Task',
    name,
  })
}

function redirect(doctype, docname) {
  if (!docname) return
  let name = doctype == 'CRM Deal' ? 'Deal' : 'Lead'
  let params = { leadId: docname }
  if (name == 'Deal') {
    params = { dealId: docname }
  }
  router.push({ name: name, params: params })
}

const openTaskFromURL = () => {
  const searchParams = new URLSearchParams(window.location.search)
  const taskName = searchParams.get('open')

  if (taskName && rows.value?.length) {
    showTask(parseInt(taskName))
    searchParams.delete('open')
    window.history.replaceState(null, '', window.location.pathname)
  }
}

</script>
