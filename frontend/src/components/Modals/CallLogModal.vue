<template>
  <Dialog v-model="show" :options="dialogOptions">
    <template #body>
      <div class="px-4 pt-5 pb-6 bg-surface-modal sm:px-6">
        <div class="flex items-center justify-between mb-5">
          <div class="flex items-center gap-2">
            <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
              {{ __(dialogOptions.title) || __('Untitled') }}
            </h3>
            <Badge v-if="callLog.isDirty" :label="'Not Saved'" theme="orange" />
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
        <div v-if="tabs.data">
          <!-- Add datetime picker before the FieldLayout -->
          <div class="mb-4">
            <div class="mb-1.5 text-xs text-ink-gray-5">{{ __('Call Time') }}</div>
            <CustomDateTimePicker
              v-model="callTime"
              :placeholder="__('Select date and time')"
              :input-class="'w-full'"
            />
          </div>
          <FieldLayout
            :tabs="tabs.data"
            v-model="callLog.doc"
            :doctype="'CRM Call Log'"
          />
          <ErrorMessage class="mt-8" :message="error" />
        </div>
      </div>
      <div class="px-4 pt-4 pb-7 sm:px-6">
        <div class="space-y-2">
          <Button
            class="w-full"
            v-for="action in dialogOptions.actions"
            :key="action.label"
            v-bind="action"
            :label="__(action.label)"
            :loading="loading"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import { usersStore } from '@/stores/users'
import { isMobileView } from '@/composables/settings'
import { showQuickEntryModal, quickEntryProps } from '@/composables/modals'
import { getRandom } from '@/utils'
import { capture } from '@/telemetry'
import { useDocument } from '@/data/document'
import { FeatherIcon, createResource, ErrorMessage, Badge, call } from 'frappe-ui'
import { ref, nextTick, computed, onMounted, watch } from 'vue'
import { sessionStore } from '@/stores/session'
import { getFormat } from '@/utils'
import CustomDateTimePicker from '../CustomDateTimePicker.vue'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({}),
  },
  options: {
    type: Object,
    default: {
      afterInsert: () => {},
    },
  },
})

const { isManager } = usersStore()

const show = defineModel()

const loading = ref(false)
const error = ref(null)
const editMode = ref(false)

const { document: callLog } = useDocument(
  'CRM Call Log',
  props.data?.name || '',
)

const dialogOptions = computed(() => {
  let title = !editMode.value ? __('New Call Log') : __('Edit Call Log')
  let size = 'xl'
  let actions = [
    {
      label: editMode.value ? __('Save') : __('Create'),
      variant: 'solid',
      onClick: () =>
        editMode.value ? updateCallLog() : createCallLog.submit(),
    },
  ]

  return { title, size, actions }
})

const tabs = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['QuickEntry', 'CRM Call Log'],
  params: { doctype: 'CRM Call Log', type: 'Quick Entry' },
  auto: true,
  transform: (data) => {
    // Configure employee field based on user permissions
    data.forEach(tab => {
      tab.sections?.forEach(section => {
        section.columns?.forEach(column => {
          column.fields?.forEach(field => {
            if (field.fieldname === 'employee') {
              field.default = session.user
              
              // Check permissions again in transform
              const roles = userRoles.data || []
              const isAdmin = roles.includes('Administrator') || roles.includes('System Manager')
              const isAdminUser = session.user === 'Administrator' || session.user.includes('Administrator')
              const canEdit = isAdmin || isAdminUser
              
              if (canEdit) {
                // Allow editing for System Manager and Administrator
                field.read_only = false
                field.description = 'Select employee for this call (editable for managers)'
              } else {
                // Read-only for other users
                field.read_only = true
                //field.description = 'Current user (non-editable)'
              }
            }
          })
        })
      })
    })
    return data
  }
})

const callBacks = {
  onSuccess: (doc) => {
    loading.value = false
    handleCallLogUpdate(doc)
  },
  onError: (err) => {
    loading.value = false
    if (err.exc_type == 'MandatoryError') {
      const errorMessage = err.messages
        .map((msg) => msg.split(': ')[2].trim())
        .join(', ')
      error.value = __('These fields are required: {0}', [errorMessage])
      return
    }
    error.value = err
  },
}

async function updateCallLog() {
  loading.value = true
  await callLog.save.submit(null, callBacks)
}

const session = sessionStore()

// Check if user has permission to edit employee field
// Fetch user roles
const userRoles = createResource({
  url: 'frappe.client.get_value',
  params: {
    doctype: 'User',
    filters: { name: session.user },
    fieldname: 'roles'
  },
  auto: true,
  transform: (data) => {
    if (data && data.roles) {
      return data.roles.split(',').map(role => role.trim())
    }
    return []
  }
})

const canEditEmployee = computed(() => {
  // Check if user is Administrator or System Manager
  const roles = userRoles.data || []
  const isAdmin = roles.includes('Administrator') || roles.includes('System Manager')
  
  // Also check if the user name contains 'Administrator' as a fallback
  const isAdminUser = session.user === 'Administrator' || session.user.includes('Administrator')
  
  console.log('User roles:', roles)
  console.log('Session user:', session.user)
  console.log('Is admin:', isAdmin || isAdminUser)
  
  return isAdmin || isAdminUser
})

