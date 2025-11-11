<template>
  <Dialog 
    :options="{
      title: __('Rejection Reason Required'),
      size: 'lg',
      actions: [
        {
          label: __('Cancel'),
          variant: 'ghost',
          onClick: handleCancel
        },
        {
          label: __('Confirm Rejection'),
          variant: 'solid',
          theme: 'red',
          loading: isSubmitting,
          disabled: !rejectionReason.trim() || isSubmitting,
          onClick: handleSubmit
        }
      ]
    }"
    v-model="show"
  >
    <template #body-title>
      <div class="flex items-center gap-2">
        <FeatherIcon name="alert-triangle" class="h-5 w-5 text-red-600" />
        <span>{{ __('Rejection Reason Required') }}</span>
      </div>
    </template>
    
    <template #body-content>
      <div class="space-y-6">
        <!-- Rejection Reason Input -->
        <div class="space-y-2">
          <label class="block text-sm font-medium text-ink-gray-7">
            {{ __('Reason for Rejection') }} <span class="text-ink-red-2">*</span>
          </label>
          <FormControl
            v-model="rejectionReason"
            type="textarea"
            :placeholder="__('Please provide detailed reason for rejecting this lead...')"
            :description="__('This information will help in future follow-ups and process improvements')"
            rows="4"
            @keyup.ctrl.enter="handleSubmit"
            @input="validateRejectionReason"
          />
          <div v-if="error" class="text-sm text-ink-red-2">
            {{ error }}
          </div>
        </div>
        
        <!-- Help Text -->
        <div class="rounded-lg bg-red-50 p-4">
          <div class="flex items-start gap-2">
            <FeatherIcon name="info" class="h-4 w-4 text-red-600 mt-0.5" />
            <div class="text-sm text-red-800">
              <p class="font-medium">{{ __('Why is rejection reason required?') }}</p>
              <p class="mt-1">
                {{ __('When rejecting a lead, providing a detailed reason helps the team understand what went wrong and plan better follow-up strategies. This information is crucial for improving our processes and success rates.') }}
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
const rejectionReason = ref('')
const error = ref('')
const isSubmitting = ref(false)

// Watch for modal open/close to reset form
watch(show, (newValue) => {
  if (newValue) {
    // Reset form when modal opens
    rejectionReason.value = ''
    error.value = ''
    isSubmitting.value = false
  } else {
    // Emit close event
    emit('update:modelValue', false)
  }
})

// Validation function
function validateRejectionReason() {
  error.value = ''
  
  if (!rejectionReason.value.trim()) {
    error.value = __('Rejection reason is required')
    return false
  }
  
  if (rejectionReason.value.trim().length < 10) {
    error.value = __('Please provide a detailed reason (at least 10 characters)')
    return false
  }
  
  return true
}

// Handle form submission
async function handleSubmit() {
  if (!validateRejectionReason()) {
    return
  }
  
  isSubmitting.value = true
  error.value = ''
  
  try {
    // Save rejection reason to the lead using custom API
    const result = await call('crm.api.lead_operations.save_rejection_reason_without_validation', {
      lead_name: props.leadId,
      rejection_reason: rejectionReason.value.trim()
    })
    
    if (!result.success) {
      error.value = result.message
      return
    }
    
    // Call the success callback to continue with status change
    if (props.onSuccess) {
      await props.onSuccess()
    }
    
    // Close modal
    show.value = false
    
  } catch (err) {
    console.error('Error saving rejection reason:', err)
    error.value = err.message || __('Failed to save rejection reason. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

// Handle modal cancellation
function handleCancel() {
  show.value = false
}

// Reset form when modal closes
watch(() => props.modelValue, (newValue) => {
  if (!newValue) {
    rejectionReason.value = ''
    error.value = ''
    isSubmitting.value = false
  }
})
</script>
