<template>
  <FormControl
    v-if="filter.fieldtype == 'Check'"
    :label="filter.label"
    type="checkbox"
    v-model="filter.value"
    @change.stop="updateFilter(filter, $event.target.checked)"
  />
  <FormControl
    v-else-if="filter.fieldtype === 'Select'"
    class="form-control cursor-pointer [&_select]:cursor-pointer"
    type="select"
    v-model="filter.value"
    :options="filter.options"
    :placeholder="filter.label"
    @change.stop="updateFilter(filter, $event.target.value)"
  />
  <FormControl
    v-else-if="filter.fieldtype === 'Link' && (filter.options === 'User' || filter.fieldname === 'employee')"
    class="form-control cursor-pointer [&_select]:cursor-pointer"
    type="select"
    v-model="filter.value"
    :options="userOptions"
    :placeholder="filter.label"
    @change.stop="updateFilter(filter, $event.target.value)"
  />
  <Link
    v-else-if="filter.fieldtype === 'Link' && typeof filter.options === 'string'"
    :value="filter.value"
    :doctype="filter.options"
    :placeholder="filter.label"
    @change="(data) => updateFilter(filter, data)"
  />
  <FormControl
    v-else-if="filter.fieldtype === 'Link' && Array.isArray(filter.options)"
    class="form-control cursor-pointer [&_select]:cursor-pointer"
    type="select"
    v-model="filter.value"
    :options="filter.options"
    :placeholder="filter.label"
    @change.stop="updateFilter(filter, $event.target.value)"
  />
  <CustomDateTimePicker
    v-else-if="['Date', 'Datetime'].includes(filter.fieldtype)"
    class="border-none"
    :model-value="filter.value"
    mode="date"
    :show-time="false"
    :prevent-auto-fill="true"
    :auto-default="false"
    :placeholder="filter.label"
    @change="(v) => updateFilter(filter, v)"
    @update:modelValue="(v) => (filter.value = v)"
  />
  <FormControl
    v-else
    v-model="filter.value"
    type="text"
    :placeholder="filter.label"
    @input.stop="debouncedFn(filter, $event.target.value)"
  />
</template>
<script setup>
import Link from '@/components/Controls/Link.vue'
import { FormControl, createResource, call } from 'frappe-ui'
import CustomDateTimePicker from './CustomDateTimePicker.vue'
import { useDebounceFn } from '@vueuse/core'
import { ref, onMounted } from 'vue'

const props = defineProps({
  filter: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['applyQuickFilter'])

const debouncedFn = useDebounceFn((f, value) => {
  emit('applyQuickFilter', f, value)
}, 500)

function updateFilter(f, value) {
  emit('applyQuickFilter', f, value)
}

// If filter targets Users, load users for dropdown
const userOptions = ref([])
onMounted(async () => {
  if (props.filter && props.filter.fieldtype === 'Link' && (props.filter.options === 'User' || props.filter.fieldname === 'employee')) {
    try {
      const res = await call('frappe.client.get_list', { doctype: 'User', fields: ['name', 'full_name'], filters: { enabled: 1 }, limit_page_length: 500 })
      const list = res || []
      userOptions.value = list.map(u => ({ label: u.full_name || u.name, value: u.name }))
      if (!userOptions.value.some(o => o.value === '')) userOptions.value.unshift({ label: '', value: '' })
    } catch (e) {
      // ignore
    }
  }
})
</script>
