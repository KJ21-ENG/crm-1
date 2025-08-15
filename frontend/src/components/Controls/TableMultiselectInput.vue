<template>
  <div>
    <div
      class="group flex flex-wrap items-center gap-1 min-h-10 p-1 rounded text-sm bg-surface-gray-2 hover:bg-surface-gray-3 focus:border-outline-gray-4 focus:ring-0 focus-visible:ring-2 focus-visible:ring-outline-gray-3 text-ink-gray-8 transition-colors w-full"
    >
      <Button
        ref="valuesRef"
        v-for="value in parsedValues"
        :key="value"
        :label="value"
        size="sm"
        theme="gray"
        variant="subtle"
        class="rounded bg-surface-white hover:!bg-surface-gray-1 focus-visible:ring-outline-gray-4"
        @keydown.delete.capture.stop="removeLastValue"
      >
        <template #suffix>
          <FeatherIcon
            class="h-3.5"
            name="x"
            @click.stop="removeValue(value)"
          />
        </template>
      </Button>
      <div class="w-full">
        <Link
          v-if="linkField"
          class="form-control flex-1 truncate cursor-text"
          :value="query"
          :filters="filters"
          :doctype="linkField.options"
          @change="(v) => addValue(v)"
          :hideMe="true"
          :onCreate="onCreateHandler"
        >
          <template #target="{ togglePopover }">
            <button
              class="w-full h-7 px-2 cursor-text flex items-center text-ink-gray-5"
              @click.stop="togglePopover"
            >
              <span v-if="!parsedValues.length">{{ placeholderText }}</span>
            </button>
          </template>
          <template #item-label="{ option }">
            <div class="truncate text-ink-gray-8">{{ option.label || option.value }}</div>
          </template>
        </Link>
      </div>
    </div>
    <ErrorMessage class="mt-2 pl-2" v-if="error" :message="error" />

    <!-- Quick Create Modal for Ticket Subject -->
    <Dialog v-model="showCreateModal" :options="{ title: __('Add New Subject') }">
      <template #body-content>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">
              {{ __('Subject Name') }}
            </label>
            <Input v-model="newSubject.subject_name" :placeholder="__('Enter subject name')" class="w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">
              {{ __('Description') }}
            </label>
            <Textarea v-model="newSubject.description" :placeholder="__('Enter description (optional)')" class="w-full" rows="3" />
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="ghost" :label="__('Cancel')" @click="closeCreateModal" />
        <Button variant="solid" :label="__('Add Subject')" :loading="creating" @click="createSubject" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import Link from '@/components/Controls/Link.vue'
import { getMeta } from '@/stores/meta'
import { ref, computed, nextTick } from 'vue'
import { Dialog, Input, Textarea, Button, call, toast } from 'frappe-ui'

const props = defineProps({
  doctype: {
    type: String,
    required: true,
  },
  placeholder: {
    type: String,
    default: 'Select options...'
  },
  errorMessage: {
    type: Function,
    default: (value) => `${value} is an Invalid value`,
  },
})

const emit = defineEmits(['change'])

const { getFields } = getMeta(props.doctype)

const values = defineModel({
  type: Array,
  default: () => [],
})

const valuesRef = ref([])
const error = ref(null)
const query = ref('')

const linkField = ref('')

const filters = computed(() => {
  if (!linkField.value) return []
  return {
    name: ['not in', parsedValues.value],
  }
})

const parsedValues = computed(() => {
  error.value = ''
  getLinkField()
  if (!linkField.value) return []
  return values.value.map((row) => row[linkField.value.fieldname])
})

const placeholderText = computed(() => {
  return props.placeholder || 'Select options...'
})

const getLinkField = () => {
  error.value = ''
  if (!linkField.value) {
    let fields = getFields()
    linkField.value = fields?.find((df) =>
      ['Link', 'User'].includes(df.fieldtype),
    )
    if (!linkField.value) {
      error.value =
        'Table MultiSelect requires a Table with atleast one Link field'
    }
  }
  return linkField.value
}

const addValue = (value) => {
  error.value = null

  if (values.value.some((row) => row[linkField.value.fieldname] === value)) {
    error.value = 'Value already exists'
    return
  }

  if (value) {
    values.value.push({ [linkField.value.fieldname]: value })
    emit('change', values.value)
    !error.value && (query.value = '')
  }
}

const removeValue = (value) => {
  let _value = values.value.filter(
    (row) => row[linkField.value.fieldname] !== value,
  )
  emit('change', _value)
}

const removeLastValue = () => {
  if (query.value) return

  let valueRef = valuesRef.value[valuesRef.value.length - 1]?.$el
  if (document.activeElement === valueRef) {
    values.value.pop()
    emit('change', values.value)
    nextTick(() => {
      if (values.value.length) {
        valueRef = valuesRef.value[valuesRef.value.length - 1].$el
        valueRef?.focus()
      }
    })
  } else {
    valueRef?.focus()
  }
}

// Quick-create support for CRM Ticket Subject
const showCreateModal = ref(false)
const creating = ref(false)
const newSubject = ref({ subject_name: '', description: '' })
let closePopoverRef = null

const onCreateHandler = (value, close) => {
  // Only handle for CRM Ticket Subject multi-select child
  if (linkField.value && linkField.value.options === 'CRM Ticket Subject') {
    newSubject.value = { subject_name: value || '', description: '' }
    showCreateModal.value = true
    closePopoverRef = close
  }
}

function closeCreateModal() {
  showCreateModal.value = false
  newSubject.value = { subject_name: '', description: '' }
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
    // Add immediately to selection
    addValue(newSubject.value.subject_name.trim())
    toast.success(__('Subject created successfully'))
    if (closePopoverRef) closePopoverRef()
    closeCreateModal()
  } catch (error) {
    console.error('Error creating subject:', error)
    toast.error(error?.messages?.[0] || __('Failed to create subject'))
  } finally {
    creating.value = false
  }
}
</script>
