<template>
  <Dialog v-model="show">
    <template #body>
      <div class="bg-surface-modal px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
              {{ __('Update Status') }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button variant="ghost" class="w-7" @click="show = false">
              <template #icon>
                <FeatherIcon name="x" class="size-4" />
              </template>
            </Button>
          </div>
        </div>
        <div class="space-y-4">
          <div class="space-y-2">
            <label class="text-sm font-medium text-ink-gray-7">
              {{ __('Current Status') }}
            </label>
            <div>
              <StatusBadge :status="ticket?.status" />
            </div>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium text-ink-gray-7">
              {{ __('New Status') }}
            </label>
            <div>
              <Select
                v-model="newStatus"
                :options="statusOptions"
                :placeholder="__('Select Status')"
              />
            </div>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium text-ink-gray-7">
              {{ __('Comment') }}
            </label>
            <div>
              <Textarea
                v-model="comment"
                :placeholder="__('Add a comment about this status change...')"
                rows="3"
              />
            </div>
          </div>
        </div>
      </div>
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="flex flex-row-reverse gap-2">
          <Button
            variant="solid"
            :label="__('Update')"
            :loading="isUpdating"
            :disabled="!newStatus || newStatus === ticket?.status"
            @click="updateStatus"
          />
          <Button
            variant="outline"
            :label="__('Cancel')"
            @click="show = false"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref } from 'vue'
import { Button, Select, Textarea, FeatherIcon } from 'frappe-ui'
import { createResource } from 'frappe-ui'
import StatusBadge from '@/components/Badges/StatusBadge.vue'

const props = defineProps({
  ticket: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['update'])
const show = defineModel()
const newStatus = ref('')
const comment = ref('')
const isUpdating = ref(false)

const statusOptions = [
  { label: 'New', value: 'New' },
  { label: 'Open', value: 'Open' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'Pending Customer', value: 'Pending Customer' },
  { label: 'Resolved', value: 'Resolved' },
  { label: 'Closed', value: 'Closed' },
]

const updateTicketStatus = createResource({
  url: 'crm.api.ticket.update_ticket_status',
  makeParams(values) {
    return {
      ticket: props.ticket.name,
      status: values.status,
      comment: values.comment,
    }
  },
})

async function updateStatus() {
  isUpdating.value = true
  try {
    await updateTicketStatus.submit({
      status: newStatus.value,
      comment: comment.value,
    })
    emit('update', newStatus.value)
    show.value = false
  } catch (error) {
    console.error('Error updating status:', error)
  }
  isUpdating.value = false
}
</script> 