<!-- WhatsApp Support Area Component -->
<template>
  <div class="flex h-full flex-col">
    <!-- Activity Section -->
    <div class="border-b p-4">
      <div v-if="whatsappActivities.loading" class="flex justify-center py-4">
        <FeatherIcon name="loader" class="h-6 w-6 animate-spin text-gray-400" />
      </div>
      <div v-else-if="whatsappActivities.data?.length" class="space-y-4">
        <div v-for="activity in whatsappActivities.data" :key="activity.name">
          <WhatsAppActivityArea :activity="activity" />
        </div>
      </div>
      <div v-else class="py-4 text-center text-gray-500">
        No WhatsApp support activities yet
      </div>
    </div>

    <!-- Search and Results -->
    <div class="flex-1 p-4">
      <div class="space-y-3">
        <!-- Search Box -->
        <div class="space-y-2">
          <label class="block text-sm font-medium">Search Support Pages</label>
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="Type to search support pages..."
            />
            <FeatherIcon 
              name="search" 
              class="absolute right-3 top-2.5 h-4 w-4 text-gray-400"
            />
          </div>
        </div>

        <!-- Search Results (independent scroll) -->
        <div v-if="searchQuery && filteredSupportPages.length > 0" class="space-y-2 max-h-64 overflow-y-auto pr-2">
          <div 
            v-for="page in filteredSupportPages"
            :key="page.name"
            class="flex items-center space-x-3 rounded-md border p-3 hover:bg-gray-50 cursor-pointer transition-colors"
            :class="selectedPages.some(p => p.name === page.name) ? 'border-blue-500 bg-blue-50' : 'border-gray-200'"
            @click="togglePageSelection(page)"
          >
            <div class="flex items-center">
              <FeatherIcon 
                v-if="selectedPages.some(p => p.name === page.name)"
                name="check-circle" 
                class="h-5 w-5 text-blue-600"
              />
              <div 
                v-else
                class="h-5 w-5 rounded-full border-2 border-gray-300"
              ></div>
            </div>
            <div class="flex-1">
              <div class="font-medium text-sm text-gray-900">{{ page.page_name }}</div>
              <div class="text-xs text-gray-500 truncate">{{ page.support_link }}</div>
              <div v-if="page.description" class="text-xs text-gray-400 mt-1">{{ page.description }}</div>
            </div>
          </div>
        </div>

        <!-- No results message -->
        <div v-else-if="searchQuery && filteredSupportPages.length === 0" class="text-center py-8 text-gray-500">
          <FeatherIcon name="search" class="h-8 w-8 mx-auto mb-2 text-gray-300" />
          <p class="text-sm">No support pages found for "{{ searchQuery }}"</p>
        </div>

        <!-- Initial state message -->
        <div v-else-if="!searchQuery" class="text-center py-8 text-gray-500">
          <FeatherIcon name="search" class="h-8 w-8 mx-auto mb-2 text-gray-300" />
          <p class="text-sm">Start typing to search for support pages</p>
        </div>
      </div>
    </div>

    <!-- Send Section -->
    <div v-if="selectedPages.length > 0" class="border-t bg-gray-50 p-4">
      <div class="flex items-center justify-between">
        <div class="text-sm text-gray-700">
          <FeatherIcon name="check-circle" class="h-4 w-4 inline mr-1 text-green-600" />
          {{ selectedPages.length }} support page{{ selectedPages.length > 1 ? 's' : '' }} selected
        </div>
        <Button
          variant="solid"
          :disabled="!whatsappStatus.connected || sending"
          :loading="sending"
          @click="sendSupportPages"
        >
          <template #prefix>
            <FeatherIcon name="send" class="h-4 w-4" />
          </template>
          Send WhatsApp Message
        </Button>
      </div>
    </div>

    <!-- Test Send Section -->
    



    <!-- WhatsApp Setup Modal -->
    <Dialog v-model="showSetupModal" :options="{ size: 'lg' }">
      <template #body>
        <div class="p-6">
          <div class="mb-4">
            <h3 class="text-lg font-semibold">WhatsApp Setup</h3>
            <p class="text-sm text-gray-600">Connect your WhatsApp account to send support messages</p>
          </div>

          <div class="space-y-4">
            <!-- Connection Status -->
            <div class="flex items-center justify-between rounded-lg border p-4">
              <div>
                <div class="font-medium">Connection Status</div>
                <div class="text-sm text-gray-600">
                  {{ whatsappStatus.connected ? 'Connected' : 'Disconnected' }}
                  <span v-if="whatsappStatus.connected && whatsappStatus.phoneNumber">
                    - {{ whatsappStatus.phoneNumber }}
                  </span>
                </div>
              </div>
              <div 
                class="h-3 w-3 rounded-full"
                :class="whatsappStatus.connected ? 'bg-green-500' : 'bg-red-500'"
              ></div>
            </div>

            <!-- QR Code Section -->
            <div v-if="!whatsappStatus.connected" class="space-y-4">
              <div class="text-center">
                <div class="font-medium mb-2">Scan QR Code</div>
                <div class="text-sm text-gray-600 mb-4">
                  Open WhatsApp on your phone and scan the QR code below
                </div>
                <div class="flex justify-center">
                                  <div 
                  v-if="qrCode"
                  class="border rounded-lg p-4 bg-white"
                >
                  <img 
                    :src="qrCode" 
                    alt="WhatsApp QR Code" 
                    class="max-w-full h-auto"
                    style="width: 256px; height: 256px;"
                  />
                  <div class="mt-3 text-center">
                    <Button
                      variant="outline"
                      size="sm"
                      @click="generateQRCode"
                      :loading="generatingQR"
                    >
                      <template #prefix>
                        <FeatherIcon name="refresh-cw" class="h-3 w-3" />
                      </template>
                      Refresh QR Code
                    </Button>
                  </div>
                </div>
                  <div v-else class="border rounded-lg p-8 bg-gray-100">
                    <div class="text-center text-gray-500">
                      <div v-if="whatsappStatus.is_initializing" class="mb-2">
                        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
                        Initializing WhatsApp...
                      </div>
                      <div v-else-if="generatingQR" class="mb-2">
                        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
                        Generating QR Code...
                      </div>
                      <div v-else class="mb-2">Loading QR Code...</div>
                      <Button
                        v-if="!whatsappStatus.is_initializing"
                        variant="outline"
                        size="sm"
                        @click="generateQRCode"
                        :loading="generatingQR"
                        :disabled="whatsappStatus.is_initializing"
                      >
                        Generate QR Code
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Connected Actions -->
            <div v-if="whatsappStatus.connected" class="space-y-3">
              <Button
                variant="outline"
                class="w-full"
                @click="refreshStatus"
              >
                <template #prefix>
                  <FeatherIcon name="refresh-cw" class="h-4 w-4" />
                </template>
                Refresh Status
              </Button>
              <Button
                variant="solid"
                theme="red"
                class="w-full"
                @click="logoutWhatsApp"
                :loading="loggingOut"
                :disabled="loggingOut"
              >
                <template #prefix>
                  <FeatherIcon name="log-out" class="h-4 w-4" />
                </template>
                {{ loggingOut ? 'Logging Out...' : 'Logout' }}
              </Button>
            </div>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue'
