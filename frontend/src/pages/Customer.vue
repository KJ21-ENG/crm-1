<template>
  <LayoutHeader v-if="customer?.data">
    <template #left-header>
      <h1 class="text-xl font-semibold text-ink-900">
        {{ customer?.data?.first_name }} {{ customer?.data?.last_name }}
      </h1>
    </template>
    <template #right-header>
      <CustomActions 
        v-if="customer?.data?.name"
        :actions="actions"
        class="flex items-center gap-1"
      />
    </template>
  </LayoutHeader>
  
  <div v-if="customer?.data" class="flex h-full overflow-hidden">
    <div class="flex flex-1 flex-col overflow-hidden">
      <div class="flex-1 overflow-y-auto">
        <div class="container mx-auto p-6">
          <!-- Customer Header -->
          <div class="mb-6">
            <div class="flex items-center gap-4">
              <Avatar 
                size="xl"
                :label="customer.data.customer_name"
                :image="customer.data.image"
              />
              <div>
                <h1 class="text-2xl font-semibold text-ink-gray-12">
                  {{ customer.data.customer_name }}
                </h1>
                <p class="text-ink-gray-7">
                  {{ customer.data.email || customer.data.mobile_no }}
                </p>
                <Badge 
                  :label="customer.data.status"
                  :theme="customer.data.status === 'Active' ? 'green' : 'gray'"
                />
              </div>
            </div>
          </div>

          <!-- Customer Details -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <!-- Basic Information -->
            <div class="bg-surface-white rounded-lg border p-6">
              <h2 class="text-lg font-medium mb-4">Customer Information</h2>
              <div class="space-y-3">
                <div v-if="customer.data.email">
                  <label class="text-sm text-ink-gray-7">Email</label>
                  <p class="text-ink-gray-12">{{ customer.data.email }}</p>
                </div>
                <div v-if="customer.data.mobile_no">
                  <label class="text-sm text-ink-gray-7">Mobile</label>
                  <p class="text-ink-gray-12">{{ customer.data.mobile_no }}</p>
                </div>
                <div v-if="customer.data.phone">
                  <label class="text-sm text-ink-gray-7">Phone</label>
                  <p class="text-ink-gray-12">{{ customer.data.phone }}</p>
                </div>
                <div v-if="customer.data.job_title">
                  <label class="text-sm text-ink-gray-7">Job Title</label>
                  <p class="text-ink-gray-12">{{ customer.data.job_title }}</p>
                </div>
                <div v-if="customer.data.pan_card_number">
                  <label class="text-sm text-ink-gray-7">PAN Card Number</label>
                  <p class="text-ink-gray-12">{{ customer.data.pan_card_number }}</p>
                </div>
                <div v-if="customer.data.aadhaar_card_number">
                  <label class="text-sm text-ink-gray-7">Aadhaar Card Number</label>
                  <p class="text-ink-gray-12">{{ customer.data.aadhaar_card_number }}</p>
                </div>
              </div>
            </div>

            <!-- Additional Information -->
            <div class="bg-surface-white rounded-lg border p-6">
              <h2 class="text-lg font-medium mb-4">Additional Details</h2>
              <div class="space-y-3">
                <div v-if="customer.data.customer_source">
                  <label class="text-sm text-ink-gray-7">Source</label>
                  <p class="text-ink-gray-12">{{ customer.data.customer_source }}</p>
                </div>
                <div v-if="customer.data.creation">
                  <label class="text-sm text-ink-gray-7">Created On</label>
                  <p class="text-ink-gray-12">{{ formatDate(customer.data.creation) }}</p>
                </div>
                <div v-if="customer.data.created_from_lead">
                  <label class="text-sm text-ink-gray-7">Created From Lead</label>
                  <p class="text-ink-gray-12">
                    <router-link 
                      :to="{ name: 'Lead', params: { leadId: customer.data.created_from_lead } }"
                      class="text-ink-blue-600 hover:underline"
                    >
                      {{ customer.data.created_from_lead }}
                    </router-link>
                  </p>
                </div>
                <div v-if="customer.data.created_from_ticket">
                  <label class="text-sm text-ink-gray-7">Created From Ticket</label>
                  <p class="text-ink-gray-12">
                    <router-link 
                      :to="{ name: 'Ticket', params: { ticketId: customer.data.created_from_ticket } }"
                      class="text-ink-blue-600 hover:underline"
                    >
                      {{ customer.data.created_from_ticket }}
                    </router-link>
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Customer Interactions -->
          <div class="bg-surface-white rounded-lg border p-6">
            <h2 class="text-lg font-medium mb-4">Customer Interactions</h2>
            
            <Tabs v-model="activeTab" :tabs="interactionTabs">
              <template #tab-panel="{ tab }">
                <div v-if="tab.name === 'leads'" class="mt-4">
                  <div v-if="interactions.leads?.length" class="space-y-3">
                    <div 
                      v-for="lead in interactions.leads" 
                      :key="lead.name"
                      class="border rounded-lg p-4"
                    >
                      <div class="flex items-center justify-between">
                        <div>
                          <router-link 
                            :to="{ name: 'Lead', params: { leadId: lead.name } }"
                            class="text-ink-blue-600 hover:underline font-medium"
                          >
                            {{ lead.lead_name }}
                          </router-link>
                          <p class="text-sm text-ink-gray-7">
                            Created: {{ formatDate(lead.creation) }}
                          </p>
                        </div>
                        <Badge :label="lead.status" />
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-center py-8 text-ink-gray-7">
                    No leads found for this customer
                  </div>
                </div>

                <div v-if="tab.name === 'tickets'" class="mt-4">
                  <div v-if="interactions.tickets?.length" class="space-y-3">
                    <div 
                      v-for="ticket in interactions.tickets" 
                      :key="ticket.name"
                      class="border rounded-lg p-4"
                    >
                      <div class="flex items-center justify-between">
                        <div>
                          <router-link 
                            :to="{ name: 'Ticket', params: { ticketId: ticket.name } }"
                            class="text-ink-blue-600 hover:underline font-medium"
                          >
                            {{ ticket.subject }}
                          </router-link>
                          <p class="text-sm text-ink-gray-7">
                            Created: {{ formatDate(ticket.creation) }}
                          </p>
                        </div>
                        <Badge :label="ticket.status" />
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-center py-8 text-ink-gray-7">
                    No tickets found for this customer
                  </div>
                </div>

                <div v-if="tab.name === 'calls'" class="mt-4">
                  <div v-if="interactions.call_logs?.length" class="space-y-3">
                    <div 
                      v-for="call in interactions.call_logs" 
                      :key="call.name"
                      class="border rounded-lg p-4"
                    >
                      <div class="flex items-center justify-between">
                        <div>
                          <p class="font-medium">{{ call.type }} Call</p>
                          <p class="text-sm text-ink-gray-7">
                            {{ formatDate(call.start_time) }} • 
                            Duration: {{ formatDuration(call.duration) }}
                          </p>
                        </div>
                        <Badge :label="call.status" />
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-center py-8 text-ink-gray-7">
                    No call logs found for this customer
                  </div>
                </div>
              </template>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else-if="customer?.loading" class="flex h-full items-center justify-center">
    <div class="text-center">
      <div class="animate-spin h-8 w-8 border-4 border-ink-blue-600 border-t-transparent rounded-full mx-auto mb-2"></div>
      <p class="text-ink-gray-7">Loading customer...</p>
    </div>
  </div>

  <div v-else class="flex h-full items-center justify-center">
    <div class="text-center">
      <p class="text-ink-gray-7">Customer not found</p>
    </div>
  </div>

  <!-- Edit Customer Dialog -->
  <Dialog
    v-model="showEditDialog"
    :options="{
      title: 'Edit Customer',
      size: 'xl'
    }"
  >
    <template #body-content>
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <FormControl
            v-model="editCustomer.first_name"
            label="First Name"
            placeholder="Enter first name"
          />
          <FormControl
            v-model="editCustomer.last_name"
            label="Last Name"
            placeholder="Enter last name"
          />
        </div>
        
        <FormControl
          v-model="editCustomer.email"
          label="Email"
          type="email"
          placeholder="Enter email address"
        />
        
        <FormControl
          v-model="editCustomer.mobile_no"
          label="Mobile Number"
          placeholder="Enter mobile number"
        />
        
        <FormControl
          v-model="editCustomer.organization"
          label="Organization"
          placeholder="Enter organization name"
        />

        <div class="grid grid-cols-2 gap-4">
          <FormControl
            v-model="editCustomer.pan_card_number"
            label="PAN Card Number"
            placeholder="Enter PAN card number (optional)"
          />
          <FormControl
            v-model="editCustomer.aadhaar_card_number"
            label="Aadhaar Card Number"
            placeholder="Enter Aadhaar number (optional)"
          />
        </div>
      </div>
    </template>
    
    <template #actions>
      <Button
        variant="solid"
        label="Update Customer"
        @click="updateCustomer"
        :loading="updating"
      />
    </template>
  </Dialog>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import CustomActions from '@/components/CustomActions.vue'
