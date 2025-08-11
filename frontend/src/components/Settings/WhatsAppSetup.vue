<template>
  <div class="flex h-full flex-col gap-6 p-8">
    <div class="flex justify-between">
      <div class="flex flex-col gap-1 w-9/12">
        <h2 class="flex gap-2 text-xl font-semibold leading-none h-5 text-ink-gray-8">
          {{ __('Add-ons') }}
        </h2>
        <p class="text-sm text-ink-gray-6">
          {{ __('Manage integrations and downloads for the Eshin CRM experience') }}
        </p>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto">
      <!-- Setup Instructions -->
      <div class="bg-surface-gray-1 rounded-lg p-6 mb-6">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-medium text-ink-gray-8">
              {{ __('Eshin Broking WhatsApp Integration') }}
            </h3>
            <p class="text-sm text-blue-600 font-medium">{{ __('Custom Multi-User Solution') }}</p>
          </div>
        </div>
        <p class="text-sm text-ink-gray-6 mb-4">
          {{ __('This custom WhatsApp integration is specifically designed for Eshin Broking\'s multi-user CRM environment. Each user can connect their own WhatsApp account without conflicts.') }}
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Benefits -->
          <div class="bg-white rounded-lg p-4 border border-outline-gray-3">
            <h4 class="font-medium text-ink-gray-8 mb-3">{{ __('Benefits') }}</h4>
            <ul class="space-y-2 text-sm text-ink-gray-6">
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                {{ __('No user conflicts - each user has their own WhatsApp session') }}
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                {{ __('Personal WhatsApp account for each user') }}
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                {{ __('Same CRM interface - seamless user experience') }}
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                {{ __('No server resource conflicts') }}
              </li>
            </ul>
          </div>

          <!-- Requirements -->
          <div class="bg-white rounded-lg p-4 border border-outline-gray-3">
            <h4 class="font-medium text-ink-gray-8 mb-3">{{ __('Requirements') }}</h4>
            <ul class="space-y-2 text-sm text-ink-gray-6">
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                {{ __('Node.js 16.0.0 or higher') }}
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                {{ __('Google Chrome browser') }}
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                {{ __('WhatsApp mobile app') }}
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                {{ __('Internet connection') }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Download Section -->
      <div class="bg-surface-gray-1 rounded-lg p-6 mb-6">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-medium text-ink-gray-8">
              {{ __('Download Eshin Broking Extension') }}
            </h3>
            <p class="text-sm text-green-600 font-medium">{{ __('Custom Chrome Extension') }}</p>
          </div>
        </div>
        <p class="text-sm text-ink-gray-6 mb-4">
          {{ __('Download and install the custom Chrome extension specifically developed for Eshin Broking\'s WhatsApp integration.') }}
        </p>

        <div class="bg-white rounded-lg p-4 border border-outline-gray-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.488"/>
                </svg>
              </div>
              <div>
                <h4 class="font-medium text-ink-gray-8">{{ extensionInfo.name || __('Eshin Broking WhatsApp Extension') }}</h4>
                <p class="text-sm text-ink-gray-6">{{ __('Version') }} {{ extensionInfo.version || '1.0.0' }} - {{ __('Custom Chrome Extension') }}</p>
                <p v-if="extensionInfo.description" class="text-xs text-ink-gray-5 mt-1">{{ __('Custom Chrome extension for Eshin Broking\'s multi-user WhatsApp integration') }}</p>
              </div>
            </div>
            <Button
              :label="__('Download Extension')"
              variant="solid"
              theme="green"
              @click="downloadExtension"
              :loading="downloading"
              :disabled="!extensionInfo.ready"
            >
              <template #prefix>
                <FeatherIcon name="download" class="h-4 w-4" />
              </template>
            </Button>
          </div>
        </div>
      </div>

      <!-- Local Service Download -->
      <div class="bg-surface-gray-1 rounded-lg p-6 mb-6">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-8 h-8 bg-gray-700 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor"><path d="M12 16l4-5h-3V4h-2v7H8l4 5zm8 2H4v2h16v-2z"/></svg>
          </div>
          <div>
            <h3 class="text-lg font-medium text-ink-gray-8">{{ __('Download Local WhatsApp Service') }}</h3>
            <p class="text-sm text-gray-600">{{ __('Node.js service that runs on your computer to enable WhatsApp messaging') }}</p>
          </div>
        </div>
        <div class="bg-white rounded-lg p-4 border border-outline-gray-3">
          <div class="flex items-center justify-between">
            <div class="text-sm text-ink-gray-6">
              <p class="mb-1">{{ __('Includes everything needed. Session cache is excluded.') }}</p>
              <p class="text-xs">{{ __('After download: unzip → open terminal in folder → npm install → npm start') }}</p>
            </div>
            <Button
              :label="__('Download Local Service')"
              variant="solid"
              theme="gray"
              @click="downloadLocalService"
              :loading="downloadingService"
            >
              <template #prefix>
                <FeatherIcon name="download" class="h-4 w-4" />
              </template>
            </Button>
          </div>
        </div>
      </div>

      <!-- Eshin App Download -->
      <div class="bg-surface-gray-1 rounded-lg p-6 mb-6">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor"><path d="M12 16l4-5h-3V4h-2v7H8l4 5zm8 2H4v2h16v-2z"/></svg>
          </div>
          <div>
            <h3 class="text-lg font-medium text-ink-gray-8">{{ __('Download Eshin App (Android)') }}</h3>
            <p class="text-sm text-indigo-600 font-medium">{{ __('APK build from this server') }}</p>
          </div>
        </div>
        <div class="bg-white rounded-lg p-4 border border-outline-gray-3">
          <div class="flex items-center justify-between">
            <div class="text-sm text-ink-gray-6">
              <p class="mb-1">{{ __('Tap to download the latest release APK') }}</p>
              <p class="text-xs">{{ __('File name: Eshin.apk') }}</p>
            </div>
            <Button
              :label="__('Download Eshin.apk')"
              variant="solid"
              theme="indigo"
              @click="downloadApk"
            >
              <template #prefix>
                <FeatherIcon name="download" class="h-4 w-4" />
              </template>
            </Button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Button, FeatherIcon } from 'frappe-ui'
