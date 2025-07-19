<template>
  <Dialog v-model="show" :options="{ size: 'lg' }">
    <template #body>
      <div class="p-6 relative">

        <div class="mb-4">
          <h3 class="text-lg font-semibold">{{ __('WhatsApp Setup') }}</h3>
          <p class="text-sm text-gray-600">{{ __('Connect your WhatsApp account to send support messages') }}</p>
        </div>

        <div class="space-y-4">
          <!-- Connection Status -->
          <div class="flex items-center justify-between rounded-lg border p-4">
            <div>
              <div class="font-medium">{{ __('Connection Status') }}</div>
              <div class="text-sm text-gray-600">
                {{ whatsappStatus.connected ? __('Connected') : __('Disconnected') }}
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
              <div class="font-medium mb-2">{{ __('Scan QR Code') }}</div>
              <div class="text-sm text-gray-600 mb-4">
                {{ __('Open WhatsApp on your phone and scan the QR code below') }}
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
                      {{ __('Refresh QR Code') }}
                    </Button>
                  </div>
                </div>
                <div v-else class="border rounded-lg p-8 bg-gray-100">
                  <div class="text-center text-gray-500">
                    <div v-if="whatsappStatus.is_initializing" class="mb-2">
                      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
                      {{ __('Initializing WhatsApp...') }}
                    </div>
                    <div v-else-if="generatingQR" class="mb-2">
                      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
                      {{ __('Generating QR Code...') }}
                    </div>
                    <div v-else class="mb-2">{{ __('Loading QR Code...') }}</div>
                    <Button
                      v-if="!whatsappStatus.is_initializing"
                      variant="outline"
                      size="sm"
                      @click="generateQRCode"
                      :loading="generatingQR"
                      :disabled="whatsappStatus.is_initializing"
                    >
                      {{ __('Generate QR Code') }}
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
              {{ __('Refresh Status') }}
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
              {{ loggingOut ? __('Logging Out...') : __('Logout') }}
            </Button>
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { createResource, Button, Dialog, toast } from 'frappe-ui'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'status-update'])

const show = defineModel()
const qrCode = ref('')
const generatingQR = ref(false)
const loggingOut = ref(false)
const whatsappStatus = ref({
  connected: false,
  phoneNumber: null,
  qr_code_available: false,
  is_initializing: false
})

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
    emit('status-update', newStatus)
  } catch (error) {
    console.error('Error checking WhatsApp status:', error)
    const errorStatus = {
      connected: false,
      phoneNumber: null,
      qr_code_available: false,
      is_initializing: false
    }
    whatsappStatus.value = errorStatus
    emit('status-update', errorStatus)
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
      emit('status-update', whatsappStatus.value)
    } else {
      toast.error(response.message || 'Failed to disconnect')
    }
  } catch (error) {
    toast.error('Error disconnecting: ' + error.message)
  } finally {
    loggingOut.value = false
  }
}

// Auto-generate QR code when modal opens and not connected
watch(show, (isOpen) => {
  if (isOpen) {
    checkWhatsAppStatus()
    // Start real-time polling when modal is open
    const statusInterval = setInterval(checkWhatsAppStatus, 2000)
    
    // Cleanup interval when modal closes
    return () => {
      clearInterval(statusInterval)
    }
  }
})
</script> 