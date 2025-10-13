<template>
  <Dialog v-model="show" :options="dialogOptions">
    <template #body-header>
      <div class="mb-6 flex items-center justify-between">
        <div>
          <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
            {{ __('POD ID Required') }}
          </h3>
          <p class="mt-1 text-sm text-ink-gray-6">
            {{ __('Please provide POD ID to proceed with status change to Sent to HO') }}
          </p>
        </div>
        <div class="flex items-center gap-1">
          <Button
            variant="ghost"
            class="w-7"
            @click="handleCancel"
          >
            <template #icon>
              <FeatherIcon name="x" class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </div>
    </template>
    
    <template #body-content>
      <div class="space-y-6">
        <!-- POD ID Input -->
        <div class="space-y-2">
          <label class="block text-sm font-medium text-ink-gray-7">
            {{ __('POD ID') }} <span class="text-ink-red-2">*</span>
          </label>
          <FormControl
            v-model="podId"
            type="text"
            :placeholder="__('Enter POD ID')"
            :description="__('Proof of Delivery ID - can be same for multiple leads')"
            @keyup.enter="handleSubmit"
          />
          <div v-if="error" class="text-sm text-ink-red-2">
            {{ error }}
          </div>
        </div>
        
        <!-- Help Text -->
        <div class="rounded-lg bg-blue-50 p-4">
          <div class="flex items-start gap-2">
            <HelpIcon class="h-4 w-4 text-blue-600 mt-0.5" />
            <div class="text-sm text-blue-800">
              <p class="font-medium">{{ __('Why is POD ID required?') }}</p>
              <p class="mt-1">
                {{ __('POD ID is mandatory when moving to Sent to HO status. This helps track and manage document delivery properly.') }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { call } from 'frappe-ui'
import HelpIcon from '@/components/Icons/HelpIcon.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  leadId: {
    type: String,
    required: true
  },
  targetStatus: {
    type: String,
    required: true
  },
  onSuccess: {
    type: Function,
    default: () => {}
  }
})

const emit = defineEmits(['update:modelValue'])

const show = defineModel()
const podId = ref('')
const error = ref('')
const isSubmitting = ref(false)

// Reset form when modal opens
watch(show, (newValue) => {
  if (newValue) {
    podId.value = ''
    error.value = ''
  }
})

const dialogOptions = computed(() => ({
  title: __('POD ID Required'),
  size: 'md',
  actions: [
    {
      label: __('Cancel'),
      variant: 'ghost',
      onClick: handleCancel
    },
    {
      label: __('Submit'),
      variant: 'solid',
      onClick: handleSubmit,
      loading: isSubmitting,
      disabled: !podId.value.trim()
    }
  ]
}))

async function handleSubmit() {
  if (!podId.value.trim()) {
    error.value = __('POD ID is required')
    return
  }
  
  isSubmitting.value = true
  error.value = ''
  
  try {
    // Save POD ID to the lead using custom API
    const podIdResult = await call('crm.api.lead_operations.save_pod_id_without_validation', {
      lead_name: props.leadId,
      pod_id: podId.value.trim()
    })
    
    if (!podIdResult.success) {
      error.value = podIdResult.message
      return
    }
    
    // Call the success callback to continue with status change
    if (props.onSuccess) {
      await props.onSuccess()
    }
    
    // Close modal
    show.value = false
    
  } catch (err) {
    console.error('Error saving POD ID:', err)
    if (err.messages?.[0]?.includes('TimestampMismatchError')) {
      error.value = __('The lead has been modified. Please refresh and try again.')
    } else {
      error.value = err.messages?.[0] || __('Failed to save POD ID. Please try again.')
    }
  } finally {
    isSubmitting.value = false
  }
}

function handleCancel() {
  show.value = false
}
</script>
