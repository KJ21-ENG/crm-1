<!-- Ticket.vue -->
<template>
  <div class="flex h-full flex-col">
    <PageHeader>
      <template #breadcrumbs>
        <div class="flex items-center gap-2 text-base">
          <router-link
            :to="{ name: 'Tickets' }"
            class="text-ink-gray-6 hover:text-ink-gray-8"
          >
            {{ __('Tickets') }}
          </router-link>
          <FeatherIcon name="chevron-right" class="h-4 w-4 text-ink-gray-6" />
          <span class="text-ink-gray-8">{{ ticket?.doc?.ticket_subject || '' }}</span>
        </div>
      </template>
      <template #actions>
        <div class="flex items-center gap-2">
          <Button
            v-if="ticket?.doc?.status !== 'Closed'"
            variant="solid"
            :label="__('Update Status')"
            @click="showStatusUpdateModal = true"
          />
          <Button
            variant="outline"
            :label="__('Edit')"
            @click="showTicketModal = true"
          />
        </div>
      </template>
    </PageHeader>

    <div class="flex flex-1 gap-4 overflow-hidden p-4">
      <!-- Main Content -->
      <div class="flex flex-1 flex-col overflow-hidden rounded-lg border bg-white">
        <div class="flex border-b">
          <TabButtons v-model="activeTab" :options="tabOptions" />
        </div>
        <div class="flex-1 overflow-auto p-4">
          <!-- Activity Tab -->
          <div v-if="activeTab === 'activity'" class="space-y-4">
            <ActivityTimeline
              :activities="activities"
              :loading="activitiesLoading"
            />
          </div>

          <!-- Details Tab -->
          <div v-if="activeTab === 'details'" class="space-y-4">
            <FieldLayout
              v-if="tabs.data"
              :tabs="tabs.data"
              :data="ticket.doc"
              @change="handleFieldChange"
            />
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="w-80 space-y-4">
        <div class="rounded-lg border bg-white p-4">
          <h3 class="mb-3 font-medium">{{ __('Quick Info') }}</h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-ink-gray-6">{{ __('Status') }}</span>
              <StatusBadge :status="ticket?.doc?.status" />
            </div>
            <div class="flex items-center justify-between">
              <span class="text-ink-gray-6">{{ __('Priority') }}</span>
              <PriorityBadge :priority="ticket?.doc?.priority" />
            </div>
            <div class="flex items-center justify-between">
              <span class="text-ink-gray-6">{{ __('Department') }}</span>
              <span>{{ ticket?.doc?.department }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-ink-gray-6">{{ __('Assigned To') }}</span>
              <Avatar
                v-if="ticket?.doc?.assigned_to"
                :label="ticket.doc.assigned_to"
                size="sm"
              />
            </div>
          </div>
        </div>

        <div class="rounded-lg border bg-white p-4">
          <h3 class="mb-3 font-medium">{{ __('Customer Info') }}</h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-ink-gray-6">{{ __('Name') }}</span>
              <span>{{ ticket?.doc?.first_name }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-ink-gray-6">{{ __('Mobile') }}</span>
              <span>{{ ticket?.doc?.mobile_no }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-ink-gray-6">{{ __('Email') }}</span>
              <span>{{ ticket?.doc?.email }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <TicketModal
      v-model="showTicketModal"
      :ticket="ticket?.doc"
      mode="edit"
    />
    <StatusUpdateModal
      v-model="showStatusUpdateModal"
      :ticket="ticket?.doc"
      @update="handleStatusUpdate"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Avatar, FeatherIcon } from 'frappe-ui'
import { useDocument } from '@/data/document'
import { createResource } from 'frappe-ui'
import PageHeader from '@/components/PageHeader.vue'
import TabButtons from '@/components/TabButtons.vue'
import ActivityTimeline from '@/components/ActivityTimeline.vue'
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import StatusBadge from '@/components/Badges/StatusBadge.vue'
import PriorityBadge from '@/components/Badges/PriorityBadge.vue'
import TicketModal from '@/components/Modals/TicketModal.vue'
import StatusUpdateModal from '@/components/Modals/StatusUpdateModal.vue'

const props = defineProps({
  ticketId: {
    type: String,
    required: true,
  },
})

const router = useRouter()
const showTicketModal = ref(false)
const showStatusUpdateModal = ref(false)
const activeTab = ref('activity')
const activitiesLoading = ref(false)
const activities = ref([])

const tabOptions = [
  {
    label: __('Activity'),
    value: 'activity',
  },
  {
    label: __('Details'),
    value: 'details',
  },
]

const { document: ticket } = useDocument('CRM Ticket', props.ticketId)

const tabs = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  params: { doctype: 'CRM Ticket', type: 'Form' },
  auto: true,
})

// Load activities when tab changes
watch(activeTab, async (newTab) => {
  if (newTab === 'activity') {
    await loadActivities()
  }
})

async function loadActivities() {
  activitiesLoading.value = true
  try {
    const response = await createResource({
      url: 'crm.api.ticket.get_ticket_activities',
      params: { ticket: props.ticketId },
    }).submit()
    activities.value = response
  } catch (error) {
    console.error('Error loading activities:', error)
  }
  activitiesLoading.value = false
}

async function handleFieldChange(field, value) {
  await ticket.setValue(field, value)
}

async function handleStatusUpdate(newStatus) {
  await ticket.setValue('status', newStatus)
  showStatusUpdateModal.value = false
}

onMounted(() => {
  if (activeTab.value === 'activity') {
    loadActivities()
  }
})
</script> 