import { 
  Avatar, 
  Badge, 
  Tabs, 
  Dialog,
  FormControl,
  Button,
  call
} from 'frappe-ui'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  customerId: {
    type: String,
    required: true
  }
})

const router = useRouter()
const activeTab = ref('leads')
const interactions = ref({
  leads: [],
  tickets: [],
  call_logs: []
})

const customer = ref({
  data: null,
  loading: true,
  error: null
})

// Edit dialog state
const showEditDialog = ref(false)
const updating = ref(false)
const editCustomer = ref({
  first_name: '',
  last_name: '',
  email: '',
  mobile_no: '',
  organization: '',
  pan_card_number: '',
  aadhaar_card_number: ''
})

// Load customer data
const loadCustomer = async () => {
  try {
    customer.value.loading = true
    customer.value.error = null
    
    const result = await call('frappe.client.get', {
      doctype: 'CRM Customer',
      name: props.customerId
    })
    
    customer.value.data = result
    customer.value.loading = false
    console.log('Customer data loaded successfully:', result)
  } catch (error) {
    customer.value.error = error.message || 'Failed to load customer'
    customer.value.loading = false
    console.error('Error loading customer:', error)
  }
}

const actions = computed(() => [
  {
    label: 'Edit Customer',
    icon: 'edit',
    onClick: () => openEditDialog()
  }
])

