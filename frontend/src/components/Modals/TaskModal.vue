<template>
  <Dialog
    v-model="show"
    :options="{
      size: 'xl',
      actions: [
        {
          label: editMode ? __('Update') : __('Create'),
          variant: 'solid',
          onClick: () => updateTask(),
        },
      ],
    }"
  >
    <template #body-title>
      <div class="flex items-center gap-3">
        <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
          {{ editMode ? __('Edit Task') : __('Create Task') }}
        </h3>
        <Button
          v-if="task?.reference_docname"
          size="sm"
          :label="
            task.reference_doctype == 'CRM Deal'
              ? __('Open Deal')
              : __('Open Lead')
          "
          @click="redirect()"
        >
          <template #suffix>
            <ArrowUpRightIcon class="w-4 h-4" />
          </template>
        </Button>
      </div>
    </template>
    <template #body-content>
      <div class="flex flex-col gap-4">
        <div>
          <FormControl
            ref="title"
            :label="__('Title')"
            v-model="_task.title"
            :placeholder="__('Call with John Doe')"
            required
          />
        </div>
        <div>
          <div class="mb-1.5 text-xs text-ink-gray-5">
            {{ __('Description') }}
          </div>
          <TextEditor
            variant="outline"
            ref="description"
            editor-class="!prose-sm overflow-auto min-h-[180px] max-h-80 py-1.5 px-2 rounded border border-[--surface-gray-2] bg-surface-gray-2 placeholder-ink-gray-4 hover:border-outline-gray-modals hover:bg-surface-gray-3 hover:shadow-sm focus:bg-surface-white focus:border-outline-gray-4 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-outline-gray-3 text-ink-gray-8 transition-colors"
            :bubbleMenu="true"
            :content="_task.description"
            @change="(val) => (_task.description = val)"
            :placeholder="
              __('Took a call with John Doe and discussed the new project.')
            "
          />
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <Dropdown :options="taskStatusOptions(updateTaskStatus)">
            <Button :label="_task.status" class="justify-between w-full">
              <template #prefix>
                <TaskStatusIcon :status="_task.status" />
              </template>
            </Button>
          </Dropdown>
          <!-- Assign To (only when opening from Lead/Ticket detail page and it has assignees) -->
          <div v-if="showManualAssignee" class="min-w-[220px] flex-1">
            <div class="mb-1.5 text-xs text-ink-gray-5">{{ __('Assign To') }}</div>
            <Link
              class="form-control"
              doctype="User"
              :filters="assignedUserFilter"
              :value="_task.assigned_to"
              @change="(v) => (_task.assigned_to = v)"
            />
          </div>
          <CustomDateTimePicker
            class="datepicker"
            v-model="_task.due_date"
            :placeholder="__('01/04/2024 11:30 PM')"
            :input-class="'border-none'"
          />
          <Dropdown :options="taskPriorityOptions(updateTaskPriority)">
            <Button :label="_task.priority" class="justify-between w-full">
              <template #prefix>
                <TaskPriorityIcon :priority="_task.priority" />
              </template>
            </Button>
          </Dropdown>
        </div>
        
        <!-- Assignment notification (hide when manual assignee select is visible) -->
        <div v-if="!showManualAssignee" class="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <div class="flex items-center gap-2">
            <FeatherIcon name="info" class="h-4 w-4 text-blue-600" />
            <p class="text-sm text-blue-800">
              {{ isRoleAssignment ? 
                __('Task will be automatically assigned to a user from "{0}" role using round-robin logic', [props.roleForAssignment]) :
                __('Task will be automatically assigned to you')
              }}
            </p>
          </div>
        </div>
        
        <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import TaskStatusIcon from '@/components/Icons/TaskStatusIcon.vue'
