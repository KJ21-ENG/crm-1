<template>
  <Dialog v-model="show" :options="{ size: '4xl' }" v-if="!ticketModalHidden">
    <template #body>
      <div class="bg-surface-modal px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
              {{ __('Create Ticket') }}
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
          <!-- Ticket Form (Left Side) -->
          <div class="lg:col-span-2">
          <FieldLayout 
            v-if="tabs.data" 
            :tabs="tabs.data" 
            v-model="ticket.doc" 
            :doctype="'CRM Ticket'"
          />
          
          <!-- Assign Task Button Section -->
          <div class="mt-4 flex items-center gap-3 rounded-lg border border-ink-gray-4 bg-ink-gray-1 p-3">
            <div class="flex-1">
              <p class="text-sm font-medium text-ink-gray-9">
                {{ ticket.doc.assign_to_role ? 
                  __('Ticket will be assigned to a user from "{0}" role', [ticket.doc.assign_to_role]) :
                  __('Task assignment is optional')
                }}
              </p>
              <p class="text-xs text-ink-gray-7" v-if="ticket.doc.assign_to_role && !pendingTaskData">
                {{ __('Task assignment is required when assigning by role') }}
              </p>
              <p class="text-xs text-green-600" v-else>
                {{ __('Task "{0}" will be created when ticket is saved', [pendingTaskData?.title || 'Task']) }}
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
          
          <ErrorMessage class="mt-4" v-if="showError" :message="__(error)" />
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
                        <div class="font-medium text-sm text-ink-gray-9">
                          {{ existingTicket.subject }}
                        </div>
                        <div class="text-xs text-ink-gray-6 mt-1">
                          <Badge 
                            :label="existingTicket.status" 
                            :theme="getStatusColor(existingTicket.status)"
                            variant="subtle"
                            class="mr-2"
                          />
                          {{ formatDate(existingTicket.creation) }}
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
                        <div class="font-medium text-sm text-ink-gray-9">
                          {{ existingLead.lead_name }}
                        </div>
                        <div class="text-xs text-ink-gray-6 mt-1">
                          <Badge 
                            :label="existingLead.status" 
                            :theme="getStatusColor(existingLead.status)"
                            variant="subtle"
                            class="mr-2"
                          />
                          {{ formatDate(existingLead.creation) }}
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Customer Contact Summary -->
                  <div v-if="customerHistory.data.summary" class="pt-4 border-t">
                    <h5 class="font-medium text-ink-gray-8 mb-2">{{ __('Customer Summary') }}</h5>
                    <div class="text-sm space-y-1">
                      <div><strong>Total Tickets:</strong> {{ customerHistory.data.summary.total_tickets }}</div>
                      <div><strong>Open Tickets:</strong> {{ customerHistory.data.summary.open_tickets }}</div>
                      <div><strong>Total Leads:</strong> {{ customerHistory.data.summary.total_leads }}</div>
                      <div v-if="customerHistory.data.summary.last_interaction">
                        <strong>Last Contact:</strong> {{ formatDate(customerHistory.data.summary.last_interaction) }}
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
                  <div v-if="!customerHistory.data.tickets?.length && !customerHistory.data.leads?.length" class="text-center py-4">
                    <div class="text-ink-gray-6 text-sm">
                      {{ __('No previous tickets or leads found for this customer') }}
                    </div>
                    <div class="text-ink-gray-5 text-xs mt-1">
                      {{ __('This appears to be a new customer') }}
                    </div>
                  </div>
                </div>

                <!-- WhatsApp Support Section -->
                <div v-if="ticket.doc.mobile_no" class="mt-4 border-t pt-4">
                  <div class="mb-4 flex items-center justify-between">
                    <h4 class="text-lg font-semibold text-ink-gray-9">
                      {{ __('Send WhatsApp Support') }}
                    </h4>
                    <div 
                      class="flex items-center gap-2 text-sm"
                      v-if="whatsappStatus"
                    >
                      <div 
                        class="h-2 w-2 rounded-full"
                        :class="whatsappStatus.connected ? 'bg-green-500' : 'bg-red-500'"
                      ></div>
                      <span class="text-gray-600">
                        {{ whatsappStatus.connected ? 'Connected' : 'Disconnected' }}
                      </span>
                    </div>
                  </div>

                  <!-- WhatsApp Setup Button -->
                  <div v-if="!whatsappStatus?.connected" class="mb-4">
                    <Button
                      variant="solid"
                      class="w-full"
                      @click="openWhatsAppSetup"
                    >
                      <template #prefix>
                        <FeatherIcon name="settings" class="h-4 w-4" />
                      </template>
                      {{ __('Setup WhatsApp') }}
                    </Button>
                  </div>

                  <!-- Support Pages Search -->
                  <div v-else class="flex flex-col gap-4">
                    <div>
                      <input
                        type="text"
                        v-model="searchQuery"
                        class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                        :placeholder="__('Search support pages...')"
                      />
                      <!-- Dropdown as part of normal flow -->
                      <div
                        v-if="filteredSupportPages.length > 0"
                        class="mt-1 max-h-48 overflow-y-auto rounded-lg border bg-white shadow-lg"
                      >
                        <div
                          v-for="page in filteredSupportPages"
                          :key="page.name"
                          class="flex cursor-pointer items-center justify-between px-3 py-2 hover:bg-gray-50"
                          @click="togglePageSelection(page)"
                        >
                          <div>
                            <div class="font-medium">{{ page.page_name }}</div>
                            <div class="text-sm text-gray-500">{{ page.description }}</div>
                          </div>
                          <div v-if="isPageSelected(page)">
                            <FeatherIcon name="check" class="h-4 w-4 text-green-500" />
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Selected Pages -->
                    <div class="space-y-2">
                      <div
                        v-for="page in selectedPages"
                        :key="page.name"
                        class="flex items-center justify-between rounded-lg border bg-gray-50 px-3 py-2"
                      >
                        <div>
                          <div class="font-medium">{{ page.page_name }}</div>
                          <div class="text-sm text-gray-500">{{ page.description }}</div>
                        </div>
                        <Button
                          variant="ghost"
                          class="text-gray-500"
                          @click="togglePageSelection(page)"
                        >
                          <FeatherIcon name="x" class="h-4 w-4" />
                        </Button>
                      </div>
                    </div>

                    <!-- Send Button -->
                    <Button
                      variant="solid"
                      class="w-full"
                      :disabled="!whatsappStatus.connected || sending || selectedPages.length === 0"
                      :loading="sending"
                      @click="sendSupportPages"
                    >
                      <template #prefix>
                        <FeatherIcon name="send" class="h-4 w-4" />
                      </template>
                      {{ selectedPages.length === 0 ? __('Select pages to send') : __('Send WhatsApp Message') }}
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="flex items-center justify-between">
          <!-- Issue Solved Checkbox -->
          <div class="flex items-center gap-2">
            <input
              type="checkbox"
              id="issueSolved"
              v-model="issueSolved"
              class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label for="issueSolved" class="text-sm text-ink-gray-7">
              {{ __('Issue Solved') }}
            </label>
          </div>
          
          <div class="flex flex-row-reverse gap-2">
            <Button
              variant="solid"
              :label="__('Create Ticket')"
              :loading="isTicketCreating"
              @click="createNewTicket"
            />

          </div>
        </div>
      </div>
    </template>
  </Dialog>
  <WhatsAppSetupModal 
    v-model="showWhatsAppSetupModal"
    @status-update="updateWhatsAppStatus"
  />
  
  <!-- Task Modal for creating tasks -->
  <TaskModal
    v-if="showTaskModal"
    v-model="showTaskModal"
    :task="taskData"
    doctype="CRM Ticket"
    :doc="createdTicketId || null"
    :roleForAssignment="taskData.role_for_assignment || ''"
    @after="handleTaskCreated"
  />
