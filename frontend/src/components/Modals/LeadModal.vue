<template>
  <Dialog v-model="show" :options="{ size: '3xl' }" v-if="!leadModalHidden">
    <template #body>
      <div class="bg-surface-modal px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
              {{ __('Create Lead') }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button
              v-if="isManager() && !isMobileView"
              variant="ghost"
              class="w-7"
              @click="openQuickEntryModal"
            >
              <template #icon>
                <EditIcon />
              </template>
            </Button>
            <Button variant="ghost" class="w-7" @click="show = false">
              <template #icon>
                <FeatherIcon name="x" class="size-4" />
              </template>
            </Button>
          </div>
        </div>
        <div>
          <FieldLayout v-if="tabs.data" :tabs="tabs.data" v-model="lead.doc" :doctype="'CRM Lead'" />
          
          <!-- Assign Task Button Section -->
          <div v-if="lead.doc.assigned_to && lead.doc.assigned_to !== user" class="mt-4 flex items-center gap-3 rounded-lg border border-ink-gray-4 bg-ink-gray-1 p-3">
            <div class="flex-1">
              <p class="text-sm font-medium text-ink-gray-9">
                {{ __('Lead will be assigned to {0}', [getUser(lead.doc.assigned_to)?.full_name || lead.doc.assigned_to]) }}
              </p>
              <p class="text-xs text-ink-gray-7" v-if="!pendingTaskData">
                {{ __('You can create a task for the assigned user to get started immediately') }}
              </p>
              <p class="text-xs text-green-600" v-else>
                {{ __('Task "{0}" will be created when lead is saved', [pendingTaskData.title]) }}
              </p>
            </div>
            
            <!-- Task Assignment Actions -->
            <div class="flex items-center gap-2">
              <!-- Assign Task Button (when no task is pending) -->
              <Button
                v-if="!pendingTaskData"
                variant="outline"
                :label="__('Assign Task')"
                @click.stop="openTaskModalForAssignment"
              >
                <template #prefix>
                  <FeatherIcon name="plus" class="h-4 w-4" />
                </template>
              </Button>
              
              <!-- Task Assigned Status (when task is pending) -->
              <template v-else>
                <Button
                  variant="solid"
                  :label="__('Task Assigned')"
                  @click.stop="editAssignedTask"
                >
                  <template #prefix>
                    <FeatherIcon name="check" class="h-4 w-4" />
                  </template>
                </Button>
                
                <!-- Clear Task Button -->
                <Button
                  variant="ghost"
                  size="sm"
                  @click.stop="clearAssignedTask"
                  class="!px-2"
                >
                  <template #icon>
                    <FeatherIcon name="x" class="h-4 w-4" />
                  </template>
                </Button>
              </template>
            </div>
          </div>
          
          <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
        </div>
      </div>
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="flex flex-row-reverse gap-2">
          <Button
            variant="solid"
            :label="__('Create')"
            :loading="isLeadCreating"
            @click="createNewLead"
          />
        </div>
      </div>
    </template>
  </Dialog>
  
  <!-- Task Modal for creating tasks -->
  <TaskModal
    v-if="showTaskModal"
    v-model="showTaskModal"
    :task="taskData"
    doctype="CRM Lead"
    :doc="createdLeadId || null"
    @after="handleTaskCreated"
  />
</template>

<script setup>
import EditIcon from '@/components/Icons/EditIcon.vue'
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import TaskModal from '@/components/Modals/TaskModal.vue'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { sessionStore } from '@/stores/session'
import { isMobileView } from '@/composables/settings'
import { showQuickEntryModal, quickEntryProps } from '@/composables/modals'
import { capture } from '@/telemetry'
import { createResource, call } from 'frappe-ui'
import { useOnboarding } from 'frappe-ui/frappe'
import { useDocument } from '@/data/document'
import { computed, onMounted, ref, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  defaults: Object,
})

const { user } = sessionStore()
const { getUser, isManager } = usersStore()
const { getLeadStatus, statusOptions } = statusesStore()
const { updateOnboardingStep } = useOnboarding('frappecrm')

const show = defineModel()
const router = useRouter()
const error = ref(null)
const isLeadCreating = ref(false)

// Task Modal state
const showTaskModal = ref(false)
const createdLeadId = ref('')
const pendingTaskData = ref(null) // Store task data that was created before lead
const leadModalHidden = ref(false) // Track if lead modal is temporarily hidden
const taskData = ref({
  title: '',
  description: '',
  assigned_to: '',
  due_date: '',
  status: 'Backlog',
  priority: 'Medium',
  reference_doctype: 'CRM Lead',
  reference_docname: '',
})

const { document: lead, triggerOnChange } = useDocument('CRM Lead')

