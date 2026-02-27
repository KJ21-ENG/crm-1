<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Customers" />
      </template>
      <template #right-header>
        <CustomActions
          v-if="customersListView?.customListActions"
          :actions="customersListView.customListActions"
        />
      </template>
    </LayoutHeader>

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
      ref="customersListView"
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
      @pageChange="(page) => viewControls.goToPage(page)"
      @pageSizeChange="(pageSize) => viewControls.handlePageSizeChange(pageSize)"
      @applyFilter="(data) => viewControls.applyFilter(data)"
      @selectionsChanged="(selections) => viewControls.updateSelections(selections)"
    />
    <div v-else-if="customersList.data" class="flex h-full items-center justify-center">
      <div class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4">
        <span>No Customers Found</span>
      </div>
    </div>

  </div>
</template>

<script setup>
import { 
  Button,
  Dialog,
  FormControl,
  FeatherIcon,
  call,
  toast
} from 'frappe-ui'
import { ref, computed } from 'vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import ViewControls from '@/components/ViewControls.vue'
import CustomersListView from '@/components/ListViews/CustomersListView.vue'
import CustomDateTimePicker from '@/components/CustomDateTimePicker.vue'
import { useRouter } from 'vue-router'
import { permissionsStore } from '@/stores/permissions'

const router = useRouter()
// Permissions
const { canWrite } = permissionsStore()
const canWriteCustomers = computed(() => canWrite('Customers'))

// Data
const showCreateDialog = ref(false)
const creating = ref(false)
const newCustomer = ref({
  first_name: '',
  last_name: '',
  email: '',
  mobile_no: '',
  alternative_mobile_no: '',
  marital_status: '',
  date_of_birth: '',
  anniversary: '',
  address_line_1: '',
  address_line_2: '',
  city: '',
  state: '',
  country: '',
  pincode: '',
  pan_card_number: '',
  aadhaar_card_number: '',
  referral_code: '',
  referral_through: ''
})

// Standard list wiring (pagination handled by ViewControls)
const customersList = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)
const customersListView = ref(null)

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
    
    // Prepare customer data, handling empty dates properly
    const customerData = {
      mobile_no: newCustomer.value.mobile_no,
      first_name: newCustomer.value.first_name,
      last_name: newCustomer.value.last_name,
      email: newCustomer.value.email,
      alternative_mobile_no: newCustomer.value.alternative_mobile_no,
      marital_status: newCustomer.value.marital_status,
      date_of_birth: newCustomer.value.date_of_birth || null,
      anniversary: newCustomer.value.anniversary || null,
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
    }
    
    console.log('Creating customer with data:', customerData)
    
    await call('crm.api.customers.create_or_update_customer', customerData)
    
    // Reset form
    newCustomer.value = {
      first_name: '',
      last_name: '',
      email: '',
      mobile_no: '',
      marital_status: '',
      date_of_birth: '',
      anniversary: '',
      address_line_1: '',
      address_line_2: '',
      city: '',
      state: '',
      country: '',
      pincode: '',
      pan_card_number: '',
      aadhaar_card_number: '',
      referral_code: '',
      referral_through: ''
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
</script> 
