<template>
  <Dialog v-model="show" :options="dialogOptions">
    <template #body-header>
      <div class="mb-6 flex items-center justify-between">
        <div>
          <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
            {{ __('Client ID Required') }}
          </h3>
          <p class="mt-1 text-sm text-ink-gray-6">
            {{ __('Please provide Client ID to proceed with status change') }}
          </p>
        </div>
        <div class="flex items-center gap-1">
          <Button
            variant="ghost"
            class="w-7"
            @click="handleCancel"
          >
            <template #icon>
              <FeatherIcon name="x" class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </div>
    </template>
    
    <template #body-content>
      <div class="space-y-6">
        <!-- Client ID Input -->
        <div class="space-y-2">
          <label class="block text-sm font-medium text-ink-gray-7">
            {{ __('Client ID') }} <span class="text-ink-red-2">*</span>
          </label>
          <FormControl
            v-model="clientId"
            type="text"
            :placeholder="__('Enter Client ID')"
            :description="__('Client identification number assigned when account is opened')"
            @keyup.enter="handleSubmit"
            @input="validateClientId"
          />
          <div v-if="error" class="text-sm text-ink-red-2">
            {{ error }}
          </div>
          <div v-if="clientIdExists" class="text-sm text-ink-orange-2">
            {{ __('This Client ID already exists in the system. Please use a different one.') }}
          </div>
        </div>
        
        <!-- Help Text -->
        <div class="rounded-lg bg-blue-50 p-4">
          <div class="flex items-start gap-2">
            <HelpIcon class="h-4 w-4 text-blue-600 mt-0.5" />
            <div class="text-sm text-blue-800">
              <p class="font-medium">{{ __('Why is Client ID required?') }}</p>
              <p class="mt-1">
                {{ __('Client ID is mandatory when moving to Account Opened or Account Activated status. This helps track and manage client accounts properly.') }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { call } from 'frappe-ui'
import HelpIcon from '@/components/Icons/HelpIcon.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  leadId: {
    type: String,
    required: true
  },
  targetStatus: {
    type: String,
    required: true
  },
  onSuccess: {
    type: Function,
    default: () => {}
  }
})

const emit = defineEmits(['update:modelValue'])

const show = defineModel()
const clientId = ref('')
const error = ref('')
const isSubmitting = ref(false)
const clientIdExists = ref(false)

// Reset form when modal opens
watch(show, (newValue) => {
  if (newValue) {
    clientId.value = ''
    error.value = ''
    clientIdExists.value = false
  }
})

const dialogOptions = computed(() => ({
  title: __('Client ID Required'),
  size: 'md',
  actions: [
    {
      label: __('Cancel'),
      variant: 'ghost',
      onClick: handleCancel
    },
    {
      label: __('Submit'),
      variant: 'solid',
      onClick: handleSubmit,
      loading: isSubmitting,
      disabled: !clientId.value.trim() || clientIdExists.value
    }
  ]
}))

// Validate Client ID uniqueness
async function validateClientId() {
  if (!clientId.value.trim()) {
    clientIdExists.value = false
    return
  }
  
  try {
    // Check if Client ID already exists in any customer account
    const allCustomers = await call('frappe.client.get_list', {
      doctype: 'CRM Customer',
      fields: ['name', 'accounts']
    })
    
    for (const customer of allCustomers) {
      if (customer.accounts) {
        try {
          const accounts = JSON.parse(customer.accounts)
          const exists = accounts.some(acc => acc.client_id === clientId.value.trim())
          if (exists) {
            clientIdExists.value = true
            return
          }
        } catch (e) {
          // Skip if accounts is invalid JSON
        }
      }
    }
    
    clientIdExists.value = false
  } catch (err) {
    console.error('Error validating Client ID:', err)
    clientIdExists.value = false
  }
}

async function handleSubmit() {
  if (!clientId.value.trim()) {
    error.value = __('Client ID is required')
    return
  }
  
  if (clientIdExists.value) {
    error.value = __('This Client ID already exists. Please use a different one.')
    return
  }
  
  isSubmitting.value = true
  error.value = ''
  
  try {
    // Get the lead details
    const leadDoc = await call('frappe.client.get', {
      doctype: 'CRM Lead',
      name: props.leadId
    })
    
    // Find customer by customer_id (preferred) or mobile number (fallback)
    let customers = []
    
    if (leadDoc.customer_id) {
      // Try to find customer by customer_id first
      customers = await call('frappe.client.get_list', {
        doctype: 'CRM Customer',
        filters: {
          name: leadDoc.customer_id
        },
        fields: ['name', 'accounts', 'mobile_no', 'customer_name']
      })
    }
    
    // If not found by customer_id, try mobile number as fallback
    if (customers.length === 0 && leadDoc.mobile_no) {
      customers = await call('frappe.client.get_list', {
        doctype: 'CRM Customer',
        filters: {
          mobile_no: leadDoc.mobile_no
        },
        fields: ['name', 'accounts', 'mobile_no', 'customer_name']
      })
    }
    
    if (customers.length === 0) {
      error.value = __('System Error: Customer not found. Customer should have been created when the lead was created. Please contact support.')
      return
    }
    
    // Use the existing customer
    const customer = customers[0]
    
    // Check for global uniqueness of Client ID across all customer accounts
    const allCustomers = await call('frappe.client.get_list', {
      doctype: 'CRM Customer',
      fields: ['name', 'accounts']
    })
    
    for (const cust of allCustomers) {
      if (cust.accounts) {
        try {
          const custAccounts = JSON.parse(cust.accounts)
          const exists = custAccounts.some(acc => acc.client_id === clientId.value.trim())
          if (exists) {
            error.value = __('This Client ID already exists in another customer account.')
            return
          }
        } catch (e) {
          // Skip if accounts is invalid JSON
        }
      }
    }
    
    // Parse existing accounts or create new array
    let accounts = []
    if (customer.accounts) {
      try {
        accounts = JSON.parse(customer.accounts)
      } catch (e) {
        accounts = []
      }
    }
    
    // Add new account to the array
    const newAccount = {
      account_type: leadDoc.account_type || 'Individual',
      client_id: clientId.value.trim(),
      created_on: new Date().toISOString(),
      lead_id: props.leadId
    }
    
    accounts.push(newAccount)
    
         // Update customer with client_id, referral_code, and accounts using custom API
     const customerUpdateResult = await call('crm.api.lead_operations.update_customer_with_client_id', {
       customer_name: customer.name,
       client_id: clientId.value.trim(),
       accounts_json: JSON.stringify(accounts)
     })
     
     if (!customerUpdateResult.success) {
       error.value = customerUpdateResult.message
       return
     }
    
    // Also store client_id in lead for reference using custom API to avoid validation issues
    const clientIdResult = await call('crm.api.lead_operations.save_client_id_without_validation', {
      lead_name: props.leadId,
      client_id: clientId.value.trim()
    })
    
    if (!clientIdResult.success) {
      error.value = clientIdResult.message
      return
    }
    
    // Call the success callback to continue with status change
    if (props.onSuccess) {
      await props.onSuccess()
    }
    
    // Close modal
    show.value = false
    
  } catch (err) {
    console.error('Error saving Client ID:', err)
    if (err.messages?.[0]?.includes('TimestampMismatchError')) {
      error.value = __('The lead has been modified. Please refresh and try again.')
    } else {
      error.value = err.messages?.[0] || __('Failed to save Client ID. Please try again.')
    }
  } finally {
    isSubmitting.value = false
  }
}

function handleCancel() {
  show.value = false
}
</script> 