// Initialize document properly
onMounted(() => {
  // Initialize lead document with required properties
  lead.doc = {
    doctype: 'CRM Lead',
    name: '', // Required for Field.vue
    first_name: '',
    last_name: '',
    email: '',
    mobile_no: '',
    lead_type: 'Sales', // Set default lead type (hidden field)
    lead_source: 'On Call', // Default value for lead source
    account_type: 'Individual', // Set default account type
    no_of_employees: '1-10',
    status: '',
    assigned_to: '', // New field for assignment tracking
    // ... other default values
  }

  // Merge with any provided defaults
  if (props.defaults) {
    Object.assign(lead.doc, props.defaults)
  }

  // Set default lead owner if not provided
  if (!lead.doc?.lead_owner) {
    lead.doc.lead_owner = user
  }
})

const leadStatuses = computed(() => {
  let statuses = statusOptions('lead', null, [], triggerOnChange)
  if (!lead.doc.status) {
    lead.doc.status = statuses?.[0]?.value
  }
  return statuses
})

function handleTaskCreated(taskDoc, isNew = false) {
  console.log('Task created:', taskDoc)
  showTaskModal.value = false
  
  // Restore the lead modal
  leadModalHidden.value = false
  
  // Clear any error messages
  error.value = null
  
  // If lead doesn't exist yet, store task data for later creation
  if (!createdLeadId.value) {
    pendingTaskData.value = {
      ...taskDoc,
      isNew: isNew
    }
    console.log('Task data stored, will be created after lead is saved')
    return
  }
  
  if (isNew) {
    // Show success message
    console.log(`Task "${taskDoc.title}" created successfully for ${getUser(taskDoc.assigned_to).full_name}`)
  }
  
  // Navigate to the lead page after task is created
  router.push({ name: 'Lead', params: { leadId: createdLeadId.value } })
}

// Function to open task modal from the assignment section
function openTaskModalForAssignment() {
  if (!lead.doc.assigned_to) {
    error.value = __('Please select a user to assign before creating a task')
    return
  }
  
  // Pre-fill task data
  taskData.value = {
    title: `Follow up on lead: ${lead.doc.first_name || 'New Lead'}`,
    description: `Task created for lead assignment - ${lead.doc.first_name} ${lead.doc.last_name || ''}`.trim(),
    assigned_to: lead.doc.assigned_to,
    due_date: '',
    status: 'Backlog',
    priority: 'Medium',
    reference_doctype: 'CRM Lead',
    reference_docname: '', // Will be empty until lead is created
  }
  
  // Temporarily hide lead modal to prevent conflicts
  leadModalHidden.value = true
  
  // Use nextTick to ensure proper modal transition
  nextTick(() => {
    showTaskModal.value = true
  })
}

// Function to edit the already assigned task
function editAssignedTask() {
  if (!pendingTaskData.value) return
  
  // Load the existing task data for editing
  taskData.value = {
    ...pendingTaskData.value,
    reference_docname: '', // Will be empty until lead is created
  }
  
  // Temporarily hide lead modal to prevent conflicts
  leadModalHidden.value = true
  
  // Use nextTick to ensure proper modal transition
  nextTick(() => {
    showTaskModal.value = true
  })
}

// Function to clear the assigned task
function clearAssignedTask() {
  // Clear the pending task data
  pendingTaskData.value = null
  
  // Clear task data
  taskData.value = {
    title: '',
    description: '',
    assigned_to: '',
    due_date: '',
    status: 'Backlog',
    priority: 'Medium',
    reference_doctype: 'CRM Lead',
    reference_docname: '',
  }
  
  console.log('Task assignment cleared')
}

const tabs = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['QuickEntry', 'CRM Lead'],
  params: { doctype: 'CRM Lead', type: 'Quick Entry' },
  auto: true,
  transform: (_tabs) => {
    _tabs.forEach((tab) => {
      tab.sections.forEach((section) => {
        section.columns.forEach((column) => {
          column.fields.forEach((field, fieldIndex) => {
            if (field.fieldname == 'status') {
              field.fieldtype = 'Select'
              field.options = leadStatuses.value
              field.prefix = getLeadStatus(lead.doc.status).color
            }
            
            // Add custom assigned_to field for tracking assignments
            if (field.fieldname == 'lead_owner') {
              // Insert assigned_to field after lead_owner
              const assignedToField = {
                fieldname: 'assigned_to',
                fieldtype: 'Link',
                label: 'Assign To',
                options: 'User',
                description: 'Assign this lead to another team member for handling'
              }
              
              // Find the current field index and insert after it
              const currentFieldIndex = column.fields.indexOf(field)
              if (currentFieldIndex !== -1) {
                column.fields.splice(currentFieldIndex + 1, 0, assignedToField)
              }
            }

            if (field.fieldtype === 'Table') {
              lead.doc[field.fieldname] = []
            }
          })
        })
      })
    })
    return _tabs
  },
})