import { createResource, Button, Dialog, toast } from 'frappe-ui'
import { FeatherIcon } from 'frappe-ui'
import WhatsAppActivityArea from '@/components/Activities/WhatsAppActivityArea.vue'

const props = defineProps({
  doctype: {
    type: String,
    required: true,
  },
  docname: {
    type: String,
    required: true,
  },
  customer: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['statusUpdate'])

// Reactive data
const searchQuery = ref('')
const selectedPages = ref([])
const showSetupModal = ref(false)
const sending = ref(false)
const sendingTest = ref(false)
const lastSendContext = ref(null)
const generatingQR = ref(false)
const qrCode = ref('')
const loggingOut = ref(false)
const whatsappStatus = ref({
  connected: false,
  phoneNumber: null,
  qr_code_available: false,
  is_initializing: false
})
const extSendBtn = ref(null)
const isHosted = typeof window !== 'undefined' && !['localhost', 'crm.localhost'].includes(window.location.hostname)

// WhatsApp activities resource
const whatsappActivities = createResource({
  url: 'crm.api.activities.get_activities',
  params: { name: props.docname },
  transform: ([versions]) => {
    return (versions || []).filter((activity) => {
      if (activity.activity_type === 'whatsapp_support') return true
      if (activity.activity_type === 'comment' && typeof activity.content === 'string') {
        return activity.content.includes('WhatsApp Support')
      }
      return false
    })
  },
  auto: true,
})

// Support pages resource
const supportPages = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Support Pages',
    fields: ['name', 'page_name', 'support_link', 'description'],
    filters: {
      is_active: 1,
    },
  },
  auto: true,
})

