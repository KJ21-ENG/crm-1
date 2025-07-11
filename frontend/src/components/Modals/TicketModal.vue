<template>
  <Dialog v-model="show" :options="{ size: '3xl' }">
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
        <div>
          <FieldLayout 
            v-if="tabs.data" 
            :tabs="tabs.data" 
            v-model="ticket.doc" 
            :doctype="'CRM Ticket'"
          />
          <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
        </div>
      </div>
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="flex flex-row-reverse gap-2">
          <Button
            variant="solid"
            :label="__('Create')"
            :loading="isTicketCreating"
            @click="createNewTicket"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import EditIcon from '@/components/Icons/EditIcon.vue'
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import { usersStore } from '@/stores/users'
import { sessionStore } from '@/stores/session'
import { isMobileView } from '@/composables/settings'
import { showQuickEntryModal, quickEntryProps } from '@/composables/modals'
import { capture } from '@/telemetry'
import { createResource } from 'frappe-ui'
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
  }
})

// Watch for changes to update the form
watch(() => ticket.doc, (newVal) => {
  console.log('Ticket doc updated:', newVal)
}, { deep: true })

const tabs = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['QuickEntry', 'CRM Ticket'],
  params: { doctype: 'CRM Ticket', type: 'Quick Entry' },
  auto: true,
  transform: (_tabs) => {
    return _tabs.forEach((tab) => {
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
            if (field.fieldname == 'first_name') {
              field.fieldtype = 'Data'
              field.required = true
              field.label = 'First Name'
            }

            if (field.fieldname == 'last_name') {
              field.fieldtype = 'Data'
              field.label = 'Last Name'
            }

            if (field.fieldname == 'email') {
              field.fieldtype = 'Data'
              field.label = 'Email'
            }

            if (field.fieldname == 'mobile_no') {
              field.fieldtype = 'Data'
              field.label = 'Mobile No'
            }

            if (field.fieldtype === 'Table') {
              ticket.doc[field.fieldname] = []
            }
          })
        })
      })
    })
  },
})

const createTicket = createResource({
  url: 'crm.api.ticket.create_ticket',  // Changed to a more generic endpoint
  makeParams(values) {
    // Debug logs for initial data
    console.log('=== TICKET CREATION DEBUG ===')
    console.log('Call Log Props:', props.callLog)
    console.log('Ticket Doc State:', ticket.doc)
    
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

    // Debug logs
    console.log('=== TICKET CREATION DEBUG ===')
    console.log('Call Log Props:', props.callLog)
    console.log('Ticket Doc State:', ticket.doc)

    // Validate required fields
    if (!validateFields()) {
      isTicketCreating.value = false
      return
    }

    // Create ticket
    const response = await createTicket.submit(ticket.doc)
    
    // Debug logs
    console.log('Final Submit Data:', ticket.doc)
    console.log('First Name Value:', ticket.doc.first_name)
    console.log('Form Values:', ticket.doc)

    if (response) {
      show.value = false
      emit('ticket-created', response)
      emit('update:modelValue', false)
    }
  } catch (e) {
    console.log('=== ERROR ===')
    console.log('Error Object:', e)
    error.value = e
  } finally {
    isTicketCreating.value = false
  }
}

// Add field validation function
function validateFields() {
  const requiredFields = {
    first_name: 'First Name',
    ticket_subject: 'Subject',
    priority: 'Priority',
    issue_type: 'Issue Type',
    status: 'Status'
  }

  // Debug validation
  console.log('=== VALIDATION DEBUG ===')
  
  for (const [field, label] of Object.entries(requiredFields)) {
    const value = ticket.doc[field]
    console.log(`Validating ${label}:`, {
      value,
      type: typeof value,
      isEmpty: !value || value.trim() === ''
    })
    
    if (!value || value.trim() === '') {
      return {
        isValid: false,
        error: `${label} is required`
      }
    }
  }

  console.log('All Validations Passed')
  return { isValid: true }
}

function openQuickEntryModal() {
  showQuickEntryModal.value = true
  quickEntryProps.value = { doctype: 'CRM Ticket' }
  nextTick(() => (show.value = false))
}
</script> 