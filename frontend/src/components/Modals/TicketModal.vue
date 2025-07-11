<template>
  <Dialog v-model="show" :options="{ size: '4xl' }">
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
                        <div class="font-medium text-sm text-ink-gray-9">
                          {{ existingTicket.ticket_subject }}
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
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="flex flex-row-reverse gap-2">
          <Button
            variant="solid"
            :label="__('Create Ticket')"
            :loading="isTicketCreating"
            @click="createNewTicket"
          />
          <Button
            v-if="hasOpenTickets"
            variant="outline"
            :label="__('View Open Tickets')"
            @click="viewOpenTickets"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import EditIcon from '@/components/Icons/EditIcon.vue'
import TicketIcon from '@/components/Icons/TaskIcon.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import { usersStore } from '@/stores/users'
import { sessionStore } from '@/stores/session'
import { isMobileView } from '@/composables/settings'
import { showQuickEntryModal, quickEntryProps } from '@/composables/modals'
import { capture } from '@/telemetry'
import { formatDate } from '@/utils'
import { createResource, Badge } from 'frappe-ui'
import { useDocument } from '@/data/document'
import { computed, onMounted, ref, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'

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
const { getUser, isManager } = usersStore()

const show = defineModel()
const router = useRouter()
const error = ref(null)
const isTicketCreating = ref(false)

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
    const mobile = ticket.doc?.mobile_no
    const email = ticket.doc?.email
    
    if (!mobile && !email) return null
    
    return {
      mobile_no: mobile,
      email: email
    }
  },
  auto: false,
})

// Watch for customer contact changes to fetch history
watch([() => ticket.doc?.mobile_no, () => ticket.doc?.email], ([mobile, email]) => {
  if (mobile || email) {
    customerHistory.reload()
  }
}, { immediate: false })

// Initialize ticket with defaults
onMounted(() => {
  // Initialize an empty doc first
  ticket.doc = {
    doctype: 'CRM Ticket',
    first_name: '',
    last_name: '',
    email: '',
    mobile_no: '',
    ticket_subject: '',
    description: '',
    priority: 'Medium',
    status: 'New',
    department: 'Support',
    issue_type: 'Account',
    assigned_to: user
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
      description: `Customer called on ${props.callLog.start_time}`
    })
    
    // Fetch customer history immediately for call log tickets
    nextTick(() => {
      if (customerNumber) {
        customerHistory.reload()
      }
    })
  }
})

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
            // Configure specific field types
            if (field.fieldname == 'status') {
              field.fieldtype = 'Select'
              field.options = [
                { label: 'New', value: 'New' },
                { label: 'Open', value: 'Open' },
                { label: 'In Progress', value: 'In Progress' },
                { label: 'Pending Customer', value: 'Pending Customer' },
                { label: 'Resolved', value: 'Resolved' },
                { label: 'Closed', value: 'Closed' }
              ]
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

            // Configure contact information fields
            if (field.fieldname == 'mobile_no') {
              field.fieldtype = 'Data'
              field.label = 'Mobile No'
              // Add change handler to trigger customer history lookup
              field.onChange = () => {
                if (ticket.doc.mobile_no) {
                  customerHistory.reload()
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

    // Create ticket
    const response = await createTicket.submit(ticket.doc)

    if (response) {
      show.value = false
      emit('ticket-created', response)
      emit('update:modelValue', false)
      
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
</script> 