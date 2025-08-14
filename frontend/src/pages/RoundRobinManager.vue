<template>
	<div class="p-4 space-y-6">
		<div class="flex items-center justify-between">
			<div>
				<h1 class="text-xl font-semibold">{{ __('Round Robin Manager') }}</h1>
				<p class="text-sm text-ink-gray-7 mt-1">{{ __('Monitor rotation, pools and history for each role. Use Reset Pointer to restart the cycle.') }}</p>
			</div>
			<div class="flex items-center gap-2">
				<Button :loading="loading" @click="reload">{{ __('Refresh') }}</Button>
			</div>
		</div>

		<div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
			<Card v-for="role in roles" :key="role.role" class="p-0 overflow-hidden">
				<!-- Header -->
				<div class="flex items-center justify-between border-b p-3">
					<div>
						<div class="text-base font-medium">{{ role.role }}</div>
						<div class="text-xs text-ink-gray-7">
							{{ __('Users') }}: {{ role.user_count }}
						</div>
					</div>
					<div class="flex items-center gap-2">
						<Button variant="subtle" size="sm" :loading="resetting[role.role]" @click="reset(role.role)">
							{{ __('Reset Pointer') }}
						</Button>
					</div>
				</div>

				<!-- Body -->
				<div class="p-3 space-y-4">
					<!-- Next up & pointer info -->
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<Avatar
								v-if="status[role.role]?.next_user"
								:size="'sm'"
								:image="getUser(status[role.role].next_user)?.user_image"
								:label="getUser(status[role.role].next_user)?.full_name || status[role.role].next_user"
							/>
							<div class="text-sm">
								<div class="font-medium">{{ __('Next up') }}</div>
								<div class="text-ink-gray-7">{{ displayName(status[role.role]?.next_user) || __('N/A') }}</div>
							</div>
						</div>
						<div class="text-xs text-ink-gray-7"></div>
					</div>
					<div class="h-2 rounded bg-ink-gray-2 overflow-hidden border border-ink-gray-4">
						<div class="h-2 bg-blue-500" :style="{ width: pointerPercent(role) + '%' }"></div>
					</div>

					<!-- Pool -->
					<div>
						<div class="text-xs font-medium mb-2">{{ __('Pool') }}</div>
						<div class="flex flex-wrap gap-1.5">
							<span v-for="name in role.user_names" :key="name" class="inline-flex items-center gap-1 rounded bg-ink-gray-2 px-2 py-0.5 text-xs">
								<Avatar :size="'xs'" :label="name" />
								<span>{{ name }}</span>
							</span>
						</div>
					</div>

					<!-- History -->
					<div>
						<div class="text-xs font-medium mb-2">{{ __('Recent Assignments') }}</div>
						<div v-if="(history[role.role] || []).length" class="space-y-1">
							<div v-for="h in (history[role.role] || []).slice(-5)" :key="(h.assigned_on || '') + '-' + h.user" class="flex items-center justify-between text-xs">
								<div class="truncate">
									<b>{{ h.user_full_name || h.user }}</b>
									<span class="ml-1 text-ink-gray-7">→ {{ h.document_type }} {{ h.document_name }}</span>
								</div>
								<div class="text-ink-gray-6 ml-2 whitespace-nowrap">{{ formatDateSafe(h.assigned_on) }}</div>
							</div>
						</div>
						<div v-else class="text-xs text-ink-gray-6">{{ __('No recent assignments') }}</div>
					</div>
				</div>
			</Card>
		</div>
	</div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { createResource, call, Card, Button } from 'frappe-ui'
import { usersStore } from '@/stores/users'
import { formatDate } from '@/utils'

const roles = ref([])
const status = reactive({})
const history = reactive({})
const loading = ref(false)
const resetting = reactive({})
const { getUser } = usersStore()

const rolesRes = createResource({
	url: 'crm.api.role_assignment.get_assignable_roles',
	auto: true,
	onSuccess(data) {
		roles.value = (data || []).filter(r => r.enabled)
		// Kick off status + history in parallel for fast paint
		Promise.allSettled([refreshStatuses(), refreshHistory()])
	}
})

async function refreshStatuses() {
	await Promise.all(
		roles.value.map(async (r) => {
			try {
				const res = await call('crm.api.role_assignment.get_role_assignment_status', { role_name: r.role })
				status[r.role] = res?.data || {}
			} catch (e) {
				status[r.role] = {}
			}
		})
	)
}

async function refreshHistory() {
	await Promise.all(
		roles.value.map(async (r) => {
			try {
				const res = await call('crm.api.role_assignment.get_assignment_history', { role_name: r.role, limit: 5 })
				history[r.role] = Array.isArray(res) ? res : []
			} catch (e) {
				history[r.role] = []
			}
		})
	)
}

async function reload() {
	loading.value = true
	try {
		await rolesRes.reload()
		await refreshStatuses()
		await refreshHistory()
	} finally {
		loading.value = false
	}
}

async function reset(role) {
	resetting[role] = true
	try {
		await call('crm.api.role_assignment.reset_role_assignment', { role_name: role })
		await refreshStatuses()
	} finally {
		resetting[role] = false
	}
}

onMounted(async () => {
	await reload()
})

function displayName(userId) {
	if (!userId) return ''
	const u = getUser(userId)
	return u?.full_name || userId
}

function pointerPercent(role) {
	const s = status[role.role] || {}
	const total = s.total_users || 0
	if (!total) return 0
	const pos = s.current_position || 0
	return Math.round((pos / total) * 100)
}

function formatDateSafe(d) {
	try {
		return d ? formatDate(d, 'D MMM, h:mm a') : ''
	} catch (e) {
		return ''
	}
}
</script>

<style scoped>
</style>


