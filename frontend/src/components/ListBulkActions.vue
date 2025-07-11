<template>
  <EditValueModal
    v-if="showEditModal"
    v-model="showEditModal"
    :doctype="doctype"
    :selectedValues="selectedValues"
    @reload="reload"
  />
  <AssignmentModal
    v-if="showAssignmentModal"
    v-model="showAssignmentModal"
    v-model:assignees="bulkAssignees"
    :docs="selectedValues"
    :doctype="doctype"
    @reload="reload"
  />
  <DeleteLinkedDocModal
    v-if="showDeleteDocModal.showLinkedDocsModal"
    v-model="showDeleteDocModal.showLinkedDocsModal"
    :doctype="props.doctype"
    :docname="showDeleteDocModal.docname"
    :reload="reload"
  />
  <BulkDeleteLinkedDocModal
    v-if="showDeleteDocModal.showDeleteModal"
    v-model="showDeleteDocModal.showDeleteModal"
    :doctype="props.doctype"
    :items="showDeleteDocModal.items"
    :reload="reload"
  />
</template>

<script setup>
import EditValueModal from '@/components/Modals/EditValueModal.vue'
import AssignmentModal from '@/components/Modals/AssignmentModal.vue'
import { setupListCustomizations } from '@/utils'
import { globalStore } from '@/stores/global'
import { capture } from '@/telemetry'
import { call, toast } from 'frappe-ui'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  doctype: {
    type: String,
    default: '',
  },
  options: {
    type: Object,
    default: () => ({
      hideEdit: false,
      hideDelete: false,
      hideAssign: false,
    }),
  },
})

const list = defineModel()

const router = useRouter()

const { $dialog, $socket } = globalStore()

const showEditModal = ref(false)
const selectedValues = ref([])
const unselectAllAction = ref(() => {})
const showDeleteDocModal = ref({
  showLinkedDocsModal: false,
  showDeleteModal: false,
  docname: null,
})
function editValues(selections, unselectAll) {
  selectedValues.value = selections
  showEditModal.value = true
  unselectAllAction.value = unselectAll
}

function convertToDeal(selections, unselectAll) {
  $dialog({
    title: __('Convert to Deal'),
    message: __('Are you sure you want to convert {0} Lead(s) to Deal(s)?', [
      selections.size,
    ]),
    variant: 'solid',
    theme: 'blue',
    actions: [
      {
        label: __('Convert'),
        variant: 'solid',
        onClick: (close) => {
          capture('bulk_convert_to_deal')
          Array.from(selections).forEach((name) => {
            call('crm.fcrm.doctype.crm_lead.crm_lead.convert_to_deal', {
              lead: name,
            }).then(() => {
              toast.success(__('Converted successfully'))
              list.value.reload()
              unselectAll()
              close()
            })
          })
        },
      },
    ],
  })
}

function deleteValues(selections, unselectAll) {
  const selectedDocs = Array.from(selections)
  if (selectedDocs.length == 1) {
    showDeleteDocModal.value = {
      showLinkedDocsModal: true,
      docname: selectedDocs[0],
    }
  } else {
    showDeleteDocModal.value = {
      showDeleteModal: true,
      items: selectedDocs,
    }
  }
}

const showAssignmentModal = ref(false)
const bulkAssignees = ref([])

function assignValues(selections, unselectAll) {
  showAssignmentModal.value = true
  selectedValues.value = selections
  unselectAllAction.value = unselectAll
}

function clearAssignemnts(selections, unselectAll) {
  $dialog({
    title: __('Clear Assignment'),
    message: __('Are you sure you want to clear assignment for {0} item(s)?', [
      selections.size,
    ]),
    variant: 'solid',
    theme: 'red',
    actions: [
      {
        label: __('Clear Assignment'),
        variant: 'solid',
        theme: 'red',
        onClick: (close) => {
          capture('bulk_clear_assignment')
          call('frappe.desk.form.assign_to.remove_multiple', {
            doctype: props.doctype,
            names: JSON.stringify(Array.from(selections)),
            ignore_permissions: true,
          }).then(() => {
            toast.success(__('Assignment cleared successfully'))
            reload(unselectAll)
            close()
          })
        },
      },
    ],
  })
}

