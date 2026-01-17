<template>
  <Dialog
    v-model="show"
    :options="{
      size: 'lg',
      title: __('Complete Follow-up Tasks'),
      actions: [
        {
          label: __('Mark Selected as Done'),
          variant: 'solid',
          disabled: selectedTasks.length === 0,
          onClick: markTasksAsDone,
        },
        {
          label: __('Skip'),
          variant: 'outline',
          onClick: skipAndProceed,
        },
      ],
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-4">
        <!-- Loading state -->
        <div v-if="loading" class="flex items-center justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
        
        <!-- No tasks found -->
        <div v-else-if="eligibleTasks.length === 0" class="text-center py-8 text-ink-gray-6">
          <FeatherIcon name="check-circle" class="h-12 w-12 mx-auto mb-3 text-green-500" />
          <p class="text-lg font-medium">{{ __('No pending follow-up tasks found') }}</p>
          <p class="text-sm mt-2">{{ __('You can proceed with the status change.') }}</p>
        </div>
        
        <!-- Tasks list -->
        <div v-else class="flex flex-col gap-2">
          <p class="text-sm text-ink-gray-6 mb-2">
            {{ __('Select the follow-up tasks you want to mark as completed:') }}
          </p>
          
          <!-- Select All -->
          <div class="flex items-center gap-2 p-2 bg-surface-gray-2 rounded mb-2">
            <input
              type="checkbox"
              id="select-all"
              :checked="allSelected"
              :indeterminate="someSelected && !allSelected"
              @change="toggleSelectAll"
              class="h-4 w-4 rounded border-gray-300"
            />
            <label for="select-all" class="text-sm font-medium text-ink-gray-7 cursor-pointer">
              {{ __('Select All') }} ({{ eligibleTasks.length }})
            </label>
          </div>
          
          <!-- Task items -->
          <div
            v-for="task in eligibleTasks"
            :key="task.name"
            class="flex items-start gap-3 p-3 border border-outline-gray-2 rounded-lg hover:bg-surface-gray-1 transition-colors"
          >
            <input
              type="checkbox"
              :id="task.name"
              :checked="selectedTasks.includes(task.name)"
              @change="toggleTask(task.name)"
              class="h-4 w-4 mt-1 rounded border-gray-300"
            />
            <div class="flex-1 min-w-0">
              <label :for="task.name" class="cursor-pointer">
                <div class="font-medium text-ink-gray-9 truncate">{{ task.title }}</div>
                <div class="flex flex-wrap items-center gap-2 mt-1 text-sm text-ink-gray-6">
                  <div class="flex items-center gap-1">
                    <TaskStatusIcon :status="task.status" />
                    <span>{{ task.status }}</span>
                  </div>
                  <span v-if="task.due_date" class="flex items-center gap-1">
                    <FeatherIcon name="calendar" class="h-3 w-3" />
                    {{ formatDate(task.due_date, 'MMM D, YYYY | hh:mm a') }}
                  </span>
                  <span v-if="task.assigned_to" class="flex items-center gap-1">
                    <UserAvatar :user="task.assigned_to" size="xs" />
                    {{ getUser(task.assigned_to).full_name }}
                  </span>
                </div>
              </label>
            </div>
          </div>
        </div>
        
        <ErrorMessage v-if="error" :message="error" class="mt-2" />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import TaskStatusIcon from '@/components/Icons/TaskStatusIcon.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import { formatDate } from '@/utils'
import { usersStore } from '@/stores/users'
import { Dialog, ErrorMessage, FeatherIcon, call } from 'frappe-ui'
import { ref, computed, watch } from 'vue'

const props = defineProps({
  doctype: {
    type: String,
    required: true,
  },
  docname: {
    type: String,
    required: true,
  },
  documentName: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['proceed', 'cancel'])

const show = defineModel()
const { getUser } = usersStore()

const loading = ref(false)
const error = ref(null)
const eligibleTasks = ref([])
const selectedTasks = ref([])

// Computed properties for select all
const allSelected = computed(() => 
  eligibleTasks.value.length > 0 && selectedTasks.value.length === eligibleTasks.value.length
)
const someSelected = computed(() => selectedTasks.value.length > 0)

// Toggle individual task selection
function toggleTask(taskName) {
  const index = selectedTasks.value.indexOf(taskName)
  if (index === -1) {
    selectedTasks.value.push(taskName)
  } else {
    selectedTasks.value.splice(index, 1)
  }
}

// Toggle select all
function toggleSelectAll() {
  if (allSelected.value) {
    selectedTasks.value = []
  } else {
    selectedTasks.value = eligibleTasks.value.map(t => t.name)
  }
}

// Fetch eligible follow-up tasks
async function fetchEligibleTasks() {
  loading.value = true
  error.value = null
  
  try {
    // Use dedicated API endpoint to fetch eligible follow-up tasks
    const tasks = await call('crm.api.task_notifications.get_eligible_followup_tasks', {
      reference_doctype: props.doctype,
      reference_docname: props.docname,
    })
    
    eligibleTasks.value = tasks || []
    console.log('FollowupTasksModal: eligible tasks found:', eligibleTasks.value.length)
    
    // Auto-select all tasks by default
    selectedTasks.value = eligibleTasks.value.map(t => t.name)
  } catch (err) {
    console.error('Error fetching eligible tasks:', err)
    error.value = err.message || __('Failed to fetch tasks')
  } finally {
    loading.value = false
  }
}

// Mark selected tasks as done
async function markTasksAsDone() {
  if (selectedTasks.value.length === 0) return
  
  loading.value = true
  error.value = null
  
  try {
    // Update all selected tasks to Done status in parallel
    await Promise.all(selectedTasks.value.map(taskName => 
      call('frappe.client.set_value', {
        doctype: 'CRM Task',
        name: taskName,
        fieldname: 'status',
        value: 'Done',
      })
    ))
    
    show.value = false
    emit('proceed', { markedAsDone: selectedTasks.value.length })
  } catch (err) {
    console.error('Error marking tasks as done:', err)
    error.value = err.message || __('Failed to update tasks')
  } finally {
    loading.value = false
  }
}

// Skip marking tasks and proceed with status change
function skipAndProceed() {
  show.value = false
  emit('proceed', { markedAsDone: 0 })
}

// Fetch tasks when modal opens
watch(show, (value) => {
  if (value) {
    console.log('FollowupTasksModal: fetching tasks for', props.doctype, props.docname)
    fetchEligibleTasks()
  } else {
    // Reset state when modal closes
    eligibleTasks.value = []
    selectedTasks.value = []
    error.value = null
  }
}, { immediate: true })
</script>