// Filtered support pages
const filteredSupportPages = computed(() => {
  if (!supportPages.data) return []
  
  if (!searchQuery.value.trim()) return []
  
  const query = searchQuery.value.toLowerCase().trim()
  return supportPages.data.filter(page => {
    return (
      page.page_name.toLowerCase().includes(query) ||
      page.description?.toLowerCase().includes(query) ||
      page.support_link.toLowerCase().includes(query)
    )
  })
})

// Generate message for sending
const generateMessage = () => {
  if (selectedPages.value.length === 0) return ''
  
  let message = "Hi! Here are some helpful support pages:\n\n"
  selectedPages.value.forEach(page => {
    message += `📋 *${page.page_name}*\n`
    if (page.description) {
      message += `${page.description}\n`
    }
    message += `🔗 ${page.support_link}\n\n`
  })
  
  return message.trim()
}

// Methods
const togglePageSelection = (page) => {
  const index = selectedPages.value.findIndex(p => p.name === page.name)
  if (index > -1) {
    selectedPages.value.splice(index, 1)
  } else {
    selectedPages.value.push(page)
  }
}

const sendSupportPages = async () => {
  if (!whatsappStatus.value.connected) {
    toast.error('WhatsApp is not connected')
    return
  }

  if (selectedPages.value.length === 0) {
    toast.error('Please select at least one support page')
    return
  }

  const message = generateMessage()
  if (!message) return

  // Prefer Chrome extension flow: trigger hidden button the extension intercepts
  try {
    sending.value = true
    const phone = await fetchCustomerMobile()
    if (!phone) {
      throw new Error('Customer mobile number not found')
    }
    // Remember context so we can log an activity when extension responds
    lastSendContext.value = {
      phone,
      message,
      supportPages: selectedPages.value.map(p => p.name),
    }
    const evt = new CustomEvent('crm-whatsapp-send-direct', { detail: { phone, message } })
    document.dispatchEvent(evt)
  } catch (error) {
    sending.value = false
    toast.error('Failed to initiate WhatsApp send: ' + error.message)
  }
}

// Fetch customer mobile via server.
// For tickets: ticket -> customer_id -> CRM Customer.mobile_no
// For leads: lead -> customer_id -> CRM Customer.mobile_no (fall back to lead.mobile_no)
async function fetchCustomerMobile() {
  try {
    // If this is a ticket, use ticket -> customer flow
    if (props.doctype === 'CRM Ticket') {
      const ticket = await createResource({
        url: 'frappe.client.get',
        params: { doctype: 'CRM Ticket', name: props.docname, fields: ['customer_id'] },
      }).fetch()
      const customerId = ticket?.customer_id
      if (!customerId) return null

      const customer = await createResource({
        url: 'frappe.client.get',
        params: { doctype: 'CRM Customer', name: customerId, fields: ['mobile_no'] },
      }).fetch()
      return customer?.mobile_no || null
    }

    // If this is a lead, try lead -> customer flow, otherwise fall back to lead.mobile_no
    if (props.doctype === 'CRM Lead') {
      const lead = await createResource({
        url: 'frappe.client.get',
        params: { doctype: 'CRM Lead', name: props.docname, fields: ['customer_id', 'mobile_no'] },
      }).fetch()

      const customerId = lead?.customer_id
      if (customerId) {
        const customer = await createResource({
          url: 'frappe.client.get',
          params: { doctype: 'CRM Customer', name: customerId, fields: ['mobile_no'] },
        }).fetch()
        if (customer?.mobile_no) return customer.mobile_no
      }

      // Fallback to mobile_no present on the lead itself
      return lead?.mobile_no || null
    }

    // Generic fallback: if parent passed a customer prop with mobile_no, use it
    if (props.customer && props.customer.mobile_no) {
      return props.customer.mobile_no
    }

    // Last resort: try to load the document by doctype and name and look for mobile_no
    const doc = await createResource({
      url: 'frappe.client.get',
      params: { doctype: props.doctype, name: props.docname, fields: ['mobile_no'] },
    }).fetch()
    return doc?.mobile_no || null
  } catch (e) {
    console.error('Failed to fetch customer mobile:', e)
    return null
  }
}

