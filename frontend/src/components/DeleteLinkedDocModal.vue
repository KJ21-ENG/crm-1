<template>
  <Dialog v-model="show" :options="{ size: 'xl' }">
    <template #body v-if="!confirmDeleteInfo.show">
      <div class="bg-surface-modal px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-4 flex items-center justify-between">
          <div>
            <h3 class="text-2xl leading-6 text-ink-gray-9 font-semibold">
              {{
                linkedDocs?.length == 0
                  ? __('Delete')
                  : __('Unlink linked documents')
              }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button variant="ghost" icon="x" @click="show = false" />
          </div>
        </div>
        <div>
          <div v-if="linkedDocs?.length > 0">
            <span class="text-ink-gray-5 text-base">
              {{
                __(
                  'Unlink these linked documents from the customer before deleting this document',
                )
              }}
            </span>
            <LinkedDocsListView
              class="mt-4"
              :rows="linkedDocs"
              :columns="[
                {
                  label: 'Document',
                  key: 'title',
                },
                {
                  label: 'Master',
                  key: 'reference_doctype',
                  width: '30%',
                },
              ]"
              @selectionsChanged="
                (selections) => viewControls.updateSelections(selections)
              "
              :linkedDocsResource="linkedDocsResource"
              :unlinkLinkedDoc="unlinkLinkedDoc"
            />
          </div>
          <div v-if="linkedDocs?.length == 0" class="text-ink-gray-5 text-base">
            {{
              __('Are you sure you want to delete {0} - {1}?', [
                props.doctype,
                props.docname,
              ])
            }}
          </div>
        </div>
      </div>
      <div class="px-4 pb-7 pt-0 sm:px-6">
        <div class="flex flex-row-reverse gap-2">
          <Button
            v-if="linkedDocs?.length > 0"
            :label="
              viewControls?.selections?.length == 0
                ? __('Unlink all')
                : __('Unlink {0} item(s)', [viewControls?.selections?.length])
            "
            variant="solid"
            theme="blue"
            icon-left="unlock"
            @click="confirmUnlink()"
          />
          <Button
            v-if="linkedDocs?.length == 0"
            variant="solid"
            icon-left="trash-2"
            :label="__('Delete')"
            :loading="isDealCreating"
            @click="deleteDoc()"
            theme="red"
          />
        </div>
      </div>
    </template>
    <template #body v-if="confirmDeleteInfo.show">
      <div class="bg-surface-modal px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-6 flex items-center justify-between">
          <div>
            <h3 class="text-2xl leading-6 text-ink-gray-9 font-semibold">
              {{ confirmDeleteInfo.title }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button variant="ghost" icon="x" @click="show = false" />
          </div>
        </div>
        <div class="text-ink-gray-5 text-base">
          {{ confirmDeleteInfo.message }}
        </div>
        <div v-if="confirmDeleteInfo.error" class="mt-3 text-red-600 text-sm">
          {{ confirmDeleteInfo.error }}
        </div>
        <div class="flex justify-end gap-2 mt-6">
          <Button variant="ghost" @click="cancel()">
            {{ __('Cancel') }}
          </Button>
          <Button
            variant="solid"
            :label="confirmDeleteInfo.loading ? __('Working...') : confirmDeleteInfo.title"
            :loading="confirmDeleteInfo.loading"
            @click="onConfirmAction()"
            theme="red"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { createResource, call, toast } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { computed, ref } from 'vue'

const show = defineModel()
const router = useRouter()
const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  doctype: {
    type: String,
    required: true,
  },
  docname: {
    type: String,
    required: true,
  },
  reload: {
    type: Function,
  },
})
const viewControls = ref({
  selections: [],
  updateSelections: (selections) => {
    viewControls.value.selections = Array.from(selections || [])
  },
})

const confirmDeleteInfo = ref({
  show: false,
  title: '',
  message: '',
  error: '',
  loading: false,
})

const linkedDocsResource = createResource({
  url: 'crm.api.doc.get_linked_docs_of_document',
  params: {
    doctype: props.doctype,
    docname: props.docname,
  },
  auto: true,
  validate(params) {
    if (!params?.doctype || !params?.docname) {
      return false
    }
  },
})

const linkedDocs = computed(() => {
  return (
    linkedDocsResource.data?.map((doc) => ({
      id: doc.reference_docname,
      ...doc,
    })) || []
  )
})

const cancel = () => {
  confirmDeleteInfo.value.show = false
  viewControls.value.updateSelections([])
}

const unlinkLinkedDoc = async (doc) => {
  let selectedDocs = []
  if (viewControls.value.selections.length > 0) {
    Array.from(viewControls.value.selections).forEach((selection) => {
      const docData = linkedDocs.value.find((d) => d.id == selection)
      selectedDocs.push({
        doctype: docData.reference_doctype,
        docname: docData.reference_docname,
      })
    })
  } else {
    selectedDocs = linkedDocs.value.map((doc) => ({
      doctype: doc.reference_doctype,
      docname: doc.reference_docname,
    }))
  }

  try {
    await call('crm.api.doc.remove_linked_doc_reference', {
    items: selectedDocs,
    remove_contact: props.doctype == 'Contact',
    delete: doc.delete,
    delete_lead_ticket: true,
      parent_doctype: props.doctype,
      parent_name: props.docname,
    })
    linkedDocsResource.reload()
    confirmDeleteInfo.value = { show: false, title: '', message: '', error: '', loading: false }
  } catch (e) {
    const msg = e?.messages?.[0] || e?.message || __('Unlink failed')
    confirmDeleteInfo.value.error = msg
    confirmDeleteInfo.value.loading = false
    throw e
  }
}


const confirmUnlink = () => {
  const items =
    viewControls.value.selections.length == 0
      ? 'all'
      : viewControls.value.selections.length
  confirmDeleteInfo.value = {
    show: true,
    title: __('Unlink linked item'),
    message: __('Are you sure you want to unlink {0} linked item(s)?', [items]),
    delete: false,
    error: '',
    loading: false,
  }
}

const removeDocLinks = async () => {
  await unlinkLinkedDoc({
    delete: confirmDeleteInfo.value.delete,
  })
  viewControls.value.updateSelections([])
}


const onConfirmAction = async () => {
  try {
    confirmDeleteInfo.value.loading = true
    await removeDocLinks()
    confirmDeleteInfo.value.show = false
  } catch (e) {
    // error already set in unlink function; keep modal open
  } finally {
    confirmDeleteInfo.value.loading = false
  }
}

const deleteDoc = async () => {
  try {
    // First, unlink any customer relationships if this is a lead or ticket
    if (['CRM Lead', 'CRM Ticket'].includes(props.doctype)) {
      const customer_id = await call('frappe.client.get_value', {
        doctype: props.doctype,
        name: props.docname,
        fieldname: 'customer_id'
      })
      
      if (customer_id && customer_id.message) {
        // Unlink the customer relationship first
        await call('crm.api.doc.remove_linked_doc_reference', {
          items: [{
            doctype: props.doctype,
            docname: props.docname
          }],
          remove_contact: false,
          delete: false,
          delete_lead_ticket: true
        })
      }
    }
    
    // Now delete the document
    await call('frappe.client.delete', {
      doctype: props.doctype,
      name: props.docname,
    })
    
    toast.success(`${props.doctype} deleted successfully`)
    router.push({ name: props.name })
    props?.reload?.()
  } catch (error) {
    console.error('❌ Deletion error:', error)
    toast.error(error.messages?.[0] || error.message || `Error deleting ${props.doctype}`)
  }
}
</script>
