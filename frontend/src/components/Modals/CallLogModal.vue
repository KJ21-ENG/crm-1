<template>
  <Dialog v-model="show" :options="dialogOptions">
    <template #body>
      <div class="px-4 pt-5 pb-6 bg-surface-modal sm:px-6">
        <div class="flex items-center justify-between mb-5">
          <div class="flex items-center gap-2">
            <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
              {{ __(dialogOptions.title) || __('Untitled') }}
            </h3>
            <Badge v-if="callLog.isDirty" :label="'Not Saved'" theme="orange" />
          </div>
          <div class="flex items-center gap-1">
            <Button
              v-if="isManager() && !isMobileView"
              variant="ghost"
              class="w-7"
              @click="openQuickEntryModal"
            >
              <template #icon>
                <EditIcon />
              </template>
            </Button>
            <Button variant="ghost" class="w-7" @click="show = false">
              <template #icon>
                <FeatherIcon name="x" class="size-4" />
              </template>
            </Button>
          </div>
        </div>
        <div v-if="tabs.data">
          <!-- Add datetime picker before the FieldLayout -->
          <div class="mb-4">
            <div class="mb-1.5 text-xs text-ink-gray-5">{{ __('Call Time') }}</div>
            <DateTimePicker
              v-model="callTime"
              :placeholder="__('Select date and time')"
              :formatter="formatDateTime"
              input-class="w-full"
            />
          </div>
          <FieldLayout
            :tabs="tabs.data"
            v-model="callLog.doc"
            :doctype="'CRM Call Log'"
          />
          <ErrorMessage class="mt-8" :message="error" />
        </div>
      </div>
      <div class="px-4 pt-4 pb-7 sm:px-6">
        <div class="space-y-2">
          <Button
            class="w-full"
            v-for="action in dialogOptions.actions"
            :key="action.label"
            v-bind="action"
            :label="__(action.label)"
            :loading="loading"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import { usersStore } from '@/stores/users'
import { isMobileView } from '@/composables/settings'
import { showQuickEntryModal, quickEntryProps } from '@/composables/modals'
import { getRandom } from '@/utils'
import { capture } from '@/telemetry'
import { useDocument } from '@/data/document'
import { FeatherIcon, createResource, ErrorMessage, Badge, DateTimePicker } from 'frappe-ui'
import { ref, nextTick, computed, onMounted, watch } from 'vue'
import { sessionStore } from '@/stores/session'
import { getFormat } from '@/utils'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({}),
  },
  options: {
    type: Object,
    default: {
      afterInsert: () => {},
    },
  },
})

const { isManager } = usersStore()

const show = defineModel()

const loading = ref(false)
const error = ref(null)
const editMode = ref(false)

const { document: callLog } = useDocument(
  'CRM Call Log',
  props.data?.name || '',
)

const dialogOptions = computed(() => {
  let title = !editMode.value ? __('New Call Log') : __('Edit Call Log')
  let size = 'xl'
  let actions = [
    {
      label: editMode.value ? __('Save') : __('Create'),
      variant: 'solid',
      onClick: () =>
        editMode.value ? updateCallLog() : createCallLog.submit(),
    },
  ]

  return { title, size, actions }
})

const tabs = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['QuickEntry', 'CRM Call Log'],
  params: { doctype: 'CRM Call Log', type: 'Quick Entry' },
  auto: true,
})

const callBacks = {
  onSuccess: (doc) => {
    loading.value = false
    handleCallLogUpdate(doc)
  },
  onError: (err) => {
    loading.value = false
    if (err.exc_type == 'MandatoryError') {
      const errorMessage = err.messages
        .map((msg) => msg.split(': ')[2].trim())
        .join(', ')
      error.value = __('These fields are required: {0}', [errorMessage])
      return
    }
    error.value = err
  },
}

async function updateCallLog() {
  loading.value = true
  await callLog.save.submit(null, callBacks)
}

const session = sessionStore()

// Add callTime ref - initialize with current date/time
const callTime = ref(new Date())

// Add watch to ensure callTime is always in correct format when changed
watch(callTime, (newValue) => {
  if (!newValue) {
    callTime.value = new Date()
  }
})

// Add onMounted hook to ensure default time is set
onMounted(() => {
  callTime.value = new Date()
  
  // Initialize callLog document with required properties
  if (!callLog.doc || !callLog.doc.name) {
    callLog.doc = {
      doctype: 'CRM Call Log',
      name: '', // Required for Field.vue
      type: 'Outgoing',
      duration: 0,
      status: 'Completed',
      // ... other default values
    }
    
    // Merge with any provided data
    if (props.data) {
      Object.assign(callLog.doc, props.data)
    }
  }
})

// Format datetime with 12-hour format for display
const formatDateTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
}

const formatDateForServer = (date) => {
  if (!date) return null
  const d = new Date(date)
  return d.toISOString().slice(0, 19).replace('T', ' ')
}

const createCallLog = createResource({
  url: 'frappe.client.insert',
  makeParams() {
    // First create the base doc with required fields
    const baseDoc = {
      doctype: 'CRM Call Log',
      id: getRandom(6),
      telephony_medium: 'Manual',
      employee: session.user,
      start_time: formatDateForServer(callTime.value), // Format date for server
      end_time: formatDateForServer(callTime.value), // Format date for server
      owner: session.user,
      status: 'Completed',
      type: callLog.doc?.type || 'Outgoing',
    }

    // Then add the call log specific data
    const doc = {
      ...baseDoc,
      ...callLog.doc,
      // Override any fields that should not be taken from callLog.doc
      start_time: formatDateForServer(callTime.value),
      end_time: formatDateForServer(callTime.value),
      employee: session.user,
      owner: session.user,
    }

    // Set from/to based on call type
    if (doc.type === 'Outgoing') {
      doc.from = session.user // Employee is the caller
      doc.caller = session.user
    } else {
      doc.to = session.user // Employee is the receiver
      doc.receiver = session.user
    }

    return { doc }
  },
  onSuccess(doc) {
    loading.value = false
    if (doc.name) {
      capture('call_log_created')
      handleCallLogUpdate(doc)
    }
  },
  onError(err) {
    callBacks.onError(err)
  },
})

function handleCallLogUpdate(doc) {
  show.value = false
  props.options.afterInsert && props.options.afterInsert(doc)
}

onMounted(() => {
  editMode.value = props.data?.name ? true : false

  if (!props.data?.name) {
    callLog.doc = { ...props.data }
  }
})

function openQuickEntryModal() {
  showQuickEntryModal.value = true
  quickEntryProps.value = { doctype: 'CRM Call Log' }
  nextTick(() => (show.value = false))
}
</script>