</template>

<script setup>
import EditIcon from '@/components/Icons/EditIcon.vue'
import TicketIcon from '@/components/Icons/TaskIcon.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import TaskModal from '@/components/Modals/TaskModal.vue'
import { usersStore } from '@/stores/users'
import { sessionStore } from '@/stores/session'
import { isMobileView } from '@/composables/settings'
import { showQuickEntryModal, quickEntryProps } from '@/composables/modals'
import { capture } from '@/telemetry'
import { formatDate } from '@/utils'
import { createResource, Badge, Button, Dialog, toast, FeatherIcon, call } from 'frappe-ui'
import { useDocument } from '@/data/document'
import { computed, onMounted, ref, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import WhatsAppSetupModal from '@/components/Modals/WhatsAppSetupModal.vue'
import { format } from 'date-fns' // Add this import if not already present

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  defaults: {
    type: Object,
    default: () => ({}),
  },
  callLog: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue', 'ticket-created'])

const { user } = sessionStore()
const { getUser, isManager, isAdmin } = usersStore()

const show = defineModel()
const router = useRouter()
const error = ref(null)
const isTicketCreating = ref(false)
const issueSolved = ref(false)  // Add issueSolved ref

// Task Modal state for role assignment
const showTaskModal = ref(false)
const createdTicketId = ref('')
const pendingTaskData = ref(null) // Store task data that was created before ticket
const ticketModalHidden = ref(false) // Track if ticket modal is temporarily hidden
const taskData = ref({
  title: '',
  description: '',
  assigned_to: '',
  due_date: '',
  status: 'Todo',
  priority: 'Medium',
  reference_doctype: 'CRM Ticket',
  reference_docname: '',
})

const { document: ticket, triggerOnChange } = useDocument('CRM Ticket')

// Customer search key for history lookup
const customerSearchKey = computed(() => {
  return ticket.doc?.mobile_no || ticket.doc?.email
})

// Check if customer has open tickets
const hasOpenTickets = computed(() => {
  return customerHistory.data?.tickets?.some(t => 
    ['New', 'Open', 'In Progress', 'Pending Customer'].includes(t.status)
  ) || false
})

// Customer history resource
const customerHistory = createResource({
  url: 'crm.api.ticket.get_customer_history',
  makeParams() {
    const customerId = ticket.doc?.customer_id
    if (customerId) return { customer_id: customerId }
    const mobile = ticket.doc?.mobile_no
    const email = ticket.doc?.email
    if (!mobile && !email) return null
    return { mobile_no: mobile, email: email }
  },
  auto: false,
})

// Watch for customer contact changes to fetch history
watch([() => ticket.doc?.mobile_no, () => ticket.doc?.email], ([mobile, email]) => {
  if (mobile || email) {
    customerHistory.reload()
  }
}, { immediate: false })

// 🆕 AUTO-FILL: Watch for mobile number changes to trigger auto-fill
watch(() => ticket.doc?.mobile_no, async (newMobile, oldMobile) => {
  // Only trigger if mobile number changed and is not empty
  if (newMobile && newMobile !== oldMobile && newMobile.length >= 10) {
    console.log('🔍 [AUTO-FILL] Mobile number changed, triggering auto-fill:', newMobile)
    await autoFillCustomerData(newMobile)
  }
}, { immediate: false })

// Initialize ticket with defaults
onMounted(async () => {
  // Initialize an empty doc first
  ticket.doc = {
    doctype: 'CRM Ticket',
    name: '', // Required for Field.vue
    first_name: '',
    last_name: '',
    email: '',
    mobile_no: '',
    pan_card_number: '', // Identity document field
    aadhaar_card_number: '', // Identity document field
    ticket_subject: '',
    subject: '',
    description: '',
    priority: 'Medium',
    status: 'New',
    department: 'Support',
    issue_type: 'Account',
    ticket_source: 'On Call', // New field for ticket source
    assign_to_role: '', // New field for role-based assignment
    ticket_owner: user,
    assigned_role: ''
  }

  // Then merge with defaults if provided
  if (props.defaults) {
    Object.assign(ticket.doc, props.defaults)
  }

  // If we have call log data, pre-fill the form
  if (props.callLog) {
    const customerNumber = props.callLog.type === 'Incoming' ? props.callLog.from : props.callLog.to
    Object.assign(ticket.doc, {
      mobile_no: customerNumber,
      ticket_subject: `Support request from call ${customerNumber}`,
      subject: `Support request from call ${customerNumber}`,
      description: `Customer called on ${props.callLog.start_time}`,
      ticket_source: 'On Call' // Set ticket source for call-based tickets
    })
  }

  // Auto-fill customer data if mobile number is provided
  const mobileNumber = ticket.doc.mobile_no
  if (mobileNumber) {
    await autoFillCustomerData(mobileNumber)
    
    // Fetch customer history
    nextTick(() => {
      customerHistory.reload()
    })
  }
})

// Auto-fill customer data from customer database
async function autoFillCustomerData(mobileNumber) {
  try {
    console.log('🔍 [AUTO-FILL] Looking up customer data for mobile:', mobileNumber)
    console.log('🔍 [AUTO-FILL] Current ticket.doc before API call:', JSON.stringify(ticket.doc, null, 2))
    
    const customerData = await createResource({
      url: 'crm.api.customers.get_customer_by_mobile',
      params: {
        mobile_no: mobileNumber
      }
    }).fetch()
    
    console.log('🔍 [AUTO-FILL] API Response:', customerData)
    console.log('🔍 [AUTO-FILL] API Response type:', typeof customerData)
    
    if (customerData) {
      console.log('✅ [AUTO-FILL] Customer found! Data:', JSON.stringify(customerData, null, 2))
      
      // Store original values for comparison
      const originalFirstName = ticket.doc.first_name
      const originalLastName = ticket.doc.last_name
      const originalEmail = ticket.doc.email
      const originalOrganization = ticket.doc.organization
      const originalPAN = ticket.doc.pan_card_number
      const originalAadhaar = ticket.doc.aadhaar_card_number
      const originalReferralCode = ticket.doc.referral_code
      
      // Auto-fill form fields with customer data
      ticket.doc.first_name = customerData.first_name || ticket.doc.first_name
      ticket.doc.last_name = customerData.last_name || ticket.doc.last_name
      ticket.doc.email = customerData.email || ticket.doc.email
      ticket.doc.organization = customerData.organization || ticket.doc.organization
      ticket.doc.pan_card_number = customerData.pan_card_number || ticket.doc.pan_card_number
      ticket.doc.aadhaar_card_number = customerData.aadhaar_card_number || ticket.doc.aadhaar_card_number
      ticket.doc.referral_code = customerData.referral_code || ticket.doc.referral_code
      if (customerData.name) {
        ticket.doc.customer_id = customerData.name
      }
      
      console.log('🔍 [AUTO-FILL] Field updates:')
      console.log('  first_name:', originalFirstName, '->', ticket.doc.first_name)
      console.log('  last_name:', originalLastName, '->', ticket.doc.last_name)
      console.log('  email:', originalEmail, '->', ticket.doc.email)
      console.log('  organization:', originalOrganization, '->', ticket.doc.organization)
      console.log('  pan_card_number:', originalPAN, '->', ticket.doc.pan_card_number)
      console.log('  aadhaar_card_number:', originalAadhaar, '->', ticket.doc.aadhaar_card_number)
      console.log('  referral_code:', originalReferralCode, '->', ticket.doc.referral_code)
      
      // Update ticket subject if it was generic
      if (!ticket.doc.ticket_subject || ticket.doc.ticket_subject.includes('call')) {
        const newSubject = `Support request from ${customerData.first_name || ''} ${customerData.last_name || ''}`.trim()
        console.log('🔍 [AUTO-FILL] Updating subject to:', newSubject)
        ticket.doc.ticket_subject = newSubject
        ticket.doc.subject = newSubject
      }
      
      console.log('✅ [AUTO-FILL] Form auto-filled successfully')
      console.log('🔍 [AUTO-FILL] Final ticket.doc:', JSON.stringify(ticket.doc, null, 2))
      customerHistory.reload()
    } else {
      console.log('ℹ️ [AUTO-FILL] No existing customer found for mobile:', mobileNumber)
    }
  } catch (error) {
    console.error('❌ [AUTO-FILL] Error looking up customer data:', error)
    console.error('❌ [AUTO-FILL] Error details:', error.message, error.stack)
  }
}

// Task Modal Functions
function openTaskModalForAssignment() {
  // Pre-fill task data - assigned_to will be set when ticket is created
  taskData.value = {
    title: `Handle ticket: ${ticket.doc.subject || 'New Ticket'}`,
    description: ticket.doc.assign_to_role ? 
      `Task created for ticket assignment to ${ticket.doc.assign_to_role} role - ${ticket.doc.subject || ''}`.trim() :
      `Task created for ticket handling - ${ticket.doc.subject || ''}`.trim(),
    assigned_to: '', // Will be set when ticket is created
    role_for_assignment: ticket.doc.assign_to_role || '', // Store role for later assignment (empty if no role)
    due_date: '',
    status: 'Todo',
    priority: ticket.doc.priority || 'Medium',
    reference_doctype: 'CRM Ticket',
    reference_docname: '', // Will be empty until ticket is created
  }
  
  // Temporarily hide ticket modal to prevent conflicts
  ticketModalHidden.value = true
  
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
    reference_docname: '', // Will be empty until ticket is created
  }
  
  // Temporarily hide ticket modal to prevent conflicts
  ticketModalHidden.value = true
  
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
    reference_doctype: 'CRM Ticket',
    reference_docname: '',
  }
  
  console.log('Task assignment cleared')
}

