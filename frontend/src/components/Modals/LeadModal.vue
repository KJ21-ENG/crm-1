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
          <div v-if="lead.doc.assign_to_role" class="mt-4 flex items-center gap-3 rounded-lg border border-ink-gray-4 bg-ink-gray-1 p-3">
            <div class="flex-1">
              <p class="text-sm font-medium text-ink-gray-9">
                {{ __('Lead will be assigned to a user from "{0}" role', [lead.doc.assign_to_role]) }}
              </p>
              <p class="text-xs text-ink-gray-7" v-if="!pendingTaskData">
                {{ __('You can create a task that will be assigned along with the lead') }}
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
    :roleForAssignment="taskData.role_for_assignment || ''"
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
onMounted(async () => {
  // Initialize lead document with required properties
  lead.doc = {
    doctype: 'CRM Lead',
    name: '', // Required for Field.vue
    first_name: '',
    last_name: '',
    email: '',
    mobile_no: '',
    pan_card_number: '', // Identity document field
    aadhaar_card_number: '', // Identity document field
    lead_type: 'Sales', // Set default lead type (hidden field)
    lead_source: 'On Call', // Default value for lead source
    account_type: 'Individual', // Set default account type
    no_of_employees: '1-10',
    status: '',
    assign_to_role: '', // New field for role-based assignment
    referral_code: '', // Will be set from API
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

  // Auto-fill customer data if mobile number is provided
  const mobileNumber = lead.doc.mobile_no
  if (mobileNumber) {
    await autoFillCustomerData(mobileNumber)
  }
  
  // Set default referral code from settings
  await setDefaultReferralCode()
})

// 🆕 AUTO-FILL: Watch for mobile number changes to trigger auto-fill
watch(() => lead.doc?.mobile_no, async (newMobile, oldMobile) => {
  // Only trigger if mobile number changed and is not empty
  if (newMobile && newMobile !== oldMobile && newMobile.length >= 10) {
    console.log('🔍 [LEAD AUTO-FILL] Mobile number changed, triggering auto-fill:', newMobile)
    await autoFillCustomerData(newMobile)
  }
}, { immediate: false })

// Set default referral code from settings
async function setDefaultReferralCode() {
  try {
    console.log('🔍 [LEAD MODAL] Fetching default referral code from settings...')
    
    const response = await createResource({
      url: 'crm.api.settings.get_default_referral_code',
      params: {}
    }).fetch()
    
    console.log('🔍 [LEAD MODAL] Default referral code response:', response)
    
    if (response && response.success && response.default_referral_code) {
      lead.doc.referral_code = response.default_referral_code
      console.log('✅ [LEAD MODAL] Default referral code set:', response.default_referral_code)
    } else {
      console.log('ℹ️ [LEAD MODAL] No default referral code configured, using empty value')
      lead.doc.referral_code = ''
    }
  } catch (error) {
    console.error('❌ [LEAD MODAL] Error fetching default referral code:', error)
    // Don't throw error, just log it and continue with empty value
    lead.doc.referral_code = ''
  }
}

// Auto-fill customer data from customer database
async function autoFillCustomerData(mobileNumber) {
  try {
    console.log('🔍 [LEAD AUTO-FILL] Looking up customer data for mobile:', mobileNumber)
    console.log('🔍 [LEAD AUTO-FILL] Current lead.doc before API call:', JSON.stringify(lead.doc, null, 2))
    
    const customerData = await createResource({
      url: 'crm.api.customers.get_customer_by_mobile',
      params: {
        mobile_no: mobileNumber
      }
    }).fetch()
    
    console.log('🔍 [LEAD AUTO-FILL] API Response:', customerData)
    console.log('🔍 [LEAD AUTO-FILL] API Response type:', typeof customerData)
    
    if (customerData) {
      console.log('✅ [LEAD AUTO-FILL] Customer found! Data:', JSON.stringify(customerData, null, 2))
      
      // Store original values for comparison
      const originalFirstName = lead.doc.first_name
      const originalLastName = lead.doc.last_name
      const originalEmail = lead.doc.email
      const originalOrganization = lead.doc.organization
      const originalPAN = lead.doc.pan_card_number
      const originalAadhaar = lead.doc.aadhaar_card_number
      const originalReferralCode = lead.doc.referral_code
      
      // Auto-fill form fields with customer data
      lead.doc.first_name = customerData.first_name || lead.doc.first_name
      lead.doc.last_name = customerData.last_name || lead.doc.last_name
      lead.doc.email = customerData.email || lead.doc.email
      lead.doc.organization = customerData.organization || lead.doc.organization
      lead.doc.pan_card_number = customerData.pan_card_number || lead.doc.pan_card_number
      lead.doc.aadhaar_card_number = customerData.aadhaar_card_number || lead.doc.aadhaar_card_number
      lead.doc.referral_code = customerData.referral_code || lead.doc.referral_code
      
      console.log('🔍 [LEAD AUTO-FILL] Field updates:')
      console.log('  first_name:', originalFirstName, '->', lead.doc.first_name)
      console.log('  last_name:', originalLastName, '->', lead.doc.last_name)
      console.log('  email:', originalEmail, '->', lead.doc.email)
      console.log('  organization:', originalOrganization, '->', lead.doc.organization)
      console.log('  pan_card_number:', originalPAN, '->', lead.doc.pan_card_number)
      console.log('  aadhaar_card_number:', originalAadhaar, '->', lead.doc.aadhaar_card_number)
      console.log('  referral_code:', originalReferralCode, '->', lead.doc.referral_code)
      
      console.log('✅ [LEAD AUTO-FILL] Lead form auto-filled successfully')
      console.log('🔍 [LEAD AUTO-FILL] Final lead.doc:', JSON.stringify(lead.doc, null, 2))
    } else {
      console.log('ℹ️ [LEAD AUTO-FILL] No existing customer found for mobile:', mobileNumber)
    }
  } catch (error) {
    console.error('❌ [LEAD AUTO-FILL] Error looking up customer data:', error)
    console.error('❌ [LEAD AUTO-FILL] Error details:', error.message, error.stack)
  }
}

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
  
  // ✅ FIX: Check if this task was created from LeadModal (no reference_docname)
  // If it has a reference_docname, it's a legitimate task creation
  if (taskDoc.reference_docname && taskDoc.reference_docname !== '') {
    // This is a real task with proper reference - navigate to lead
    if (isNew) {
      console.log(`Task "${taskDoc.title}" created successfully for ${getUser(taskDoc.assigned_to).full_name}`)
    }
    router.push({ name: 'Lead', params: { leadId: taskDoc.reference_docname } })
    return
  }
  
  // ✅ FIX: If no reference_docname, this is a task created from LeadModal
  // Store it as pending task data instead of creating duplicate
  pendingTaskData.value = {
    title: taskDoc.title,
    description: taskDoc.description,
    assigned_to: taskDoc.assigned_to,
    due_date: taskDoc.due_date,
    status: taskDoc.status,
    priority: taskDoc.priority,
    reference_doctype: 'CRM Lead',
    reference_docname: '', // Will be set when lead is created
    isNew: true // Mark as new for proper handling
  }
  
  console.log('Task data stored, will be created after lead is saved')
}

