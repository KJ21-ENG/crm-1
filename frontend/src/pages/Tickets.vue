<!-- Tickets.vue -->
<template>
  <div class="flex h-full flex-col">
    <PageHeader>
      <template #title>{{ __('Tickets') }}</template>
      <template #actions>
        <Button
          variant="solid"
          :label="__('New Ticket')"
          @click="showTicketModal = true"
        >
          <template #prefix>
            <TicketIcon class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </PageHeader>

    <div class="flex flex-1 flex-col overflow-hidden p-4">
      <!-- Debug info -->
      <div v-if="tickets.loading" class="text-gray-600">
        Loading tickets...
      </div>
      <div v-else-if="tickets.error" class="text-red-600">
        Error: {{ tickets.error }}
      </div>
      <div v-else>
        <div class="mb-4 text-sm text-gray-600">
          Found {{ tickets.data?.length || 0 }} tickets
        </div>
        
        <!-- Simple list view for debugging -->
        <div v-if="tickets.data?.length" class="space-y-4">
          <div v-for="ticket in tickets.data" :key="ticket.name" 
            class="rounded-lg border border-gray-200 p-4 hover:bg-gray-50"
          >
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium">{{ ticket.ticket_subject }}</div>
                <div class="text-sm text-gray-600">{{ ticket.first_name }}</div>
              </div>
              <div class="flex items-center gap-3">
                <StatusBadge :status="ticket.status" />
                <PriorityBadge :priority="ticket.priority" />
                <div class="text-sm text-gray-600">
                  {{ formatDate(ticket.creation) }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="flex h-full items-center justify-center">
          <div class="flex flex-col items-center gap-3 text-xl font-medium text-gray-400">
            <TicketIcon class="h-10 w-10" />
            <span>{{ __('No Tickets Found') }}</span>
            <Button :label="__('Create')" @click="showTicketModal = true">
              <template #prefix>
                <FeatherIcon name="plus" class="h-4" />
              </template>
            </Button>
          </div>
        </div>
      </div>
    </div>

    <TicketModal 
      v-model="showTicketModal" 
      @ticket-created="handleTicketCreated"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Button, FeatherIcon } from 'frappe-ui'
import { createResource } from 'frappe-ui'
import { formatDate } from '@/utils'
import PageHeader from '@/components/PageHeader.vue'
import TicketIcon from '@/components/Icons/TicketIcon.vue'
import TicketModal from '@/components/Modals/TicketModal.vue'
import StatusBadge from '@/components/Badges/StatusBadge.vue'
import PriorityBadge from '@/components/Badges/PriorityBadge.vue'

const router = useRouter()
const showTicketModal = ref(false)

// Use createResource for simpler data fetching
const tickets = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Ticket',
    fields: ['name', 'ticket_subject', 'first_name', 'status', 'priority', 'creation'],
    order_by: 'creation desc',
    limit: 50
  },
  auto: true
})

function handleTicketCreated() {
  console.log('Ticket created, refreshing list...')
  tickets.reload()
}
</script> 