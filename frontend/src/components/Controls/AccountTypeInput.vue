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
            :label="__('Add New Account Type')"
            @click="() => showAddModal(close)"
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

    <!-- Add Account Type Modal -->
    <Dialog v-model="showModal" :options="{ title: __('Add New Account Type') }">
      <template #body-content>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">
              {{ __('Account Type') }}
            </label>
            <Input
              v-model="newType.account_type"
              :placeholder="__('Enter account type')"
              class="w-full"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">
              {{ __('Description') }}
            </label>
            <Textarea
              v-model="newType.description"
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
          :label="__('Add')"
          :loading="creating"
          @click="createAccountType"
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

const newType = ref({
  account_type: '',
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

function showAddModal(close) {
  newType.value = { account_type: '', description: '' }
  showModal.value = true
  close()
}

async function createAccountType() {
  if (!newType.value.account_type.trim()) {
    toast.error(__('Account type is required'))
    return
  }

  creating.value = true
  try {
    const doc = await call('frappe.client.insert', {
      doc: {
        doctype: 'CRM Account Type',
        account_type: newType.value.account_type.trim(),
        description: newType.value.description.trim(),
        is_active: 1,
      },
    })

    await options.reload()

    emit(valuePropPassed.value ? 'change' : 'update:modelValue', newType.value.account_type.trim())

    toast.success(__('Account type created'))
    showModal.value = false
  } catch (error) {
    console.error('Error creating account type:', error)
    if (error.message && error.message.includes('UniqueValidationError')) {
      toast.error(__('This account type already exists'))
    } else {
      toast.error(__('Failed to create account type'))
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