// Handle task modal events
function handleTaskCreated(task) {
  console.log('Task created from modal:', task)
  
  // Store the task data for later association with the ticket
  pendingTaskData.value = task
  
  // Restore ticket modal visibility
  ticketModalHidden.value = false
  showTaskModal.value = false
  
  console.log('Task pending for ticket creation:', pendingTaskData.value)
}

const tabs = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['QuickEntry', 'CRM Ticket'],
  params: { doctype: 'CRM Ticket', type: 'Quick Entry' },
  auto: true,
  transform: (_tabs) => {
    _tabs.forEach((tab) => {
      tab.sections.forEach((section) => {
        section.columns.forEach((column) => {
          column.fields.forEach((field) => {
            // Ensure customer info fields are editable in Quick Entry (override read_only)
            if (
              ['first_name', 'last_name', 'email', 'mobile_no', 'phone', 'organization', 'pan_card_number', 'aadhaar_card_number']
                .includes(field.fieldname)
            ) {
              field.read_only = 0
            }
            // Configure specific field types
            if (field.fieldname == 'status') {
              field.fieldtype = 'Link'
              field.options = 'CRM Ticket Status'
            }

            if (field.fieldname == 'priority') {
              field.fieldtype = 'Select'
              field.options = [
                { label: 'Low', value: 'Low' },
                { label: 'Medium', value: 'Medium' },
                { label: 'High', value: 'High' },
                { label: 'Urgent', value: 'Urgent' }
              ]
            }

            if (field.fieldname == 'issue_type') {
              field.fieldtype = 'Select'
              field.options = [
                { label: 'Technical', value: 'Technical' },
                { label: 'Billing', value: 'Billing' },
                { label: 'Account', value: 'Account' },
                { label: 'General', value: 'General' },
                { label: 'Complaint', value: 'Complaint' }
              ]
            }

            if (field.fieldname == 'department') {
              field.fieldtype = 'Select'
              field.options = [
                { label: 'Support', value: 'Support' },
                { label: 'Technical', value: 'Technical' },
                { label: 'Billing', value: 'Billing' },
                { label: 'General', value: 'General' }
              ]
            }
            
            // Add custom assign_to_role field for role-based assignments
            if (field.fieldname == 'ticket_owner') {
              // Insert assign_to_role field after ticket_owner
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

              // Make Ticket Owner editable only for admin
              if (!isAdmin()) {
                field.read_only = 1
                field.description = 'Only Administrator can change Ticket Owner'
              }
            }

            // Configure contact information fields
            if (field.fieldname == 'mobile_no') {
              field.fieldtype = 'Data'
              field.label = 'Mobile No'
              field.maxlength = 10
              field.description = 'Enter 10-digit mobile number only'
              // Add change handler to trigger customer history lookup and auto-fill
              field.onChange = () => {
                if (ticket.doc.mobile_no) {
                  customerHistory.reload()
                  // Auto-fill will be triggered by the watcher above
                }
              }
              // Add input handler to restrict to numbers only
              field.onInput = (event) => {
                // Remove non-numeric characters
                const value = event.target.value.replace(/[^0-9]/g, '')
                // Limit to 10 digits
                if (value.length > 10) {
                  event.target.value = value.substring(0, 10)
                  ticket.doc.mobile_no = value.substring(0, 10)
                } else {
                  ticket.doc.mobile_no = value
                }
              }
            }

            if (field.fieldname == 'email') {
              field.fieldtype = 'Data'
              field.label = 'Email'
              // Add change handler to trigger customer history lookup
              field.onChange = () => {
                if (ticket.doc.email) {
                  customerHistory.reload()
                }
            }
            }

            if (field.fieldtype === 'Table') {
              ticket.doc[field.fieldname] = []
            }
          })
        })
      })
    })
    return _tabs
  },
})

