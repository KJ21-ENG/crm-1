<template>
  <div class="flex h-full flex-col">
    <!-- Header -->
    <div class="border-b bg-white px-5 py-4">
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-semibold text-ink-900">Customers</h1>
        <Button
          variant="solid"
          label="New Customer"
          @click="showCreateDialog = true"
        >
          <template #prefix>
            <FeatherIcon name="plus" class="h-4" />
          </template>
        </Button>
      </div>
      
      <!-- Search Bar -->
      <div class="mt-4 flex gap-2">
        <div class="flex-1">
          <FormControl
            v-model="searchQuery"
            placeholder="Search customers by name, email, or mobile..."
          />
        </div>
      </div>
    </div>

    <!-- Customer List -->
    <div class="flex-1 overflow-auto">
      <div v-if="customers.loading" class="p-8">
        <div class="flex items-center justify-center">
          <LoadingIndicator class="h-6 w-6" />
          <span class="ml-2">Loading customers...</span>
        </div>
      </div>

      <div v-else-if="filteredCustomers.length === 0" class="p-8">
        <div class="text-center">
          <h3 class="text-lg font-medium text-ink-700">No customers found</h3>
          <p class="mt-2 text-ink-600">
            {{ searchQuery ? 'Try adjusting your search criteria.' : 'Create your first customer to get started.' }}
          </p>
        </div>
      </div>

      <div v-else class="divide-y">
        <div
          v-for="customer in filteredCustomers"
          :key="customer.name"
          class="flex items-center justify-between p-4 hover:bg-gray-50 cursor-pointer"
          @click="navigateToCustomer(customer.name)"
        >
          <div class="flex items-center space-x-4">
            <Avatar
              :label="customer.first_name + ' ' + customer.last_name"
              :image="customer.image"
              size="md"
            />
            <div>
              <h3 class="font-medium text-ink-900">
                {{ customer.first_name }} {{ customer.last_name }}
              </h3>
              <div class="flex items-center space-x-2 text-sm text-ink-600">
                <span v-if="customer.email">{{ customer.email }}</span>
                <span v-if="customer.email && customer.mobile_no">•</span>
                <span v-if="customer.mobile_no">{{ customer.mobile_no }}</span>
              </div>
            </div>
          </div>
          
          <div class="flex items-center space-x-2">
            <Badge
              v-if="customer.status"
              :label="customer.status"
              :theme="customer.status === 'Active' ? 'green' : 'gray'"
            />
            <FeatherIcon name="chevron-right" class="h-4 w-4 text-ink-400" />
          </div>
        </div>
      </div>
    </div>

    <!-- Create Customer Dialog -->
    <Dialog
      v-model="showCreateDialog"
      :options="{
        title: 'Create New Customer',
        size: 'xl'
      }"
    >
      <template #body-content>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <FormControl
              v-model="newCustomer.first_name"
              label="First Name"
              placeholder="Enter first name"
            />
            <FormControl
              v-model="newCustomer.last_name"
              label="Last Name"
              placeholder="Enter last name"
            />
          </div>
          
          <FormControl
            v-model="newCustomer.email"
            label="Email"
            type="email"
            placeholder="Enter email address"
          />
          
          <FormControl
            v-model="newCustomer.mobile_no"
            label="Mobile Number"
            placeholder="Enter mobile number"
          />

          <div class="grid grid-cols-2 gap-4">
            <FormControl
              v-model="newCustomer.pan_card_number"
              label="PAN Card Number"
              placeholder="Enter PAN card number (optional)"
            />
            <FormControl
              v-model="newCustomer.aadhaar_card_number"
              label="Aadhaar Card Number"
              placeholder="Enter Aadhaar number (optional)"
            />
          </div>
        </div>
      </template>
      
      <template #actions>
        <Button
          variant="solid"
          label="Create Customer"
          @click="createCustomer"
          :loading="creating"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { 
  createListResource,
  Avatar,
  Button,
  Badge,
  Dialog,
  FormControl,
  LoadingIndicator,
  FeatherIcon,
  call
} from 'frappe-ui'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Data
const searchQuery = ref('')
const showCreateDialog = ref(false)
const creating = ref(false)
const newCustomer = ref({
  first_name: '',
  last_name: '',
  email: '',
  mobile_no: '',
  pan_card_number: '',
  aadhaar_card_number: ''
})

// Load customers
const customers = createListResource({
  doctype: 'CRM Customer',
  fields: [
    'name',
    'first_name', 
    'last_name',
    'email',
    'mobile_no',
    'status',
    'image',
    'creation'
  ],
  orderBy: 'creation desc',
  auto: true
})

// Computed
const filteredCustomers = computed(() => {
  if (!searchQuery.value) return customers.data || []
  
  const query = searchQuery.value.toLowerCase()
  return (customers.data || []).filter(customer => {
    const fullName = `${customer.first_name} ${customer.last_name}`.toLowerCase()
    const email = (customer.email || '').toLowerCase()
    const mobile = (customer.mobile_no || '').toLowerCase()
    
    return fullName.includes(query) ||
           email.includes(query) ||
           mobile.includes(query)
  })
})

// Methods
const navigateToCustomer = (customerId) => {
  router.push({ name: 'Customer', params: { customerId } })
}

const createCustomer = async () => {
  if (!newCustomer.value.first_name || !newCustomer.value.last_name || !newCustomer.value.mobile_no) {
    // Show error message - all fields required
    console.error('First name, last name, and mobile number are required')
    return
  }
  
  try {
    creating.value = true
    await call('crm.api.customers.create_or_update_customer', {
      mobile_no: newCustomer.value.mobile_no,
      first_name: newCustomer.value.first_name,
      last_name: newCustomer.value.last_name,
      email: newCustomer.value.email,
      pan_card_number: newCustomer.value.pan_card_number,
      aadhaar_card_number: newCustomer.value.aadhaar_card_number,
      customer_source: 'Direct'
    })
    
    // Reset form
    newCustomer.value = {
      first_name: '',
      last_name: '',
      email: '',
      mobile_no: '',
      pan_card_number: '',
      aadhaar_card_number: ''
    }
    
    showCreateDialog.value = false
    customers.reload()
  } catch (error) {
    console.error('Error creating customer:', error)
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  customers.reload()
})
</script> 