const generateQRCode = async () => {
  if (generatingQR.value) return // Prevent multiple simultaneous calls
  
  generatingQR.value = true
  try {
    const response = await createResource({
      url: 'crm.api.whatsapp_setup.get_local_whatsapp_qr',
    }).fetch()

    if (response.success) {
      qrCode.value = response.qr_code
    } else {
      // If QR code is being generated, retry after a short delay
      if (response.message && response.message.includes('being generated')) {
        setTimeout(() => {
          generateQRCode()
        }, 2000) // Retry after 2 seconds
      } else {
        toast.error('Failed to generate QR code: ' + response.message)
      }
    }
  } catch (error) {
    toast.error('Error generating QR code: ' + error.message)
  } finally {
    generatingQR.value = false
  }
}

const checkWhatsAppStatus = async () => {
  try {
    const response = await createResource({
      url: 'crm.api.whatsapp_setup.get_local_whatsapp_status',
    }).fetch()

    const newStatus = {
      connected: response.connected || false,
      phoneNumber: response.phone_number || null,
      qr_code_available: response.qr_code_available || false,
      is_initializing: response.is_initializing || false
    }
    
    // Update QR code if available and we don't have one
    if (newStatus.qr_code_available && !qrCode.value && !newStatus.connected) {
      generateQRCode()
    }
    
    // Clear QR code if connected
    if (newStatus.connected && qrCode.value) {
      qrCode.value = ''
    }
    
    // If not connected and QR code is available but we don't have it, get it immediately
    if (!newStatus.connected && newStatus.qr_code_available && !qrCode.value && !generatingQR.value) {
      generateQRCode()
    }
    
    // If not connected and not initializing, try to get QR code
    if (!newStatus.connected && !newStatus.is_initializing && !qrCode.value && !generatingQR.value) {
      generateQRCode()
    }
    
    // If we just finished initializing and don't have a QR code, try to get one
    if (!newStatus.connected && !newStatus.is_initializing && !qrCode.value && !generatingQR.value && 
        whatsappStatus.value.is_initializing && !newStatus.is_initializing) {
      // We just finished initializing, try to get QR code
      setTimeout(() => {
        generateQRCode()
      }, 1000) // Wait 1 second for QR code to be generated
    }
    

    
    whatsappStatus.value = newStatus
    emit('statusUpdate', newStatus)
  } catch (error) {
    console.error('Error checking WhatsApp status:', error)
    const errorStatus = {
      connected: false,
      phoneNumber: null,
      qr_code_available: false,
      is_initializing: false
    }
    whatsappStatus.value = errorStatus
    emit('statusUpdate', errorStatus)
  }
}

const refreshStatus = () => {
  checkWhatsAppStatus()
}

const logoutWhatsApp = async () => {
  loggingOut.value = true
  try {
    const response = await createResource({
      url: 'crm.api.whatsapp_setup.disconnect_local_whatsapp',
    }).fetch()

    if (response.success) {
      toast.success('WhatsApp disconnected successfully')
      whatsappStatus.value = {
        connected: false,
        phoneNumber: null,
        qr_code_available: false,
        is_initializing: false
      }
      qrCode.value = ''
      emit('statusUpdate', whatsappStatus.value)
    } else {
      toast.error(response.message || 'Failed to disconnect')
    }
  } catch (error) {
    toast.error('Error disconnecting: ' + error.message)
  } finally {
    loggingOut.value = false
  }
}