const createTicket = createResource({
  url: 'crm.api.ticket.create_ticket',
  makeParams(values) {
    // If we have a call log, include it in the request
    if (props.callLog) {
      return {
        doc: {
          ...ticket.doc,
          call_log: props.callLog.name,
          creation_source: 'Call Log'
        }
      }
    }
    
    // For direct ticket creation
    return {
      doc: {
        ...ticket.doc,
        creation_source: 'Manual Entry'
      }
    }
  },
})

async function createNewTicket() {
  try {
    isTicketCreating.value = true
    error.value = null

    // Validate required fields
    const validation = validateFields()
    if (!validation.isValid) {
      error.value = validation.error
      isTicketCreating.value = false
      return
    }

    // If issue is solved, set status to Closed
    if (issueSolved.value) {
      ticket.doc.status = 'Closed'
      ticket.doc.resolved = 1
      ticket.doc.resolved_on = format(new Date(), 'yyyy-MM-dd HH:mm:ss')
      ticket.doc.resolution_time = 0 // Since it was resolved immediately
      ticket.doc.resolution_details = 'Ticket closed at creation as issue was already resolved.'
    }

    // Create ticket
    const response = await createTicket.submit(ticket.doc)

    if (response) {
      // Store the created ticket ID for task reference
      createdTicketId.value = response.name
      
      // Handle role-based assignment
      let assignedUser = null
      if (ticket.doc.assign_to_role) {
        try {
          const assignmentResult = await call('crm.api.ticket.assign_ticket_to_role', {
            ticket_name: response.name,
            role_name: ticket.doc.assign_to_role,
            assigned_by: null, // Will use current user
            skip_task_creation: pendingTaskData.value != null // Skip task creation if we have a pending task
          })
          
          if (assignmentResult.success) {
            assignedUser = assignmentResult.assigned_user
            console.log(`Ticket assigned to ${assignmentResult.assigned_user} (${ticket.doc.assign_to_role} role)`)
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
            doctype: 'CRM Ticket',
            name: response.name,
            fieldname: 'assigned_role',
            value: 'Support User'
          })
          console.log('Set default assigned_role to "Support User" for auto-reassignment')
        } catch (err) {
          console.error('Failed to set default assigned_role:', err)
        }
      }
      
      // Create task if pending task exists and doesn't have a real task ID
      if (pendingTaskData.value && (!pendingTaskData.value.name || pendingTaskData.value.name === null)) {
        try {
          const taskDoc = {
            ...pendingTaskData.value,
            reference_doctype: 'CRM Ticket',
            reference_docname: response.name
          }
          
          // If task has role_for_assignment and we have an assigned user, use that user
          if (taskDoc.role_for_assignment && assignedUser) {
            taskDoc.assigned_to = assignedUser
            delete taskDoc.role_for_assignment
          } else if (!taskDoc.role_for_assignment) {
            // If no role was selected, assign to current user
            taskDoc.assigned_to = user
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
            value: response.name
          })
          pendingTaskData.value = null // Clear pending task
        } catch (err) {
          console.error('Failed to update task reference:', err)
        }
      }
      
      show.value = false
      emit('ticket-created', response)
      emit('update:modelValue', false)
      
      // Navigate to ticket detail page
      router.push({ name: 'Ticket', params: { ticketId: response.name } })
      
      // Capture analytics
      capture('ticket_created', {
        source: props.callLog ? 'call_log' : 'manual',
        department: ticket.doc.department,
        priority: ticket.doc.priority,
        has_customer_history: !!(customerHistory.data?.tickets?.length || customerHistory.data?.leads?.length)
      })
    }
  } catch (e) {
    console.error('Error creating ticket:', e)
    error.value = e.messages?.[0] || 'Error creating ticket'
  } finally {
    isTicketCreating.value = false
  }
}