const createLead = createResource({
  url: 'frappe.client.insert',
  makeParams(values) {
    // Prepare the document
    const doc = {
      doctype: 'CRM Lead',
      ...values,
    }
    
    // Handle assignment: if assigned_to is provided, set it in _assign field
    if (values.assigned_to) {
      doc._assign = JSON.stringify([values.assigned_to])
      // Remove assigned_to from the doc as it's not a real field
      delete doc.assigned_to
    }
    
    return { doc }
  },
})

function createNewLead() {
  if (lead.doc.website && !lead.doc.website.startsWith('http')) {
    lead.doc.website = 'https://' + lead.doc.website
  }

  createLead.submit(lead.doc, {
    validate() {
      error.value = null
      if (!lead.doc.first_name) {
        error.value = __('First Name is mandatory')
        return error.value
      }
      if (!lead.doc.lead_source) {
        error.value = __('Lead Source is mandatory')
        return error.value
      }
      if (!lead.doc.account_type) {
        error.value = __('Account Type is mandatory')
        return error.value
      }
      if (lead.doc.annual_revenue) {
        if (typeof lead.doc.annual_revenue === 'string') {
          lead.doc.annual_revenue = lead.doc.annual_revenue.replace(/,/g, '')
        } else if (isNaN(lead.doc.annual_revenue)) {
          error.value = __('Annual Revenue should be a number')
          return error.value
        }
      }
      if (
        lead.doc.mobile_no &&
        isNaN(lead.doc.mobile_no.replace(/[-+() ]/g, ''))
      ) {
        error.value = __('Mobile No should be a number')
        return error.value
      }
      if (lead.doc.email && !lead.doc.email.includes('@')) {
        error.value = __('Invalid Email')
        return error.value
      }
      if (!lead.doc.status) {
        error.value = __('Status is required')
        return error.value
      }
      isLeadCreating.value = true
    },
    async onSuccess(data) {
      // Store the created lead ID for task reference
      createdLeadId.value = data.name
      
      // If there's an assigned_to user, handle the assignment
      if (lead.doc.assigned_to && lead.doc.assigned_to !== user) {
        try {
          await call('frappe.desk.form.assign_to.add', {
            assign_to: [lead.doc.assigned_to],
            doctype: 'CRM Lead',
            name: data.name,
            description: `Lead assigned by ${user} during creation`
          })
        } catch (err) {
          console.error('Assignment failed:', err)
          // Continue even if assignment fails
        }
      }
      
      // If there's a pending task, create it now with the lead reference
      if (pendingTaskData.value) {
        try {
          const taskDoc = {
            ...pendingTaskData.value,
            reference_doctype: 'CRM Lead',
            reference_docname: data.name
          }
          
          // Create the task
          await call('frappe.client.insert', {
            doc: {
              doctype: 'CRM Task',
              ...taskDoc
            }
          })
          
          console.log(`Task "${taskDoc.title}" created successfully for ${getUser(taskDoc.assigned_to).full_name}`)
          pendingTaskData.value = null // Clear pending task
        } catch (err) {
          console.error('Failed to create pending task:', err)
          // Continue even if task creation fails
        }
      }
      
      capture('lead_created')
      isLeadCreating.value = false
      
      // Close modal and navigate to lead page
      show.value = false
      router.push({ name: 'Lead', params: { leadId: data.name } })
      
      updateOnboardingStep('create_first_lead', true, false, () => {
        localStorage.setItem('firstLead' + user, data.name)
      })
    },
    onError(err) {
      isLeadCreating.value = false
      if (!err.messages) {
        error.value = err.message
        return
      }
      error.value = err.messages.join('\n')
    },
  })
}

function openQuickEntryModal() {
  showQuickEntryModal.value = true
  quickEntryProps.value = { doctype: 'CRM Lead' }
  nextTick(() => (show.value = false))
}

// Watch for TaskModal closing to restore LeadModal
watch(showTaskModal, (newValue) => {
  if (!newValue && leadModalHidden.value) {
    // TaskModal was closed, restore the lead modal
    leadModalHidden.value = false
  }
})

onMounted(() => {
  // Set default lead owner if not provided
  if (!lead.doc?.lead_owner) {
    lead.doc.lead_owner = getUser().name
  }

  // Set default status if not provided
  if (!lead.doc?.status && leadStatuses.value[0]?.value) {
    lead.doc.status = leadStatuses.value[0].value
  }
})
</script>
