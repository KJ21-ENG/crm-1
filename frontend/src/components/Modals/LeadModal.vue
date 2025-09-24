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
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Lead Form (Left Side) -->
          <div class="lg:col-span-2">
            <FieldLayout v-if="tabs.data" :tabs="tabs.data" v-model="lead.doc" :doctype="'CRM Lead'" />

            <!-- Assign Task Button Section -->
            <div class="mt-4 flex items-center gap-3 rounded-lg border border-ink-gray-4 bg-ink-gray-1 p-3">
              <div class="flex-1">
                <p class="text-sm font-medium text-ink-gray-9">
                  {{ lead.doc.assign_to_role ? 
                    __('Lead will be assigned to a user from "{0}" role', [lead.doc.assign_to_role]) :
                    __('Task assignment is optional')
                  }}
                </p>
                <p class="text-xs text-ink-gray-7" v-if="lead.doc.assign_to_role && !pendingTaskData">
                  {{ __('Task assignment is required when assigning by role') }}
                </p>
                <p class="text-xs text-green-600" v-else>
                  {{ __('Task "{0}" will be created when lead is saved', [pendingTaskData?.title || 'Task']) }}
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

          <!-- Customer History (Right Side) -->
          <div class="lg:col-span-1">
            <div class="sticky top-4">
              <div class="rounded-lg border bg-white p-4">
                <h4 class="mb-4 text-lg font-semibold text-ink-gray-9">
                  {{ __('Customer History') }}
                </h4>

                <!-- Show message when no contact info -->
                <div v-if="!customerSearchKey" class="text-center py-6">
                  <div class="text-ink-gray-6 text-sm">
                    {{ __('Enter mobile number or email to see customer history') }}
                  </div>
                </div>

                <!-- Loading state -->
                <div v-else-if="customerHistory.loading" class="text-center py-6">
                  <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900 mx-auto mb-2"></div>
                  <div class="text-sm text-ink-gray-6">{{ __('Loading history...') }}</div>
                </div>

                <!-- Customer History Results -->
                <div v-else-if="customerHistory.data" class="space-y-4">
                  <!-- Existing Tickets -->
                  <div v-if="customerHistory.data.tickets?.length">
                    <h5 class="font-medium text-ink-gray-8 mb-2 flex items-center gap-2">
                      <TicketIcon class="h-4 w-4" />
                      {{ __('Existing Tickets') }} ({{ customerHistory.data.tickets.length }})
                    </h5>
                    <div class="space-y-2 max-h-40 overflow-y-auto">
                      <div
                        v-for="existingTicket in customerHistory.data.tickets"
                        :key="existingTicket.name"
                        class="p-3 rounded border bg-orange-50 hover:bg-orange-100 transition-colors cursor-pointer"
                        @click="router.push({ name: 'Ticket', params: { ticketId: existingTicket.name } })"
                      >
                        <div class="text-xs text-ink-gray-6">
                          <Badge 
                            :label="existingTicket.status" 
                            :theme="getStatusColor(existingTicket.status)"
                            variant="subtle"
                            class="mr-2"
                          />
                          {{ formatDate(existingTicket.creation, 'DD/MM/YYYY') }}
                        </div>
                        <div class="text-[13px] text-ink-gray-8 mt-1 leading-5">
                          <div>
                            <strong>ID :-</strong>
                            <span class="ml-1">{{ existingTicket.name }}</span>
                          </div>
                          <div>
                            <strong>Description :-</strong>
                            <span class="ml-1">{{ existingTicket.description || existingTicket.subject || existingTicket.ticket_subject || '-' }}</span>
                          </div>
                        </div>
                        <div v-if="existingTicket.status !== 'Closed'" class="text-xs text-orange-600 mt-1">
                          ⚠️ {{ __('Open ticket exists') }}
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Existing Leads -->
                  <div v-if="customerHistory.data.leads?.length">
                    <h5 class="font-medium text-ink-gray-8 mb-2 flex items-center gap-2">
                      <LeadsIcon class="h-4 w-4" />
                      {{ __('Existing Leads') }} ({{ customerHistory.data.leads.length }})
                    </h5>
                    <div class="space-y-2 max-h-40 overflow-y-auto">
                      <div
                        v-for="existingLead in customerHistory.data.leads"
                        :key="existingLead.name"
                        class="p-3 rounded border bg-blue-50 hover:bg-blue-100 transition-colors cursor-pointer"
                        @click="router.push({ name: 'Lead', params: { leadId: existingLead.name } })"
                      >
                        <div class="text-xs text-ink-gray-6">
                          <Badge 
                            :label="existingLead.status" 
                            :theme="getStatusColor(existingLead.status)"
                            variant="subtle"
                            class="mr-2"
                          />
                          {{ formatDate(existingLead.creation, 'DD/MM/YYYY') }}
                        </div>
                        <div class="text-[13px] text-ink-gray-8 mt-1 leading-5">
                          <div>
                            <strong>ID :-</strong>
                            <span class="ml-1">{{ existingLead.name }}</span>
                          </div>
                          <div>
                            <strong>Description :-</strong>
                            <span class="ml-1">{{ existingLead.description || existingLead.lead_name || '-' }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Referral History -->
                  <div v-if="referralHistory.data?.length">
                    <h5 class="font-medium text-ink-gray-8 mb-2 flex items-center gap-2">
                      <CustomersIcon class="h-4 w-4" />
                      {{ __('Referral History') }} ({{ referralHistory.data.length }})
                    </h5>
                    <div class="space-y-2 max-h-40 overflow-y-auto">
                      <div
                        v-for="referral in referralHistory.data"
                        :key="referral.lead_id"
                        class="p-3 rounded border bg-green-50 hover:bg-green-100 transition-colors cursor-pointer"
                        @click="router.push({ name: 'Lead', params: { leadId: referral.lead_id } })"
                      >
                        <div class="font-medium text-sm text-ink-gray-9">
                          {{ referral.lead_name }}
                        </div>
                        <div class="text-xs text-ink-gray-6 mt-1">
                          <Badge 
                            :label="referral.status" 
                            :theme="getStatusColor(referral.status)"
                            variant="subtle"
                            class="mr-2"
                          />
                          {{ formatDate(referral.creation, 'DD/MM/YYYY') }}
                        </div>
                        <div class="text-xs text-ink-gray-6 mt-1 flex items-center gap-2">
                          <Badge 
                            :label="referral.account_type || 'N/A'" 
                            theme="blue"
                            variant="subtle"
                            class="text-xs"
                          />
                          <span class="text-green-600">
                            🎯 {{ __('Referred using:') }} {{ referral.referral_through }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Warning for open tickets -->
                  <div v-if="hasOpenTickets" class="p-3 bg-yellow-50 border border-yellow-200 rounded">
                    <div class="flex items-center gap-2 text-yellow-700">
                      <FeatherIcon name="alert-triangle" class="h-4 w-4" />
                      <span class="font-medium text-sm">{{ __('Warning') }}</span>
                    </div>
                    <div class="text-xs text-yellow-600 mt-1">
                      {{ __('Customer has open tickets. Consider updating existing ticket instead of creating new one.') }}
                    </div>
                  </div>

                  <!-- No history found -->
                  <div v-if="!customerHistory.data.tickets?.length && !customerHistory.data.leads?.length && !referralHistory.data?.length" class="text-center py-4">
                    <div class="text-ink-gray-6 text-sm">
                      {{ __('No previous tickets, leads, or referrals found for this customer') }}
                    </div>
                    <div class="text-ink-gray-5 text-xs mt-1">
                      {{ __('This appears to be a new customer') }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
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
import { formatDate } from '@/utils'
import { useRouter } from 'vue-router'
import TicketIcon from '@/components/Icons/TaskIcon.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import CustomersIcon from '@/components/Icons/CustomersIcon.vue'
import { Badge, Button, Dialog, toast, FeatherIcon } from 'frappe-ui'

const props = defineProps({
  defaults: Object,
})

const { user } = sessionStore()
const { getUser, isManager, isAdmin } = usersStore()
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
  status: 'Todo',
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
    lead_category: 'Direct', // Set default lead category (Direct/Indirect)
    lead_source: 'On Call', // Default value for lead source
    account_type: 'Individual', // Set default account type
    no_of_employees: '1-10',
    status: '',
    assign_to_role: '', // New field for role-based assignment
    referral_through: '', // Client ID used during lead creation
    // client_id removed from Quick Entry defaults - field is managed server-side
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
  
  // Set default account type
  setDefaultAccountType()
})
// Customer search key for history lookup
const customerSearchKey = computed(() => {
  return lead.doc?.mobile_no || lead.doc?.email
})

// Check if customer has open tickets
const hasOpenTickets = computed(() => {
  return customerHistory.data?.tickets?.some(t => 
    ['New', 'Open', 'In Progress', 'Pending Customer'].includes(t.status)
  ) || false
})

// Customer history resource (reuse API from Ticket)
const customerHistory = createResource({
  url: 'crm.api.ticket.get_customer_history',
  makeParams() {
    // Prefer matching by customer_id if available
    const customerId = lead.doc?.customer_id
    if (customerId) return { customer_id: customerId }
    const mobile = lead.doc?.mobile_no
    const email = lead.doc?.email
    if (!mobile && !email) return null
    return { mobile_no: mobile, email: email }
  },
  auto: false,
})

// 🆕 Referral history resource
const referralHistory = createResource({
  url: 'crm.api.referral_analytics.get_referral_details',
  makeParams() {
    const customerId = lead.doc?.customer_id
    if (customerId) {
      // Get customer's referral codes from accounts
      return { customer_id: customerId }
    }
    return null
  },
  auto: false,
})

// Watch for contact changes
watch([() => lead.doc?.mobile_no, () => lead.doc?.email], ([mobile, email]) => {
  if (mobile || email) {
    customerHistory.reload()
    // Also reload referral history when customer changes
    referralHistory.reload()
  }
}, { immediate: false })

function getStatusColor(status) {
  const colors = {
    New: 'blue',
    Open: 'orange',
    'In Progress': 'yellow',
    'Pending Customer': 'purple',
    Resolved: 'green',
    Closed: 'gray',
  }
  return colors[status] || 'gray'
}

// 🆕 AUTO-FILL: Watch for mobile number changes to trigger auto-fill
watch(() => lead.doc?.mobile_no, async (newMobile, oldMobile) => {
  // Only trigger if mobile number changed and is not empty
  if (newMobile !== oldMobile) {
    // Clear customer related fields to avoid stale data
    clearCustomerFields()
    // Also clear linked history context
    lead.doc.customer_id = ''
    referralHistory.clear?.()
    customerHistory.clear?.()
    if (newMobile && newMobile.length >= 10) {
      console.log('🔍 [LEAD AUTO-FILL] Mobile number changed, triggering auto-fill:', newMobile)
      await autoFillCustomerData(newMobile)
    }
  }
}, { immediate: false })

// 🆕 LEAD CATEGORY: Watch for lead category changes to handle referral code validation
watch(() => lead.doc?.lead_category, (newLeadCategory, oldLeadCategory) => {
  if (newLeadCategory !== oldLeadCategory) {
    
    // Store the previous referral code when switching from Direct to Indirect
    if (oldLeadCategory === 'Direct' && newLeadCategory === 'Indirect') {
      // Store the current referral code temporarily
      lead.doc._previousReferralCode = lead.doc.referral_through
      // Clear the referral code
      lead.doc.referral_through = ''
    } else if (newLeadCategory === 'Direct') {
      // Restore previous referral code if available, otherwise get default
      if (lead.doc._previousReferralCode) {
        lead.doc.referral_through = lead.doc._previousReferralCode
        delete lead.doc._previousReferralCode
      } else {
        setDefaultReferralThrough()
      }
    }
  }
}, { immediate: false })

// Set default referral code from settings for Direct leads
async function setDefaultReferralThrough() {
  if (lead.doc.lead_category === 'Direct' && !lead.doc.referral_through) {
    try {
      const defaultCode = await call('crm.api.referral_analytics.get_default_referral_code')
      if (defaultCode) {
        lead.doc.referral_through = defaultCode
      }
    } catch (error) {
      console.error('Error getting default referral code:', error)
    }
  }
}

// Set default account type
function setDefaultAccountType() {
  if (!lead.doc.account_type) {
    lead.doc.account_type = 'Individual'
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
      const originalReferralThrough = lead.doc.referral_through
      
      // Auto-fill form fields with customer data
      lead.doc.first_name = customerData.first_name || lead.doc.first_name
      lead.doc.last_name = customerData.last_name || lead.doc.last_name
      lead.doc.email = customerData.email || lead.doc.email
      lead.doc.organization = customerData.organization || lead.doc.organization
      lead.doc.pan_card_number = customerData.pan_card_number || lead.doc.pan_card_number
      lead.doc.aadhaar_card_number = customerData.aadhaar_card_number || lead.doc.aadhaar_card_number
      lead.doc.referral_through = customerData.referral_through || lead.doc.referral_through
      lead.doc.marital_status = customerData.marital_status || lead.doc.marital_status
      lead.doc.date_of_birth = customerData.date_of_birth || lead.doc.date_of_birth
      lead.doc.anniversary = customerData.anniversary || lead.doc.anniversary
      // Set customer_id to link history immediately
      if (customerData.name) {
        lead.doc.customer_id = customerData.name
      }
      
      console.log('🔍 [LEAD AUTO-FILL] Field updates:')
      console.log('  first_name:', originalFirstName, '->', lead.doc.first_name)
      console.log('  last_name:', originalLastName, '->', lead.doc.last_name)
      console.log('  email:', originalEmail, '->', lead.doc.email)
      console.log('  organization:', originalOrganization, '->', lead.doc.organization)
      console.log('  pan_card_number:', originalPAN, '->', lead.doc.pan_card_number)
      console.log('  aadhaar_card_number:', originalAadhaar, '->', lead.doc.aadhaar_card_number)
      console.log('  referral_through:', originalReferralThrough, '->', lead.doc.referral_through)
      console.log('  marital_status:', lead.doc.marital_status)
      console.log('  date_of_birth:', lead.doc.date_of_birth)
      console.log('  anniversary:', lead.doc.anniversary)
      
      console.log('✅ [LEAD AUTO-FILL] Lead form auto-filled successfully')
      console.log('🔍 [LEAD AUTO-FILL] Final lead.doc:', JSON.stringify(lead.doc, null, 2))
      // Refresh customer history using customer_id for accuracy
      customerHistory.reload()
      // Also reload referral history after auto-fill
      referralHistory.reload()
    } else {
      console.log('ℹ️ [LEAD AUTO-FILL] No existing customer found for mobile:', mobileNumber)
      // Ensure histories are cleared for non-existing numbers
      lead.doc.customer_id = ''
      referralHistory.clear?.()
      customerHistory.clear?.()
    }
  } catch (error) {
    console.error('❌ [LEAD AUTO-FILL] Error looking up customer data:', error)
    console.error('❌ [LEAD AUTO-FILL] Error details:', error.message, error.stack)
  }
}