function validateFields() {
  const requiredFields = {
    first_name: 'First Name',
    ticket_subject: 'Subject',
    priority: 'Priority',
    issue_type: 'Issue Type',
    ticket_source: 'Ticket Source',
    status: 'Status'
  }
  
  for (const [field, label] of Object.entries(requiredFields)) {
    const value = ticket.doc[field]
    
    if (!value || value.trim() === '') {
      return {
        isValid: false,
        error: `${label} is required`
      }
    }
  }

  // Validate mobile number if provided
  if (ticket.doc.mobile_no) {
    // Remove all non-numeric characters
    const cleanMobile = ticket.doc.mobile_no.replace(/[^0-9]/g, '')
    
    // Check if it's a valid number
    if (isNaN(cleanMobile) || cleanMobile.length === 0) {
      return {
        isValid: false,
        error: 'Mobile No should contain only numbers'
      }
    }
    
    // Check if it's exactly 10 digits
    if (cleanMobile.length !== 10) {
      return {
        isValid: false,
        error: 'Mobile No should be exactly 10 digits'
      }
    }
    
    // Update the mobile number to clean format
    ticket.doc.mobile_no = cleanMobile
  }

  // Require task assignment only if a role is selected
  if (ticket.doc.assign_to_role && !pendingTaskData.value) {
    return {
      isValid: false,
      error: 'Task assignment is required when assigning by role'
    }
  }
  
  // Validate task has required fields
  if (pendingTaskData.value) {
    if (!pendingTaskData.value.title || !pendingTaskData.value.due_date) {
      return {
        isValid: false,
        error: 'Task title and due date are required'
      }
    }
  }

  return { isValid: true }
}

