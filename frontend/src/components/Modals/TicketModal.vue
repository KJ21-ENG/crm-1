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
                <div v-else>
                  <!-- Previous Tickets -->
                  <div v-if="customerHistory.data?.tickets?.length" class="mb-6">
                    <div class="mb-2 text-sm font-medium text-ink-gray-7">
                      {{ __('Previous Tickets') }}
                    </div>
                    <div class="space-y-3">
                      <div
                        v-for="ticket in customerHistory.data.tickets"
                        :key="ticket.name"
                        class="flex items-start gap-2 rounded-lg border p-2"
                      >
                        <TicketIcon class="mt-0.5 h-4 w-4 text-ink-gray-6" />
                        <div class="flex-1 text-sm">
                          <div class="mb-1 font-medium text-ink-gray-9">
                            {{ ticket.ticket_subject }}
                          </div>
                          <div class="flex items-center gap-2 text-xs text-ink-gray-6">
                            <Badge 
                              :label="ticket.status" 
                              :theme="getStatusColor(ticket.status)"
                              variant="subtle"
                            />
                            <span>{{ formatDate(ticket.creation) }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Previous Leads -->
                  <div v-if="customerHistory.data?.leads?.length">
                    <div class="mb-2 text-sm font-medium text-ink-gray-7">
                      {{ __('Previous Leads') }}
                    </div>
                    <div class="space-y-3">
                      <div
                        v-for="lead in customerHistory.data.leads"
                        :key="lead.name"
                        class="flex items-start gap-2 rounded-lg border p-2"
                      >
                        <LeadsIcon class="mt-0.5 h-4 w-4 text-ink-gray-6" />
                        <div class="flex-1 text-sm">
                          <div class="mb-1 font-medium text-ink-gray-9">
                            {{ lead.lead_name }}
                          </div>
                          <div class="flex items-center gap-2 text-xs text-ink-gray-6">
                            <Badge 
                              :label="lead.status" 
                              :theme="getStatusColor(lead.status)"
                              variant="subtle"
                            />
                            <span>{{ formatDate(lead.creation) }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- No History Found -->
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
            <Button
              v-if="hasOpenTickets"
              variant="outline"
              :label="__('View Open Tickets')"
              @click="viewOpenTickets"
            />
          </div>
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
const issueSolved = ref(false)  // New ref for Issue Solved checkbox

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
    assigned_to: user,
    resolved: 0,
    resolved_on: null
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
    // If issue is solved, set appropriate fields
    if (issueSolved.value) {
      ticket.doc.status = 'Resolved'
      ticket.doc.resolved = 1
      ticket.doc.resolved_on = new Date().toISOString()
    }

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
        has_customer_history: !!(customerHistory.data?.tickets?.length || customerHistory.data?.leads?.length),
        issue_solved: issueSolved.value
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