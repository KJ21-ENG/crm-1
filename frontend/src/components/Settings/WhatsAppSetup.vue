<template>
  <div class="flex h-full flex-col gap-6 p-8">
    <div class="flex justify-between">
      <div class="flex flex-col gap-1 w-9/12">
        <h2 class="flex gap-2 text-xl font-semibold leading-none h-5 text-ink-gray-8">
          {{ __('WhatsApp Setup') }}
        </h2>
        <p class="text-sm text-ink-gray-6">
          {{ __('Configure WhatsApp integration for multi-user access') }}
        </p>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto">
      <!-- Setup Instructions -->
      <div class="bg-surface-gray-1 rounded-lg p-6 mb-6">
        <h3 class="text-lg font-medium text-ink-gray-8 mb-4">
          {{ __('Multi-User WhatsApp Integration') }}
        </h3>
        <p class="text-sm text-ink-gray-6 mb-4">
          {{ __('This setup allows each user to connect their own WhatsApp account without conflicts.') }}
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
        <h3 class="text-lg font-medium text-ink-gray-8 mb-4">
          {{ __('Download Chrome Extension') }}
        </h3>
        <p class="text-sm text-ink-gray-6 mb-4">
          {{ __('Download and install the Chrome extension to enable WhatsApp integration.') }}
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
                <h4 class="font-medium text-ink-gray-8">{{ extensionInfo.name || __('CRM WhatsApp Extension') }}</h4>
                <p class="text-sm text-ink-gray-6">{{ __('Version') }} {{ extensionInfo.version || '1.0.0' }} - {{ __('Chrome Extension') }}</p>
                <p v-if="extensionInfo.description" class="text-xs text-ink-gray-5 mt-1">{{ extensionInfo.description }}</p>
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

      <!-- Installation Instructions -->
      <div class="bg-surface-gray-1 rounded-lg p-6 mb-6">
        <h3 class="text-lg font-medium text-ink-gray-8 mb-4">
          {{ __('Installation Instructions') }}
        </h3>

        <div class="space-y-4">
          <!-- Step 1 -->
          <div class="bg-white rounded-lg p-4 border border-outline-gray-3">
            <div class="flex items-start gap-3">
              <div class="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0 mt-0.5">
                1
              </div>
              <div class="flex-1">
                <h4 class="font-medium text-ink-gray-8 mb-2">{{ __('Install Local WhatsApp Service') }}</h4>
                <div class="bg-gray-50 rounded p-3 mb-3">
                  <code class="text-sm text-gray-700">
                    cd apps/crm/local-whatsapp-service<br>
                    ./install.sh<br>
                    ./start-service.sh
                  </code>
                </div>
                <p class="text-sm text-ink-gray-6">
                  {{ __('This installs the local service that runs on each user\'s machine.') }}
                </p>
              </div>
            </div>
          </div>

          <!-- Step 2 -->
          <div class="bg-white rounded-lg p-4 border border-outline-gray-3">
            <div class="flex items-start gap-3">
              <div class="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0 mt-0.5">
                2
              </div>
              <div class="flex-1">
                <h4 class="font-medium text-ink-gray-8 mb-2">{{ __('Install Chrome Extension') }}</h4>
                <ol class="list-decimal list-inside text-sm text-ink-gray-6 space-y-1 mb-3">
                  <li>{{ __('Open Chrome and go to') }} <code class="bg-gray-100 px-1 rounded">chrome://extensions/</code></li>
                  <li>{{ __('Enable "Developer mode" (toggle in top right)') }}</li>
                  <li>{{ __('Click "Load unpacked"') }}</li>
                  <li>{{ __('Select the downloaded extension folder') }}</li>
                  <li>{{ __('Extension appears in the list') }}</li>
                </ol>
                <p class="text-sm text-ink-gray-6">
                  {{ __('The extension will inject WhatsApp functionality into the CRM.') }}
                </p>
              </div>
            </div>
          </div>

          <!-- Step 3 -->
          <div class="bg-white rounded-lg p-4 border border-outline-gray-3">
            <div class="flex items-start gap-3">
              <div class="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0 mt-0.5">
                3
              </div>
              <div class="flex-1">
                <h4 class="font-medium text-ink-gray-8 mb-2">{{ __('Connect WhatsApp') }}</h4>
                <ol class="list-decimal list-inside text-sm text-ink-gray-6 space-y-1 mb-3">
                  <li>{{ __('Start local service (if not auto-started)') }}</li>
                  <li>{{ __('Open CRM in Chrome') }}</li>
                  <li>{{ __('Click extension icon in toolbar') }}</li>
                  <li>{{ __('Click "Connect WhatsApp"') }}</li>
                  <li>{{ __('Scan QR code with WhatsApp mobile app') }}</li>
                  <li>{{ __('Wait for connection (green dot appears)') }}</li>
                </ol>
                <p class="text-sm text-ink-gray-6">
                  {{ __('Each user connects their own WhatsApp account.') }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Troubleshooting -->
      <div class="bg-surface-gray-1 rounded-lg p-6">
        <h3 class="text-lg font-medium text-ink-gray-8 mb-4">
          {{ __('Troubleshooting') }}
        </h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-white rounded-lg p-4 border border-outline-gray-3">
            <h4 class="font-medium text-ink-gray-8 mb-2">{{ __('Common Issues') }}</h4>
            <ul class="space-y-2 text-sm text-ink-gray-6">
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                {{ __('Service not starting - Check Node.js version') }}
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                {{ __('Extension not working - Check permissions') }}
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                {{ __('Connection fails - Clear session data') }}
              </li>
            </ul>
          </div>

          <div class="bg-white rounded-lg p-4 border border-outline-gray-3">
            <h4 class="font-medium text-ink-gray-8 mb-2">{{ __('Support') }}</h4>
            <ul class="space-y-2 text-sm text-ink-gray-6">
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                {{ __('Check local service logs') }}
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                {{ __('Review Chrome DevTools console') }}
              </li>
              <li class="flex items-start gap-2">
                <div class="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                {{ __('Contact system administrator') }}
              </li>
            </ul>
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
  name: 'CRM WhatsApp Extension',
  version: '1.0.0',
  description: 'Chrome extension for multi-user WhatsApp integration',
  ready: false
})

// Fetch extension info
const extensionInfoResource = createResource({
  url: 'crm.api.whatsapp_setup.get_extension_info',
  auto: true,
  onSuccess: (data) => {
    extensionInfo.value = {
      name: data.name || 'CRM WhatsApp Extension',
      version: data.version || '1.0.0',
      description: data.description || 'Chrome extension for multi-user WhatsApp integration',
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
</script> 