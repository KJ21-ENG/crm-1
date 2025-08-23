<template>
  <div class="p-8">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <h2 class="text-xl font-semibold">{{ __('Office Settings') }}</h2>
      </div>
      <div class="flex items-center gap-2">
        <Button :loading="saving" variant="solid" @click="saveAll">{{ __('Update') }}</Button>
      </div>
    </div>

    <div>
      <div class="flex border-b mb-4">
        <button :class="['px-4 py-2', activeTab === 'hours' ? 'border-b-2 border-ink-gray-8' : 'text-gray-500']" @click="activeTab = 'hours'">{{ __('Office Hours') }}</button>
        <button :class="['px-4 py-2', activeTab === 'holidays' ? 'border-b-2 border-ink-gray-8' : 'text-gray-500']" @click="activeTab = 'holidays'">{{ __('Holidays') }}</button>
      </div>

      <div v-if="activeTab === 'hours'" class="space-y-4">
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

      <div v-if="activeTab === 'holidays'" class="space-y-4">
        <div class="flex items-center gap-2">
          <div class="w-48">
            <CustomDateTimePicker v-model="holidayDate" mode="date" :input-class="'border px-2 py-1 rounded w-full'" :placeholder="__('Choose date')" />
          </div>
          <input type="text" v-model="holidayDesc" placeholder="Description" class="px-2 py-1 border rounded w-64" />
          <Button @click="addHoliday">{{ __('Add') }}</Button>
        </div>

        <div v-if="holidays.length === 0" class="text-gray-500">{{ __('No holidays added') }}</div>
        <div v-else class="space-y-2">
          <div v-for="h in holidays" :key="h.name" class="flex items-center justify-between border p-2 rounded">
            <div>{{ h.date }} — {{ h.description }}</div>
            <div>
              <Button variant="outline" @click="removeHoliday(h)">{{ __('Delete') }}</Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createResource, call, toast, Button } from 'frappe-ui'
import CustomDateTimePicker from '@/components/CustomDateTimePicker.vue'

const saving = ref(false)
const rows = ref([])

const weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

const activeTab = ref('hours')

const holidays = ref([])
const holidayDate = ref('')
const holidayDesc = ref('')

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
    await loadHolidays()
  } catch (e) {
    toast.error(__('Failed to load office hours'))
  }
}

async function loadHolidays() {
  try {
    const res = await call('crm.api.office_hours.get_holidays')
    holidays.value = res || []
  } catch (e) {
    toast.error(__('Failed to load holidays'))
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

async function addHoliday() {
  if (!holidayDate.value) return toast.error(__('Please select a date'))
  try {
    const res = await call('crm.api.office_hours.save_holidays', { days: JSON.stringify([{ date: holidayDate.value, description: holidayDesc.value }]) })
    await loadHolidays()
    holidayDate.value = ''
    holidayDesc.value = ''
    toast.success(__('Holiday added'))
  } catch (e) {
    toast.error(__('Failed to add holiday'))
  }
}

async function removeHoliday(h) {
  try {
    await call('frappe.client.delete', { doctype: 'CRM Holiday', name: h.name })
    await loadHolidays()
    toast.success(__('Holiday removed'))
  } catch (e) {
    toast.error(__('Failed to remove holiday'))
  }
}

onMounted(load)
</script>



