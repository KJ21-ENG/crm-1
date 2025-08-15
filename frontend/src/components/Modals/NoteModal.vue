<template>
  <Dialog v-model="show" :options="{
    size: 'xl',
    actions: [
      {
        label: editMode ? __('Update') : __('Create'),
        variant: 'solid',
        onClick: () => updateNote(),
      },
    ],
  }">
    <template #body-title>
      <div class="flex items-center gap-3">
        <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
          {{ editMode ? __('Edit Note') : __('Create Note') }}
        </h3>
        <Button v-if="_note?.reference_docname" size="sm" :label="
          _note.reference_doctype == 'CRM Deal'
            ? __('Open Deal')
            : _note.reference_doctype == 'CRM Ticket'
              ? __('Open Ticket')
              : __('Open Lead')
          " @click="redirect()">
          <template #suffix>
            <ArrowUpRightIcon class="w-4 h-4" />
          </template>
        </Button>
      </div>
    </template>
    <template #body-content>
      <div class="flex flex-col gap-4">
        <div>
          <FormControl ref="title" :label="__('Title')" v-model="_note.title" :placeholder="__('Call with John Doe')"
            required />
        </div>
        <div>
          <div class="mb-1.5 text-xs text-ink-gray-5">{{ __('Content') }}</div>
          <TextEditor variant="outline" ref="content"
            editor-class="!prose-sm overflow-auto min-h-[180px] max-h-80 py-1.5 px-2 rounded border border-[--surface-gray-2] bg-surface-gray-2 placeholder-ink-gray-4 hover:border-outline-gray-modals hover:bg-surface-gray-3 hover:shadow-sm focus:bg-surface-white focus:border-outline-gray-4 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-outline-gray-3 text-ink-gray-8 transition-colors"
            :bubbleMenu="true" :content="_note.content" @change="(val) => (_note.content = val)" :placeholder="__('Took a call with John Doe and discussed the new project.')
              " />
        </div>
        <!-- Link Note to Lead/Ticket -->
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div>
            <FormControl
              type="select"
              :label="__('Document Type')"
              v-model="_note.reference_doctype"
              :options="['CRM Lead', 'CRM Ticket']"
            />
          </div>
          <div>
            <label class="mb-1 block text-sm text-ink-gray-7">{{ __('Document') }}</label>
            <Link
              class="form-control"
              :doctype="_note.reference_doctype || 'CRM Lead'"
              :value="_note.reference_docname"
              @change="(v) => (_note.reference_docname = v)"
            />
          </div>
        </div>
        <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import ArrowUpRightIcon from '@/components/Icons/ArrowUpRightIcon.vue'
import { capture } from '@/telemetry'
import { TextEditor, call, ErrorMessage } from 'frappe-ui'
import { useOnboarding } from 'frappe-ui/frappe'
import { ref, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import Link from '@/components/Controls/Link.vue'

const props = defineProps({
  note: {
    type: Object,
    default: {},
  },
  doctype: {
    type: String,
    default: 'CRM Lead',
  },
  doc: {
    type: String,
    default: '',
  },
})

const show = defineModel()
const notes = defineModel('reloadNotes')

const emit = defineEmits(['after'])

const router = useRouter()

const { updateOnboardingStep } = useOnboarding('frappecrm')

const error = ref(null)
const title = ref(null)
const editMode = ref(false)
let _note = ref({})

async function updateNote() {
  if (_note.value.name) {
    let d = await call('frappe.client.set_value', {
      doctype: 'FCRM Note',
      name: _note.value.name,
      fieldname: {
        title: _note.value.title,
        content: _note.value.content,
        reference_doctype: _note.value.reference_doctype || props.doctype,
        reference_docname: _note.value.reference_docname || props.doc || '',
      },
    })
    if (d.name) {
      notes.value?.reload()
      emit('after', d)
    }
  } else {
    let d = await call('frappe.client.insert', {
      doc: {
        doctype: 'FCRM Note',
        title: _note.value.title,
        content: _note.value.content,
        reference_doctype: _note.value.reference_doctype || props.doctype,
        reference_docname: _note.value.reference_docname || props.doc || '',
      },
    }, {
      onError: (err) => {
        if (err.error.exc_type == 'MandatoryError') {
          error.value = "Title is mandatory"
        }
      }
    })
    if (d.name) {
      updateOnboardingStep('create_first_note')
      capture('note_created')
      notes.value?.reload()
      emit('after', d, true)
    }
  }
  show.value = false
}

function redirect() {
  if (!_note.value?.reference_docname) return
  // Determine route name and params based on reference_doctype
  let routeName = 'Lead'
  let params = { leadId: _note.value.reference_docname }

  if (_note.value.reference_doctype === 'CRM Deal') {
    routeName = 'Deal'
    params = { dealId: _note.value.reference_docname }
  } else if (_note.value.reference_doctype === 'CRM Ticket') {
    routeName = 'Ticket'
    params = { ticketId: _note.value.reference_docname }
  } else if (_note.value.reference_doctype === 'CRM Customer') {
    routeName = 'Customer'
    params = { customerId: _note.value.reference_docname }
  }

  router.push({ name: routeName, params })
}

watch(
  () => show.value,
  (value) => {
    if (!value) return
    editMode.value = false
    nextTick(() => {
      title.value?.el?.focus()
      _note.value = { ...props.note }
      // ensure defaults for linking when creating from Notes page
      if (!_note.value.reference_doctype) _note.value.reference_doctype = props.doctype
      if (_note.value.reference_docname == null) _note.value.reference_docname = props.doc || ''
      if (_note.value.title || _note.value.content) {
        editMode.value = true
      }
    })
  },
)
</script>
