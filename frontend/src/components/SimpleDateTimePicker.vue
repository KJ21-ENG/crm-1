<template>
  <flat-pickr
    v-bind="$attrs"
    :modelValue="modelValue"
    @update:modelValue="emit('update:modelValue', $event)"
    :config="config"
    class="frappe-dtp-input"
    placeholder="Select date and time"
  />
</template>

<script setup>
import flatPickr from 'vue-flatpickr-component'
import 'flatpickr/dist/themes/material_blue.css'

const props = defineProps({
  modelValue: [String, Date]
})
const emit = defineEmits(['update:modelValue'])

const config = {
  enableTime: true,
  dateFormat: 'Y-m-d H:i',
  time_24hr: false,
  allowInput: false,
  wrap: false,
  minuteIncrement: 5,
}
</script>

<style scoped>
.frappe-dtp-input {
  width: 100%;
  font-size: 1rem;
  padding: 0.5em 0.75em;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #22223b;
  font-family: inherit;
  transition: border 0.2s, box-shadow 0.2s;
  outline: none;
  box-sizing: border-box;
  height: 40px;
  min-height: unset;
  max-width: unset;
}
.frappe-dtp-input:focus {
  border: 1.5px solid #383838;
  box-shadow: 0 0 0 2px #e5e7eb;
}
/* Flatpickr popup and calendar to match Frappe theme */
:deep(.flatpickr-calendar) {
  border-radius: 6px;
  box-shadow: 0 2px 16px rgba(31, 41, 55, 0.10);
  border: 1px solid #e5e7eb;
  background: #fff;
  font-family: inherit;
}
:deep(.flatpickr-months .flatpickr-month) {
  background: #f8fafc;
  color: #22223b;
}
:deep(.flatpickr-current-month input.cur-year) {
  color: #22223b;
}
:deep(.flatpickr-months .flatpickr-prev-month),
:deep(.flatpickr-months .flatpickr-next-month) {
  color: #383838;
}
:deep(.flatpickr-monthDropdown-months .flatpickr-monthDropdown-month.selected),
:deep(.flatpickr-monthDropdown-months .flatpickr-monthDropdown-month:hover) {
  background: #383838;
  color: #fff;
}
:deep(.flatpickr-day.selected),
:deep(.flatpickr-day.startRange),
:deep(.flatpickr-day.endRange),
:deep(.flatpickr-day.selected.inRange),
:deep(.flatpickr-day.startRange.inRange),
:deep(.flatpickr-day.endRange.inRange),
:deep(.flatpickr-day.selected:focus),
:deep(.flatpickr-day.selected:hover) {
  background: #383838 !important;
  color: #fff !important;
  border-radius: 50%;
}
:deep(.flatpickr-day.today) {
  border-color: #a1a1aa;
  color: #22223b;
}
:deep(.flatpickr-time input),
:deep(.flatpickr-time .flatpickr-am-pm) {
  color: #22223b;
  background: #f8fafc;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
  font-size: 1rem;
}
:deep(.flatpickr-time input:focus) {
  border: 1.5px solid #383838;
  box-shadow: 0 0 0 2px #e5e7eb;
}
:deep(.flatpickr-time .flatpickr-am-pm.selected) {
  background: #383838;
  color: #fff;
}
:deep(.flatpickr-weekday) {
  color: #6b7280;
}
:deep(.flatpickr-calendar .flatpickr-next-month),
:deep(.flatpickr-calendar .flatpickr-prev-month) {
  color: #383838;
}
:deep(.flatpickr-calendar .flatpickr-monthDropdown-months .flatpickr-monthDropdown-month) {
  color: #22223b;
}
:deep(.flatpickr-calendar .flatpickr-monthDropdown-months .flatpickr-monthDropdown-month.selected) {
  background: #383838;
  color: #fff;
}
:deep(.flatpickr-calendar .flatpickr-time-separator) {
  color: #22223b;
}
:deep(.flatpickr-calendar .flatpickr-time input) {
  color: #22223b;
}
:deep(.flatpickr-calendar .flatpickr-time input:focus) {
  border: 1.5px solid #383838;
  box-shadow: 0 0 0 2px #e5e7eb;
}
:deep(.flatpickr-calendar .flatpickr-am-pm) {
  color: #22223b;
}
:deep(.flatpickr-calendar .flatpickr-am-pm.selected) {
  background: #383838;
  color: #fff;
}
:deep(.flatpickr-calendar .flatpickr-button) {
  background: #383838;
  color: #fff;
  border-radius: 6px;
  border: none;
  font-weight: 500;
  transition: background 0.2s;
}
:deep(.flatpickr-calendar .flatpickr-button:hover) {
  background: #111113;
}
:deep(.flatpickr-months .flatpickr-month .flatpickr-current-month .flatpickr-monthDropdown-months .flatpickr-monthDropdown-month.selected) {
  background: #383838;
  color: #fff;
}
:deep(.flatpickr-months .flatpickr-month .flatpickr-current-month .flatpickr-monthDropdown-months .flatpickr-monthDropdown-month:hover) {
  background: #383838;
  color: #fff;
}
</style> 