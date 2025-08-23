<template>
  <div class="p-8">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-semibold">{{ __('Office Hours') }}</h2>
      <Button :loading="saving" variant="solid" @click="saveAll">{{ __('Update') }}</Button>
    </div>

    <div class="space-y-4">
      <div v-for="(row, idx) in rows" :key="row.workday" class="flex items-center gap-4">
        <div class="w-48">{{ __(row.workday) }}</div>
        <input type="time" class="px-2 py-1 border rounded" v-model="row.start_time" />
        <span class="text-gray-400">to</span>
        <input type="time" class="px-2 py-1 border rounded" v-model="row.end_time" />
        <label class="ml-4 flex items-center gap-2">
          <input type="checkbox" v-model="row.office_open" />
          <span class="text-sm text-gray-600">{{ __('Open') }}</span>
        </label>
        <div class="ml-4 text-sm text-red-600" v-if="row.error">{{ row.error }}</div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createResource, call, toast, Button } from 'frappe-ui'

const saving = ref(false)
const rows = ref([])

const weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

async function load() {
  try {
    const res = await call('crm.api.office_hours.get_office_hours')

    // Normalize to have one entry per weekday
    const map = {}
    ;(res || []).forEach(r => map[r.workday] = { ...r })

    rows.value = weekdays.map(w => {
      const existing = map[w]
      return {
        name: existing?.name || null,
        workday: w,
        start_time: existing?.start_time ? existing.start_time.substr(0,5) : '',
        end_time: existing?.end_time ? existing.end_time.substr(0,5) : '',
        office_open: existing?.office_open === 0 || existing?.office_open === '0' || existing?.office_open === false ? false : true,
        error: ''
      }
    })
  } catch (e) {
    toast.error(__('Failed to load office hours'))
  }
}

function validateRow(row) {
  row.error = ''
  row.error = ''
  // If office is closed for that day, skip validation
  if (row.office_open === false || row.office_open === '0') return true

  if (!row.start_time || !row.end_time) {
    row.error = __('Start and end times are required when office is open')
    return false
  }
  // start_time and end_time are HH:MM strings
  if (row.start_time >= row.end_time) {
    row.error = __('Start time must be before end time')
    return false
  }
  return true
}

async function saveAll() {
  // validate
  let ok = true
  for (const r of rows.value) {
    if (!validateRow(r)) ok = false
  }
  if (!ok) {
    toast.error(__('Please fix validation errors'))
    return
  }

  saving.value = true
  try {
    const payload = []
    for (const r of rows.value) {
      // convert to HH:MM:SS if non-empty
      const start = r.start_time ? r.start_time + ':00' : ''
      const end = r.end_time ? r.end_time + ':00' : ''

      // collect and send batched payload to server
      payload.push({ name: r.name, workday: r.workday, start_time: start, end_time: end, office_open: !!r.office_open })
    }

    // call backend batch save
    await call('crm.api.office_hours.save_office_hours', { days: payload })
    toast.success(__('Office hours updated'))
    await load()
  } catch (e) {
    toast.error(__('Failed to save office hours'))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>