import TaskPriorityIcon from '@/components/Icons/TaskPriorityIcon.vue'
import ArrowUpRightIcon from '@/components/Icons/ArrowUpRightIcon.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import Link from '@/components/Controls/Link.vue'
import { taskStatusOptions, taskPriorityOptions, getFormat } from '@/utils'
import { usersStore } from '@/stores/users'
import { capture } from '@/telemetry'
import { TextEditor, Dropdown, Tooltip, call, createResource } from 'frappe-ui'
import { useOnboarding } from 'frappe-ui/frappe'
import { ref, watch, nextTick, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import CustomDateTimePicker from '../CustomDateTimePicker.vue'

const props = defineProps({
  task: {
    type: Object,
    default: {},
  },
  doctype: {
    type: String,
    default: 'CRM Lead',
  },
  doc: {
    type: String,
    default: '',
  },
  roleForAssignment: {
    type: String,
    default: '',
  },
})

const show = defineModel()
const tasks = defineModel('reloadTasks')

const emit = defineEmits(['updateTask', 'after'])

const router = useRouter()
const { users, getUser } = usersStore()
const { updateOnboardingStep } = useOnboarding('frappecrm')

const error = ref(null)
const title = ref(null)
const editMode = ref(false)
const isRoleAssignment = ref(false)
const _task = ref({
  title: '',
  description: '',
  assigned_to: '',
  due_date: '',
  status: 'Todo',
  priority: 'Low',
  reference_doctype: props.doctype,
  reference_docname: null,
})

// Load parent doc assignees from _assign (JSON array)
const assignedUsers = createResource({
  url: 'frappe.client.get_value',
  params: {
    doctype: props.doctype,
    filters: { name: props.doc },
    fieldname: '_assign',
  },
  auto: false,
  transform: (data) => {
    try {
      const raw = data?._assign || ''
      const arr = raw ? JSON.parse(raw) : []
      return Array.isArray(arr) ? arr : []
    } catch (e) {
      return []
    }
  },
  onSuccess: (ids) => {
    if (ids?.length && !_task.value.assigned_to) {
      _task.value.assigned_to = ids[0]
    }
  },
})

const showManualAssignee = computed(() => {
  return Boolean(props.doc) && Array.isArray(assignedUsers.data) && assignedUsers.data.length > 0
})

const assignedUserFilter = computed(() => {
  return assignedUsers.data?.length ? { name: ['in', assignedUsers.data] } : {}
})

function updateTaskStatus(status) {
  _task.value.status = status
}

function updateTaskPriority(priority) {
  _task.value.priority = priority
}

function redirect() {
  if (!props.task?.reference_docname) return
  let name = props.task.reference_doctype == 'CRM Deal' ? 'Deal' : 'Lead'
  let params = { leadId: props.task.reference_docname }
  if (name == 'Deal') {
    params = { dealId: props.task.reference_docname }
  }
  router.push({ name: name, params: params })
}

async function updateTask() {
  if (!_task.value.assigned_to) {
    _task.value.assigned_to = getUser().name
  }
  
  // Ensure due_date is sent; default to current datetime if empty
  if (!_task.value.due_date) {
    const now = new Date()
    const pad = (n) => String(n).padStart(2, '0')
    const iso = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
    _task.value.due_date = iso
  }
  
  if (_task.value.name) {
    let d = await call('frappe.client.set_value', {
      doctype: 'CRM Task',
      name: _task.value.name,
      fieldname: _task.value,
    })
    if (d.name) {
      tasks.value?.reload()
      emit('after', d)
    }
  } else {
    // ✅ FIX: Defer task creation when parent document doesn't exist yet (Lead/Ticket)
    // If no reference document (props.doc is empty/null) and doctype is CRM Lead or CRM Ticket,
    // this is being called before the parent is created from the modal. Return task data only.
    if ((!props.doc || props.doc === '') && (props.doctype === 'CRM Lead' || props.doctype === 'CRM Ticket')) {
      // Don't create the task yet - just return the task data
      // This prevents duplicate creation from LeadModal
      console.log('Task creation deferred - no reference document exists yet')
      emit('after', {
        ..._task.value,
        reference_doctype: props.doctype,
        reference_docname: props.doc || '',
        name: null // No actual task created yet
      }, true) // Mark as "new" for proper handling
      show.value = false
      return
    }
    // Normal task creation with proper reference
    console.log('Creating task with data:', _task.value)
    let d = await call(
      'frappe.client.insert',
      {
        doc: {
          doctype: 'CRM Task',
          reference_doctype: props.doctype,
          reference_docname: props.doc || null,
          ..._task.value,
        },
      },
      {
        onError: (err) => {
          console.error('Task creation error:', err)
          if (err.error.exc_type == 'MandatoryError') {
            error.value = 'Title is mandatory'
          }
        },
      },
    )
    if (d.name) {
      updateOnboardingStep('create_first_task')
      capture('task_created')
      tasks.value?.reload()
      emit('after', d, true)
    }
  }
  show.value = false
}

function render() {
  editMode.value = false
  nextTick(() => {
    title.value?.el?.focus?.()
    _task.value = { ...props.task }
    if (_task.value.title) {
      editMode.value = true
    }
  })
}

// Handle automatic assignment
watch(
  () => props.roleForAssignment,
  async (role) => {
    if (role) {
      isRoleAssignment.value = true
      
      try {
        // Get the next user for this role
        const result = await call('crm.api.role_assignment.preview_next_assignment', {
          role_name: role
        })
        
        if (result.success && result.next_user) {
          _task.value.assigned_to = result.next_user
          console.log(`Pre-selected user ${result.next_user} for role ${role}`)
        } else {
          console.warn('Could not get next user for role:', role)
        }
      } catch (err) {
        console.error('Error getting next user for role:', err)
      }
    } else {
      isRoleAssignment.value = false
      // If no role selected, assign to current user
      _task.value.assigned_to = getUser().name
      console.log(`Pre-selected current user ${getUser().name} for task`)
    }
  },
  { immediate: true }
)

onMounted(() => show.value && render())

watch(show, (value) => {
  if (!value) return
  render()
  if (props.doc) {
    assignedUsers.fetch()
  }
})
</script>

<style scoped>
:deep(.datepicker svg) {
  width: 0.875rem;
  height: 0.875rem;
}
</style>
