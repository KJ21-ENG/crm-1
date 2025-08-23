<template>
  <div class="flex h-full flex-col gap-6 p-6 text-ink-gray-8">
    <div class="flex justify-between px-2 pt-2">
      <div class="flex flex-col gap-1 w-9/12">
        <h2 class="flex gap-2 text-xl font-semibold leading-none h-5">
          {{ __('Office Hours') }}
        </h2>
        <p class="text-p-base text-ink-gray-6">
          {{ __('Control auto-assign and reassign timings. Auto runs only during office hours and skips holidays.') }}
        </p>
      </div>
      <div class="flex item-center space-x-2 w-3/12 justify-end">
        <Button :label="__('Save')" variant="solid" :loading="saving" @click="save" />
      </div>
    </div>

    <div class="flex flex-col gap-6 overflow-y-auto">
      <div class="rounded border p-4 bg-white">
        <div class="flex gap-6 items-center">
          <Switch v-model="enforceOfficeHours" />
          <div>
            <div class="font-medium">{{ __('Enforce Office Hours') }}</div>
            <div class="text-sm text-ink-gray-6">{{ __('When enabled, automatic assignments and reassignments run only during office hours on working days.') }}</div>
          </div>
        </div>
        <div class="flex gap-6 items-center mt-4">
          <Switch v-model="enforceManual" />
          <div>
            <div class="font-medium">{{ __('Enforce on Manual Assignment') }}</div>
            <div class="text-sm text-ink-gray-6">{{ __('If enabled, manual assignments are also blocked outside office hours.') }}</div>
          </div>
        </div>
      </div>

      <div class="rounded border p-4 bg-white">
        <div class="mb-3 font-medium">{{ __('Office Hours by Day') }}</div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div v-for="(row, idx) in hours" :key="idx" class="flex items-center gap-3">
            <Select :options="weekdayOptions" v-model="row.workday" class="w-40" />
            <input class="border rounded px-2 py-1 w-28" type="time" v-model="row.start_time" />
            <span>—</span>
            <input class="border rounded px-2 py-1 w-28" type="time" v-model="row.end_time" />
            <Button variant="ghost" size="sm" @click="remove(idx)">
              <FeatherIcon name="trash-2" class="h-4 w-4" />
            </Button>
          </div>
        </div>
        <div class="mt-3 flex gap-2">
          <Button variant="outline" @click="addRow" :label="__('Add Day')" />
          <Button variant="ghost" @click="seed" :label="__('Seed Mon–Fri 10–18, Sat 10–15')" />
        </div>
      </div>

      <div class="rounded border p-4 bg-white">
        <div class="mb-3 font-medium">{{ __('Holiday List') }}</div>
        <div class="flex gap-3 items-center">
          <Select
            class="min-w-64"
            :options="holidayOptions"
            v-model="holidayList"
            :placeholder="__('Select or type to search')"
            @search="searchHolidayLists"
          />
          <Button variant="outline" @click="openHolidayEditor" :label="__('Manage Holidays')" />
        </div>
      </div>
    </div>

    <Dialog v-model="showHolidayDialog" :options="{ size: 'lg' }">
      <template #body>
        <div class="p-4">
          <div class="font-semibold mb-2">{{ __('Additional Holidays') }}</div>
          <div class="text-sm text-ink-gray-6 mb-3">{{ __('Add date entries for the selected holiday list.') }}</div>
          <div class="space-y-2 max-h-72 overflow-y-auto">
            <div v-for="(d, i) in holidayDates" :key="i" class="flex gap-2 items-center">
              <input type="date" class="border rounded px-2 py-1" v-model="holidayDates[i]" />
              <Button variant="ghost" size="sm" @click="holidayDates.splice(i,1)">
                <FeatherIcon name="x" class="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div class="mt-3 flex gap-2">
            <Button variant="outline" @click="holidayDates.push('')" :label="__('Add Date')" />
            <Button variant="solid" :loading="savingHolidays" @click="saveHolidayList" :label="__('Save Holidays')" />
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createResource, Dialog, Button, Select, Switch, FeatherIcon, toast } from 'frappe-ui'

const enforceOfficeHours = ref(true)
const enforceManual = ref(false)
const holidayList = ref('')
const hours = ref([])
const saving = ref(false)
const holidayOptions = ref([])
const showHolidayDialog = ref(false)
const savingHolidays = ref(false)
const holidayDates = ref([])

const weekdayOptions = [
  { label: 'Monday', value: 'Monday' },
  { label: 'Tuesday', value: 'Tuesday' },
  { label: 'Wednesday', value: 'Wednesday' },
  { label: 'Thursday', value: 'Thursday' },
  { label: 'Friday', value: 'Friday' },
  { label: 'Saturday', value: 'Saturday' },
  { label: 'Sunday', value: 'Sunday' },
]

function addRow() {
  hours.value.push({ workday: 'Monday', start_time: '10:00', end_time: '18:00' })
}
function remove(idx) {
  hours.value.splice(idx, 1)
}

async function load() {
  const data = await createResource({ url: 'crm.api.office_hours.get_settings' }).fetch()
  enforceOfficeHours.value = Boolean(data.enforce_office_hours)
  enforceManual.value = Boolean(data.enforce_on_manual_assignment)
  holidayList.value = data.holiday_list || ''
  hours.value = (data.office_hours || []).map(r => ({
    workday: r.workday,
    start_time: (r.start_time || '').slice(0,5),
    end_time: (r.end_time || '').slice(0,5),
  }))
}

async function save() {
  try {
    saving.value = true
    const payload = {
      enforce_office_hours: enforceOfficeHours.value ? 1 : 0,
      enforce_on_manual_assignment: enforceManual.value ? 1 : 0,
      holiday_list: holidayList.value,
      office_hours: hours.value.map(r => ({
        workday: r.workday,
        start_time: r.start_time + ':00',
        end_time: r.end_time + ':00',
      }))
    }
    await createResource({ url: 'crm.api.office_hours.set_settings', params: payload }).fetch()
    toast.success(__('Office Hours saved'))
  } catch (e) {
    toast.error(__('Failed to save Office Hours'))
    console.error(e)
  } finally {
    saving.value = false
  }
}

async function seed() {
  await createResource({ url: 'crm.api.office_hours.seed_default_hours' }).fetch()
  await load()
}

async function searchHolidayLists(q) {
  const rows = await createResource({ url: 'crm.api.office_hours.list_holiday_lists', params: { search: q } }).fetch()
  holidayOptions.value = (rows || []).map(r => ({ label: r.name, value: r.name }))
}

function openHolidayEditor() {
  if (!holidayList.value) {
    toast.error(__('Select a Holiday List first'))
    return
  }
  showHolidayDialog.value = true
}

async function saveHolidayList() {
  try {
    savingHolidays.value = true
    const rows = holidayDates.value.filter(Boolean)
    if (!holidayList.value) return
    await createResource({ url: 'crm.api.office_hours.upsert_holiday_list', params: { name: holidayList.value, dates: JSON.stringify(rows) } }).fetch()
    toast.success(__('Holiday list saved'))
  } catch (e) {
    toast.error(__('Failed to save holiday list'))
  } finally {
    savingHolidays.value = false
    showHolidayDialog.value = false
  }
}

onMounted(load)
</script>