// Clear customer-related fields when mobile changes to a non-existing customer
function clearCustomerFields() {
  const fieldsToClear = [
    'first_name',
    'last_name',
    'email',
    'organization',
    'pan_card_number',
    'aadhaar_card_number',
    'referral_through',
    'marital_status',
    'date_of_birth',
    'anniversary'
  ]
  fieldsToClear.forEach((key) => {
    if (Object.prototype.hasOwnProperty.call(lead.doc, key)) {
      lead.doc[key] = ''
    }
  })
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
  // Pre-fill task data - assigned_to will be set when lead is created
  taskData.value = {
    title: `Follow up on lead: ${lead.doc.first_name || 'New Lead'}`,
    description: lead.doc.assign_to_role ? 
      `Task created for lead assignment to ${lead.doc.assign_to_role} role - ${lead.doc.first_name} ${lead.doc.last_name || ''}`.trim() :
      `Task created for lead follow-up - ${lead.doc.first_name} ${lead.doc.last_name || ''}`.trim(),
    assigned_to: '', // Will be set when lead is created
    role_for_assignment: lead.doc.assign_to_role || '', // Store role for later assignment (empty if no role)
    due_date: '',
    status: 'Todo',
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
    status: 'Todo',
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
      // Align Contact Information like Ticket: keep First, Last, Mobile in main section (3 cols)
      // and move remaining contact fields to a collapsible 3-column expander
      const contactSectionIndex = (tab.sections || []).findIndex(
        (s) => (s.label || '').toLowerCase() === 'contact information'
      )
      if (contactSectionIndex !== -1) {
        const contactSection = tab.sections[contactSectionIndex]
        const keepFieldnames = ['first_name', 'last_name', 'mobile_no']

        // Gather all fields from all columns
        const allFields = []
        ;(contactSection.columns || []).forEach((col) => {
          ;(col.fields || []).forEach((f) => allFields.push(f))
        })

        const keptFields = allFields.filter((f) => keepFieldnames.includes(f.fieldname))
        const additionalFields = allFields.filter((f) => !keepFieldnames.includes(f.fieldname))

        // Rebuild main contact section into three columns
        const colNames = [
          contactSection.columns?.[0]?.name || 'column_contact_primary_a',
          contactSection.columns?.[1]?.name || 'column_contact_primary_b',
          contactSection.columns?.[2]?.name || 'column_contact_primary_c',
        ]
        const keptByName = (name) => keptFields.find((f) => f.fieldname === name)
        contactSection.columns = [
          { name: colNames[0], fields: [keptByName('first_name')].filter(Boolean) },
          { name: colNames[1], fields: [keptByName('last_name')].filter(Boolean) },
          { name: colNames[2], fields: [keptByName('mobile_no')].filter(Boolean) },
        ]

        // Additional fields into 3-column collapsible section
        if (additionalFields.length) {
          const colA = { name: 'column_additional_contact_a', fields: [] }
          const colB = { name: 'column_additional_contact_b', fields: [] }
          const colC = { name: 'column_additional_contact_c', fields: [] }
          additionalFields.forEach((f, i) => {
            if (i % 3 === 0) colA.fields.push(f)
            else if (i % 3 === 1) colB.fields.push(f)
            else colC.fields.push(f)
          })
          const additionalSection = {
            name: 'additional_contact_info',
            label: 'Additional Contact Information',
            collapsible: true,
            opened: false,
            hideBorder: true,
            columns: [colA, colB, colC],
          }
          tab.sections.splice(contactSectionIndex + 1, 0, additionalSection)
        }
      }

      tab.sections.forEach((section) => {
        section.columns.forEach((column) => {
          column.fields.forEach((field, fieldIndex) => {
            // Ensure customer info fields are editable in Quick Entry
            if (['first_name', 'last_name', 'email', 'mobile_no', 'pan_card_number', 'aadhaar_card_number', 'phone'].includes(field.fieldname)) {
              field.read_only = 0
            }
            // Mark mandatory fields to show asterisk in UI
            if (['first_name', 'mobile_no'].includes(field.fieldname)) {
              field.reqd = 1
            }
            if (field.fieldname == 'status') {
              field.fieldtype = 'Select'
              field.options = leadStatuses.value
              field.prefix = getLeadStatus(lead.doc.status).color
            }
            
            // Configure contact information fields
            if (field.fieldname == 'mobile_no') {
              field.fieldtype = 'Data'
              field.label = 'Mobile No'
              field.maxlength = 10
              field.description = ''
              field.placeholder = 'Mobile No'
              field.read_only = 0
              // Add change handler to trigger auto-fill and validation
              field.onChange = () => {
                // Auto-fill will be triggered by the watcher above
                console.log('🔍 [LEAD] Mobile number field changed:', lead.doc.mobile_no)
              }
              // Add input handler to restrict to numbers only
              field.onInput = (event) => {
                // Remove non-numeric characters
                const value = event.target.value.replace(/[^0-9]/g, '')
                // Limit to 10 digits
                if (value.length > 10) {
                  event.target.value = value.substring(0, 10)
                  lead.doc.mobile_no = value.substring(0, 10)
                } else {
                  lead.doc.mobile_no = value
                }
              }
            }

            // Configure lead_category field
            if (field.fieldname == 'lead_category') {
              field.fieldtype = 'Select'
              field.options = 'Direct\nIndirect'
              field.default = 'Direct'
              field.description = ''
            }

            // Configure referral_through field based on lead_category
            if (field.fieldname == 'referral_through') {
              field.fieldtype = 'Data'
              field.label = 'Referral Through'
              field.placeholder = 'Referral Through'
              // Use mandatory_depends_on for dynamic required field
              field.mandatory_depends_on = "eval:doc.lead_category=='Direct'"
              // Use depends_on for dynamic description
              field.depends_on = "eval:doc.lead_category"
              field.description = ''
              field.read_only = 0
            }

            // Remove helper descriptions for identity fields
            if (field.fieldname == 'pan_card_number') {
              field.description = ''
              field.placeholder = 'PAN Card Number'
            }
            if (field.fieldname == 'aadhaar_card_number') {
              field.description = ''
              field.placeholder = 'Aadhaar Card Number'
            }
            
            // Configure account_type field
            if (field.fieldname == 'account_type') {
              // Switch to Link with creatable dropdown, like Ticket Subject
              field.fieldtype = 'Link'
              field.label = 'Account Type'
              field.options = 'CRM Account Type'
              field.mandatory = 1
              field.description = ''
            }
            
            // Make Lead Owner editable only for admin
            if (field.fieldname == 'lead_owner') {
              if (!isAdmin()) {
                field.read_only = 1
                field.description = ''
              }
            }

            // Remove client_id from Quick Entry: hide it
            if (field.fieldname == 'client_id') {
              field.visible = 0
              field.read_only = 1
              field.description = ''
            }
            


            // Add custom assign_to_role field for role-based assignments
            // Place `assign_to_role` immediately after the `status` field for uniform layout
            if (field.fieldname == 'status') {
              const assignToRoleField = {
                fieldname: 'assign_to_role',
                fieldtype: 'Select',
                label: 'Assign To Role',
                options: [
                  { label: '', value: '' },
                  { label: 'Sales User', value: 'Sales User' },
                  { label: 'Sales Manager', value: 'Sales Manager' },
                  { label: 'Support User', value: 'Support User' },
                  { label: 'Support Manager', value: 'Support Manager' }
                ]
              }

              // Insert assign_to_role after the status field in the same column
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
    async validate() {
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
      if (lead.doc.mobile_no) {
        // Remove all non-numeric characters
        const cleanMobile = lead.doc.mobile_no.replace(/[^0-9]/g, '')
        
        // Check if it's a valid number
        if (isNaN(cleanMobile) || cleanMobile.length === 0) {
          error.value = __('Mobile No should contain only numbers')
          return error.value
        }
        
        // Check if it's exactly 10 digits
        if (cleanMobile.length !== 10) {
          error.value = __('Mobile No should be exactly 10 digits')
          return error.value
        }
        
        // Update the mobile number to clean format
        lead.doc.mobile_no = cleanMobile
      }
      if (lead.doc.email && !lead.doc.email.includes('@')) {
        error.value = __('Invalid Email')
        return error.value
      }
      if (!lead.doc.status) {
        error.value = __('Status is required')
        return error.value
      }
      
      // Require task assignment only if a role is selected
      if (lead.doc.assign_to_role && !pendingTaskData.value) {
        error.value = __('Task assignment is required when assigning by role')
        return error.value
      }
      
      // Validate task has required fields
      if (pendingTaskData.value) {
        if (!pendingTaskData.value.title || !pendingTaskData.value.due_date) {
          error.value = __('Task title and due date are required')
          return error.value
        }
      }
      
      // Conditional validation for referral through based on lead category
      if (lead.doc.lead_category === 'Direct' && !lead.doc.referral_through) {
        error.value = __('Referral Through (Client ID) is mandatory for Direct leads')
        return error.value
      }
      
      // Validate self-referral (same mobile number using their own Client ID)
      if (lead.doc.referral_through && lead.doc.mobile_no) {
        try {
          const customers = await call('frappe.client.get_list', {
            doctype: 'CRM Customer',
            filters: {
              mobile_no: lead.doc.mobile_no
            },
            fields: ['name', 'accounts']
          })
          
          for (const customer of customers) {
            if (customer.accounts) {
              try {
                const accounts = JSON.parse(customer.accounts)
                const selfReferral = accounts.some(acc => acc.client_id === lead.doc.referral_through)
                if (selfReferral) {
                  error.value = __('Self-referral is not allowed. You cannot use your own Client ID as a referral code.')
                  return error.value
                }
              } catch (e) {
                // Skip if accounts is invalid JSON
              }
            }
          }
        } catch (err) {
          console.error('Error checking self-referral:', err)
          // Continue if validation fails
        }
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
            assigned_by: null, // Will use current user
            skip_task_creation: pendingTaskData.value != null // Skip task creation if we have a pending task
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
      } else {
        // If no role selected, set default role for auto-reassignment functionality
        try {
          await call('frappe.client.set_value', {
            doctype: 'CRM Lead',
            name: data.name,
            fieldname: 'assigned_role',
            value: 'Sales User'
          })
          console.log('Set default assigned_role to "Sales User" for auto-reassignment')
        } catch (err) {
          console.error('Failed to set default assigned_role:', err)
        }
      }
      
      // ✅ FIX: Only create task if pending task exists and doesn't have a real task ID
      // This prevents duplicate creation if TaskModal already created a task
      if (pendingTaskData.value && (!pendingTaskData.value.name || pendingTaskData.value.name === null)) {
        try {
          // Determine the correct assignee for the task (match Ticket behavior):
          // 1) If role-based assignment returned a user, use that
          // 2) Else fallback to current user
          const assignedToForTask = assignedUser || user

          const taskDoc = {
            ...pendingTaskData.value,
            reference_doctype: 'CRM Lead',
            reference_docname: data.name,
            assigned_to: assignedToForTask,
          }
          
          // Clean auxiliary field if present
          if (taskDoc.role_for_assignment) delete taskDoc.role_for_assignment
          
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
      
      // Create or find customer for this lead
      try {
        await call('crm.api.customers.create_or_find_customer', {
          lead_name: data.name,
          mobile_no: lead.doc.mobile_no,
          customer_name: `${lead.doc.first_name} ${lead.doc.last_name}`.trim(),
          email: lead.doc.email
        })
        console.log('Customer created/found successfully for lead')
      } catch (err) {
        console.error('Failed to create/find customer:', err)
        // Continue even if customer creation fails
      }
      
      // If referral through is provided, update customer accounts when account is opened
      if (lead.doc.referral_through && lead.doc.lead_category === 'Direct') {
        try {
          await call('crm.api.referral_analytics.update_customer_accounts', {
            customer_name: data.name,
            client_id: lead.doc.referral_through,
            account_type: lead.doc.account_type || 'Individual'
          })
          console.log('Customer accounts updated successfully')
        } catch (err) {
          console.error('Failed to update customer accounts:', err)
          // Continue even if account update fails
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
  setDefaultAccountType()
  setDefaultReferralThrough()
})
</script>
