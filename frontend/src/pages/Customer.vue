<template>
  <LayoutHeader v-if="customer?.data">
    <template #left-header>
      <h1 class="text-xl font-semibold text-ink-900">
        {{ customer?.data?.first_name }} {{ customer?.data?.last_name }}
      </h1>
    </template>
    <template #right-header>
      <CustomActions 
        v-if="customer?.data?.name && canWriteCustomers"
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
                
                <!-- Customer Accounts -->
                <div v-if="customerAccounts.length > 0">
                  <label class="text-sm text-ink-gray-7">Accounts</label>
                  <div class="space-y-2">
                    <div 
                      v-for="account in customerAccounts" 
                      :key="account.client_id"
                      class="flex items-center justify-between p-2 bg-ink-gray-1 rounded border"
                    >
                      <div class="flex items-center gap-2">
                        <span class="text-sm font-medium text-ink-gray-12">
                          {{ account.account_type }} → {{ account.client_id }}
                        </span>
                      </div>
                      <div class="flex items-center gap-2">
                        <Badge 
                          label="Active" 
                          theme="green" 
                          size="sm"
                        />
                        <span class="text-xs text-ink-gray-7">
                          {{ formatDate(account.created_on) }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-if="customer.data.phone">
                  <label class="text-sm text-ink-gray-7">Phone</label>
                  <p class="text-ink-gray-12">{{ customer.data.phone }}</p>
                </div>
                <div v-if="customer.data.marital_status">
                  <label class="text-sm text-ink-gray-7">Marital Status</label>
                  <p class="text-ink-gray-12">{{ customer.data.marital_status }}</p>
                </div>
                <div v-if="customer.data.date_of_birth">
                  <label class="text-sm text-ink-gray-7">Date of Birth</label>
                  <p class="text-ink-gray-12">{{ formatDate(customer.data.date_of_birth) }}</p>
                </div>
                <div v-if="customer.data.anniversary">
                  <label class="text-sm text-ink-gray-7">Anniversary</label>
                  <p class="text-ink-gray-12">{{ formatDate(customer.data.anniversary) }}</p>
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
                <div v-if="customer.data.referral_code">
                  <label class="text-sm text-ink-gray-7">Client ID</label>
                  <p class="text-ink-gray-12">{{ customer.data.referral_code }}</p>
                </div>
                <div v-if="customer.data.referral_through">
                  <label class="text-sm text-ink-gray-7">Referral Through</label>
                  <p class="text-ink-gray-12">{{ customer.data.referral_through }}</p>
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
            
            <!-- Address Information -->
            <div class="bg-surface-white rounded-lg border p-6 lg:col-span-2">
              <h2 class="text-lg font-medium mb-4">Address</h2>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div v-if="customer.data.address_line_1">
                  <label class="text-sm text-ink-gray-7">Address Line 1</label>
                  <p class="text-ink-gray-12">{{ customer.data.address_line_1 }}</p>
                </div>
                <div v-if="customer.data.address_line_2">
                  <label class="text-sm text-ink-gray-7">Address Line 2</label>
                  <p class="text-ink-gray-12">{{ customer.data.address_line_2 }}</p>
                </div>
                <div v-if="customer.data.city">
                  <label class="text-sm text-ink-gray-7">City</label>
                  <p class="text-ink-gray-12">{{ customer.data.city }}</p>
                </div>
                <div v-if="customer.data.state">
                  <label class="text-sm text-ink-gray-7">State</label>
                  <p class="text-ink-gray-12">{{ customer.data.state }}</p>
                </div>
                <div v-if="customer.data.country">
                  <label class="text-sm text-ink-gray-7">Country</label>
                  <p class="text-ink-gray-12">{{ customer.data.country }}</p>
                </div>
                <div v-if="customer.data.pincode">
                  <label class="text-sm text-ink-gray-7">Pincode</label>
                  <p class="text-ink-gray-12">{{ customer.data.pincode }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Customer Interactions -->
          <div class="bg-surface-white rounded-lg border p-6">
            <h2 class="text-lg font-medium mb-4">Customer Interactions</h2>
            
            <Tabs as="div" v-model="tabIndex" :tabs="interactionTabs">
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

                <div v-if="tab.name === 'referrals'" class="mt-4">
                  <!-- Referral Summary -->
                  <div class="mb-6 p-4 bg-ink-blue-50 rounded-lg">
                    <h3 class="text-lg font-medium text-ink-gray-9 mb-2">Referral Summary</h3>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div class="text-center">
                        <div class="text-2xl font-bold text-ink-blue-600">{{ referralStats.total_referrals }}</div>
                        <div class="text-sm text-ink-gray-7">Total Referrals</div>
                      </div>
                      <div class="text-center">
                        <div class="text-2xl font-bold text-ink-green-600">{{ customerAccounts.length }}</div>
                        <div class="text-sm text-ink-gray-7">Active Accounts</div>
                      </div>
                      <div class="text-center">
                        <div class="text-2xl font-bold text-ink-orange-600">{{ referralStats.referral_details.length }}</div>
                        <div class="text-sm text-ink-gray-7">Unique Referrers</div>
                      </div>
                    </div>
                  </div>

                  <!-- Customer's Client IDs (Referral Codes) -->
                  <div class="mb-6">
                    <h4 class="text-md font-medium text-ink-gray-9 mb-3">Your Referral Codes (Client IDs)</h4>
                    <div class="space-y-2">
                      <div 
                        v-for="account in customerAccounts" 
                        :key="account.client_id"
                        class="flex items-center justify-between p-3 bg-ink-gray-1 rounded border"
                      >
                        <div class="flex items-center gap-3">
                          <div class="w-3 h-3 bg-ink-green-500 rounded-full"></div>
                          <div>
                            <span class="font-medium text-ink-gray-12">
                              {{ account.account_type }} → {{ account.client_id }}
                            </span>
                            <p class="text-xs text-ink-gray-7">
                              Created: {{ formatDate(account.created_on) }}
                            </p>
                          </div>
                        </div>
                        <Badge 
                          :label="`${getReferralCountForClientId(account.client_id)} referrals`"
                          theme="blue"
                          size="sm"
                        />
                      </div>
                    </div>
                  </div>

                  <!-- Referral Details -->
                  <div v-if="referralStats.referral_details.length > 0">
                    <h4 class="text-md font-medium text-ink-gray-9 mb-3">Referral Details</h4>
                    <div class="space-y-3">
                      <div 
                        v-for="referral in referralStats.referral_details" 
                        :key="referral.lead_id"
                        class="border rounded-lg p-4"
                      >
                        <div class="flex items-center justify-between">
                          <div>
                            <router-link 
                              :to="{ name: 'Lead', params: { leadId: referral.lead_id } }"
                              class="text-ink-blue-600 hover:underline font-medium"
                            >
                              {{ referral.lead_name }}
                            </router-link>
                            <p class="text-sm text-ink-gray-7">
                              Used your code: <span class="font-medium">{{ referral.referral_through }}</span>
                            </p>
                            <div class="flex items-center gap-2 mt-1">
                              <Badge 
                                :label="referral.account_type || 'N/A'" 
                                theme="blue"
                                variant="subtle"
                                class="text-xs"
                              />
                              <span class="text-sm text-ink-gray-7">
                                Created: {{ formatDate(referral.creation) }}
                              </span>
                            </div>
                          </div>
                          <Badge :label="referral.status" />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-center py-8 text-ink-gray-7">
                    No referrals found for this customer
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
          v-model="editCustomer.alternative_mobile_no"
          label="Alternative Mobile Number"
          placeholder="Enter alternative mobile number"
        />

        <FormControl
          v-model="editCustomer.marital_status"
          label="Marital Status"
          type="select"
          :options="['', 'Married', 'Unmarried']"
          placeholder="Select marital status"
        />

        <div class="grid grid-cols-2 gap-4">
          <div class="field">
            <div class="mb-2 text-sm text-ink-gray-5">Date of Birth</div>
            <div class="relative">
              <CustomDateTimePicker
                v-model="editCustomer.date_of_birth"
                placeholder="Enter Date of Birth"
                :input-class="'border-none'"
                :mode="'date'"
                :show-time="false"
                :auto-default="false"
                :year-quick-select="true"
              />
            </div>
          </div>
          <div class="field">
            <div class="mb-2 text-sm text-ink-gray-5">Anniversary</div>
            <div class="relative">
              <CustomDateTimePicker
                v-model="editCustomer.anniversary"
                placeholder="Enter Anniversary"
                :input-class="'border-none'"
                :mode="'date'"
                :show-time="false"
                :auto-default="false"
                :year-quick-select="true"
              />
            </div>
          </div>
        </div>

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
        
        <div class="grid grid-cols-2 gap-4 mt-2">
          <FormControl v-model="editCustomer.referral_code" label="Client ID" />
          <FormControl v-model="editCustomer.referral_through" label="Referral Through" />
        </div>
        
        <!-- Address Fields -->
        <div class="grid grid-cols-2 gap-4 mt-2">
          <FormControl v-model="editCustomer.address_line_1" label="Address Line 1" />
          <FormControl v-model="editCustomer.address_line_2" label="Address Line 2" />
        </div>
        <div class="grid grid-cols-3 gap-4 mt-2">
          <FormControl v-model="editCustomer.city" label="City" />
          <FormControl v-model="editCustomer.state" label="State" />
          <FormControl v-model="editCustomer.pincode" label="Pincode" />
        </div>
        <FormControl class="mt-2" v-model="editCustomer.country" label="Country" />
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
  call,
  toast
} from 'frappe-ui'
import { ref, computed, onMounted } from 'vue'
import { permissionsStore } from '@/stores/permissions'
import { useRouter } from 'vue-router'
import CustomDateTimePicker from '@/components/CustomDateTimePicker.vue'

const props = defineProps({
  customerId: {
    type: String,
    required: true
  }
})

const router = useRouter()
  const tabIndex = ref(0)
const interactions = ref({
  leads: [],
  tickets: [],
  call_logs: []
})

// Referral statistics
const referralStats = ref({
  total_referrals: 0,
  referral_details: []
})

// Parse customer accounts from JSON
const customerAccounts = computed(() => {
  if (!customer.value.data?.accounts) return []
  
  try {
    const accounts = JSON.parse(customer.value.data.accounts)
    return Array.isArray(accounts) ? accounts : []
  } catch (error) {
    console.error('Error parsing customer accounts:', error)
    return []
  }
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
    aadhaar_card_number: '',
    referral_code: '',
    referral_through: ''
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

// Module permissions
const { canWrite } = permissionsStore()
const canWriteCustomers = computed(() => canWrite('Customers'))

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
  },
  { 
    name: 'referrals', 
    label: `Referrals (${referralStats.value.total_referrals || 0})` 
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
      customer_id: customer.value.data.name,
      customer_mobile: customer.value.data.mobile_no
    })
    interactions.value = result
    
    // Also load referral statistics
    await loadReferralStats()
  } catch (error) {
    console.error('Error loading customer interactions:', error)
  }
}