import { toast } from 'frappe-ui'
import { createResource } from 'frappe-ui'

const downloading = ref(false)
const extensionInfo = ref({
  name: 'Eshin Broking WhatsApp Extension',
  version: '1.1.0',
  description: 'Custom Chrome extension for Eshin Broking\'s multi-user WhatsApp integration',
  ready: false
})

const downloadingService = ref(false)

// Fetch extension info
const extensionInfoResource = createResource({
  url: 'crm.api.whatsapp_setup.get_extension_info',
  auto: true,
  onSuccess: (data) => {
    extensionInfo.value = {
      name: data.name || 'Eshin Broking WhatsApp Extension',
      version: data.version || '1.1.0',
      description: data.description || 'Custom Chrome extension for Eshin Broking\'s multi-user WhatsApp integration',
      ready: data.ready || false
    }
  },
  onError: (error) => {
    console.error('Failed to fetch extension info:', error)
  }
})

onMounted(() => {
  extensionInfoResource.fetch()
})

const downloadExtension = async () => {
  downloading.value = true
  
  try {
    console.log('Starting download...')
    // Create a zip file of the extension
    const response = await fetch('/api/method/crm.api.whatsapp_setup.download_extension', {
      credentials: 'include',
      headers: {
        'Accept': 'application/zip, application/octet-stream, */*'
      }
    })
    
    console.log('Response status:', response.status)
    console.log('Response headers:', response.headers)
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'crm-whatsapp-extension.zip'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      toast.success(__('Extension downloaded successfully!'))
    } else {
      // Try to get error details
      let errorMessage = 'Download failed'
      try {
        const errorData = await response.json()
        errorMessage = errorData.message || errorData._server_messages || 'Download failed'
      } catch (e) {
        errorMessage = `HTTP ${response.status}: ${response.statusText}`
      }
      throw new Error(errorMessage)
    }
  } catch (error) {
    console.error('Download error:', error)
    toast.error(__('Failed to download extension: ') + error.message)
  } finally {
    downloading.value = false
  }
}

const downloadLocalService = async () => {
  downloadingService.value = true
  try {
    const response = await fetch('/api/method/crm.api.whatsapp_setup.download_local_service', {
      credentials: 'include',
      headers: { 'Accept': 'application/zip, application/octet-stream, */*' },
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'local-whatsapp-service.zip'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    toast.success(__('Local service downloaded successfully!'))
  } catch (e) {
    console.error('Local service download error:', e)
    toast.error(__('Failed to download local service: ') + e.message)
  } finally {
    downloadingService.value = false
  }
}

const downloadApk = async () => {
  try {
    const resp = await fetch('/api/method/crm.api.whatsapp_setup.download_eshen_app_apk', {
      credentials: 'include',
      headers: { 'Accept': 'application/vnd.android.package-archive, application/octet-stream, */*' },
    })
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}: ${resp.statusText}`)
    }
    const blob = await resp.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'Eshin.apk'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    toast.success(__('APK download started'))
  } catch (e) {
    console.error('APK download error:', e)
    toast.error(__('Failed to download APK: ') + e.message)
  }
}
</script> 