const openSetupModal = () => {
  showSetupModal.value = true
}

// Expose method to parent component
defineExpose({
  openSetupModal
})

// Lifecycle
onMounted(() => {
  if (!isHosted) {
    checkWhatsAppStatus()
  }
  // Check status every 2 seconds for real-time updates (server-side only for local dev)
  const statusInterval = !isHosted ? setInterval(checkWhatsAppStatus, 2000) : null
  
  // Cleanup interval on unmount
  const onExtStatus = (e) => {
    const detail = e.detail || {}
    const connected = detail.status === 'connected'
    console.log('[CRM WhatsApp] ui:status', detail)
    whatsappStatus.value = {
      connected,
      phoneNumber: detail.phoneNumber || null,
      qr_code_available: !connected && !!detail.qrCodeAvailable,
      is_initializing: detail.status === 'connecting',
    }
    // Propagate status to parent so header reflects extension status immediately
    emit('statusUpdate', whatsappStatus.value)
  }

  const onExtSend = (e) => {
    const { success, error } = e.detail || {}
    console.log('[CRM WhatsApp] ui:sendResult', e.detail)
    sending.value = false
    sendingTest.value = false
    if (success) {
      toast.success('Support pages sent successfully!')
      selectedPages.value = []
      searchQuery.value = ''
      // Log activity on server so it appears in timeline
      try {
        const ctx = lastSendContext.value || {}
        createResource({
          url: 'crm.api.whatsapp_support.log_support_activity',
          params: {
            doctype: props.doctype,
            docname: props.docname,
            customer_mobile: ctx.phone,
            support_pages: ctx.supportPages,
            message: ctx.message,
            status: 'success',
          },
          auto: true,
          onSuccess: () => {
            whatsappActivities.reload()
            // Trigger Activities parent to refresh via socket-like event fallback
            document.dispatchEvent(new CustomEvent('crm-activities-reload'))
          },
        })
      } catch (_) {
        whatsappActivities.reload()
      }
    } else {
      toast.error('Failed to send support pages' + (error ? `: ${error}` : ''))
      // Log failed attempt as well
      try {
        const ctx = lastSendContext.value || {}
        createResource({
          url: 'crm.api.whatsapp_support.log_support_activity',
          params: {
            doctype: props.doctype,
            docname: props.docname,
            customer_mobile: ctx.phone,
            support_pages: ctx.supportPages,
            message: ctx.message,
            status: 'failed',
            error,
          },
          auto: true,
          onSuccess: () => {
            whatsappActivities.reload()
            document.dispatchEvent(new CustomEvent('crm-activities-reload'))
          },
        })
      } catch (_) {}
    }
  }

  document.addEventListener('crm-whatsapp-status', onExtStatus)
  document.addEventListener('crm-whatsapp-send', onExtSend)

  // Ask extension for current status on mount so header indicator is up to date
  document.dispatchEvent(new Event('crm-whatsapp-request-status'))

  onBeforeUnmount(() => {
    if (statusInterval) clearInterval(statusInterval)
    document.removeEventListener('crm-whatsapp-status', onExtStatus)
    document.removeEventListener('crm-whatsapp-send', onExtSend)
  })
})

// Test sender
const sendTestWhatsApp = () => {
  const phoneRaw = '6353131826'
  // Let extension/service handle country code formatting; pass as-is
  sendingTest.value = true
  try {
    const evt = new CustomEvent('crm-whatsapp-send-direct', { detail: { phone: phoneRaw, message: 'Test message from CRM' } })
    document.dispatchEvent(evt)
  } catch (e) {
    sendingTest.value = false
    toast.error('Failed to trigger extension: ' + e.message)
  }
}

// Auto-generate QR code when modal opens and not connected
watch(showSetupModal, (isOpen) => {
  if (isOpen && !whatsappStatus.value.connected) {
    // Always try to generate QR code when modal opens
    setTimeout(() => {
      generateQRCode()
    }, 500)
  }
})
</script> 