async function loadReferralStats() {
  try {
    // Get all Client IDs for this customer
    const clientIds = customerAccounts.value.map(acc => acc.client_id)
    
    if (clientIds.length === 0) {
      referralStats.value = { total_referrals: 0, referral_details: [] }
      return
    }
    
    // ✅ FIXED: Use the referral analytics API instead of direct lead queries
    // This ensures we get customer names from the customer table, not null values from leads
    const referralDetails = await call('crm.api.referral_analytics.get_referral_details', {
      referral_codes: clientIds.join(','),
      customer_id: customer.value.data.name
    })
    
    // Filter out self-referrals (same mobile number)
    const validReferrals = referralDetails.filter(lead => 
      lead.mobile_no !== customer.value.data.mobile_no
    )
    
    // Process referral data with proper customer names
    const processedReferrals = validReferrals.map(lead => ({
      lead_id: lead.name,
      lead_name: getDisplayName(lead), // ✅ Smart name resolution
      referral_through: lead.referral_through,
      status: lead.status,
      creation: lead.creation,
      lead_category: lead.lead_category,
      mobile_no: lead.mobile_no
    }))
    
    referralStats.value = {
      total_referrals: processedReferrals.length,
      referral_details: processedReferrals
    }
    
    // ✅ Debug logging to track data flow
    console.log('Referral Stats Updated:', {
      clientIds,
      rawReferralDetails: referralDetails,
      validReferrals,
      processedReferrals,
      finalStats: referralStats.value
    })
    
  } catch (error) {
    console.error('Error loading referral stats:', error)
    referralStats.value = { total_referrals: 0, referral_details: [] }
  }
}