function getStatusColor(status) {
  const colors = {
    'New': 'blue',
    'Open': 'orange', 
    'In Progress': 'yellow',
    'Pending Customer': 'purple',
    'Resolved': 'green',
    'Closed': 'gray'
  }
  return colors[status] || 'gray'
}

function viewOpenTickets() {
  // Navigate to tickets list filtered by this customer
  const filters = {}
  if (ticket.doc.mobile_no) {
    filters.mobile_no = ticket.doc.mobile_no
  } else if (ticket.doc.email) {
    filters.email = ticket.doc.email
  }
  
  router.push({
    name: 'Tickets',
    query: { 
      filters: JSON.stringify(filters),
      status: 'Open'
    }
  })
  show.value = false
}

function openQuickEntryModal() {
  showQuickEntryModal.value = true
  quickEntryProps.value = { doctype: 'CRM Ticket' }
  nextTick(() => (show.value = false))
}

// WhatsApp Support functionality
const searchQuery = ref('')
const selectedPages = ref([])
const sending = ref(false)
const whatsappStatus = ref({
  connected: false,
  phoneNumber: null,
})

// Support pages resource
const supportPages = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Support Pages',
    fields: ['name', 'page_name', 'support_link', 'description'],
    filters: {
      is_active: 1,
    },
  },
  auto: true,
})