const interactionTabs = computed(() => [
  { 
    name: 'leads', 
    label: `Leads (${interactions.value.leads?.length || 0})` 
  },
  { 
    name: 'tickets', 
    label: `Tickets (${interactions.value.tickets?.length || 0})` 
  },
  { 
    name: 'calls', 
    label: `Call Logs (${interactions.value.call_logs?.length || 0})` 
  }
])

onMounted(async () => {
  console.log('Loading customer with ID:', props.customerId)
  
  await loadCustomer()
  
  console.log('Customer loaded:', customer.value.data)
  console.log('Customer loading:', customer.value.loading) 
  console.log('Customer error:', customer.value.error)
  
  if (customer.value.data?.mobile_no) {
    loadCustomerInteractions()
  }
})

async function loadCustomerInteractions() {
  try {
    const result = await call('crm.api.customers.get_customer_interactions', {
      customer_mobile: customer.value.data.mobile_no
    })
    interactions.value = result
  } catch (error) {
    console.error('Error loading customer interactions:', error)
  }
}

function openEditDialog() {
  // Populate edit form with current customer data
  editCustomer.value = {
    first_name: customer.value.data.first_name || '',
    last_name: customer.value.data.last_name || '',
    email: customer.value.data.email || '',
    mobile_no: customer.value.data.mobile_no || '',
    organization: customer.value.data.organization || '',
    pan_card_number: customer.value.data.pan_card_number || '',
    aadhaar_card_number: customer.value.data.aadhaar_card_number || ''
  }
  showEditDialog.value = true
}

async function updateCustomer() {
  try {
    updating.value = true
    
    // Call the update API
    await call('frappe.client.set_value', {
      doctype: 'CRM Customer',
      name: props.customerId,
      fieldname: editCustomer.value
    })
    
    // Refresh customer data
    await loadCustomer()
    
    // Close dialog
    showEditDialog.value = false
    
    // Show success message (you can add toast notification here)
    console.log('Customer updated successfully!')
    
  } catch (error) {
    console.error('Error updating customer:', error)
    // Show error message (you can add toast notification here)
  } finally {
    updating.value = false
  }
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatDuration(seconds) {
  if (!seconds) return '0s'
  const mins = Math.floor(seconds / 60)
  const secs = Math.round(seconds % 60)
  return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`
}
</script> 