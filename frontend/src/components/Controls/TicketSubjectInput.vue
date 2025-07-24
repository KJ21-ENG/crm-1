<template>
  <div class="space-y-1.5 p-[2px] -m-[2px]">
    <label class="block" :class="labelClasses" v-if="attrs.label">
      {{ __(attrs.label) }}
    </label>
    <Autocomplete
      ref="autocomplete"
      :options="options.data"
      v-model="value"
      :size="attrs.size || 'sm'"
      :variant="attrs.variant"
      :placeholder="attrs.placeholder"
      :filterable="false"
    >
      <template #target="{ open, togglePopover }">
        <slot name="target" v-bind="{ open, togglePopover }" />
      </template>

      <template #prefix>
        <slot name="prefix" />
      </template>

      <template #item-prefix="{ active, selected, option }">
        <slot name="item-prefix" v-bind="{ active, selected, option }" />
      </template>

      <template #item-label="{ active, selected, option }">
        <slot name="item-label" v-bind="{ active, selected, option }">
          <div class="flex-1 truncate text-ink-gray-7">
            {{ option.label }}
          </div>
        </slot>
      </template>

      <template #footer="{ value, close }">
        <div>
          <Button
            variant="ghost"
            class="w-full !justify-start"
            :label="__('Add New Subject')"
            @click="() => showAddSubjectModal(close)"
          >
            <template #prefix>
              <FeatherIcon name="plus" class="h-4" />
            </template>
          </Button>
        </div>
        <div>
          <Button
            variant="ghost"
            class="w-full !justify-start"
            :label="__('Clear')"
            @click="() => clearValue(close)"
          >
            <template #prefix>
              <FeatherIcon name="x" class="h-4" />
            </template>
          </Button>
        </div>
      </template>
    </Autocomplete>

    <!-- Add Subject Modal -->
    <Dialog v-model="showModal" :options="{ title: __('Add New Subject') }">
      <template #body-content>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">
              {{ __('Subject Name') }}
            </label>
            <Input
              v-model="newSubject.subject_name"
              :placeholder="__('Enter subject name')"
              class="w-full"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">
              {{ __('Description') }}
            </label>
            <Textarea
              v-model="newSubject.description"
              :placeholder="__('Enter description (optional)')"
              class="w-full"
              rows="3"
            />
          </div>
        </div>
      </template>
      <template #actions>
        <Button
          variant="ghost"
          :label="__('Cancel')"
          @click="showModal = false"
        />
        <Button
          variant="solid"
          :label="__('Add Subject')"
          :loading="creating"
          @click="createSubject"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { Dialog, Input, Textarea, Button, FeatherIcon } from 'frappe-ui'
import Autocomplete from '@/components/frappe-ui/Autocomplete.vue'
import { watchDebounced } from '@vueuse/core'
import { createResource, call, toast } from 'frappe-ui'
import { useAttrs, computed, ref } from 'vue'

const props = defineProps({
  doctype: {
    type: String,
    required: true,
  },
  filters: {
    type: [Array, Object, String],
    default: [],
  },
  modelValue: {
    type: String,
    default: '',
  },
  hideMe: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'change'])

const attrs = useAttrs()

const valuePropPassed = computed(() => 'value' in attrs)

const value = computed({
  get: () => (valuePropPassed.value ? attrs.value : props.modelValue),
  set: (val) => {
    return (
      val?.value &&
      emit(valuePropPassed.value ? 'change' : 'update:modelValue', val?.value)
    )
  },
})

const autocomplete = ref(null)
const text = ref('')
const showModal = ref(false)
const creating = ref(false)

const newSubject = ref({
  subject_name: '',
  description: '',
})

watchDebounced(
  () => autocomplete.value?.query,
  (val) => {
    val = val || ''
    if (text.value === val) return
    text.value = val
    reload(val)
  },
  { debounce: 300, immediate: true },
)

watchDebounced(
  () => props.doctype,
  () => reload(''),
  { debounce: 300, immediate: true },
)

const options = createResource({
  url: 'frappe.desk.search.search_link',
  cache: [props.doctype, text.value, props.hideMe, props.filters],
  method: 'POST',
  params: {
    txt: text.value,
    doctype: props.doctype,
    filters: props.filters,
  },
  transform: (data) => {
    let allData = data.map((option) => {
      return {
        label: option.label || option.value,
        value: option.value,
        description: option.description,
      }
    })
    if (!props.hideMe && props.doctype == 'User') {
      allData.unshift({
        label: '@me',
        value: '@me',
      })
    }
    return allData
  },
})

function reload(val) {
  if (!props.doctype) return
  if (
    options.data?.length &&
    val === options.params?.txt &&
    props.doctype === options.params?.doctype
  )
    return

  options.update({
    params: {
      txt: val,
      doctype: props.doctype,
      filters: props.filters,
    },
  })
  options.reload()
}

function clearValue(close) {
  emit(valuePropPassed.value ? 'change' : 'update:modelValue', '')
  close()
}

function showAddSubjectModal(close) {
  newSubject.value = {
    subject_name: '',
    description: '',
  }
  showModal.value = true
  close()
}

async function createSubject() {
  if (!newSubject.value.subject_name.trim()) {
    toast.error(__('Subject name is required'))
    return
  }

  creating.value = true
  try {
    const doc = await call('frappe.client.insert', {
      doc: {
        doctype: 'CRM Ticket Subject',
        subject_name: newSubject.value.subject_name.trim(),
        description: newSubject.value.description.trim(),
        is_active: 1,
      },
    })
    
    // Reload options to include the new subject
    await options.reload()
    
    // Set the new subject as selected
    // Use the actual subject name as the value, not the document name
    emit(valuePropPassed.value ? 'change' : 'update:modelValue', newSubject.value.subject_name.trim())
    
    toast.success(__('Subject created successfully'))
    showModal.value = false
  } catch (error) {
    console.error('Error creating subject:', error)
    
    // Handle specific error types
    if (error.message && error.message.includes('UniqueValidationError')) {
      toast.error(__('A subject with this name already exists. Please choose a different name.'))
    } else {
      toast.error(__('Failed to create subject. Please try again.'))
    }
  } finally {
    creating.value = false
  }
}

const labelClasses = computed(() => {
  return [
    {
      sm: 'text-xs',
      md: 'text-base',
    }[attrs.size || 'sm'],
    'text-ink-gray-5',
  ]
})
</script> 