// Filtered support pages
const filteredSupportPages = computed(() => {
  if (!supportPages.data) return []
  
  if (!searchQuery.value.trim()) return []
  
  const query = searchQuery.value.toLowerCase().trim()
  return supportPages.data.filter(page => {
    return (
      page.page_name.toLowerCase().includes(query) ||
      page.description?.toLowerCase().includes(query) ||
      page.support_link.toLowerCase().includes(query)
    )
  })
})

// Generate message for sending
const generateMessage = () => {
  if (selectedPages.value.length === 0) return ''
  
  let message = "Hi! Here are some helpful support pages:\n\n"
  selectedPages.value.forEach(page => {
    message += `📋 *${page.page_name}*\n`
    if (page.description) {
      message += `${page.description}\n`
    }
    message += `🔗 ${page.support_link}\n\n`
  })
  
  return message.trim()
}

// Methods
const togglePageSelection = (page) => {
  const index = selectedPages.value.findIndex(p => p.name === page.name)
  if (index > -1) {
    selectedPages.value.splice(index, 1)
  } else {
    selectedPages.value.push(page)
  }
}

const isPageSelected = (page) => {
  return selectedPages.value.some(p => p.name === page.name)
}

const sendSupportPages = async () => {
  // If extension is connected we allow sending

  if (selectedPages.value.length === 0) {
    toast.error('Please select at least one support page')
    return
  }

  if (!ticket.doc.mobile_no) {
    toast.error('Please enter a mobile number')
    return
  }

  sending.value = true
  
  try {
    const message = generateMessage()
    
    // Send WhatsApp message via local service
    const response = await createResource({
      url: 'crm.api.whatsapp_setup.send_local_whatsapp_message',
      params: {
        to: ticket.doc.mobile_no,
        message: message,
      },
    }).fetch()

    if (response.success) {
      toast.success('Support pages sent successfully!')
      selectedPages.value = []
      searchQuery.value = ''
    } else {
      toast.error(response.message || 'Failed to send support pages')
    }
  } catch (error) {
    toast.error('Error sending support pages: ' + error.message)
  } finally {
    sending.value = false
  }
}

