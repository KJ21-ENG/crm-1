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
      
    </div>

    <!-- Customer List (standard paginated list like other pages) -->
    <ViewControls
      ref="viewControls"
      v-model="customersList"
      v-model:loadMore="loadMore"
      v-model:resizeColumn="triggerResize"
      v-model:updatedPageCount="updatedPageCount"
      doctype="CRM Customer"
    />
    <CustomersListView
      v-if="customersList.data && rows.length"
      v-model="customersList.data.page_length_count"
      v-model:list="customersList"
      :rows="rows"
      :columns="customersList.data.columns"
      :options="{
        showTooltip: false,
        resizeColumn: true,
        rowCount: customersList.data.row_count,
        totalCount: customersList.data.total_count,
      }"
      @loadMore="() => loadMore++"
      @columnWidthUpdated="() => triggerResize++"
      @updatePageCount="(count) => (updatedPageCount = count)"
      @applyFilter="(data) => viewControls.applyFilter(data)"
      @selectionsChanged="(selections) => viewControls.updateSelections(selections)"
    />
    <div v-else-if="customersList.data" class="flex h-full items-center justify-center">
      <div class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4">
        <span>No Customers Found</span>
        <Button :label="'New Customer'" @click="showCreateDialog = true">
          <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
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

          <!-- Address Fields -->
          <div class="grid grid-cols-2 gap-4">
            <FormControl
              v-model="newCustomer.address_line_1"
              label="Address Line 1"
              placeholder="House No, Street"
            />
            <FormControl
              v-model="newCustomer.address_line_2"
              label="Address Line 2"
              placeholder="Area, Landmark (optional)"
            />
          </div>
          <div class="grid grid-cols-3 gap-4">
            <FormControl v-model="newCustomer.city" label="City" />
            <FormControl v-model="newCustomer.state" label="State" />
            <FormControl v-model="newCustomer.pincode" label="Pincode" />
          </div>
          <FormControl v-model="newCustomer.country" label="Country" />

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

          <!-- Referral Fields -->
          <div class="grid grid-cols-2 gap-4">
            <FormControl
              v-model="newCustomer.referral_code"
              label="Referral Code"
              placeholder="Enter referral code (optional)"
            />
            <FormControl
              v-model="newCustomer.referral_through"
              label="Referral Through"
              placeholder="Who referred? (optional)"
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
  Avatar,
  Button,
  Badge,
  Dialog,
  FormControl,
  LoadingIndicator,
  FeatherIcon,
  call,
  toast
} from 'frappe-ui'
import { ref, computed, onMounted } from 'vue'
import ViewControls from '@/components/ViewControls.vue'
import CustomersListView from '@/components/ListViews/CustomersListView.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Data
const showCreateDialog = ref(false)
const creating = ref(false)
const newCustomer = ref({
  first_name: '',
  last_name: '',
  email: '',
  mobile_no: '',
  address_line_1: '',
  address_line_2: '',
  city: '',
  state: '',
  country: '',
  pincode: '',
  pan_card_number: '',
  aadhaar_card_number: '',
  referral_code: ''
})

// Standard list wiring (pagination handled by ViewControls)
const customersList = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Computed
const rows = computed(() => {
  if (!customersList.value?.data?.data || !['list', 'group_by'].includes(customersList.value.data.view_type)) return []
  return customersList.value?.data.data.map((c) => {
    let _rows = {}
    customersList.value?.data.rows.forEach((row) => {
      _rows[row] = c[row]
      const col = customersList.value?.data.columns?.find((col) => (col.key || col.value) == row)
      const fieldType = col?.type
      if (fieldType && ['Date','Datetime'].includes(fieldType) && !['modified','creation'].includes(row)) {
        _rows[row] = new Date(c[row]).toLocaleString()
      }
      if (row === 'customer_name' || row === 'full_name') {
        _rows[row] = { label: c.customer_name || `${c.first_name || ''} ${c.last_name || ''}`.trim(), image_label: c.customer_name, image: c.image }
      } else if (['modified','creation'].includes(row)) {
        _rows[row] = { label: new Date(c[row]).toLocaleString(), timeAgo: '' }
      }
    })
    return _rows
  })
})

// Methods
const navigateToCustomer = (customerId) => {
  router.push({ name: 'Customer', params: { customerId } })
}

const createCustomer = async () => {
  // Basic required checks
  if (!newCustomer.value.first_name || !newCustomer.value.last_name || !newCustomer.value.mobile_no) {
    toast.error('First name, last name, and mobile number are required')
    return
  }
  // Optional validations for India specifics
  const pan = (newCustomer.value.pan_card_number || '').toUpperCase().trim()
  if (pan) {
    const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]$/
    if (!panRegex.test(pan)) {
      toast.error('Invalid PAN. Expected format: ABCDE1234F')
      return
    }
    newCustomer.value.pan_card_number = pan
  }
  const aadhaar = (newCustomer.value.aadhaar_card_number || '').trim()
  if (aadhaar) {
    const aadhaarRegex = /^[2-9][0-9]{11}$/
    if (!aadhaarRegex.test(aadhaar)) {
      toast.error('Invalid Aadhaar. It should be a 12-digit number starting 2-9')
      return
    }
  }
  const pincode = (newCustomer.value.pincode || '').trim()
  if (pincode && !/^[1-9][0-9]{5}$/.test(pincode)) {
    toast.error('Invalid Pincode. It should be a 6-digit number')
    return
  }
  
  try {
    creating.value = true
    await call('crm.api.customers.create_or_update_customer', {
      mobile_no: newCustomer.value.mobile_no,
      first_name: newCustomer.value.first_name,
      last_name: newCustomer.value.last_name,
      email: newCustomer.value.email,
      address_line_1: newCustomer.value.address_line_1,
      address_line_2: newCustomer.value.address_line_2,
      city: newCustomer.value.city,
      state: newCustomer.value.state,
      country: newCustomer.value.country,
      pincode: newCustomer.value.pincode,
      pan_card_number: newCustomer.value.pan_card_number,
      aadhaar_card_number: newCustomer.value.aadhaar_card_number,
      referral_code: newCustomer.value.referral_code,
      referral_through: newCustomer.value.referral_through,
      customer_source: 'Direct'
    })
    
    // Reset form
    newCustomer.value = {
      first_name: '',
      last_name: '',
      email: '',
      mobile_no: '',
      address_line_1: '',
      address_line_2: '',
      city: '',
      state: '',
      country: '',
      pincode: '',
      pan_card_number: '',
      aadhaar_card_number: '',
      referral_code: ''
      ,referral_through: ''
    }
    
    showCreateDialog.value = false
    // Refresh list via resource bound to ViewControls
    customersList.value?.reload && customersList.value.reload()
  } catch (error) {
    console.error('Error creating customer:', error)
    toast.error(error.messages?.[0] || 'Failed to create customer')
  } finally {
    creating.value = false
  }
}

onMounted(() => {})
</script> 