function getReferralCountForClientId(clientId) {
  return referralStats.value.referral_details.filter(
    ref => ref.referral_through === clientId
  ).length
}

// ✅ Helper function to get the best available display name
function getDisplayName(lead) {
  // Priority 1: Customer table name (most reliable)
  if (lead.lead_name && lead.lead_name !== 'null null') {
    return lead.lead_name
  }
  
  // Priority 2: Combined first_name + last_name from customer table
  if (lead.first_name || lead.last_name) {
    const firstName = lead.first_name || ''
    const lastName = lead.last_name || ''
    const combined = `${firstName} ${lastName}`.trim()
    if (combined && combined !== 'null null') {
      return combined
    }
  }
  
  // Priority 3: Mobile number as identifier
  if (lead.mobile_no) {
    return `Customer (${lead.mobile_no})`
  }
  
  // Priority 4: Lead ID as fallback
  return `Lead ${lead.lead_id}`
}

function openEditDialog() {
  // Populate edit form with current customer data
  editCustomer.value = {
    first_name: customer.value.data.first_name || '',
    last_name: customer.value.data.last_name || '',
    email: customer.value.data.email || '',
    mobile_no: customer.value.data.mobile_no || '',
    alternative_mobile_no: customer.value.data.alternative_mobile_no || '',
    organization: customer.value.data.organization || '',
    address_line_1: customer.value.data.address_line_1 || '',
    address_line_2: customer.value.data.address_line_2 || '',
    city: customer.value.data.city || '',
    state: customer.value.data.state || '',
    country: customer.value.data.country || '',
    pincode: customer.value.data.pincode || '',
    pan_card_number: customer.value.data.pan_card_number || '',
    aadhaar_card_number: customer.value.data.aadhaar_card_number || '',
    referral_code: customer.value.data.referral_code || '',
    referral_through: customer.value.data.referral_through || '',
    marital_status: customer.value.data.marital_status || '',
    // For date fields, preserve the actual value (including null) instead of converting to empty string
    date_of_birth: customer.value.data.date_of_birth,
    anniversary: customer.value.data.anniversary
  }
  showEditDialog.value = true
}