const checkWhatsAppStatus = async () => {
  try {
    const response = await createResource({
      url: 'crm.api.whatsapp_setup.get_local_whatsapp_status',
    }).fetch()

    whatsappStatus.value = {
      connected: response.connected || false,
      phoneNumber: response.phone_number || null,
    }
  } catch (error) {
    console.error('Error checking WhatsApp status:', error)
    whatsappStatus.value = {
      connected: false,
      phoneNumber: null,
    }
  }
}

// WhatsApp setup modal
const showWhatsAppSetupModal = ref(false)

const updateWhatsAppStatus = (status) => {
  whatsappStatus.value = status
}

const openWhatsAppSetup = () => {
  showWhatsAppSetupModal.value = true
}

// Check WhatsApp status on mount
onMounted(() => {
  checkWhatsAppStatus()
})

// Watch for modal opening to refresh WhatsApp status
watch(show, (isOpen) => {
  if (isOpen) {
    checkWhatsAppStatus()
  }
})

// Watch for TaskModal closing to restore TicketModal
watch(showTaskModal, (newValue) => {
  if (!newValue && ticketModalHidden.value) {
    // TaskModal was closed, restore the ticket modal
    ticketModalHidden.value = false
  }
})

const showError = computed(() => {
  if (!error.value) return false
  // Filter out unwanted or generic errors
  const unwanted = [
    'Error creating ticket',
    'An error occurred',
    'Unknown error',
    'Something went wrong',
    'Error',
    'Please enter a value',
    'Please enter a valid value',
  ]
  return !unwanted.includes(error.value.trim())
})
</script> 