function bulkUpdateTicketStatus(selections, unselectAll) {
  let selectedTickets = Array.from(selections)
  
  $dialog({
    title: __('Update Ticket Status'),
    fields: [
      {
        fieldtype: 'Select',
        fieldname: 'status',
        label: __('New Status'),
        options: ['New', 'Open', 'In Progress', 'Pending Customer', 'Resolved', 'Closed'],
        reqd: 1,
      },
    ],
    primary_action_label: __('Update Status'),
    primary_action: (values) => {
      if (values.status) {
        capture('bulk_update_ticket_status')
        call('crm.api.ticket.bulk_update_tickets', {
          ticket_names: selectedTickets,
          updates: { status: values.status }
        }).then(() => {
          toast.success(__('Status updated successfully for {0} tickets', [selectedTickets.length]))
          reload(unselectAll)
        }).catch((error) => {
          toast.error(__('Error updating status: {0}', [error.message]))
        })
      }
    },
  })
}

function bulkSetTicketPriority(selections, unselectAll) {
  let selectedTickets = Array.from(selections)
  
  $dialog({
    title: __('Set Ticket Priority'),
    fields: [
      {
        fieldtype: 'Select',
        fieldname: 'priority',
        label: __('Priority'),
        options: ['Low', 'Medium', 'High', 'Urgent'],
        reqd: 1,
      },
    ],
    primary_action_label: __('Set Priority'),
    primary_action: (values) => {
      if (values.priority) {
        capture('bulk_set_ticket_priority')
        call('crm.api.ticket.bulk_set_priority', {
          ticket_names: selectedTickets,
          priority: values.priority
        }).then(() => {
          toast.success(__('Priority updated successfully for {0} tickets', [selectedTickets.length]))
          reload(unselectAll)
        }).catch((error) => {
          toast.error(__('Error updating priority: {0}', [error.message]))
        })
      }
    },
  })
}

function bulkCloseTickets(selections, unselectAll) {
  let selectedTickets = Array.from(selections)
  
  $dialog({
    title: __('Close Tickets'),
    message: __('Are you sure you want to close {0} ticket(s)?', [selectedTickets.length]),
    fields: [
      {
        fieldtype: 'Text',
        fieldname: 'resolution',
        label: __('Resolution (Optional)'),
        placeholder: __('Enter resolution details...'),
      },
    ],
    variant: 'solid',
    theme: 'red',
    primary_action_label: __('Close Tickets'),
    primary_action: (values) => {
      capture('bulk_close_tickets')
      call('crm.api.ticket.bulk_close_tickets', {
        ticket_names: selectedTickets,
        resolution: values.resolution || null
      }).then(() => {
        toast.success(__('Successfully closed {0} tickets', [selectedTickets.length]))
        reload(unselectAll)
      }).catch((error) => {
        toast.error(__('Error closing tickets: {0}', [error.message]))
      })
    },
  })
}

const customBulkActions = ref([])
const customListActions = ref([])

function bulkActions(selections, unselectAll) {
  let actions = []

  if (!props.options.hideEdit) {
    actions.push({
      label: __('Edit'),
      onClick: () => editValues(selections, unselectAll),
    })
  }

  if (!props.options.hideDelete) {
    actions.push({
      label: __('Delete'),
      onClick: () => deleteValues(selections, unselectAll),
    })
  }

  if (!props.options.hideAssign) {
    actions.push({
      label: __('Assign To'),
      onClick: () => assignValues(selections, unselectAll),
    })
    actions.push({
      label: __('Clear Assignment'),
      onClick: () => clearAssignemnts(selections, unselectAll),
    })
  }

  if (props.doctype === 'CRM Lead') {
    actions.push({
      label: __('Convert to Deal'),
      onClick: () => convertToDeal(selections, unselectAll),
    })
  }

  if (props.doctype === 'CRM Ticket') {
    actions.push({
      label: __('Update Status'),
      onClick: () => bulkUpdateTicketStatus(selections, unselectAll),
    })
    actions.push({
      label: __('Set Priority'),
      onClick: () => bulkSetTicketPriority(selections, unselectAll),
    })
    actions.push({
      label: __('Close Tickets'),
      onClick: () => bulkCloseTickets(selections, unselectAll),
    })
  }

  customBulkActions.value.forEach((action) => {
    actions.push({
      label: __(action.label),
      onClick: () =>
        action.onClick({
          list: list.value,
          selections,
          unselectAll,
          call,
          createToast: toast.create,
          toast,
          $dialog,
          router,
        }),
    })
  })
  return actions
}

function reload(unselectAll) {
  unselectAllAction.value?.()
  unselectAll?.()
  list.value?.reload()
}

onMounted(async () => {
  if (!list.value?.data) return
  let customization = await setupListCustomizations(list.value.data, {
    list: list.value,
    call,
    createToast: toast.create,
    toast,
    $dialog,
    $socket,
    router,
  })
  customBulkActions.value =
    customization?.bulkActions || list.value?.data?.bulkActions || []
  customListActions.value =
    customization?.actions || list.value?.data?.listActions || []
})

defineExpose({
  bulkActions,
  customListActions,
})
</script>