async function updateCustomer() {
  try {
    updating.value = true
    
    // Client-side validations (optional fields allowed)
    // PAN: uppercase, pattern ABCDE1234F
    if (editCustomer.value.pan_card_number) {
      const pan = String(editCustomer.value.pan_card_number).toUpperCase().trim()
      const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]$/
      if (!panRegex.test(pan)) {
        updating.value = false
        toast.error('Invalid PAN. Expected format: ABCDE1234F')
        return
      }
      editCustomer.value.pan_card_number = pan
    }

    // Aadhaar: 12 digits starting 2-9
    if (editCustomer.value.aadhaar_card_number) {
      const aadhaar = String(editCustomer.value.aadhaar_card_number).trim()
      const aadhaarRegex = /^[2-9][0-9]{11}$/
      if (!aadhaarRegex.test(aadhaar)) {
        updating.value = false
        toast.error('Invalid Aadhaar. It should be a 12-digit number starting 2-9')
        return
      }
      editCustomer.value.aadhaar_card_number = aadhaar
    }

    // Pincode: 6 digits
    if (editCustomer.value.pincode) {
      const pin = String(editCustomer.value.pincode).trim()
      if (!/^[1-9][0-9]{5}$/.test(pin)) {
        updating.value = false
        toast.error('Invalid Pincode. It should be a 6-digit number')
        return
      }
      editCustomer.value.pincode = pin
    }

    // Prepare data for API call, only including changed fields
    const updateData = {}
    const originalData = customer.value.data
    
    // Only include fields that have actually changed
    Object.keys(editCustomer.value).forEach(key => {
      const newValue = editCustomer.value[key]
      const oldValue = originalData[key]
      
      // Handle date fields specially
      if (key === 'date_of_birth' || key === 'anniversary') {
        if (newValue !== oldValue) {
          // If new value is empty string and old value exists, convert to null
          if (newValue === '' && oldValue) {
            updateData[key] = null
          } else if (newValue !== '') {
            // Only update if new value is not empty
            updateData[key] = newValue
          }
        }
      } else {
        // For non-date fields, only update if changed
        if (newValue !== oldValue) {
          updateData[key] = newValue
        }
      }
    })
    
    console.log('Original customer data:', originalData)
    console.log('Edit form data:', editCustomer.value)
    console.log('Fields to update:', updateData)
    
    // If no fields changed, don't make API call
    if (Object.keys(updateData).length === 0) {
      console.log('No fields changed, skipping update')
      updating.value = false
      return
    }
    
    // Call the update API
    await call('frappe.client.set_value', {
      doctype: 'CRM Customer',
      name: props.customerId,
      fieldname: updateData
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