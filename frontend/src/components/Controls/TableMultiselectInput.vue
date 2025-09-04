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
          ref="linkRef"
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
            <div v-if="linkField && linkField.options === 'CRM Ticket Subject'" class="flex items-center justify-between gap-2 w-full">
              <div class="flex-1 truncate text-ink-gray-8">{{ option.label || option.value }}</div>
              <Button
                variant="ghost"
                size="sm"
                class="!px-1 text-ink-gray-5 hover:text-ink-red-5"
                @mousedown.prevent.stop
                @click.prevent.stop="(e) => confirmAndDelete(option, e)"
              >
                <template #icon>
                  <FeatherIcon name="trash" class="h-4 w-4" />
                </template>
              </Button>
            </div>
            <div v-else class="truncate text-ink-gray-8">{{ option.label || option.value }}</div>
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
import { Dialog, Input, Textarea, Button, FeatherIcon, call, toast } from 'frappe-ui'

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
const linkRef = ref(null)

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

// Inline delete of subjects (mirror AccountTypeInput and TicketSubjectInput behavior)
async function confirmAndDelete(option, evt) {
  try {
    if (evt) {
      evt.preventDefault()
      evt.stopPropagation()
    }
    // CRM-styled confirmation
    const confirmed = await new Promise((resolve) => {
      const confirmDialog = document.createElement('div')
      confirmDialog.innerHTML = `
        <div class=\"fixed inset-0 bg-black/40 z-[9998]\"></div>
        <div class=\"fixed inset-0 z-[9999] flex items-center justify-center p-4\">
          <div class=\"w-full max-w-sm rounded-lg bg-white shadow-xl\">
            <div class=\"px-4 py-3 border-b text-ink-gray-9 font-medium\">${__('Confirm Delete')}</div>
            <div class=\"px-4 py-4 text-sm text-ink-gray-7\">${__('Delete \"{0}\"?', [option.label])}</div>
            <div class=\"px-4 py-3 flex justify-end gap-2 border-t\">
              <button id=\"tsm-cancel\" class=\"px-3 py-1.5 text-sm rounded border\">${__('Cancel')}</button>
              <button id=\"tsm-ok\" class=\"px-3 py-1.5 text-sm rounded bg-red-600 text-white\">${__('Delete')}</button>
            </div>
          </div>
        </div>`
      document.body.appendChild(confirmDialog)
      confirmDialog.querySelector('#tsm-cancel').addEventListener('click', () => {
        document.body.removeChild(confirmDialog)
        resolve(false)
      })
      confirmDialog.querySelector('#tsm-ok').addEventListener('click', () => {
        document.body.removeChild(confirmDialog)
        resolve(true)
      })
    })
    if (!confirmed) return

    await call('frappe.client.delete', {
      doctype: 'CRM Ticket Subject',
      name: option.value,
    })

    // If deleted subject was selected in the multiselect, remove it from the value
    const selected = parsedValues.value
    if (selected.includes(option.value)) {
      removeValue(option.value)
    }

    // Reload dropdown options
    await linkRef.value?.reload()
    toast.success(__('Deleted'))
  } catch (error) {
    console.error('Delete error:', error)
    toast.error(getFriendlyError(error))
  }
}

function stripHtml(input) {
  try {
    return (input || '').replace(/<[^>]*>/g, '')
  } catch {
    return input || ''
  }
}

function getFriendlyError(err) {
  const raw = err?.messages?.[0] || err?.message || ''
  const msg = stripHtml(raw)
  if (/LinkExistsError/i.test(msg) || /Cannot delete|cancel because/i.test(msg)) {
    const m = msg.match(/Cannot delete.*? because\s+(.*?)\s+is linked with\s+([A-Za-z ]+)\s+([A-Z0-9\-]+)/i)
    if (m) {
      return __("Cannot delete: {0} is used in {1} {2}", [m[1], m[2], m[3]])
    }
    return __('Cannot delete: record is linked to other documents')
  }
  if (/PermissionError|No permission/i.test(msg)) return __('Not permitted')
  if (/Expectation Failed|417/i.test(msg)) return __('Request failed. Please try again')
  return msg || __('Something went wrong')
}
</script>