// Function to open task modal from the assignment section
function openTaskModalForAssignment() {
  if (!lead.doc.assign_to_role) {
    error.value = __('Please select a role to assign before creating a task')
    return
  }
  
  // Pre-fill task data - assigned_to will be set when lead is created
  taskData.value = {
    title: `Follow up on lead: ${lead.doc.first_name || 'New Lead'}`,
    description: `Task created for lead assignment to ${lead.doc.assign_to_role} role - ${lead.doc.first_name} ${lead.doc.last_name || ''}`.trim(),
    assigned_to: '', // Will be set when lead is created with role assignment
    role_for_assignment: lead.doc.assign_to_role, // Store role for later assignment
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
            
            // Configure contact information fields
            if (field.fieldname == 'mobile_no') {
              field.fieldtype = 'Data'
              field.label = 'Mobile No'
              // Add change handler to trigger auto-fill
              field.onChange = () => {
                // Auto-fill will be triggered by the watcher above
                console.log('🔍 [LEAD] Mobile number field changed:', lead.doc.mobile_no)
              }
            }

            // Add custom assign_to_role field for role-based assignments
            if (field.fieldname == 'lead_owner') {
              // Insert assign_to_role field after lead_owner
              const assignToRoleField = {
                fieldname: 'assign_to_role',
                fieldtype: 'Select',
                label: 'Assign To Role',
                options: [
                  { label: '', value: '' },
                  { label: 'Sales User', value: 'Sales User' },
                  { label: 'Sales Manager', value: 'Sales Manager' },
                  { label: 'Support User', value: 'Support User' },
                  { label: 'CRM User', value: 'CRM User' },
                  { label: 'CRM Manager', value: 'CRM Manager' }
                ],
                description: 'Select role for automatic user assignment'
              }
              
              // Find the current field index and insert after it
              const currentFieldIndex = column.fields.indexOf(field)
              if (currentFieldIndex !== -1) {
                column.fields.splice(currentFieldIndex + 1, 0, assignToRoleField)
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
    
    // Handle role-based assignment: if assign_to_role is provided, store it
    if (values.assign_to_role) {
      doc.assigned_role = values.assign_to_role
      // Remove assign_to_role from the doc as it's not a real field
      delete doc.assign_to_role
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
      if (!lead.doc.referral_code) {
        error.value = __('Referral Code is mandatory')
        return error.value
      }
      isLeadCreating.value = true
    },
    async onSuccess(data) {
      // Store the created lead ID for task reference
      createdLeadId.value = data.name
      
      // Handle role-based assignment
      let assignedUser = null
      if (lead.doc.assign_to_role) {
        try {
          const assignmentResult = await call('crm.api.role_assignment.assign_to_role', {
            lead_name: data.name,
            role_name: lead.doc.assign_to_role,
            assigned_by: null // Will use current user
          })
          
          if (assignmentResult.success) {
            assignedUser = assignmentResult.assigned_user
            console.log(`Lead assigned to ${assignmentResult.assigned_user} (${lead.doc.assign_to_role} role)`)
            console.log('Assignment message:', assignmentResult.message)
            if (assignmentResult.task_created) {
              console.log('Task created:', assignmentResult.task_created)
            }
          } else {
            console.error('Role-based assignment failed:', assignmentResult.error)
          }
        } catch (err) {
          console.error('Role-based assignment failed:', err)
          // Continue even if assignment fails
        }
      }
      
      // ✅ FIX: Only create task if pending task exists and doesn't have a real task ID
      // This prevents duplicate creation if TaskModal already created a task
      if (pendingTaskData.value && (!pendingTaskData.value.name || pendingTaskData.value.name === null)) {
        try {
          const taskDoc = {
            ...pendingTaskData.value,
            reference_doctype: 'CRM Lead',
            reference_docname: data.name
          }
          
          // If task has role_for_assignment and we have an assigned user, use that user
          if (taskDoc.role_for_assignment && assignedUser) {
            taskDoc.assigned_to = assignedUser
            delete taskDoc.role_for_assignment
          }
          
          // Remove the name field if it's null (prevents insertion conflicts)
          delete taskDoc.name
          
          // Create the task
          const createdTask = await call('frappe.client.insert', {
            doc: {
              doctype: 'CRM Task',
              ...taskDoc
            }
          })
          
          console.log(`Task "${taskDoc.title}" created successfully for ${assignedUser ? getUser(assignedUser).full_name : 'assigned user'}`)
          pendingTaskData.value = null // Clear pending task
        } catch (err) {
          console.error('Failed to create pending task:', err)
          // Continue even if task creation fails
        }
      } else if (pendingTaskData.value && pendingTaskData.value.name) {
        // Task was already created by TaskModal, just update the reference
        console.log('Task already exists, updating reference_docname')
        try {
          await call('frappe.client.set_value', {
            doctype: 'CRM Task',
            name: pendingTaskData.value.name,
            fieldname: 'reference_docname',
            value: data.name
          })
          pendingTaskData.value = null // Clear pending task
        } catch (err) {
          console.error('Failed to update task reference:', err)
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
