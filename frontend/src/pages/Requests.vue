<template>
  <div class="p-5 space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold">{{ __('Assignment Requests') }}</h1>
      <div class="flex items-center gap-2">
        <select v-model="filterStatus" class="form-control">
          <option value="">{{ __('All') }}</option>
          <option value="Pending">{{ __('Pending') }}</option>
          <option value="Approved">{{ __('Approved') }}</option>
          <option value="Rejected">{{ __('Rejected') }}</option>
        </select>
        <Button @click="reload" variant="outline">{{ __('Reload') }}</Button>
      </div>
    </div>

    <div class="bg-white border rounded-md">
      <div class="grid grid-cols-7 gap-3 px-4 py-2 text-xs font-medium text-ink-gray-6 border-b">
        <div>{{ __('Created') }}</div>
        <div>{{ __('DocType') }}</div>
        <div>{{ __('Name') }}</div>
        <div>{{ __('Requested User') }}</div>
        <div>{{ __('Requested By') }}</div>
        <div>{{ __('Status') }}</div>
        <div class="text-right">{{ __('Actions') }}</div>
      </div>
      <div v-if="requests.data?.length" class="divide-y">
        <div v-for="r in requests.data" :key="r.name" class="grid grid-cols-7 gap-3 px-4 py-2 items-center text-sm">
          <div>{{ formatDate(r.creation) }}</div>
          <div>{{ r.reference_doctype }}</div>
          <div>
            <RouterLink :to="linkFor(r)">
              <span class="text-primary-600 hover:underline">{{ r.reference_name }}</span>
            </RouterLink>
          </div>
          <div>{{ r.requested_user }}</div>
          <div>{{ r.requested_by }}</div>
          <div>
            <span :class="badgeClass(r.status)" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">{{ r.status }}</span>
          </div>
          <div class="text-right flex items-center justify-end gap-2">
            <Button v-if="isAdmin && r.status==='Pending'" size="sm" variant="solid" @click="approve(r)">{{ __('Approve') }}</Button>
            <Button v-if="isAdmin && r.status==='Pending'" size="sm" variant="subtle" theme="red" @click="reject(r)">{{ __('Reject') }}</Button>
          </div>
        </div>
      </div>
      <div v-else class="p-6 text-center text-ink-gray-6 text-sm">{{ __('No requests found') }}</div>
    </div>
  </div>
</template>

<script setup>
import { createResource, call } from 'frappe-ui'
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { usersStore } from '@/stores/users'
import { formatDate } from '@/utils'

const { isAdmin } = usersStore()

// Protect page on mount: only admin users
if (!isAdmin()) {
  // redirect to dashboard
  const r = useRouter()
  r.replace({ name: 'Dashboard' })
}

const filterStatus = ref('Pending')

const requests = createResource({
  url: 'crm.api.assignment_requests.get_assignment_requests',
  makeParams: () => ({ status: filterStatus.value }),
  auto: true,
})

function reload() { requests.fetch() }

watch(filterStatus, () => reload())

function badgeClass(status) {
  switch (status) {
    case 'Pending': return 'bg-yellow-100 text-yellow-800'
    case 'Approved': return 'bg-green-100 text-green-800'
    case 'Rejected': return 'bg-red-100 text-red-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

function linkFor(r) {
  if (r.reference_doctype === 'CRM Lead') {
    return { name: 'Lead', params: { leadId: r.reference_name } }
  }
  if (r.reference_doctype === 'CRM Ticket') {
    return { name: 'Ticket', params: { ticketId: r.reference_name } }
  }
  return { name: 'Dashboard' }
}

async function approve(r) {
  const res = await call('crm.api.assignment_requests.approve_assignment_request', { name: r.name })
  if (res?.success) reload()
}

async function reject(r) {
  const reason = window.prompt('Enter rejection reason (optional)')
  const res = await call('crm.api.assignment_requests.reject_assignment_request', { name: r.name, reason })
  if (res?.success) reload()
}
</script>