// Add callTime ref - initialize with current date/time
const callTime = ref(new Date())

// Add watch to ensure callTime is always in correct format when changed
watch(callTime, (newValue) => {
  if (!newValue) {
    callTime.value = new Date()
  }
})

// Add onMounted hook to ensure default time is set
onMounted(() => {
  callTime.value = new Date()
  
  // Initialize callLog document with required properties
  if (!callLog.doc || !callLog.doc.name) {
    callLog.doc = {
      doctype: 'CRM Call Log',
      name: '', // Required for Field.vue
      type: 'Outgoing',
      duration: 0,
      status: 'Completed',
      employee: session.user, // Default to current user
      customer: '', // Will be filled by user
      customer_name: '', // Will be auto-populated or filled by user
      // ... other default values
    }
    
    // Merge with any provided data
    if (props.data) {
      Object.assign(callLog.doc, props.data)
    }
  }
  
  // Always ensure employee is set to current user
  if (callLog.doc) {
    callLog.doc.employee = session.user
  }
  
  // Force update to ensure employee field is set
  nextTick(() => {
    if (callLog.doc) {
      callLog.doc.employee = session.user
    }
  })
})

// Format datetime with 12-hour format for display
const formatDateTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
}

const formatDateForServer = (date) => {
  if (!date) return null
  const d = new Date(date)
  return d.toISOString().slice(0, 19).replace('T', ' ')
}

// Customer search functionality
const customerSearchLoading = ref(false)

async function searchCustomerByMobile(mobileNo) {
  if (!mobileNo || mobileNo.length < 3) {
    return
  }
  
  customerSearchLoading.value = true
  
  try {
    const result = await call('crm.api.customer_search.search_customer_by_mobile', {
      mobile_no: mobileNo
    })
    
    if (result && callLog.doc) {
      callLog.doc.customer_name = result.customer_name
    }
  } catch (error) {
    console.error('Error searching customer:', error)
    // Set default name if search fails
    if (callLog.doc) {
      callLog.doc.customer_name = `Lead from call ${mobileNo}`
    }
  } finally {
    customerSearchLoading.value = false
  }
}

// Watch for changes in customer field to auto-search
watch(() => callLog.doc?.customer, (newValue, oldValue) => {
  if (newValue && newValue !== oldValue && newValue.length >= 3) {
    // Debounce the search to avoid too many API calls
    setTimeout(() => {
      searchCustomerByMobile(newValue)
    }, 500)
  }
})

// Watch to ensure employee field is set to current user (only for non-managers)
watch(() => callLog.doc?.employee, (newValue) => {
  if (!canEditEmployee.value && newValue !== session.user) {
    callLog.doc.employee = session.user
  }
})

// Watch for tabs data to be loaded and set employee field
watch(() => tabs.data, (newTabsData) => {
  if (newTabsData && callLog.doc) {
    callLog.doc.employee = session.user
  }
}, { immediate: true })

const createCallLog = createResource({
  url: 'frappe.client.insert',
  makeParams() {
    // First create the base doc with required fields
    const baseDoc = {
      doctype: 'CRM Call Log',
      id: getRandom(6),
      telephony_medium: 'Manual',
      employee: callLog.doc?.employee || session.user,
      start_time: formatDateForServer(callTime.value), // Format date for server
      end_time: formatDateForServer(callTime.value), // Format date for server
      owner: session.user,
      status: callLog.doc?.status || 'Completed',
      type: callLog.doc?.type || 'Outgoing',
    }

    // Then add the call log specific data
    const doc = {
      ...baseDoc,
      ...callLog.doc,
      // Override any fields that should not be taken from callLog.doc
      start_time: formatDateForServer(callTime.value),
      end_time: formatDateForServer(callTime.value),
      owner: session.user,
    }

    // Set employee based on user permissions
    if (!canEditEmployee.value) {
      // For regular users, always set to current user
      doc.employee = session.user
    } else {
      // For managers, use the selected employee or default to current user
      doc.employee = doc.employee || session.user
    }

    // Set legacy fields for backward compatibility
    if (doc.type === 'Outgoing') {
      doc.from = doc.employee // Employee is the caller
      doc.to = doc.customer // Customer is the one being called
      doc.caller = doc.employee
      doc.receiver = null
    } else {
      doc.from = doc.customer // Customer is the one calling
      doc.to = doc.employee // Employee is the receiver
      doc.caller = null
      doc.receiver = doc.employee
    }

    return { doc }
  },
  onSuccess(doc) {
    loading.value = false
    if (doc.name) {
      capture('call_log_created')
      handleCallLogUpdate(doc)
    }
  },
  onError(err) {
    callBacks.onError(err)
  },
})

function handleCallLogUpdate(doc) {
  show.value = false
  props.options.afterInsert && props.options.afterInsert(doc)
}

onMounted(() => {
  editMode.value = props.data?.name ? true : false

  if (!props.data?.name) {
    callLog.doc = { ...props.data }
  }
})

function openQuickEntryModal() {
  showQuickEntryModal.value = true
  quickEntryProps.value = { doctype: 'CRM Call Log' }
  nextTick(() => (show.value = false))
}
</script>
