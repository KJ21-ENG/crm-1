<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs routeName="Celebrations" />
      </template>
      <template #right-header>
        <Button :label="__('Refresh')" @click="celebrations.reload()" :loading="celebrations.loading">
          <template #icon>
            <FeatherIcon name="refresh-cw" class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-auto p-5">
      <div class="mb-6 rounded-xl border border-amber-200 bg-gradient-to-r from-amber-50 via-white to-rose-50 p-5 shadow-sm">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-full bg-amber-100">
            <FeatherIcon name="gift" class="h-5 w-5 text-amber-700" />
          </div>
          <div>
            <h1 class="text-xl font-semibold text-gray-900">Today's Celebrations</h1>
            <p class="text-sm text-gray-600">
              Customers to personally greet today.
            </p>
          </div>
        </div>
      </div>

      <div v-if="celebrations.loading" class="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <div
          v-for="section in 2"
          :key="section"
          class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
        >
          <div class="animate-pulse space-y-3">
            <div class="h-4 w-1/3 rounded bg-gray-200"></div>
            <div class="h-12 rounded bg-gray-100"></div>
            <div class="h-12 rounded bg-gray-100"></div>
            <div class="h-12 rounded bg-gray-100"></div>
          </div>
        </div>
      </div>

      <Alert v-else-if="celebrations.error" variant="error" class="mb-4">
        <div class="flex items-center">
          <FeatherIcon name="alert-circle" class="mr-2 h-5 w-5" />
          {{ celebrations.error }}
        </div>
      </Alert>

      <div v-else-if="!totalCelebrations" class="rounded-xl border border-dashed border-gray-200 bg-white p-8 text-center text-sm text-gray-500 shadow-sm">
        No birthdays or anniversaries today.
      </div>

      <div v-else class="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <section class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-sm font-semibold text-gray-900">Birthdays</h2>
            <Badge variant="orange" size="sm">
              {{ `${birthdays.length}` }}
            </Badge>
          </div>

          <div v-if="birthdays.length" class="space-y-3">
            <div
              v-for="customer in birthdays"
              :key="customer.name"
              class="rounded-lg border border-gray-100 px-3 py-3 transition-colors hover:border-amber-200 hover:bg-amber-50"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ customer.customer_name }}</p>
                  <p v-if="customer.organization" class="mt-1 text-xs text-gray-500">
                    {{ customer.organization }}
                  </p>
                  <p class="mt-1 text-xs text-gray-600">
                    {{ customer.mobile_no || 'No mobile number' }}
                  </p>
                </div>
                <div class="text-right">
                  <p class="text-xs font-medium uppercase tracking-wide text-amber-700">Birthday</p>
                  <p class="mt-1 text-xs text-gray-500">{{ formatCelebrationDate(customer.date_of_birth) }}</p>
                </div>
              </div>

              <div class="mt-3 flex items-center justify-between gap-3">
                <Button variant="ghost" @click="openCustomer(customer.name)">
                  <template #icon>
                    <FeatherIcon name="external-link" class="h-4 w-4" />
                  </template>
                  {{ __('Open Customer') }}
                </Button>
                <Badge v-if="customer.contacted" variant="green" size="sm">
                  Contacted
                </Badge>
                <Button
                  v-else
                  :loading="markingKey === `Birthday-${customer.name}`"
                  @click="markCelebrationContacted(customer.name, 'Birthday')"
                >
                  <template #icon>
                    <FeatherIcon name="check-circle" class="h-4 w-4" />
                  </template>
                  {{ __('Mark as contacted') }}
                </Button>
              </div>
            </div>
          </div>
          <div v-else class="rounded-lg bg-gray-50 px-3 py-4 text-sm text-gray-500">
            No birthdays today.
          </div>
        </section>

        <section class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-sm font-semibold text-gray-900">Anniversaries</h2>
            <Badge variant="red" size="sm">
              {{ `${anniversaries.length}` }}
            </Badge>
          </div>

          <div v-if="anniversaries.length" class="space-y-3">
            <div
              v-for="customer in anniversaries"
              :key="customer.name"
              class="rounded-lg border border-gray-100 px-3 py-3 transition-colors hover:border-rose-200 hover:bg-rose-50"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ customer.customer_name }}</p>
                  <p v-if="customer.organization" class="mt-1 text-xs text-gray-500">
                    {{ customer.organization }}
                  </p>
                  <p class="mt-1 text-xs text-gray-600">
                    {{ customer.mobile_no || 'No mobile number' }}
                  </p>
                </div>
                <div class="text-right">
                  <p class="text-xs font-medium uppercase tracking-wide text-rose-700">Anniversary</p>
                  <p class="mt-1 text-xs text-gray-500">{{ formatCelebrationDate(customer.anniversary) }}</p>
                </div>
              </div>

              <div class="mt-3 flex items-center justify-between gap-3">
                <Button variant="ghost" @click="openCustomer(customer.name)">
                  <template #icon>
                    <FeatherIcon name="external-link" class="h-4 w-4" />
                  </template>
                  {{ __('Open Customer') }}
                </Button>
                <Badge v-if="customer.contacted" variant="green" size="sm">
                  Contacted
                </Badge>
                <Button
                  v-else
                  :loading="markingKey === `Anniversary-${customer.name}`"
                  @click="markCelebrationContacted(customer.name, 'Anniversary')"
                >
                  <template #icon>
                    <FeatherIcon name="check-circle" class="h-4 w-4" />
                  </template>
                  {{ __('Mark as contacted') }}
                </Button>
              </div>
            </div>
          </div>
          <div v-else class="rounded-lg bg-gray-50 px-3 py-4 text-sm text-gray-500">
            No anniversaries today.
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createResource, FeatherIcon, Alert, Badge, call, toast } from 'frappe-ui'

const router = useRouter()

const celebrations = createResource({
  url: 'crm.api.dashboard.get_today_celebrations',
  auto: true,
  transform(data) {
    return data?.message || data || { birthdays: [], anniversaries: [] }
  },
})

const birthdays = computed(() => celebrations.data?.birthdays || [])
const anniversaries = computed(() => celebrations.data?.anniversaries || [])
const totalCelebrations = computed(() => birthdays.value.length + anniversaries.value.length)
const markingKey = ref('')

function formatCelebrationDate(value) {
  if (!value) return ''
  if (typeof value === 'string') {
    const match = value.match(/^(\d{4})-(\d{2})-(\d{2})/)
    if (match) {
      const [, year, month, day] = match
      const date = new Date(Number(year), Number(month) - 1, Number(day))
      return date.toLocaleDateString(undefined, { day: 'numeric', month: 'short' })
    }
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleDateString(undefined, { day: 'numeric', month: 'short' })
}

function openCustomer(customerName) {
  if (!customerName) return
  router.push({ name: 'Customer', params: { customerId: customerName } })
}

async function markCelebrationContacted(customerId, celebrationType) {
  markingKey.value = `${celebrationType}-${customerId}`
  try {
    const response = await call('crm.api.dashboard.mark_celebration_contacted', {
      customer_id: customerId,
      celebration_type: celebrationType,
    })
    celebrations.data = response
    window.dispatchEvent(new Event('crm:celebrations-updated'))
    toast.success(__('Marked as contacted'))
  } catch (error) {
    toast.error(error.message || __('Failed to mark as contacted'))
  } finally {
    markingKey.value = ''
  }
}
</script>
