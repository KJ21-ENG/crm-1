<template>
  <Dialog v-model="show" :options="{ size: 'lg' }">
    <template #body>
      <div class="p-6">
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
                </div>
                <div v-else class="border rounded-lg p-8 bg-gray-100">
                  <div class="text-center text-gray-500">
                    <div class="mb-2">{{ __('Loading QR Code...') }}</div>
                    <Button
                      variant="outline"
                      size="sm"
                      @click="generateQRCode"
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
              @click="disconnectWhatsApp"
            >
              <template #prefix>
                <FeatherIcon name="log-out" class="h-4 w-4" />
              </template>
              {{ __('Disconnect WhatsApp') }}
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
const whatsappStatus = ref({
  connected: false,
  phoneNumber: null,
})

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
    emit('status-update', newStatus)
  } catch (error) {
    console.error('Error checking WhatsApp status:', error)
    const errorStatus = {
      connected: false,
      phoneNumber: null,
    }
    whatsappStatus.value = errorStatus
    emit('status-update', errorStatus)
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
      emit('status-update', disconnectedStatus)
      qrCode.value = ''
      toast.success('WhatsApp disconnected successfully')
    } else {
      toast.error('Failed to disconnect WhatsApp')
    }
  } catch (error) {
    toast.error('Error disconnecting WhatsApp: ' + error.message)
  }
}

// Auto-generate QR code when modal opens and not connected
watch(show, (isOpen) => {
  if (isOpen) {
    checkWhatsAppStatus()
    if (!whatsappStatus.value.connected && !qrCode.value) {
      generateQRCode()
    }
  }
})
</script> 