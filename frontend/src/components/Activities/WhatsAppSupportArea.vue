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
    <div class="flex-1 overflow-auto p-4">
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

        <!-- Search Results -->
        <div v-if="searchQuery && filteredSupportPages.length > 0" class="space-y-2">
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
                  </div>
                  <div v-else class="border rounded-lg p-8 bg-gray-100">
                    <div class="text-center text-gray-500">
                      <div class="mb-2">Loading QR Code...</div>
                      <Button
                        variant="outline"
                        size="sm"
                        @click="generateQRCode"
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
                @click="disconnectWhatsApp"
              >
                <template #prefix>
                  <FeatherIcon name="log-out" class="h-4 w-4" />
                </template>
                Disconnect WhatsApp
              </Button>
            </div>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
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
const qrCode = ref('')
const whatsappStatus = ref({
  connected: false,
  phoneNumber: null,
})

// WhatsApp activities resource
const whatsappActivities = createResource({
  url: 'crm.api.activities.get_activities',
  params: { name: props.docname },
  transform: ([versions, calls, notes, tasks, attachments]) => {
    return versions.filter(activity => activity.activity_type === 'whatsapp_support')
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

  sending.value = true
  
  try {
    const message = generateMessage()
    
    const response = await createResource({
      url: 'crm.api.whatsapp_support.send_support_pages',
      params: {
        doctype: props.doctype,
        docname: props.docname,
        customer_mobile: props.customer.mobile_no,
        support_pages: selectedPages.value.map(p => p.name),
        message: message,
      },
    }).fetch()

    if (response.success) {
      toast.success('Support pages sent successfully!')
      selectedPages.value = []
      searchQuery.value = ''
      whatsappActivities.reload()
    } else {
      toast.error(response.message || 'Failed to send support pages')
    }
  } catch (error) {
    toast.error('Error sending support pages: ' + error.message)
  } finally {
    sending.value = false
  }
}

const generateQRCode = async () => {
  try {
    const response = await createResource({
      url: 'crm.api.whatsapp_support.get_qr_code',
    }).fetch()

    if (response.success) {
      qrCode.value = response.qr_code
    } else {
      toast.error('Failed to generate QR code')
    }
  } catch (error) {
    toast.error('Error generating QR code: ' + error.message)
  }
}

const checkWhatsAppStatus = async () => {
  try {
    const response = await createResource({
      url: 'crm.api.whatsapp_support.get_status',
    }).fetch()

    const newStatus = {
      connected: response.connected || false,
      phoneNumber: response.phone_number || null,
    }
    
    whatsappStatus.value = newStatus
    emit('statusUpdate', newStatus)
  } catch (error) {
    console.error('Error checking WhatsApp status:', error)
    const errorStatus = {
      connected: false,
      phoneNumber: null,
    }
    whatsappStatus.value = errorStatus
    emit('statusUpdate', errorStatus)
  }
}

const refreshStatus = () => {
  checkWhatsAppStatus()
}

const disconnectWhatsApp = async () => {
  try {
    const response = await createResource({
      url: 'crm.api.whatsapp_support.disconnect',
    }).fetch()

    if (response.success) {
      const disconnectedStatus = {
        connected: false,
        phoneNumber: null,
      }
      whatsappStatus.value = disconnectedStatus
      emit('statusUpdate', disconnectedStatus)
      qrCode.value = ''
      toast.success('WhatsApp disconnected successfully')
    } else {
      toast.error('Failed to disconnect WhatsApp')
    }
  } catch (error) {
    toast.error('Error disconnecting WhatsApp: ' + error.message)
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
  checkWhatsAppStatus()
  
  // Check status every 30 seconds
  const statusInterval = setInterval(checkWhatsAppStatus, 30000)
  
  // Cleanup interval on unmount
  return () => {
    clearInterval(statusInterval)
  }
})

// Auto-generate QR code when modal opens and not connected
watch(showSetupModal, (isOpen) => {
  if (isOpen && !whatsappStatus.value.connected && !qrCode.value) {
    generateQRCode()
  }
})
</script> 